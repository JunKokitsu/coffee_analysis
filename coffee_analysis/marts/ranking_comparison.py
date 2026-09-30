from pathlib import Path

from coffee_analysis.infrastructure.analytical_database import AnalyticalDatabase
from coffee_analysis.infrastructure.data_directories import DataDirectories


class RankingComparison:
    def __init__(self, database: AnalyticalDatabase, directories: DataDirectories) -> None:
        self._database = database
        self._directories = directories

    def build(self) -> Path:
        destination = self._directories.marts_file("distritos_comparacao_ranking.parquet")
        return self._database.export_parquet(self._comparison_query(), destination)

    def _comparison_query(self) -> str:
        employment_metrics = self._directories.marts_file("distritos_metricas_rais.parquet")
        employment_index = self._directories.marts_file("distritos_indice_oportunidade_rais.parquet")
        survey_metrics = self._directories.marts_file("distritos_metricas.parquet")
        survey_index = self._directories.marts_file("distritos_indice_oportunidade.parquet")
        return f"""
            SELECT
                codigo_distrito,
                indice_rais.nome_distrito,
                metricas_rais.mercado_potencial_mensal AS mercado_potencial_mensal_rais,
                metricas_od.mercado_potencial_mensal AS mercado_potencial_mensal_od,
                metricas_rais.mercado_mensal_por_ponto_de_venda AS mercado_mensal_por_ponto_de_venda_rais,
                metricas_od.mercado_mensal_por_ponto_de_venda AS mercado_mensal_por_ponto_de_venda_od,
                indice_rais.indice_oportunidade AS indice_oportunidade_rais,
                indice_od.indice_oportunidade AS indice_oportunidade_od,
                indice_rais.posicao_ranking AS posicao_ranking_rais,
                indice_od.posicao_ranking AS posicao_ranking_od,
                indice_rais.posicao_ranking - indice_od.posicao_ranking AS posicoes_ganhas_com_od
            FROM '{employment_index}' AS indice_rais
            JOIN '{survey_index}' AS indice_od USING (codigo_distrito)
            JOIN '{employment_metrics}' AS metricas_rais USING (codigo_distrito)
            JOIN '{survey_metrics}' AS metricas_od USING (codigo_distrito)
            ORDER BY posicao_ranking_od
        """
