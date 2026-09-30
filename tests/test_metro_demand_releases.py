from pathlib import Path

from coffee_analysis.staging.mobility.metro_demand_releases import (
    DATASET_PAGE_URL,
    METRO_TRANSPARENCY_ADDRESS,
    MetroDemandReleases,
)
from tests.recorded_http_client import RecordedHttpClient

FIXTURES_DIRECTORY = Path(__file__).parent / "fixtures"


def dataset_page() -> str:
    return (FIXTURES_DIRECTORY / "metro_dataset_page.html").read_text(encoding="utf-8")


def resource_page() -> str:
    return (FIXTURES_DIRECTORY / "metro_resource_page.html").read_text(encoding="utf-8")


def test_resource_paths_finds_the_two_resources_published_for_2026() -> None:
    releases = MetroDemandReleases(RecordedHttpClient({}))
    assert releases.resource_paths(dataset_page(), 2026) == [
        "/dataset/demanda/resource/fb3b16e9-a4b7-4434-a2ac-04193e905b43",
        "/dataset/demanda/resource/080b0607-b5e5-43e5-9fe8-90c321a69536",
    ]


def test_resource_paths_finds_the_two_resources_published_for_2025() -> None:
    releases = MetroDemandReleases(RecordedHttpClient({}))
    assert releases.resource_paths(dataset_page(), 2025) == [
        "/dataset/demanda/resource/a464481f-2428-43f5-8c7f-7e884103e6b2",
        "/dataset/demanda/resource/2e8d3764-ffff-4a8a-b5c0-443be898b036",
    ]


def test_csv_url_in_extracts_the_csv_link() -> None:
    releases = MetroDemandReleases(RecordedHttpClient({}))
    assert releases.csv_url_in(resource_page()) == (
        "https://transparencia.metrosp.com.br/sites/default/files/"
        "Demanda%20de%20Passageiros%20por%20Esta%C3%A7%C3%A3o%20-%20M%C3%A9dia%20Dias%20%C3%9Ateis%20-%202026_6.csv"
    )


def test_csv_url_for_year_reads_dataset_and_resource_pages() -> None:
    resource_url = f"{METRO_TRANSPARENCY_ADDRESS}/dataset/demanda/resource/fb3b16e9-a4b7-4434-a2ac-04193e905b43"
    other_resource_url = f"{METRO_TRANSPARENCY_ADDRESS}/dataset/demanda/resource/080b0607-b5e5-43e5-9fe8-90c321a69536"
    releases = MetroDemandReleases(
        RecordedHttpClient(
            {
                DATASET_PAGE_URL: "metro_dataset_page.html",
                resource_url: "metro_resource_page_no_csv.html",
                other_resource_url: "metro_resource_page.html",
            }
        )
    )
    assert releases.csv_url_for_year(2026) is not None
    assert releases.csv_url_for_year(2026).endswith("2026_6.csv")
