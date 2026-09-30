from pathlib import Path

from coffee_analysis.infrastructure.analytical_database import AnalyticalDatabase
from coffee_analysis.infrastructure.data_directories import DataDirectories

BAKERY_NAME_PATTERN = r"(^|[^A-Z])(PADARIA|PANIFICADORA|PANIFICACAO|PAES|PAO|BAKERY|BOULANGERIE)([^A-Z]|$)"
COFFEE_NAME_PATTERN = r"(^|[^A-Z])(CAFE|CAFES|CAFETERIA|COFFEE|ESPRESSO|EXPRESSO|BARISTA|TORREFACAO|TORRA)([^A-Z]|$)"


class CoffeeShopClassification:
    def __init__(self, database: AnalyticalDatabase, directories: DataDirectories) -> None:
        self._database = database
        self._directories = directories

    def build(self) -> Path:
        destination = self._directories.marts_file("estabelecimentos_cafe.parquet")
        return self._database.export_parquet(self._classified_query(), destination)

    def _classified_query(self) -> str:
        establishments = self._directories.staging_file("cnpj", "estabelecimentos_alimentacao.parquet")
        companies = self._directories.staging_file("cnpj", "empresas_alimentacao.parquet")
        addresses = self._directories.staging_file("cnefe", "enderecos.parquet")
        postal_codes = self._directories.staging_file("cnefe", "cep_distrito.parquet")
        return f"""
            WITH base AS (
                SELECT
                    estabelecimentos.cnpj,
                    estabelecimentos.nome_fantasia,
                    empresas.razao_social,
                    estabelecimentos.cnae AS cnae_principal,
                    estabelecimentos.situacao_cadastral,
                    estabelecimentos.data_inicio_atividade,
                    estabelecimentos.data_situacao_cadastral,
                    estabelecimentos.cep,
                    estabelecimentos.numero,
                    estabelecimentos.logradouro,
                    estabelecimentos.bairro,
                    strip_accents(upper(coalesce(estabelecimentos.nome_fantasia, '') || ' ' || coalesce(empresas.razao_social, ''))) AS nome_normalizado
                FROM '{establishments}' AS estabelecimentos
                LEFT JOIN '{companies}' AS empresas USING (cnpj_basico)
            ),
            classificado AS (
                SELECT
                    *,
                    CASE
                        WHEN regexp_matches(nome_normalizado, '{COFFEE_NAME_PATTERN}') THEN 'cafeteria'
                        WHEN cnae_principal = '5611203' THEN 'lanchonete'
                        WHEN cnae_principal = '4721102' THEN 'padaria'
                        WHEN cnae_principal = '1091102' AND regexp_matches(nome_normalizado, '{BAKERY_NAME_PATTERN}') THEN 'padaria'
                    END AS categoria,
                    situacao_cadastral = 2 AS ativo
                FROM base
            ),
            enderecos AS (
                SELECT cep, numero, arg_max(codigo_distrito, (quantidade_enderecos, -CAST(codigo_distrito AS BIGINT))) AS codigo_distrito, avg(latitude) AS latitude, avg(longitude) AS longitude
                FROM '{addresses}'
                GROUP BY cep, numero
            )
            SELECT
                classificado.*,
                coalesce(enderecos.codigo_distrito, cep_distrito.codigo_distrito) AS codigo_distrito,
                coalesce(enderecos.latitude, cep_distrito.latitude) AS latitude,
                coalesce(enderecos.longitude, cep_distrito.longitude) AS longitude,
                CASE WHEN enderecos.latitude IS NOT NULL THEN 'endereco' WHEN cep_distrito.latitude IS NOT NULL THEN 'cep' ELSE 'sem_localizacao' END AS precisao_localizacao
            FROM classificado
            LEFT JOIN enderecos USING (cep, numero)
            LEFT JOIN '{postal_codes}' AS cep_distrito ON classificado.cep = cep_distrito.cep
            WHERE classificado.categoria IS NOT NULL
        """
