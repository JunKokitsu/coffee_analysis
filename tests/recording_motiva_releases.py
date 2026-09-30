from coffee_analysis.infrastructure.http_client import HttpClient
from coffee_analysis.staging.mobility.motiva_demand_releases import MotivaDemandReleases


class RecordingMotivaDemandReleases(MotivaDemandReleases):
    def __init__(self, http_client: HttpClient) -> None:
        super().__init__(http_client)
        self.requested_slugs: list[str] = []

    def pdf_urls(self, page_slug: str) -> list[str]:
        self.requested_slugs.append(page_slug)
        return self._urls_for_slug(page_slug)

    def _urls_for_slug(self, page_slug: str) -> list[str]:
        base_urls: dict[str, list[str]] = {
            "linha-4-amarela": [
                "https://trilhos.motiva.com.br/content/dam/linha-4-amarela/entrada-de-passageiros-por-estacao/relatorio_2024.pdf",
                "https://trilhos.motiva.com.br/content/dam/linha-4-amarela/entrada-de-passageiros-por-estacao/relatorio_2023.pdf",
            ],
            "linha-5-lilas": [
                "https://trilhos.motiva.com.br/content/dam/linha-5-lilas/entrada-de-passageiros-por-estacao/dados_2024.pdf",
            ],
            "viamobilidade8e9": [
                "https://trilhos.motiva.com.br/content/dam/viamobilidade8e9/entrada-de-passageiros-por-estacao/report.pdf",
            ],
        }
        return base_urls.get(page_slug, [])
