from pathlib import Path

import pytest

from ponto_do_cafe.infrastructure.data_directories import DataDirectories
from ponto_do_cafe.staging.mobility.origin_destination_survey_download import OriginDestinationSurveyDownload
from tests.recording_archive_extractor import RecordingArchiveExtractor
from tests.recording_download_client import RecordingDownloadClient


def test_origin_destination_survey_download_downloads_zip(tmp_path: Path) -> None:
    client = RecordingDownloadClient()
    extractor = RecordingArchiveExtractor()
    directories = DataDirectories(tmp_path, "2026-09")

    download = OriginDestinationSurveyDownload(client, extractor, directories)
    download.build()

    assert len(client.download_calls) == 1
    assert client.download_calls[0][0] == "https://transparencia.metrosp.com.br/sites/default/files/Site_190225_PesquisaOD2023.zip"
    assert client.download_calls[0][1] == tmp_path / "data" / "raw" / "pesquisa_od" / "2023" / "Site_190225_PesquisaOD2023.zip"


def test_origin_destination_survey_download_extracts_when_directory_missing(tmp_path: Path) -> None:
    client = RecordingDownloadClient()
    extractor = RecordingArchiveExtractor()
    directories = DataDirectories(tmp_path, "2026-09")

    download = OriginDestinationSurveyDownload(client, extractor, directories)
    download.build()

    assert len(extractor.unzip_calls) == 1
    assert extractor.unzip_calls[0][0] == tmp_path / "data" / "raw" / "pesquisa_od" / "2023" / "Site_190225_PesquisaOD2023.zip"
    assert extractor.unzip_calls[0][1] == tmp_path / "data" / "raw" / "pesquisa_od" / "2023"
    assert extractor.unzip_calls[0][2] == ()
    assert extractor.unzip_calls[0][3] is False


def test_origin_destination_survey_download_skips_extraction_when_directory_exists(tmp_path: Path) -> None:
    client = RecordingDownloadClient()
    extractor = RecordingArchiveExtractor()
    directories = DataDirectories(tmp_path, "2026-09")
    survey_directory = tmp_path / "data" / "raw" / "pesquisa_od" / "2023"
    extracted_directory = survey_directory / "Site_190225"
    extracted_directory.mkdir(parents=True)

    download = OriginDestinationSurveyDownload(client, extractor, directories)
    download.build()

    assert len(extractor.unzip_calls) == 0


def test_origin_destination_survey_download_returns_survey_directory(tmp_path: Path) -> None:
    client = RecordingDownloadClient()
    extractor = RecordingArchiveExtractor()
    directories = DataDirectories(tmp_path, "2026-09")

    download = OriginDestinationSurveyDownload(client, extractor, directories)
    result = download.build()

    assert result == tmp_path / "data" / "raw" / "pesquisa_od" / "2023"
