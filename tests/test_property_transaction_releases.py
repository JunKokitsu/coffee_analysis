from datetime import date
from pathlib import Path

from coffee_analysis.staging.itbi.property_transaction_releases import (
    ITBI_PAGE_ADDRESS,
    PropertyTransactionReleases,
)
from tests.recorded_http_client import RecordedHttpClient

FIXTURES_DIRECTORY = Path(__file__).parent / "fixtures"


def itbi_page() -> str:
    return (FIXTURES_DIRECTORY / "itbi_page.html").read_text(encoding="utf-8")


def test_releases_in_finds_the_recorded_release() -> None:
    releases = PropertyTransactionReleases(RecordedHttpClient({})).releases_in(itbi_page())
    matching_release = next(release for release in releases if release.file_name == "guias-de-itbi-pagas-27082026-xls-xlsx")
    assert matching_release.publication_date == date(2026, 8, 27)


def test_releases_in_deduplicates_by_file_name() -> None:
    page = "guias-de-itbi-pagas-27082026-xls-xlsx guias-de-itbi-pagas-27082026-xls-xlsx"
    releases = PropertyTransactionReleases(RecordedHttpClient({})).releases_in(page)
    assert len(releases) == 1


def test_latest_picks_the_most_recent_publication_date() -> None:
    releases = PropertyTransactionReleases(RecordedHttpClient({ITBI_PAGE_ADDRESS: "itbi_two_releases.html"}))
    latest = releases.latest()
    assert latest is not None
    assert latest.file_name == "guias-de-itbi-pagas-27082026-xls-xlsx"


def test_latest_reads_the_page_through_the_http_client() -> None:
    releases = PropertyTransactionReleases(RecordedHttpClient({ITBI_PAGE_ADDRESS: "itbi_page.html"}))
    latest = releases.latest()
    assert latest is not None
    assert latest.file_name == "guias-de-itbi-pagas-27082026-xls-xlsx"
    assert latest.download_url() == "https://prefeitura.sp.gov.br/documents/d/fazenda/guias-de-itbi-pagas-27082026-xls-xlsx"
    assert latest.competence_folder() == "2026-08-27"


def test_latest_returns_none_when_page_has_no_release() -> None:
    releases = PropertyTransactionReleases(RecordedHttpClient({ITBI_PAGE_ADDRESS: "itbi_empty.html"}))
    assert releases.latest() is None
