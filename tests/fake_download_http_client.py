from pathlib import Path

from ponto_do_cafe.infrastructure.http_client import HttpClient

FAKE_FILE_CONTENT = b"conteudo de teste"


class FakeDownloadHttpClient(HttpClient):
    def __init__(self) -> None:
        super().__init__()
        self.download_calls: list[tuple[str, Path, tuple[str, str] | None]] = []
        self.download_in_parts_calls: list[tuple[str, Path, int, tuple[str, str] | None]] = []

    def download(self, url: str, destination: Path, authentication: tuple[str, str] | None = None) -> Path:
        self.download_calls.append((url, destination, authentication))
        return self._write_fake_file(destination)

    def download_in_parts(self, url: str, destination: Path, part_size: int, authentication: tuple[str, str] | None = None) -> Path:
        self.download_in_parts_calls.append((url, destination, part_size, authentication))
        return self._write_fake_file(destination)

    def _write_fake_file(self, destination: Path) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(FAKE_FILE_CONTENT)
        return destination
