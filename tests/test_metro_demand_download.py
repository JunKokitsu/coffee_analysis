from pathlib import Path

import pytest

from coffee_analysis.infrastructure.data_directories import DataDirectories
from coffee_analysis.staging.mobility.metro_demand_download import MetroDemandDownload
from tests.recording_file_http_client import RecordingFileHttpClient
from tests.recording_metro_releases import RecordingMetroReleases


def test_metro_demand_download_for_two_years(tmp_path: Path) -> None:
    http_client = RecordingFileHttpClient()
    releases = RecordingMetroReleases(http_client)
    directories = DataDirectories(tmp_path, "2026-09")
    downloader = MetroDemandDownload(http_client, releases, directories)

    result = downloader.build()

    assert result == tmp_path / "data" / "raw" / "metro" / "2026-09"
    assert len(http_client.downloaded_files) == 2
    assert http_client.downloaded_files[0][0] == "https://exemplo.com/demanda_2025.csv"
    assert http_client.downloaded_files[1][0] == "https://exemplo.com/demanda_2026.csv"


def test_metro_demand_download_destination_paths(tmp_path: Path) -> None:
    http_client = RecordingFileHttpClient()
    releases = RecordingMetroReleases(http_client)
    directories = DataDirectories(tmp_path, "2026-09")
    downloader = MetroDemandDownload(http_client, releases, directories)

    downloader.build()

    expected_2025 = tmp_path / "data" / "raw" / "metro" / "2026-09" / "demanda_estacoes_2025.csv"
    expected_2026 = tmp_path / "data" / "raw" / "metro" / "2026-09" / "demanda_estacoes_2026.csv"
    assert http_client.downloaded_files[0][1] == expected_2025
    assert http_client.downloaded_files[1][1] == expected_2026


def test_metro_demand_download_skips_existing_file(tmp_path: Path) -> None:
    http_client = RecordingFileHttpClient()
    releases = RecordingMetroReleases(http_client)
    directories = DataDirectories(tmp_path, "2026-09")

    existing_file = tmp_path / "data" / "raw" / "metro" / "2026-09" / "demanda_estacoes_2025.csv"
    existing_file.parent.mkdir(parents=True, exist_ok=True)
    existing_file.write_bytes(b"existing content")

    downloader = MetroDemandDownload(http_client, releases, directories)
    downloader.build()

    assert len(releases.requested_years) == 1
    assert 2025 not in releases.requested_years
    assert 2026 in releases.requested_years


def test_metro_demand_download_raises_error_when_url_not_found(tmp_path: Path) -> None:
    http_client = RecordingFileHttpClient()
    releases = RecordingMetroReleases(http_client)
    directories = DataDirectories(tmp_path, "2018-09")
    downloader = MetroDemandDownload(http_client, releases, directories)

    with pytest.raises(FileNotFoundError, match="URL não encontrada para demanda do metrô em 2017"):
        downloader.build()
