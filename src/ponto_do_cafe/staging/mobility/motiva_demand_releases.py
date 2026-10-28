import re

from ponto_do_cafe.infrastructure.http_client import HttpClient

MOTIVA_ADDRESS = "https://trilhos.motiva.com.br"
PDF_PATH_PATTERN = re.compile(r'/content/dam/[^"]*/entrada-de-passageiros-por-estacao/[^"]*\.pdf')


class MotivaDemandReleases:
    def __init__(self, http_client: HttpClient) -> None:
        self._http_client = http_client

    def pdf_paths_in(self, page: str) -> list[str]:
        return sorted(set(PDF_PATH_PATTERN.findall(page)))

    def pdf_urls(self, page_slug: str) -> list[str]:
        page = self._http_client.text(self._page_url(page_slug))
        return [f"{MOTIVA_ADDRESS}{path}" for path in self.pdf_paths_in(page)]

    def _page_url(self, page_slug: str) -> str:
        return f"{MOTIVA_ADDRESS}/{page_slug}/historico-de-pessoas-transportadas/"
