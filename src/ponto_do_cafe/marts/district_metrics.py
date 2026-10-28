from datetime import date
from pathlib import Path

from ponto_do_cafe.infrastructure.analytical_database import AnalyticalDatabase
from ponto_do_cafe.infrastructure.data_directories import DataDirectories

POF_REFERENCE_MONTH = 201801
COFFEE_CUP_ITEM_CODE = "7438"
SNACK_ITEM_CODE = "7435"
WORKPLACE_CONSUMPTION_SHARE = 0.5
CLOSED_REGISTRATION_STATUSES = "3, 4, 8"


class DistrictMetrics:
    def __init__(self, database: AnalyticalDatabase, directories: DataDirectories, reference_date: date) -> None:
        self._database = database
        self._directories = directories
        self._reference_date = reference_date

    def build(self) -> Path:
        destination = self._directories.marts_file("distritos_metricas_rais.parquet")
        self._database.export_parquet(self._metrics_query(), destination)
        return destination

    def _competition_query(self) -> str:
        establishments = self._directories.marts_file("estabelecimentos_cafe.parquet")
        reference = f"DATE '{self._reference_date.isoformat()}'"
        return f"""
            SELECT
                codigo_distrito,
                count(*) FILTER (WHERE ativo AND categoria = 'cafeteria') AS cafeterias_ativas,
                count(*) FILTER (WHERE ativo AND categoria = 'lanchonete') AS lanchonetes_ativas,
                count(*) FILTER (WHERE ativo AND categoria = 'padaria') AS padarias_ativas,
                count(*) FILTER (WHERE categoria = 'cafeteria' AND data_inicio_atividade > {reference} - INTERVAL 12 MONTH) AS cafeterias_abertas_12_meses,
                count(*) FILTER (WHERE categoria = 'cafeteria' AND data_inicio_atividade > {reference} - INTERVAL 24 MONTH) AS cafeterias_abertas_24_meses,
                count(*) FILTER (
                    WHERE categoria = 'cafeteria'
                        AND situacao_cadastral IN ({CLOSED_REGISTRATION_STATUSES})
                        AND data_situacao_cadastral > {reference} - INTERVAL 24 MONTH
                ) AS cafeterias_fechadas_24_meses
            FROM '{establishments}'
            WHERE codigo_distrito IS NOT NULL
            GROUP BY codigo_distrito
        """

    def _metrics_query(self) -> str:
        districts = self._directories.staging_file("censo_2022", "distritos.parquet")
        income = self._directories.marts_file("distritos_renda_gasto_cafe.parquet")
        prices = self._directories.staging_file("ipca", "variacao_mensal_rmsp.parquet")
        workforce = self._directories.marts_file("distritos_empregos_formais.parquet")
        property_prices = self._directories.marts_file("distritos_preco_m2_comercial.parquet")
        survival = self._directories.marts_file("sobrevivencia_distritos.parquet")
        return f"""
            WITH fator AS (
                SELECT
                    exp(sum(ln(1 + variacao_mensal_percentual / 100)) FILTER (WHERE codigo_item = '{COFFEE_CUP_ITEM_CODE}')) AS fator_cafezinho,
                    exp(sum(ln(1 + variacao_mensal_percentual / 100)) FILTER (WHERE codigo_item = '{SNACK_ITEM_CODE}')) AS fator_lanche
                FROM '{prices}'
                WHERE mes > {POF_REFERENCE_MONTH}
            ),
            sobrevivencia AS (
                SELECT codigo_distrito, taxa_sobrevivencia AS sobrevivencia_3_anos, negocios_expostos AS amostra_sobrevivencia_3_anos
                FROM '{survival}'
                WHERE anos = 3 AND categoria = 'cafeteria_e_lanchonete'
            ),
            base AS (
                SELECT
                    distritos.codigo_distrito,
                    distritos.nome_distrito,
                    distritos.area_km2,
                    distritos.populacao_2022,
                    distritos.domicilios_2022,
                    renda.renda_media_domiciliar_2010,
                    renda.renda_media_domiciliar_salarios_minimos,
                    renda.gasto_cafe_fora_por_domicilio_2018 * fator.fator_cafezinho AS gasto_cafe_fora_por_domicilio_atual,
                    renda.gasto_lanches_fora_por_domicilio_2018 * fator.fator_lanche AS gasto_lanches_fora_por_domicilio_atual,
                    renda.gasto_cafe_fora_por_domicilio_2018 * fator.fator_cafezinho
                        + renda.gasto_lanches_fora_por_domicilio_2018 * fator.fator_lanche AS gasto_cesta_cafeteria_por_domicilio_atual,
                    distritos.domicilios_2022 * renda.gasto_cafe_fora_por_domicilio_2018 * fator.fator_cafezinho AS gasto_mensal_cafe_residentes,
                    distritos.domicilios_2022 * (
                        renda.gasto_cafe_fora_por_domicilio_2018 * fator.fator_cafezinho
                        + renda.gasto_lanches_fora_por_domicilio_2018 * fator.fator_lanche
                    ) AS gasto_mensal_residentes,
                    coalesce(trabalho.vinculos_ativos_total, 0) AS vinculos_formais,
                    trabalho.media_vinculos_por_lanchonete,
                    trabalho.mediana_vinculos_por_lanchonete,
                    coalesce(concorrencia.cafeterias_ativas, 0) AS cafeterias_ativas,
                    coalesce(concorrencia.lanchonetes_ativas, 0) AS lanchonetes_ativas,
                    coalesce(concorrencia.padarias_ativas, 0) AS padarias_ativas,
                    coalesce(concorrencia.cafeterias_abertas_12_meses, 0) AS cafeterias_abertas_12_meses,
                    coalesce(concorrencia.cafeterias_abertas_24_meses, 0) AS cafeterias_abertas_24_meses,
                    coalesce(concorrencia.cafeterias_fechadas_24_meses, 0) AS cafeterias_fechadas_24_meses,
                    sobrevivencia.sobrevivencia_3_anos,
                    sobrevivencia.amostra_sobrevivencia_3_anos,
                    imoveis.preco_mediano_m2_comercial,
                    imoveis.transacoes_comerciais
                FROM read_parquet('{districts}') AS distritos
                CROSS JOIN fator
                LEFT JOIN '{income}' AS renda USING (codigo_distrito)
                LEFT JOIN '{workforce}' AS trabalho USING (codigo_distrito)
                LEFT JOIN ({self._competition_query()}) AS concorrencia USING (codigo_distrito)
                LEFT JOIN sobrevivencia USING (codigo_distrito)
                LEFT JOIN '{property_prices}' AS imoveis USING (codigo_distrito)
            ),
            cidade AS (
                SELECT
                    sum(gasto_mensal_residentes) / sum(populacao_2022) AS gasto_per_capita_cidade,
                    sum(gasto_mensal_cafe_residentes) / sum(populacao_2022) AS gasto_cafe_per_capita_cidade
                FROM base
            ),
            mercado AS (
                SELECT
                    base.*,
                    cidade.gasto_per_capita_cidade,
                    cidade.gasto_cafe_per_capita_cidade,
                    (1 - {WORKPLACE_CONSUMPTION_SHARE}) * base.gasto_mensal_residentes
                        + {WORKPLACE_CONSUMPTION_SHARE} * base.vinculos_formais * cidade.gasto_per_capita_cidade AS mercado_potencial_mensal,
                    (1 - {WORKPLACE_CONSUMPTION_SHARE}) * base.gasto_mensal_cafe_residentes
                        + {WORKPLACE_CONSUMPTION_SHARE} * base.vinculos_formais * cidade.gasto_cafe_per_capita_cidade AS mercado_cafe_mensal
                FROM base
                CROSS JOIN cidade
            )
            SELECT
                *,
                cafeterias_ativas + lanchonetes_ativas + padarias_ativas AS pontos_de_venda_cafe,
                mercado_potencial_mensal / nullif(cafeterias_ativas, 0) AS mercado_mensal_por_cafeteria,
                mercado_potencial_mensal / nullif(cafeterias_ativas + lanchonetes_ativas + padarias_ativas, 0) AS mercado_mensal_por_ponto_de_venda,
                cafeterias_ativas * 10000.0 / nullif(populacao_2022 + vinculos_formais, 0) AS cafeterias_por_10_mil_pessoas,
                cafeterias_abertas_24_meses / nullif(cafeterias_ativas, 0) AS crescimento_oferta_24_meses,
                cafeterias_abertas_24_meses - cafeterias_fechadas_24_meses AS saldo_cafeterias_24_meses,
                populacao_2022 / area_km2 AS densidade_demografica
            FROM mercado
            ORDER BY codigo_distrito
        """
