import json
from pathlib import Path

import geopandas
import polars

from coffee_analysis.analytical_database import AnalyticalDatabase
from coffee_analysis.dashboard.index_version import IndexVersion
from coffee_analysis.data_directories import DataDirectories


class DashboardData:
    def __init__(self, database: AnalyticalDatabase, directories: DataDirectories) -> None:
        self._database = database
        self._directories = directories

    def ranking(self, version: IndexVersion) -> polars.DataFrame:
        metrics = self._directories.marts_file(version.metrics_file)
        index = self._directories.marts_file(version.index_file)
        return self._database.frame(f"""
            SELECT
                indice.codigo_distrito,
                indice.nome_distrito,
                indice.posicao_ranking,
                indice.indice_oportunidade,
                metricas.mercado_potencial_mensal,
                metricas.mercado_mensal_por_ponto_de_venda,
                metricas.cafeterias_ativas,
                metricas.pontos_de_venda_cafe,
                metricas.sobrevivencia_3_anos,
                metricas.preco_mediano_m2_comercial
            FROM '{index}' AS indice
            JOIN '{metrics}' AS metricas USING (codigo_distrito)
            ORDER BY indice.posicao_ranking
        """)

    def comparison(self) -> polars.DataFrame:
        comparison = self._directories.marts_file("distritos_comparacao_ranking.parquet")
        return self._database.frame(f"SELECT * FROM '{comparison}' ORDER BY posicao_ranking_od")

    def district_profile(self) -> polars.DataFrame:
        metrics = self._directories.marts_file("distritos_metricas.parquet")
        index = self._directories.marts_file("distritos_indice_oportunidade.parquet")
        mobility = self._directories.marts_file("distritos_mobilidade.parquet")
        return self._database.frame(f"""
            SELECT metricas.*, indice.* EXCLUDE (codigo_distrito, nome_distrito), mobilidade.* EXCLUDE (codigo_distrito, viagens_atraidas_nao_residenciais)
            FROM '{metrics}' AS metricas
            JOIN '{index}' AS indice USING (codigo_distrito)
            JOIN '{mobility}' AS mobilidade USING (codigo_distrito)
            ORDER BY metricas.nome_distrito
        """).drop("geometry", strict=False)

    def influence_areas(self) -> polars.DataFrame:
        areas = self._directories.marts_file("areas_influencia.parquet")
        return self._database.frame(f"SELECT * FROM '{areas}' ORDER BY endereco_candidato, raio_metros")

    def quality_results(self) -> polars.DataFrame:
        results = self._directories.quality_file(f"resultado_{self._directories.competence}.parquet")
        if not results.exists():
            return polars.DataFrame()
        return polars.read_parquet(results)

    def district_shapes(self) -> dict[str, object]:
        districts = geopandas.read_parquet(self._directories.staging_file("censo_2022", "distritos.parquet"))
        simplified = districts[["codigo_distrito", "geometry"]].copy()
        simplified["geometry"] = simplified.geometry.simplify(0.0005)
        return json.loads(simplified.to_json())

    def updated_at(self) -> float:
        report = self._directories.report_file("piloto_novas_cafeterias.md")
        return Path(report).stat().st_mtime
