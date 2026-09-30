from collections.abc import Callable
from pathlib import Path

from coffee_analysis.infrastructure.archive_extractor import ArchiveExtractor
from coffee_analysis.infrastructure.data_directories import DataDirectories
from coffee_analysis.infrastructure.ftp_client import FtpClient
from coffee_analysis.infrastructure.http_client import HttpClient
from coffee_analysis.staging.cnpj.company_registry_download import CompanyRegistryDownload
from coffee_analysis.staging.cnpj.company_registry_releases import CompanyRegistryReleases
from coffee_analysis.staging.ibge.ibge_download import IbgeDownload
from coffee_analysis.staging.itbi.property_transaction_releases import PropertyTransactionReleases
from coffee_analysis.staging.itbi.property_transactions_download import PropertyTransactionsDownload
from coffee_analysis.staging.mobility.metro_demand_download import MetroDemandDownload
from coffee_analysis.staging.mobility.metro_demand_releases import MetroDemandReleases
from coffee_analysis.staging.mobility.motiva_demand_download import MotivaDemandDownload
from coffee_analysis.staging.mobility.motiva_demand_releases import MotivaDemandReleases
from coffee_analysis.staging.mobility.origin_destination_survey_download import OriginDestinationSurveyDownload
from coffee_analysis.staging.mobility.rail_stations_download import RailStationsDownload
from coffee_analysis.staging.rais.rais_download import RaisDownload
from coffee_analysis.staging.rais.rais_releases import RaisReleases


class DownloadSteps:
    def __init__(self, directories: DataDirectories) -> None:
        self._directories = directories
        self._http_client = HttpClient()
        self._ftp_client = FtpClient()
        self._extractor = ArchiveExtractor()

    def build(self) -> dict[str, Callable[[], Path]]:
        return {
            "baixar_cnpj": self._company_registry_download().build,
            "baixar_ibge": self._ibge_download().build,
            "baixar_rais": self._rais_download().build,
            "baixar_itbi": self._property_transactions_download().build,
            "baixar_pesquisa_od": self._origin_destination_survey_download().build,
            "baixar_metro": self._metro_demand_download().build,
            "baixar_motiva": self._motiva_demand_download().build,
            "baixar_geosampa": self._rail_stations_download().build,
        }

    def _company_registry_download(self) -> CompanyRegistryDownload:
        releases = CompanyRegistryReleases(self._http_client)
        return CompanyRegistryDownload(self._http_client, releases, self._directories)

    def _ibge_download(self) -> IbgeDownload:
        return IbgeDownload(self._http_client, self._extractor, self._directories)

    def _rais_download(self) -> RaisDownload:
        return RaisDownload(self._ftp_client, RaisReleases(), self._extractor, self._directories)

    def _property_transactions_download(self) -> PropertyTransactionsDownload:
        releases = PropertyTransactionReleases(self._http_client)
        return PropertyTransactionsDownload(self._http_client, releases, self._directories)

    def _origin_destination_survey_download(self) -> OriginDestinationSurveyDownload:
        return OriginDestinationSurveyDownload(self._http_client, self._extractor, self._directories)

    def _metro_demand_download(self) -> MetroDemandDownload:
        releases = MetroDemandReleases(self._http_client)
        return MetroDemandDownload(self._http_client, releases, self._directories)

    def _motiva_demand_download(self) -> MotivaDemandDownload:
        releases = MotivaDemandReleases(self._http_client)
        return MotivaDemandDownload(self._http_client, releases, self._directories)

    def _rail_stations_download(self) -> RailStationsDownload:
        return RailStationsDownload(self._http_client, self._directories)
