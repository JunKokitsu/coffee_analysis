from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class StationDemandRecord:
    numero_linha: int
    nome_estacao: str
    competencia: date
    demanda_media_dias_uteis: float
