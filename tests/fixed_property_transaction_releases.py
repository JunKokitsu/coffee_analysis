from ponto_do_cafe.infrastructure.http_client import HttpClient
from ponto_do_cafe.staging.itbi.property_transaction_release import PropertyTransactionRelease
from ponto_do_cafe.staging.itbi.property_transaction_releases import PropertyTransactionReleases


class FixedPropertyTransactionReleases(PropertyTransactionReleases):
    def __init__(self, release: PropertyTransactionRelease | None) -> None:
        super().__init__(HttpClient())
        self._release = release

    def latest(self) -> PropertyTransactionRelease | None:
        return self._release
