from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

from ponto_do_cafe.infrastructure.data_directories import DataDirectories
from ponto_do_cafe.infrastructure.http_client import HttpClient
from ponto_do_cafe.staging.mobility.motiva_demand_releases import MotivaDemandReleases

PAGE_SLUG_TO_FOLDER = {
    "linha-4-amarela": "linha-4",
    "linha-5-lilas": "linha-5",
    "viamobilidade8e9": "linha-8-e-9",
}


class MotivaDemandDownload:
    def __init__(
        self,
        http_client: HttpClient,
        releases: MotivaDemandReleases,
        directories: DataDirectories,
    ) -> None:
        self._http_client = http_client
        self._releases = releases
        self._directories = directories

    def build(self) -> Path:
        downloads = [(url, folder_name) for page_slug, folder_name in PAGE_SLUG_TO_FOLDER.items() for url in self._releases.pdf_urls(page_slug)]
        for url, folder_name in downloads:
            self._download_pdf(url, folder_name)
        return self._directories.raw_file("motiva", self._directories.competence)

    def _download_pdf(self, url: str, folder_name: str) -> None:
        file_name = self._extract_file_name_from_url(url)
        destination = self._directories.raw_file(
            "motiva",
            self._directories.competence,
            folder_name,
            file_name,
        )
        self._http_client.download(url, destination)

    def _extract_file_name_from_url(self, url: str) -> str:
        parsed_url = urlparse(url)
        path_object = PurePosixPath(parsed_url.path)
        return path_object.name
