from pathlib import Path

from ponto_do_cafe.infrastructure.data_directories import DataDirectories
from ponto_do_cafe.infrastructure.http_client import HttpClient
from ponto_do_cafe.staging.mobility.metro_demand_releases import MetroDemandReleases


class MetroDemandDownload:
    def __init__(
        self,
        http_client: HttpClient,
        releases: MetroDemandReleases,
        directories: DataDirectories,
    ) -> None:
        self._http_client = http_client
        self._releases = releases
        self._directories = directories

    def build(self) -> Path:
        base_year = int(self._directories.competence.split("-")[0])
        for year in [base_year - 1, base_year]:
            self._download_year_if_needed(year)
        return self._directories.raw_file("metro", self._directories.competence)

    def _download_year_if_needed(self, year: int) -> None:
        destination = self._destination_for_year(year)
        if self._file_already_exists(destination):
            return
        url = self._releases.csv_url_for_year(year)
        self._require_url_found(url, year)
        self._http_client.download(url, destination)

    def _destination_for_year(self, year: int) -> Path:
        return self._directories.raw_file("metro", self._directories.competence, f"demanda_estacoes_{year}.csv")

    def _file_already_exists(self, destination: Path) -> bool:
        return destination.exists() and destination.stat().st_size > 0

    def _require_url_found(self, url: str | None, year: int) -> None:
        if url is not None:
            return
        raise FileNotFoundError(f"URL não encontrada para demanda do metrô em {year}")
