import re

from coffee_analysis.infrastructure.http_client import HttpClient

RECEITA_CNPJ_ADDRESS = "https://arquivos.receitafederal.gov.br/public.php/webdav/Dados/Cadastros/CNPJ/"
RECEITA_CNPJ_TOKEN = "gn672Ad4CF8N6TK"
MONTH_FOLDER_PATTERN = re.compile(r"/CNPJ/(\d{4}-\d{2})/")


class CompanyRegistryReleases:
    def __init__(self, http_client: HttpClient) -> None:
        self._http_client = http_client

    def months(self, propfind_body: str) -> list[str]:
        return sorted(set(MONTH_FOLDER_PATTERN.findall(propfind_body)))

    def latest_until(self, competence: str) -> str | None:
        response = self._http_client.request(
            "PROPFIND",
            RECEITA_CNPJ_ADDRESS,
            headers={"Depth": "1"},
            authentication=(RECEITA_CNPJ_TOKEN, ""),
        )
        return self._latest_among(self.months(response.text), competence)

    def _latest_among(self, months: list[str], competence: str) -> str | None:
        eligible = [month for month in months if month <= competence]
        return self._last_or_none(eligible)

    def _last_or_none(self, eligible: list[str]) -> str | None:
        if eligible:
            return eligible[-1]
        return None
