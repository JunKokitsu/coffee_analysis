from coffee_analysis.staging.mobility.motiva_demand_releases import MotivaDemandReleases

ENCODED_PDF_URL = "https://trilhos.motiva.com.br/content/dam/linha-4-amarela/entrada-de-passageiros-por-estacao/Demanda%20de%20passageiros%20-%20Maio%202026.pdf"


class EncodedNameMotivaDemandReleases(MotivaDemandReleases):
    def pdf_urls(self, page_slug: str) -> list[str]:
        return [ENCODED_PDF_URL]
