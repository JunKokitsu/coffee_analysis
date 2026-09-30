import re
from datetime import date

from coffee_analysis.infrastructure.http_client import HttpClient
from coffee_analysis.staging.itbi.property_transaction_release import PropertyTransactionRelease

ITBI_PAGE_ADDRESS = "https://prefeitura.sp.gov.br/web/fazenda/w/acesso_a_informacao/31501"
RELEASE_FILE_NAME_PATTERN = re.compile(r"guias-de-itbi-pagas-(\d{2})(\d{2})(\d{4})-xls-xlsx")


class PropertyTransactionReleases:
    def __init__(self, http_client: HttpClient) -> None:
        self._http_client = http_client

    def releases_in(self, page: str) -> list[PropertyTransactionRelease]:
        matches_by_file_name = {match.group(0): match for match in RELEASE_FILE_NAME_PATTERN.finditer(page)}
        return [self._release_from_match(match) for match in matches_by_file_name.values()]

    def latest(self) -> PropertyTransactionRelease | None:
        page = self._http_client.text(ITBI_PAGE_ADDRESS)
        return self._latest_release(self.releases_in(page))

    def _release_from_match(self, match: re.Match[str]) -> PropertyTransactionRelease:
        day, month, year = match.groups()
        return PropertyTransactionRelease(match.group(0), date(int(year), int(month), int(day)))

    def _latest_release(self, releases: list[PropertyTransactionRelease]) -> PropertyTransactionRelease | None:
        if releases:
            return max(releases, key=self._publication_date)
        return None

    def _publication_date(self, release: PropertyTransactionRelease) -> date:
        return release.publication_date
