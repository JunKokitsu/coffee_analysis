from pathlib import Path

from coffee_analysis.infrastructure.data_directories import DataDirectories
from coffee_analysis.infrastructure.http_client import HttpClient
from coffee_analysis.staging.itbi.property_transaction_release import PropertyTransactionRelease
from coffee_analysis.staging.itbi.property_transaction_releases import PropertyTransactionReleases


class PropertyTransactionsDownload:
    def __init__(self, http_client: HttpClient, releases: PropertyTransactionReleases, directories: DataDirectories) -> None:
        self._http_client = http_client
        self._releases = releases
        self._directories = directories

    def build(self) -> Path:
        release = self._latest_release()
        print(f"ITBI: publicação {release.competence_folder()}", flush=True)
        destination = self._directories.raw_file("itbi", release.competence_folder(), "guias_itbi.xlsx")
        self._http_client.download(release.download_url(), destination)
        return destination.parent

    def _latest_release(self) -> PropertyTransactionRelease:
        release = self._releases.latest()
        return self._require_release(release)

    def _require_release(self, release: PropertyTransactionRelease | None) -> PropertyTransactionRelease:
        if release is not None:
            return release
        raise FileNotFoundError("arquivo do ITBI não encontrado na página da Prefeitura")
