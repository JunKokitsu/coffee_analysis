from datetime import date
from pathlib import Path

from coffee_analysis.metro_demand_sheet import MetroDemandSheet
from coffee_analysis.station_demand_record import StationDemandRecord

SHEET = """METRÔ DE SÃO PAULO;;;;;;;;;;;;;
LINHA 1-AZUL;;;;;;;;;;;;;
Estação;Jan;Fev;Mar;Abr;Mai;Jun;Jul;Ago;Set;Out;Nov;Dez;Média
Jabaquara; 63 ; 67 ;;;;;;;;;;; 65
Total; 900 ; 950 ;;;;;;;;;;; 925
LINHA 15-PRATA;;;;;;;;;;;;;
Estação;Jan;Fev;Mar;Abr;Mai;Jun;Jul;Ago;Set;Out;Nov;Dez;Média
Vila Prudente; 1.020,5 ;;;;;;;;;;;; 1.020,5
"""


def test_records_follow_line_headers_and_skip_totals(tmp_path: Path) -> None:
    path = tmp_path / "demanda_estacoes_2026.csv"
    path.write_text(SHEET, encoding="latin-1")
    records = MetroDemandSheet(path).records()
    assert records == [
        StationDemandRecord(1, "Jabaquara", date(2026, 1, 1), 63.0),
        StationDemandRecord(1, "Jabaquara", date(2026, 2, 1), 67.0),
        StationDemandRecord(15, "Vila Prudente", date(2026, 1, 1), 1020.5),
    ]
