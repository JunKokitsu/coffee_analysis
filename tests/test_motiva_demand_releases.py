from pathlib import Path

from coffee_analysis.staging.mobility.motiva_demand_releases import MOTIVA_ADDRESS, MotivaDemandReleases
from tests.recorded_http_client import RecordedHttpClient

FIXTURES_DIRECTORY = Path(__file__).parent / "fixtures"


def linha_4_page() -> str:
    return (FIXTURES_DIRECTORY / "motiva_linha_4_page.html").read_text(encoding="utf-8")


def test_pdf_paths_in_returns_unique_and_sorted_paths() -> None:
    paths = MotivaDemandReleases(RecordedHttpClient({})).pdf_paths_in(linha_4_page())
    assert len(paths) == len(set(paths))
    assert paths == sorted(paths)
    assert all("/entrada-de-passageiros-por-estacao/" in path for path in paths)
    assert all(path.endswith(".pdf") for path in paths)


def test_pdf_urls_prefixes_the_motiva_address() -> None:
    releases = MotivaDemandReleases(
        RecordedHttpClient({f"{MOTIVA_ADDRESS}/linha-4-amarela/historico-de-pessoas-transportadas/": "motiva_linha_4_page.html"})
    )
    urls = releases.pdf_urls("linha-4-amarela")
    assert all(url.startswith(MOTIVA_ADDRESS) for url in urls)
    assert urls == sorted(urls)
    assert len(urls) == len(set(urls))
