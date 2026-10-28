import threading
from collections.abc import Iterator
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from ponto_do_cafe.infrastructure.http_client import HttpClient
from tests.range_ignoring_handler import RangeIgnoringHandler
from tests.range_request_handler import RangeRequestHandler

CONTENT = (b"0123456789" * 9) + b"01234"


def start_server(content: bytes) -> tuple[ThreadingHTTPServer, type[RangeRequestHandler]]:
    handler_class = type("BoundRangeRequestHandler", (RangeRequestHandler,), {"content": content, "request_count": 0})
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler_class)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, handler_class


@pytest.fixture
def http_server() -> Iterator[tuple[ThreadingHTTPServer, type[RangeRequestHandler]]]:
    server, handler_class = start_server(CONTENT)
    yield server, handler_class
    server.shutdown()


def server_url(server: ThreadingHTTPServer) -> str:
    return f"http://127.0.0.1:{server.server_port}/file"


def test_text_returns_body(http_server: tuple[ThreadingHTTPServer, type[RangeRequestHandler]]) -> None:
    server, _ = http_server
    assert HttpClient().text(server_url(server)) == CONTENT.decode()


def test_download_writes_content_and_is_idempotent(
    http_server: tuple[ThreadingHTTPServer, type[RangeRequestHandler]],
    tmp_path: Path,
) -> None:
    server, handler_class = http_server
    destination = tmp_path / "downloaded.bin"
    client = HttpClient()
    client.download(server_url(server), destination)
    assert destination.read_bytes() == CONTENT
    requests_after_first_download = handler_class.request_count
    client.download(server_url(server), destination)
    assert handler_class.request_count == requests_after_first_download


def test_download_in_parts_reconstructs_content(
    http_server: tuple[ThreadingHTTPServer, type[RangeRequestHandler]],
    tmp_path: Path,
) -> None:
    server, _ = http_server
    destination = tmp_path / "reconstructed.bin"
    HttpClient().download_in_parts(server_url(server), destination, part_size=10)
    assert destination.read_bytes() == CONTENT
    assert not (tmp_path / "partes").exists()


def test_download_in_parts_resumes_incomplete_part(
    http_server: tuple[ThreadingHTTPServer, type[RangeRequestHandler]],
    tmp_path: Path,
) -> None:
    server, _ = http_server
    destination = tmp_path / "resumed.bin"
    parts_directory = destination.parent / "partes"
    parts_directory.mkdir(parents=True)
    incomplete_part_path = parts_directory / f"{destination.name}.{0:012d}"
    incomplete_part_path.write_bytes(CONTENT[:4])
    HttpClient().download_in_parts(server_url(server), destination, part_size=10)
    assert destination.read_bytes() == CONTENT


def test_download_in_parts_rejects_server_that_ignores_range(tmp_path: Path) -> None:
    handler_class = type("BoundRangeIgnoringHandler", (RangeIgnoringHandler,), {"content": CONTENT, "request_count": 0})
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler_class)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    destination = tmp_path / "corrompido.bin"
    with pytest.raises(RuntimeError):
        HttpClient(failed_part_attempt_delay_seconds=0).download_in_parts(server_url(server), destination, part_size=10)
    server.shutdown()
    assert not destination.exists()


def test_download_in_parts_keeps_parts_of_other_files(
    http_server: tuple[ThreadingHTTPServer, type[RangeRequestHandler]],
    tmp_path: Path,
) -> None:
    server, _ = http_server
    other_part = tmp_path / "partes" / "outro_arquivo.zip.000000000000"
    other_part.parent.mkdir()
    other_part.write_bytes(b"parcial")
    HttpClient().download_in_parts(server_url(server), tmp_path / "reconstruido.bin", part_size=10)
    assert other_part.read_bytes() == b"parcial"
