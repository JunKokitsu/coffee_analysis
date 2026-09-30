from pathlib import Path

import requests

SIDRA_VALUES_ADDRESS = "https://apisidra.ibge.gov.br/values"


class SidraTable:
    def __init__(self, query_path: str, destination: Path) -> None:
        self._query_path = query_path
        self._destination = destination

    def download(self) -> Path:
        if self._destination.exists():
            return self._destination
        response = requests.get(f"{SIDRA_VALUES_ADDRESS}/{self._query_path}", timeout=120)
        response.raise_for_status()
        self._destination.parent.mkdir(parents=True, exist_ok=True)
        self._destination.write_bytes(response.content)
        return self._destination
