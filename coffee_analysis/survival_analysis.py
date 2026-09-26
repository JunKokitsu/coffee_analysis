from datetime import date
from pathlib import Path

from coffee_analysis.analytical_database import AnalyticalDatabase
from coffee_analysis.data_directories import DataDirectories

FIRST_COHORT_DATE = "2012-01-01"
CLOSED_REGISTRATION_STATUSES = "3, 4, 8"


class SurvivalAnalysis:
    def __init__(self, database: AnalyticalDatabase, directories: DataDirectories, reference_date: date) -> None:
        self._database = database
        self._directories = directories
        self._reference_date = reference_date

    def build(self) -> Path:
        return self._database.export_parquet(
            self._survival_query(),
            self._directories.processed_file("sobrevivencia_distritos.parquet"),
        )

    def _survival_query(self) -> str:
        establishments = self._directories.processed_file("estabelecimentos_cafe.parquet")
        return f"""
            WITH coortes AS (
                SELECT
                    codigo_distrito,
                    categoria,
                    data_inicio_atividade,
                    CASE WHEN situacao_cadastral IN ({CLOSED_REGISTRATION_STATUSES}) THEN data_situacao_cadastral END AS data_fechamento
                FROM '{establishments}'
                WHERE data_inicio_atividade >= DATE '{FIRST_COHORT_DATE}'
                    AND categoria IN ('cafeteria', 'lanchonete')
                    AND codigo_distrito IS NOT NULL
            ),
            horizontes(anos) AS (VALUES (1), (2), (3), (5)),
            exposicao AS (
                SELECT coortes.*, horizontes.anos
                FROM coortes
                CROSS JOIN horizontes
                WHERE coortes.data_inicio_atividade + to_years(horizontes.anos) <= DATE '{self._reference_date.isoformat()}'
            ),
            resultado AS (
                SELECT
                    coalesce(codigo_distrito, 'cidade') AS codigo_distrito,
                    coalesce(categoria, 'cafeteria_e_lanchonete') AS categoria,
                    anos,
                    count(*) AS negocios_expostos,
                    count(*) FILTER (
                        WHERE data_fechamento IS NULL OR data_fechamento > data_inicio_atividade + to_years(anos)
                    ) AS negocios_sobreviventes
                FROM exposicao
                GROUP BY GROUPING SETS ((codigo_distrito, categoria, anos), (codigo_distrito, anos), (categoria, anos), (anos))
            )
            SELECT *, negocios_sobreviventes / negocios_expostos AS taxa_sobrevivencia
            FROM resultado
        """
