from pathlib import Path

from coffee_analysis.infrastructure.ftp_client import FtpClient

FAKE_FILE_CONTENT = b"conteudo de teste"


class FakeRaisFtpClient(FtpClient):
    def __init__(self) -> None:
        super().__init__()
        self.download_calls: list[tuple[str, str, Path]] = []

    def download(self, host: str, remote_path: str, destination: Path) -> Path:
        self.download_calls.append((host, remote_path, destination))
        return self._write_fake_file(destination)

    def _write_fake_file(self, destination: Path) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(FAKE_FILE_CONTENT)
        return destination
