from pathlib import Path

from coffee_analysis.infrastructure.http_client import HttpClient


class RecordingDownloadClient(HttpClient):
    def __init__(self) -> None:
        super().__init__()
        self.download_calls: list[tuple[str, Path]] = []

    def download(
        self,
        url: str,
        destination: Path,
        authentication: tuple[str, str] | None = None,
    ) -> Path:
        self.download_calls.append((url, destination))
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"conteudo")
        return destination
