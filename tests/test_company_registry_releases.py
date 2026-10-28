from pathlib import Path

from ponto_do_cafe.staging.cnpj.company_registry_releases import (
    RECEITA_CNPJ_ADDRESS,
    CompanyRegistryReleases,
)
from tests.recorded_http_client import RecordedHttpClient

FIXTURES_DIRECTORY = Path(__file__).parent / "fixtures"


def propfind_body() -> str:
    return (FIXTURES_DIRECTORY / "cnpj_propfind.xml").read_text(encoding="utf-8")


def test_months_lists_every_folder_in_ascending_order() -> None:
    months = CompanyRegistryReleases(RecordedHttpClient({})).months(propfind_body())
    assert months[0] == "2023-05"
    assert months[-1] == "2026-09"
    assert months == sorted(months)


def test_latest_until_returns_exact_competence_when_available() -> None:
    releases = CompanyRegistryReleases(RecordedHttpClient({RECEITA_CNPJ_ADDRESS: "cnpj_propfind.xml"}))
    assert releases.latest_until("2026-09") == "2026-09"


def test_latest_until_returns_earlier_competence_when_exact_month_is_absent() -> None:
    releases = CompanyRegistryReleases(RecordedHttpClient({RECEITA_CNPJ_ADDRESS: "cnpj_propfind.xml"}))
    assert releases.latest_until("2026-07") == "2026-07"


def test_latest_until_returns_none_before_every_release() -> None:
    releases = CompanyRegistryReleases(RecordedHttpClient({RECEITA_CNPJ_ADDRESS: "cnpj_propfind.xml"}))
    assert releases.latest_until("2020-01") is None
