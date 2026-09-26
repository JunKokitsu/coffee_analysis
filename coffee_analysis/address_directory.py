from pathlib import Path

from coffee_analysis.analytical_database import AnalyticalDatabase
from coffee_analysis.data_directories import DataDirectories


class AddressDirectory:
    def __init__(self, database: AnalyticalDatabase, directories: DataDirectories) -> None:
        self._database = database
        self._directories = directories

    def build(self) -> Path:
        self._database.execute(self._addresses_view())
        self._database.export_parquet(self._addresses_query(), self._directories.processed_file("enderecos_cnefe.parquet"))
        return self._database.export_parquet(self._postal_code_query(), self._directories.processed_file("cep_distrito.parquet"))

    def _addresses_view(self) -> str:
        source = self._directories.raw_file("ibge", "3550308_SAO_PAULO.csv")
        return f"""
            CREATE OR REPLACE VIEW enderecos_cnefe_bruto AS
            SELECT
                CEP AS cep,
                COD_DISTRITO AS codigo_distrito,
                COD_SETOR AS codigo_setor,
                COD_ESPECIE AS codigo_especie,
                upper(trim(concat_ws(' ', NOM_TIPO_SEGLOGR, NOM_TITULO_SEGLOGR, NOM_SEGLOGR))) AS logradouro,
                TRY_CAST(NUM_ENDERECO AS INTEGER) AS numero,
                TRY_CAST(LATITUDE AS DOUBLE) AS latitude,
                TRY_CAST(LONGITUDE AS DOUBLE) AS longitude
            FROM read_csv('{source}', delim=';', header=true, all_varchar=true)
        """

    def _addresses_query(self) -> str:
        return """
            SELECT
                cep,
                logradouro,
                numero,
                mode(codigo_distrito) AS codigo_distrito,
                avg(latitude) AS latitude,
                avg(longitude) AS longitude,
                count(*) AS quantidade_enderecos,
                count(*) FILTER (WHERE codigo_especie = '6') AS quantidade_estabelecimentos
            FROM enderecos_cnefe_bruto
            GROUP BY cep, logradouro, numero
        """

    def _postal_code_query(self) -> str:
        return """
            WITH contagem AS (
                SELECT cep, codigo_distrito, count(*) AS quantidade
                FROM enderecos_cnefe_bruto
                GROUP BY cep, codigo_distrito
            ),
            ordenado AS (
                SELECT *, row_number() OVER (PARTITION BY cep ORDER BY quantidade DESC) AS posicao
                FROM contagem
            ),
            centroide AS (
                SELECT cep, avg(latitude) AS latitude, avg(longitude) AS longitude
                FROM enderecos_cnefe_bruto
                GROUP BY cep
            )
            SELECT ordenado.cep, ordenado.codigo_distrito, centroide.latitude, centroide.longitude
            FROM ordenado
            JOIN centroide USING (cep)
            WHERE ordenado.posicao = 1
        """
