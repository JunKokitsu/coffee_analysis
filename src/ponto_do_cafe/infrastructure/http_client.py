import re
import time
from pathlib import Path
from typing import BinaryIO

import requests
import urllib3.util
from requests.adapters import HTTPAdapter

DEFAULT_TIMEOUT_SECONDS = 120
RETRY_TOTAL_ATTEMPTS = 5
RETRY_BACKOFF_FACTOR = 2
RETRYABLE_STATUS_CODES = (429, 500, 502, 503, 504)
MAXIMUM_PART_ATTEMPTS = 400
FAILED_PART_ATTEMPT_DELAY_SECONDS = 5.0
PARTIAL_CONTENT_STATUS = 206
STREAM_CHUNK_SIZE_BYTES = 1024 * 1024
PARTIAL_FILE_SUFFIX = ".parcial"
PARTS_DIRECTORY_NAME = "partes"
CONTENT_LENGTH_HEADER_NAME = "Content-Length"
CONTENT_LENGTH_PATTERN = re.compile(r"<[^>]*getcontentlength[^>]*>(\d+)</[^>]*getcontentlength[^>]*>")


class HttpClient:
    def __init__(self, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS, failed_part_attempt_delay_seconds: float = FAILED_PART_ATTEMPT_DELAY_SECONDS) -> None:
        self._timeout_seconds = timeout_seconds
        self._failed_part_attempt_delay_seconds = failed_part_attempt_delay_seconds
        self._session = self._build_session()

    def _build_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0"})
        self._mount_retrying_adapter(session)
        return session

    def _mount_retrying_adapter(self, session: requests.Session) -> None:
        adapter = HTTPAdapter(max_retries=self._build_retry())
        session.mount("http://", adapter)
        session.mount("https://", adapter)

    def _build_retry(self) -> urllib3.util.Retry:
        return urllib3.util.Retry(
            total=RETRY_TOTAL_ATTEMPTS,
            backoff_factor=RETRY_BACKOFF_FACTOR,
            status_forcelist=RETRYABLE_STATUS_CODES,
            allowed_methods=None,
        )

    def text(self, url: str) -> str:
        response = self._session.get(url, timeout=self._timeout_seconds)
        response.raise_for_status()
        return response.text

    def request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        authentication: tuple[str, str] | None = None,
    ) -> requests.Response:
        response = self._session.request(
            method,
            url,
            headers=headers,
            auth=authentication,
            timeout=self._timeout_seconds,
        )
        response.raise_for_status()
        return response

    def download(
        self,
        url: str,
        destination: Path,
        authentication: tuple[str, str] | None = None,
    ) -> Path:
        if self._file_is_complete(destination):
            return destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        self._stream_download_to_destination(url, destination, authentication)
        return destination

    def _stream_download_to_destination(
        self,
        url: str,
        destination: Path,
        authentication: tuple[str, str] | None,
    ) -> None:
        partial = self._partial_path(destination)
        response = self._session.get(url, auth=authentication, timeout=self._timeout_seconds, stream=True)
        response.raise_for_status()
        self._write_response_to_new_file(response, partial)
        partial.rename(destination)

    def download_in_parts(
        self,
        url: str,
        destination: Path,
        part_size: int,
        authentication: tuple[str, str] | None = None,
    ) -> Path:
        if self._file_is_complete(destination):
            return destination
        parts_directory = destination.parent / PARTS_DIRECTORY_NAME
        parts_directory.mkdir(parents=True, exist_ok=True)
        total_size = self._discover_total_size(url, authentication)
        part_paths = self._download_all_parts(url, parts_directory, destination.name, total_size, part_size, authentication)
        self._concatenate_parts(part_paths, destination)
        self._remove_parts(part_paths, parts_directory)
        return destination

    def _discover_total_size(self, url: str, authentication: tuple[str, str] | None) -> int:
        content_length = self._content_length_from_head(url, authentication)
        if content_length is not None:
            return content_length
        return self._content_length_from_propfind(url, authentication)

    def _content_length_from_head(self, url: str, authentication: tuple[str, str] | None) -> int | None:
        response = self._session.head(url, auth=authentication, timeout=self._timeout_seconds)
        header_value = response.headers.get(CONTENT_LENGTH_HEADER_NAME)
        if header_value is None:
            return None
        return int(header_value)

    def _content_length_from_propfind(self, url: str, authentication: tuple[str, str] | None) -> int:
        response = self.request("PROPFIND", url, headers={"Depth": "0"}, authentication=authentication)
        return self._parse_content_length(response.text)

    def _parse_content_length(self, propfind_body: str) -> int:
        match = CONTENT_LENGTH_PATTERN.search(propfind_body)
        return self._require_content_length_match(match)

    def _require_content_length_match(self, match: re.Match[str] | None) -> int:
        if match is not None:
            return int(match.group(1))
        raise ValueError("resposta do PROPFIND sem getcontentlength")

    def _download_all_parts(
        self,
        url: str,
        parts_directory: Path,
        file_name: str,
        total_size: int,
        part_size: int,
        authentication: tuple[str, str] | None,
    ) -> list[Path]:
        part_ranges = self._build_part_ranges(total_size, part_size)
        return [self._download_part(url, parts_directory, file_name, part_range, authentication) for part_range in part_ranges]

    def _build_part_ranges(self, total_size: int, part_size: int) -> list[tuple[int, int]]:
        starts = range(0, total_size, part_size)
        return [(start, min(start + part_size, total_size) - 1) for start in starts]

    def _download_part(
        self,
        url: str,
        parts_directory: Path,
        file_name: str,
        part_range: tuple[int, int],
        authentication: tuple[str, str] | None,
    ) -> Path:
        start, end = part_range
        part_path = parts_directory / f"{file_name}.{start:012d}"
        expected_size = end - start + 1
        self._attempt_part_until_complete(url, part_path, start, end, expected_size, authentication)
        return part_path

    def _attempt_part_until_complete(
        self,
        url: str,
        part_path: Path,
        start: int,
        end: int,
        expected_size: int,
        authentication: tuple[str, str] | None,
    ) -> None:
        for _ in range(MAXIMUM_PART_ATTEMPTS):
            self._attempt_part_once(url, part_path, start, end, expected_size, authentication)
        self._require_part_complete(part_path, expected_size)

    def _attempt_part_once(
        self,
        url: str,
        part_path: Path,
        start: int,
        end: int,
        expected_size: int,
        authentication: tuple[str, str] | None,
    ) -> None:
        if self._part_is_complete(part_path, expected_size):
            return
        self._append_part_chunk(url, part_path, start, end, authentication)

    def _require_part_complete(self, part_path: Path, expected_size: int) -> None:
        if self._part_is_complete(part_path, expected_size):
            return
        raise RuntimeError(f"não foi possível completar a parte {part_path} após {MAXIMUM_PART_ATTEMPTS} tentativas")

    def _part_is_complete(self, part_path: Path, expected_size: int) -> bool:
        return part_path.exists() and part_path.stat().st_size >= expected_size

    def _current_part_size(self, part_path: Path) -> int:
        if part_path.exists():
            return part_path.stat().st_size
        return 0

    def _append_part_chunk(
        self,
        url: str,
        part_path: Path,
        start: int,
        end: int,
        authentication: tuple[str, str] | None,
    ) -> None:
        obtained = self._current_part_size(part_path)
        response = self._request_part_range(url, start + obtained, end, authentication)
        appended = self._append_response_if_partial_content(response, part_path)
        self._wait_after_failed_attempt(appended)

    def _request_part_range(
        self,
        url: str,
        start: int,
        end: int,
        authentication: tuple[str, str] | None,
    ) -> requests.Response | None:
        try:
            return self._session.get(
                url,
                headers={"Range": f"bytes={start}-{end}"},
                auth=authentication,
                timeout=self._timeout_seconds,
                stream=True,
            )
        except requests.RequestException:
            return None

    def _append_response_if_partial_content(self, response: requests.Response | None, part_path: Path) -> bool:
        if response is None:
            return False
        with response:
            return self._append_partial_content(response, part_path)

    def _append_partial_content(self, response: requests.Response, part_path: Path) -> bool:
        if response.status_code != PARTIAL_CONTENT_STATUS:
            return False
        return self._append_response_to_file(response, part_path)

    def _append_response_to_file(self, response: requests.Response, part_path: Path) -> bool:
        try:
            self._append_chunks(response, part_path)
        except requests.RequestException:
            return False
        return True

    def _append_chunks(self, response: requests.Response, part_path: Path) -> None:
        with part_path.open("ab") as file:
            self._write_response_chunks(response, file)

    def _wait_after_failed_attempt(self, appended: bool) -> None:
        if appended:
            return
        time.sleep(self._failed_part_attempt_delay_seconds)

    def _concatenate_parts(self, part_paths: list[Path], destination: Path) -> None:
        partial = self._partial_path(destination)
        self._write_concatenated_partial(part_paths, partial)
        partial.rename(destination)

    def _write_concatenated_partial(self, part_paths: list[Path], partial: Path) -> None:
        with partial.open("wb") as file:
            self._copy_all_parts(part_paths, file)

    def _copy_all_parts(self, part_paths: list[Path], file: BinaryIO) -> None:
        for part_path in part_paths:
            file.write(part_path.read_bytes())

    def _remove_parts(self, part_paths: list[Path], parts_directory: Path) -> None:
        for part_path in part_paths:
            part_path.unlink()
        self._remove_directory_if_empty(parts_directory)

    def _remove_directory_if_empty(self, directory: Path) -> None:
        if any(directory.iterdir()):
            return
        directory.rmdir()

    def _write_response_to_new_file(self, response: requests.Response, destination: Path) -> None:
        with destination.open("wb") as file:
            self._write_response_chunks(response, file)

    def _write_response_chunks(self, response: requests.Response, file: BinaryIO) -> None:
        for chunk in response.iter_content(chunk_size=STREAM_CHUNK_SIZE_BYTES):
            file.write(chunk)

    def _partial_path(self, destination: Path) -> Path:
        return destination.with_name(destination.name + PARTIAL_FILE_SUFFIX)

    def _file_is_complete(self, destination: Path) -> bool:
        return destination.exists() and destination.stat().st_size > 0
