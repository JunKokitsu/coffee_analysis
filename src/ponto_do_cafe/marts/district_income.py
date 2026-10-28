from pathlib import Path

from ponto_do_cafe.infrastructure.analytical_database import AnalyticalDatabase
from ponto_do_cafe.infrastructure.data_directories import DataDirectories

MINIMUM_WAGE_2010 = 510.0


class DistrictIncome:
    def __init__(self, database: AnalyticalDatabase, directories: DataDirectories) -> None:
        self._database = database
        self._directories = directories

    def build(self) -> Path:
        return self._database.export_parquet(
            self._district_query(),
            self._directories.marts_file("distritos_renda_gasto_cafe.parquet"),
        )

    def _district_query(self) -> str:
        sectors_file = self._directories.staging_file("censo_2010", "setores_renda.parquet")
        spending_file = self._directories.staging_file("pof", "gasto_cafe_sp.parquet")
        return f"""
            WITH setores AS (
                SELECT *, renda_total / domicilios AS renda_media_domiciliar
                FROM '{sectors_file}'
                WHERE domicilios > 0 AND renda_total IS NOT NULL
            ),
            classes AS (
                SELECT * FROM '{spending_file}' WHERE limite_inferior_salarios_minimos IS NOT NULL
            ),
            setores_com_gasto AS (
                SELECT setores.*, classes.gasto_cafe_fora_domicilio, classes.gasto_lanches_fora_domicilio, classes.gasto_cafe_moido
                FROM setores
                JOIN classes
                    ON setores.renda_media_domiciliar / {MINIMUM_WAGE_2010} >= classes.limite_inferior_salarios_minimos
                    AND setores.renda_media_domiciliar / {MINIMUM_WAGE_2010} < coalesce(classes.limite_superior_salarios_minimos, 1e9)
            )
            SELECT
                codigo_distrito,
                sum(renda_total) / sum(domicilios) AS renda_media_domiciliar_2010,
                sum(renda_total) / sum(domicilios) / {MINIMUM_WAGE_2010} AS renda_media_domiciliar_salarios_minimos,
                sum(domicilios) AS domicilios_2010,
                sum(domicilios * gasto_cafe_fora_domicilio) / sum(domicilios) AS gasto_cafe_fora_por_domicilio_2018,
                sum(domicilios * gasto_lanches_fora_domicilio) / sum(domicilios) AS gasto_lanches_fora_por_domicilio_2018,
                sum(domicilios * gasto_cafe_moido) / sum(domicilios) AS gasto_cafe_moido_por_domicilio_2018
            FROM setores_com_gasto
            GROUP BY codigo_distrito
        """
