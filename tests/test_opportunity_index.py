from pathlib import Path

import polars

from ponto_do_cafe.infrastructure.analytical_database import AnalyticalDatabase
from ponto_do_cafe.marts.opportunity_index import OpportunityIndex


def test_best_district_combines_market_survival_and_low_cost(tmp_path: Path) -> None:
    metrics = tmp_path / "metricas.parquet"
    polars.DataFrame(
        {
            "codigo_distrito": ["1", "2", "3"],
            "nome_distrito": ["Bom", "Médio", "Ruim"],
            "mercado_mensal_por_ponto_de_venda": [5000.0, 3000.0, 1000.0],
            "crescimento_oferta_24_meses": [0.1, 0.2, 0.5],
            "sobrevivencia_3_anos": [0.8, 0.7, 0.5],
            "amostra_sobrevivencia_3_anos": [100, 100, 100],
            "preco_mediano_m2_comercial": [3000.0, 5000.0, 9000.0],
            "transacoes_comerciais": [20, 20, 20],
        }
    ).write_parquet(metrics)
    destination = OpportunityIndex(AnalyticalDatabase(), metrics, tmp_path / "indice.parquet").build()
    ranking = polars.read_parquet(destination).sort("posicao_ranking")
    assert ranking["nome_distrito"].to_list() == ["Bom", "Médio", "Ruim"]
    assert ranking["indice_oportunidade"][0] == 100.0


def test_small_samples_receive_neutral_percentile(tmp_path: Path) -> None:
    metrics = tmp_path / "metricas.parquet"
    polars.DataFrame(
        {
            "codigo_distrito": ["1", "2"],
            "nome_distrito": ["Amostra pequena", "Amostra grande"],
            "mercado_mensal_por_ponto_de_venda": [1000.0, 1000.0],
            "crescimento_oferta_24_meses": [0.1, 0.1],
            "sobrevivencia_3_anos": [0.99, 0.5],
            "amostra_sobrevivencia_3_anos": [5, 100],
            "preco_mediano_m2_comercial": [1.0, 1.0],
            "transacoes_comerciais": [1, 1],
        }
    ).write_parquet(metrics)
    destination = OpportunityIndex(AnalyticalDatabase(), metrics, tmp_path / "indice.parquet").build()
    index = polars.read_parquet(destination)
    small_sample = index.filter(polars.col("codigo_distrito") == "1")
    assert small_sample["percentil_sobrevivencia"][0] == 0.5
    assert small_sample["percentil_custo_ocupacao"][0] == 0.5
