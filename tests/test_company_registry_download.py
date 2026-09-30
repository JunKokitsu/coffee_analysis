from pathlib import Path

import pytest

from coffee_analysis.infrastructure.data_directories import DataDirectories
from coffee_analysis.staging.cnpj.company_registry_download import PART_SIZE_BYTES, CompanyRegistryDownload
from coffee_analysis.staging.cnpj.company_registry_releases import RECEITA_CNPJ_ADDRESS, RECEITA_CNPJ_TOKEN
from tests.fake_download_http_client import FakeDownloadHttpClient
from tests.fixed_company_registry_releases import FixedCompanyRegistryReleases


def build_directories(tmp_path: Path) -> DataDirectories:
    return DataDirectories(tmp_path, "2026-09")


def test_build_downloads_twenty_files_and_returns_month_folder(tmp_path: Path) -> None:
    http_client = FakeDownloadHttpClient()
    releases = FixedCompanyRegistryReleases("2026-09")
    download = CompanyRegistryDownload(http_client, releases, build_directories(tmp_path))
    result = download.build()
    assert len(http_client.download_in_parts_calls) == 20
    assert result == tmp_path / "data" / "raw" / "cnpj" / "2026-09"


def test_build_uses_expected_url_path_size_and_authentication(tmp_path: Path) -> None:
    http_client = FakeDownloadHttpClient()
    releases = FixedCompanyRegistryReleases("2026-09")
    download = CompanyRegistryDownload(http_client, releases, build_directories(tmp_path))
    download.build()
    url, destination, part_size, authentication = http_client.download_in_parts_calls[0]
    assert url == f"{RECEITA_CNPJ_ADDRESS}2026-09/Estabelecimentos0.zip"
    assert destination == tmp_path / "data" / "raw" / "cnpj" / "2026-09" / "Estabelecimentos0.zip"
    assert part_size == PART_SIZE_BYTES
    assert authentication == (RECEITA_CNPJ_TOKEN, "")


def test_build_downloads_both_estabelecimentos_and_empresas_files(tmp_path: Path) -> None:
    http_client = FakeDownloadHttpClient()
    releases = FixedCompanyRegistryReleases("2026-09")
    download = CompanyRegistryDownload(http_client, releases, build_directories(tmp_path))
    download.build()
    downloaded_file_names = {destination.name for _, destination, _, _ in http_client.download_in_parts_calls}
    assert downloaded_file_names == {f"{prefix}{digit}.zip" for prefix in ("Estabelecimentos", "Empresas") for digit in range(10)}


def test_build_raises_when_no_release_found_until_competence(tmp_path: Path) -> None:
    http_client = FakeDownloadHttpClient()
    releases = FixedCompanyRegistryReleases(None)
    download = CompanyRegistryDownload(http_client, releases, build_directories(tmp_path))
    with pytest.raises(FileNotFoundError):
        download.build()
