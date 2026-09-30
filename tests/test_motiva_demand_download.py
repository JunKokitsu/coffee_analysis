from pathlib import Path

from coffee_analysis.infrastructure.data_directories import DataDirectories
from coffee_analysis.staging.mobility.motiva_demand_download import MotivaDemandDownload
from tests.recording_file_http_client import RecordingFileHttpClient
from tests.encoded_name_motiva_releases import EncodedNameMotivaDemandReleases
from tests.recording_motiva_releases import RecordingMotivaDemandReleases


def test_motiva_demand_download_creates_base_directory(tmp_path: Path) -> None:
    http_client = RecordingFileHttpClient()
    releases = RecordingMotivaDemandReleases(http_client)
    directories = DataDirectories(tmp_path, "2026-09")
    downloader = MotivaDemandDownload(http_client, releases, directories)

    result = downloader.build()

    assert result == tmp_path / "data" / "raw" / "motiva" / "2026-09"


def test_motiva_demand_download_organizes_by_folder(tmp_path: Path) -> None:
    http_client = RecordingFileHttpClient()
    releases = RecordingMotivaDemandReleases(http_client)
    directories = DataDirectories(tmp_path, "2026-09")
    downloader = MotivaDemandDownload(http_client, releases, directories)

    downloader.build()

    files_by_folder = {}
    for url, destination in http_client.downloaded_files:
        folder = destination.parent.name
        files_by_folder.setdefault(folder, []).append((url, destination.name))

    assert "linha-4" in files_by_folder
    assert "linha-5" in files_by_folder
    assert "linha-8-e-9" in files_by_folder


def test_motiva_demand_download_extracts_file_names_from_urls(tmp_path: Path) -> None:
    http_client = RecordingFileHttpClient()
    releases = RecordingMotivaDemandReleases(http_client)
    directories = DataDirectories(tmp_path, "2026-09")
    downloader = MotivaDemandDownload(http_client, releases, directories)

    downloader.build()

    file_destinations = [destination.name for url, destination in http_client.downloaded_files]

    assert "relatorio_2024.pdf" in file_destinations
    assert "relatorio_2023.pdf" in file_destinations
    assert "dados_2024.pdf" in file_destinations
    assert "report.pdf" in file_destinations


def test_motiva_demand_download_requests_all_pages(tmp_path: Path) -> None:
    http_client = RecordingFileHttpClient()
    releases = RecordingMotivaDemandReleases(http_client)
    directories = DataDirectories(tmp_path, "2026-09")
    downloader = MotivaDemandDownload(http_client, releases, directories)

    downloader.build()

    assert "linha-4-amarela" in releases.requested_slugs
    assert "linha-5-lilas" in releases.requested_slugs
    assert "viamobilidade8e9" in releases.requested_slugs


def test_motiva_demand_download_total_files(tmp_path: Path) -> None:
    http_client = RecordingFileHttpClient()
    releases = RecordingMotivaDemandReleases(http_client)
    directories = DataDirectories(tmp_path, "2026-09")
    downloader = MotivaDemandDownload(http_client, releases, directories)

    downloader.build()

    assert len(http_client.downloaded_files) == 4


def test_motiva_demand_download_keeps_encoded_file_name(tmp_path: Path) -> None:
    http_client = RecordingFileHttpClient()
    releases = EncodedNameMotivaDemandReleases(http_client)
    MotivaDemandDownload(http_client, releases, DataDirectories(tmp_path, "2026-09")).build()
    names = {destination.name for _, destination in http_client.downloaded_files}
    assert names == {"Demanda%20de%20passageiros%20-%20Maio%202026.pdf"}
