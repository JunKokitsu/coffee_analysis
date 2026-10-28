import ftplib
from pathlib import Path

DEFAULT_TIMEOUT_SECONDS = 120
PARTIAL_FILE_SUFFIX = ".parcial"


class FtpClient:
    def __init__(self, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> None:
        self._timeout_seconds = timeout_seconds

    def download(self, host: str, remote_path: str, destination: Path) -> Path:
        if self._file_is_complete(destination):
            return destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        self._retrieve_to_destination(host, remote_path, destination)
        return destination

    def _retrieve_to_destination(self, host: str, remote_path: str, destination: Path) -> None:
        partial = self._partial_path(destination)
        with ftplib.FTP(host, timeout=self._timeout_seconds) as connection:
            connection.login()
            self._retrieve_binary(connection, remote_path, partial)
        partial.rename(destination)

    def _retrieve_binary(self, connection: ftplib.FTP, remote_path: str, partial: Path) -> None:
        with partial.open("wb") as file:
            connection.retrbinary(f"RETR {remote_path}", file.write)

    def _partial_path(self, destination: Path) -> Path:
        return destination.with_name(destination.name + PARTIAL_FILE_SUFFIX)

    def _file_is_complete(self, destination: Path) -> bool:
        return destination.exists() and destination.stat().st_size > 0
