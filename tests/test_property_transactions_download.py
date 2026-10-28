from datetime import date
from pathlib import Path

import pytest

from ponto_do_cafe.infrastructure.data_directories import DataDirectories
from ponto_do_cafe.staging.itbi.property_transaction_release import PropertyTransactionRelease
from ponto_do_cafe.staging.itbi.property_transactions_download import PropertyTransactionsDownload
from tests.fake_download_http_client import FakeDownloadHttpClient
from tests.fixed_property_transaction_releases import FixedPropertyTransactionReleases


def build_directories(tmp_path: Path) -> DataDirectories:
    return DataDirectories(tmp_path, "2026-09")


def test_build_downloads_to_expected_path_and_returns_competence_folder(tmp_path: Path) -> None:
    release = PropertyTransactionRelease("guias-de-itbi-pagas-27082026-xls-xlsx", date(2026, 8, 27))
    http_client = FakeDownloadHttpClient()
    releases = FixedPropertyTransactionReleases(release)
    download = PropertyTransactionsDownload(http_client, releases, build_directories(tmp_path))
    result = download.build()
    assert len(http_client.download_calls) == 1
    url, destination, authentication = http_client.download_calls[0]
    assert url == release.download_url()
    assert destination == tmp_path / "data" / "raw" / "itbi" / "2026-08-27" / "guias_itbi.xlsx"
    assert authentication is None
    assert result == tmp_path / "data" / "raw" / "itbi" / "2026-08-27"


def test_build_raises_when_no_release_found(tmp_path: Path) -> None:
    http_client = FakeDownloadHttpClient()
    releases = FixedPropertyTransactionReleases(None)
    download = PropertyTransactionsDownload(http_client, releases, build_directories(tmp_path))
    with pytest.raises(FileNotFoundError):
        download.build()
