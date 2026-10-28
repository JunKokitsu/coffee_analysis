from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CandidateAddress:
    description: str
    street: str
    number: int

    def locate_query(self, addresses_file: Path) -> str:
        return f"""
            SELECT
                '{self.description}' AS endereco_candidato,
                logradouro,
                numero,
                codigo_distrito,
                latitude,
                longitude
            FROM '{addresses_file}'
            WHERE logradouro = '{self.street}' AND latitude IS NOT NULL AND numero IS NOT NULL
            ORDER BY abs(numero - {self.number})
            LIMIT 1
        """
