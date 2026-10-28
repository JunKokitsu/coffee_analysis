from ponto_do_cafe.infrastructure.http_client import HttpClient
from ponto_do_cafe.staging.mobility.metro_demand_releases import MetroDemandReleases


class RecordingMetroReleases(MetroDemandReleases):
    def __init__(self, http_client: HttpClient) -> None:
        super().__init__(http_client)
        self.requested_years: list[int] = []

    def csv_url_for_year(self, year: int) -> str | None:
        self.requested_years.append(year)
        return self._url_for_year(year)

    def _url_for_year(self, year: int) -> str | None:
        if year < 2020:
            return None
        return f"https://exemplo.com/demanda_{year}.csv"
