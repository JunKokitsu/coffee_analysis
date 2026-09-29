from pathlib import Path

from coffee_analysis.analytical_database import AnalyticalDatabase
from coffee_analysis.data_directories import DataDirectories

AWAY_FROM_HOME_CONSUMPTION_SHARE = 0.5


class OriginDestinationMarket:
    def __init__(self, database: AnalyticalDatabase, directories: DataDirectories) -> None:
        self._database = database
        self._directories = directories

    def build(self) -> Path:
        destination = self._directories.marts_file("distritos_metricas_od.parquet")
        return self._database.export_parquet(self._market_query(), destination)

    def _market_query(self) -> str:
        metrics = self._directories.processed_file("distritos_metricas.parquet")
        mobility = self._directories.marts_file("distritos_mobilidade.parquet")
        return f"""
            WITH cidade AS (
                SELECT
                    sum(metricas.gasto_mensal_residentes) / sum(mobilidade.viagens_atraidas_nao_residenciais) AS gasto_por_viagem_atraida_cidade,
                    sum(metricas.gasto_mensal_cafe_residentes) / sum(mobilidade.viagens_atraidas_nao_residenciais) AS gasto_cafe_por_viagem_atraida_cidade
                FROM '{metrics}' AS metricas
                JOIN '{mobility}' AS mobilidade USING (codigo_distrito)
            ),
            mercado AS (
                SELECT
                    metricas.* REPLACE (
                        (1 - {AWAY_FROM_HOME_CONSUMPTION_SHARE}) * metricas.gasto_mensal_residentes
                            + {AWAY_FROM_HOME_CONSUMPTION_SHARE} * mobilidade.viagens_atraidas_nao_residenciais * cidade.gasto_por_viagem_atraida_cidade
                            AS mercado_potencial_mensal,
                        (1 - {AWAY_FROM_HOME_CONSUMPTION_SHARE}) * metricas.gasto_mensal_cafe_residentes
                            + {AWAY_FROM_HOME_CONSUMPTION_SHARE} * mobilidade.viagens_atraidas_nao_residenciais * cidade.gasto_cafe_por_viagem_atraida_cidade
                            AS mercado_cafe_mensal
                    ),
                    mobilidade.viagens_atraidas_nao_residenciais,
                    cidade.gasto_por_viagem_atraida_cidade
                FROM '{metrics}' AS metricas
                JOIN '{mobility}' AS mobilidade USING (codigo_distrito)
                CROSS JOIN cidade
            )
            SELECT * REPLACE (
                mercado_potencial_mensal / nullif(cafeterias_ativas, 0) AS mercado_mensal_por_cafeteria,
                mercado_potencial_mensal / nullif(pontos_de_venda_cafe, 0) AS mercado_mensal_por_ponto_de_venda
            )
            FROM mercado
            ORDER BY codigo_distrito
        """
