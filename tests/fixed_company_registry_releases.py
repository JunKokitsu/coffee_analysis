from ponto_do_cafe.infrastructure.http_client import HttpClient
from ponto_do_cafe.staging.cnpj.company_registry_releases import CompanyRegistryReleases


class FixedCompanyRegistryReleases(CompanyRegistryReleases):
    def __init__(self, month: str | None) -> None:
        super().__init__(HttpClient())
        self._month = month

    def latest_until(self, competence: str) -> str | None:
        return self._month
