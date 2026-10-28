from pathlib import Path

import pytest

from ponto_do_cafe.infrastructure.data_directories import DataDirectories
from ponto_do_cafe.staging.mobility.rail_stations_download import RailStationsDownload
from tests.recording_download_client import RecordingDownloadClient


def test_rail_stations_download_downloads_metro_and_trem_layers(tmp_path: Path) -> None:
    client = RecordingDownloadClient()
    directories = DataDirectories(tmp_path, "2026-09")

    download = RailStationsDownload(client, directories)
    download.build()

    assert len(client.download_calls) == 2
    assert client.download_calls[0][0] == "https://wfs.geosampa.prefeitura.sp.gov.br/geoserver/ows?service=WFS&version=2.0.0&request=GetFeature&outputFormat=application/json&srsName=EPSG:4326&typeNames=geoportal:estacao_metro"
    assert client.download_calls[0][1] == tmp_path / "data" / "raw" / "geosampa" / "2026-09" / "estacao_metro.json"
    assert client.download_calls[1][0] == "https://wfs.geosampa.prefeitura.sp.gov.br/geoserver/ows?service=WFS&version=2.0.0&request=GetFeature&outputFormat=application/json&srsName=EPSG:4326&typeNames=geoportal:estacao_trem"
    assert client.download_calls[1][1] == tmp_path / "data" / "raw" / "geosampa" / "2026-09" / "estacao_trem.json"


def test_rail_stations_download_returns_geosampa_directory(tmp_path: Path) -> None:
    client = RecordingDownloadClient()
    directories = DataDirectories(tmp_path, "2026-09")

    download = RailStationsDownload(client, directories)
    result = download.build()

    assert result == tmp_path / "data" / "raw" / "geosampa" / "2026-09"
