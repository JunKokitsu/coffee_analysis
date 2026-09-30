from pathlib import Path

from coffee_analysis.infrastructure.analytical_database import AnalyticalDatabase
from coffee_analysis.infrastructure.data_directories import DataDirectories

MINIMUM_BUILT_AREA = 15


class CommercialPropertyPrices:
    def __init__(self, database: AnalyticalDatabase, directories: DataDirectories) -> None:
        self._database = database
        self._directories = directories

    def build(self) -> Path:
        destination = self._directories.marts_file("distritos_preco_m2_comercial.parquet")
        return self._database.export_parquet(self._district_prices_query(), destination)

    def _district_prices_query(self) -> str:
        transactions = self._directories.staging_file("itbi", "transacoes.parquet")
        postal_codes = self._directories.staging_file("cnefe", "cep_distrito.parquet")
        return f"""
            WITH validas AS (
                SELECT transacoes.*, cep_distrito.codigo_distrito, valor_transacao / area_construida AS preco_m2
                FROM '{transactions}' AS transacoes
                JOIN '{postal_codes}' AS cep_distrito USING (cep)
                WHERE natureza_transacao LIKE '1.%'
                    AND (descricao_uso LIKE 'LOJA%' OR descricao_padrao = 'COMERCIAL HORIZONTAL')
                    AND proporcao_transmitida = 100
                    AND area_construida >= {MINIMUM_BUILT_AREA}
                    AND valor_transacao > 0
            )
            SELECT
                codigo_distrito,
                count(*) AS transacoes_comerciais,
                median(preco_m2) AS preco_mediano_m2_comercial,
                quantile_cont(preco_m2, 0.25) AS preco_m2_comercial_percentil_25,
                quantile_cont(preco_m2, 0.75) AS preco_m2_comercial_percentil_75
            FROM validas
            GROUP BY codigo_distrito
        """
