from pathlib import Path

from ponto_do_cafe.infrastructure.analytical_database import AnalyticalDatabase
from ponto_do_cafe.infrastructure.data_directories import DataDirectories


class CensusSectorIncome:
    def __init__(self, database: AnalyticalDatabase, directories: DataDirectories) -> None:
        self._database = database
        self._directories = directories

    def build(self) -> Path:
        destination = self._directories.staging_file("censo_2010", "setores_renda.parquet")
        return self._database.export_parquet(self._sectors_query(), destination)

    def _sectors_query(self) -> str:
        basic_file = self._directories.raw_file("ibge", "Basico_SP1.csv")
        income_file = self._directories.raw_file("ibge", "DomicilioRenda_SP1.csv")
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
            )
            SELECT basico.codigo_setor, basico.codigo_distrito, basico.domicilios, renda.renda_total
            FROM basico
            LEFT JOIN renda USING (codigo_setor)
            ORDER BY basico.codigo_setor
        """
