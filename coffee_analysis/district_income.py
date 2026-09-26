from pathlib import Path

from coffee_analysis.analytical_database import AnalyticalDatabase
from coffee_analysis.data_directories import DataDirectories

MINIMUM_WAGE_2010 = 510.0


class DistrictIncome:
    def __init__(self, database: AnalyticalDatabase, directories: DataDirectories) -> None:
        self._database = database
        self._directories = directories

    def build(self) -> Path:
        return self._database.export_parquet(
            self._district_query(),
            self._directories.processed_file("distritos_renda_gasto_cafe.parquet"),
        )

    def _district_query(self) -> str:
        basic_file = self._directories.raw_file("ibge", "Basico_SP1.csv")
        income_file = self._directories.raw_file("ibge", "DomicilioRenda_SP1.csv")
        spending_file = self._directories.processed_file("pof_gasto_cafe_sp.parquet")
        return f"""
            WITH basico AS (
                SELECT
                    CAST(Cod_setor AS VARCHAR) AS codigo_setor,
                    CAST(Cod_distrito AS VARCHAR) AS codigo_distrito,
                    TRY_CAST(V001 AS DOUBLE) AS domicilios
                FROM read_csv('{basic_file}', delim=';', header=true, all_varchar=true, encoding='latin-1')
            ),
            renda AS (
                SELECT CAST(Cod_setor AS VARCHAR) AS codigo_setor, TRY_CAST(V003 AS DOUBLE) AS renda_total
                FROM read_csv('{income_file}', delim=';', header=true, all_varchar=true, encoding='latin-1')
            ),
            setores AS (
                SELECT
                    basico.codigo_setor,
                    basico.codigo_distrito,
                    basico.domicilios,
                    renda.renda_total,
                    renda.renda_total / basico.domicilios AS renda_media_domiciliar
                FROM basico
                JOIN renda USING (codigo_setor)
                WHERE basico.domicilios > 0 AND renda.renda_total IS NOT NULL
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
