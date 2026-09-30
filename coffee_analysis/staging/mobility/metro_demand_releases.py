import re

from coffee_analysis.infrastructure.http_client import HttpClient

METRO_TRANSPARENCY_ADDRESS = "https://transparencia.metrosp.com.br"
DATASET_PAGE_URL = f"{METRO_TRANSPARENCY_ADDRESS}/dataset/demanda"
CSV_LINK_PATTERN = re.compile(rf"{re.escape(METRO_TRANSPARENCY_ADDRESS)}/sites/default/files/[^\"]+\.csv")


class MetroDemandReleases:
    def __init__(self, http_client: HttpClient) -> None:
        self._http_client = http_client

    def resource_paths(self, dataset_page: str, year: int) -> list[str]:
        return self._resource_pattern(year).findall(dataset_page)

    def csv_url_in(self, resource_page: str) -> str | None:
        return self._url_or_none(CSV_LINK_PATTERN.search(resource_page))

    def csv_url_for_year(self, year: int) -> str | None:
        dataset_page = self._http_client.text(DATASET_PAGE_URL)
        return self._first_csv_url(self.resource_paths(dataset_page, year))

    def _resource_pattern(self, year: int) -> re.Pattern[str]:
        title = f"Demanda de Passageiros por Estação - Média Dias Úteis - {year}"
        return re.compile(rf'(/dataset/demanda/resource/[a-f0-9-]+)"[^>]*title="{re.escape(title)}"')

    def _first_csv_url(self, resource_paths: list[str]) -> str | None:
        csv_urls = (self._csv_url_for_resource(resource_path) for resource_path in resource_paths)
        return next((csv_url for csv_url in csv_urls if csv_url is not None), None)

    def _csv_url_for_resource(self, resource_path: str) -> str | None:
        resource_page = self._http_client.text(f"{METRO_TRANSPARENCY_ADDRESS}{resource_path}")
        return self.csv_url_in(resource_page)

    def _url_or_none(self, match: re.Match[str] | None) -> str | None:
        if match is not None:
            return match.group(0)
        return None
