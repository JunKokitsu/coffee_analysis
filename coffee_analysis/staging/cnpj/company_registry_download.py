from pathlib import Path

from coffee_analysis.infrastructure.data_directories import DataDirectories
from coffee_analysis.infrastructure.http_client import HttpClient
from coffee_analysis.staging.cnpj.company_registry_releases import (
    RECEITA_CNPJ_ADDRESS,
    RECEITA_CNPJ_TOKEN,
    CompanyRegistryReleases,
)

PART_SIZE_BYTES = 67108864
FILE_DIGITS = range(10)


class CompanyRegistryDownload:
    def __init__(self, http_client: HttpClient, releases: CompanyRegistryReleases, directories: DataDirectories) -> None:
        self._http_client = http_client
        self._releases = releases
        self._directories = directories

    def build(self) -> Path:
        month = self._latest_month()
        print(f"CNPJ: publicação {month}", flush=True)
        for digit in FILE_DIGITS:
            self._download_pair(month, digit)
        return self._directories.raw_file("cnpj", month)

    def _latest_month(self) -> str:
        month = self._releases.latest_until(self._directories.competence)
        return self._require_month(month)

    def _require_month(self, month: str | None) -> str:
        if month is not None:
            return month
        raise FileNotFoundError(f"nenhuma publicação do CNPJ até {self._directories.competence}")

    def _download_pair(self, month: str, digit: int) -> None:
        self._download_file(month, f"Estabelecimentos{digit}.zip")
        self._download_file(month, f"Empresas{digit}.zip")

    def _download_file(self, month: str, file_name: str) -> None:
        url = f"{RECEITA_CNPJ_ADDRESS}{month}/{file_name}"
        destination = self._directories.raw_file("cnpj", month, file_name)
        self._http_client.download_in_parts(url, destination, PART_SIZE_BYTES, authentication=(RECEITA_CNPJ_TOKEN, ""))
