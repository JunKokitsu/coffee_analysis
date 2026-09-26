from pathlib import Path

from coffee_analysis.candidate_address import CandidateAddress


class CandidateAddresses:
    def __init__(self, addresses: tuple[CandidateAddress, ...]) -> None:
        self._addresses = addresses

    def locate_query(self, addresses_file: Path) -> str:
        queries = [f"({address.locate_query(addresses_file)})" for address in self._addresses]
        return " UNION ALL ".join(queries)
