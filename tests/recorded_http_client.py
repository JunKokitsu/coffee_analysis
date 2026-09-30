from pathlib import Path

import requests

from coffee_analysis.infrastructure.http_client import HttpClient

FIXTURES_DIRECTORY = Path(__file__).parent / "fixtures"


class RecordedHttpClient(HttpClient):
    def __init__(self, responses_by_url: dict[str, str]) -> None:
        self._responses_by_url = responses_by_url

    def text(self, url: str) -> str:
        return self._fixture_content(url)

    def request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        authentication: tuple[str, str] | None = None,
    ) -> requests.Response:
        response = requests.Response()
        response.status_code = 207
        response._content = self._fixture_content(url).encode("utf-8")
        return response

    def _fixture_content(self, url: str) -> str:
        fixture_name = self._responses_by_url[url]
        return (FIXTURES_DIRECTORY / fixture_name).read_text(encoding="utf-8")
