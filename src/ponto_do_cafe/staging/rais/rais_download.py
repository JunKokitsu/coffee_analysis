from pathlib import Path

from ponto_do_cafe.infrastructure.archive_extractor import ArchiveExtractor
from ponto_do_cafe.infrastructure.data_directories import DataDirectories
from ponto_do_cafe.infrastructure.ftp_client import FtpClient
from ponto_do_cafe.staging.rais.rais_releases import RaisReleases

RAIS_HOST = "ftp.mtps.gov.br"
RAIS_DIRECTORY = "/pdet/microdados/RAIS"
RAIS_FILE_NAMES = ("RAIS_ESTAB_PUB", "RAIS_VINC_PUB_SP")


class RaisDownload:
    def __init__(self, ftp_client: FtpClient, releases: RaisReleases, extractor: ArchiveExtractor, directories: DataDirectories) -> None:
        self._ftp_client = ftp_client
        self._releases = releases
        self._extractor = extractor
        self._directories = directories

    def build(self) -> Path:
        year = self._releases.latest_year()
        print(f"RAIS: ano-base {year}", flush=True)
        for file_name in RAIS_FILE_NAMES:
            self._download_and_extract(year, file_name)
        return self._directories.raw_file("rais", year)

    def _download_and_extract(self, year: str, file_name: str) -> None:
        archive = self._download_archive(year, file_name)
        self._extract_if_needed(year, archive, file_name)

    def _download_archive(self, year: str, file_name: str) -> Path:
        remote_path = f"{RAIS_DIRECTORY}/{year}/{file_name}.7z"
        destination = self._directories.raw_file("rais", year, f"{file_name}.7z")
        return self._ftp_client.download(RAIS_HOST, remote_path, destination)

    def _extract_if_needed(self, year: str, archive: Path, file_name: str) -> None:
        marker = self._directories.raw_file("rais", year, f"{file_name}.COMT")
        if self._marker_exists(marker):
            return
        self._extractor.extract_seven_zip(archive, archive.parent)

    def _marker_exists(self, marker: Path) -> bool:
        return marker.exists() and marker.stat().st_size > 0
