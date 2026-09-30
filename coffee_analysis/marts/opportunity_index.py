from pathlib import Path

from coffee_analysis.infrastructure.analytical_database import AnalyticalDatabase

MARKET_WEIGHT = 0.40
SURVIVAL_WEIGHT = 0.25
ENTRY_PRESSURE_WEIGHT = 0.15
OCCUPANCY_COST_WEIGHT = 0.20
NEUTRAL_PERCENTILE = 0.5
MINIMUM_SURVIVAL_SAMPLE = 30
MINIMUM_PROPERTY_TRANSACTIONS = 5


class OpportunityIndex:
    def __init__(self, database: AnalyticalDatabase, metrics: Path, destination: Path) -> None:
        self._database = database
        self._metrics = metrics
        self._destination = destination

    def build(self) -> Path:
        return self._database.export_parquet(self._index_query(), self._destination)

    def _percentile(self, column: str) -> str:
        return f"CASE WHEN {column} IS NOT NULL THEN percent_rank() OVER (PARTITION BY {column} IS NULL ORDER BY {column}) END"

    def _index_query(self) -> str:
        return f"""
            WITH confiaveis AS (
                SELECT
                    codigo_distrito,
                    nome_distrito,
                    mercado_mensal_por_ponto_de_venda,
                    crescimento_oferta_24_meses,
                    CASE WHEN amostra_sobrevivencia_3_anos >= {MINIMUM_SURVIVAL_SAMPLE} THEN sobrevivencia_3_anos END AS sobrevivencia_3_anos,
                    CASE WHEN transacoes_comerciais >= {MINIMUM_PROPERTY_TRANSACTIONS} THEN preco_mediano_m2_comercial END AS preco_mediano_m2_comercial
                FROM '{self._metrics}'
            ),
            percentis AS (
                SELECT
                    codigo_distrito,
                    nome_distrito,
                    coalesce({self._percentile("mercado_mensal_por_ponto_de_venda")}, {NEUTRAL_PERCENTILE}) AS percentil_mercado,
                    coalesce({self._percentile("sobrevivencia_3_anos")}, {NEUTRAL_PERCENTILE}) AS percentil_sobrevivencia,
                    coalesce({self._percentile("crescimento_oferta_24_meses")}, {NEUTRAL_PERCENTILE}) AS percentil_pressao_entrada,
                    coalesce({self._percentile("preco_mediano_m2_comercial")}, {NEUTRAL_PERCENTILE}) AS percentil_custo_ocupacao
                FROM confiaveis
            ),
            indice AS (
                SELECT
                    *,
                    100 * (
                        {MARKET_WEIGHT} * percentil_mercado
                        + {SURVIVAL_WEIGHT} * percentil_sobrevivencia
                        + {ENTRY_PRESSURE_WEIGHT} * (1 - percentil_pressao_entrada)
                        + {OCCUPANCY_COST_WEIGHT} * (1 - percentil_custo_ocupacao)
                    ) AS indice_oportunidade
                FROM percentis
            )
            SELECT *, rank() OVER (ORDER BY indice_oportunidade DESC) AS posicao_ranking
            FROM indice
            ORDER BY posicao_ranking
        """
