from pathlib import Path

from coffee_analysis.infrastructure.archive_extractor import ArchiveExtractor
from coffee_analysis.infrastructure.data_directories import DataDirectories
from coffee_analysis.infrastructure.http_client import HttpClient


class OriginDestinationSurveyDownload:
    def __init__(
        self,
        http_client: HttpClient,
        extractor: ArchiveExtractor,
        directories: DataDirectories,
    ) -> None:
        self._http_client = http_client
        self._extractor = extractor
        self._directories = directories

    def build(self) -> Path:
        survey_directory = self._directories.raw_file("pesquisa_od", "2023")
        archive = survey_directory / "Site_190225_PesquisaOD2023.zip"
        url = "https://transparencia.metrosp.com.br/sites/default/files/Site_190225_PesquisaOD2023.zip"

        self._http_client.download(url, archive)
        self._extract_if_needed(archive, survey_directory)
        return survey_directory

    def _extract_if_needed(self, archive: Path, survey_directory: Path) -> None:
        extracted_directory = survey_directory / "Site_190225"
        if extracted_directory.exists():
            return
        self._extractor.unzip(archive, survey_directory)
