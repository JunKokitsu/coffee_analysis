from pathlib import Path

import polars
import pytest

from coffee_analysis.analytical_database import AnalyticalDatabase
from coffee_analysis.data_directories import DataDirectories
from coffee_analysis.origin_destination_market import OriginDestinationMarket


def test_away_from_home_spending_follows_attracted_trips(tmp_path: Path) -> None:
    directories = DataDirectories(tmp_path, "2026-09")
    polars.DataFrame(
        {
            "codigo_distrito": ["1", "2"],
            "gasto_mensal_residentes": [1000.0, 3000.0],
            "gasto_mensal_cafe_residentes": [100.0, 300.0],
            "mercado_potencial_mensal": [0.0, 0.0],
            "mercado_cafe_mensal": [0.0, 0.0],
            "mercado_mensal_por_cafeteria": [0.0, 0.0],
            "mercado_mensal_por_ponto_de_venda": [0.0, 0.0],
            "cafeterias_ativas": [2, 0],
            "pontos_de_venda_cafe": [4, 10],
        }
    ).write_parquet(directories.marts_file("distritos_metricas_rais.parquet"))
    polars.DataFrame({"codigo_distrito": ["1", "2"], "viagens_atraidas_nao_residenciais": [300.0, 100.0]}).write_parquet(
        directories.marts_file("distritos_mobilidade.parquet")
    )
    market = polars.read_parquet(OriginDestinationMarket(AnalyticalDatabase(), directories).build()).sort("codigo_distrito")
    assert market["mercado_potencial_mensal"].to_list() == pytest.approx([500.0 + 1500.0, 1500.0 + 500.0])
    assert market["mercado_potencial_mensal"].sum() == pytest.approx(4000.0)
    assert market["mercado_mensal_por_cafeteria"].to_list()[0] == pytest.approx(1000.0)
    assert market["mercado_mensal_por_cafeteria"].to_list()[1] is None
