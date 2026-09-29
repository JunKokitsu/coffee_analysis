from pathlib import Path

from coffee_analysis.analytical_database import AnalyticalDatabase
from coffee_analysis.data_directories import DataDirectories
from coffee_analysis.sidra_table import SidraTable

MINIMUM_WAGE_2018 = 954.0
POF_EXPENSE_TYPES = "103679,103692,103694,103697"


class HouseholdCoffeeSpending:
    def __init__(self, database: AnalyticalDatabase, directories: DataDirectories) -> None:
        self._database = database
        self._directories = directories

    def build(self) -> Path:
        table = SidraTable(
            f"t/6972/n3/35/v/1201/p/2018/c339/all/c12190/{POF_EXPENSE_TYPES}",
            self._directories.raw_file("pof", "pof_6972_sp.json"),
        )
        source = table.download()
        return self._database.export_parquet(
            self._spending_query(source),
            self._directories.staging_file("pof", "gasto_cafe_sp.parquet"),
        )

    def _spending_query(self, source: Path) -> str:
        return f"""
            WITH bruto AS (
                SELECT D4N AS classe_rendimento, D5C AS codigo_despesa, TRY_CAST(V AS DOUBLE) AS valor
                FROM read_json_auto('{source}')
                WHERE NC <> 'Nível Territorial (Código)'
            ),
            pivotado AS (
                SELECT
                    classe_rendimento,
                    max(valor) FILTER (WHERE codigo_despesa = '103694') AS gasto_cafe_fora_domicilio,
                    max(valor) FILTER (WHERE codigo_despesa = '103697') AS gasto_lanches_fora_domicilio,
                    max(valor) FILTER (WHERE codigo_despesa = '103679') AS gasto_cafe_moido,
                    max(valor) FILTER (WHERE codigo_despesa = '103692') AS gasto_alimentacao_fora_domicilio
                FROM bruto
                GROUP BY classe_rendimento
            ),
            limites AS (
                SELECT
                    *,
                    list_transform(
                        regexp_extract_all(replace(classe_rendimento, '.', ''), '[0-9]+'),
                        numero -> CAST(numero AS DOUBLE)
                    ) AS valores
                FROM pivotado
            )
            SELECT
                classe_rendimento,
                CASE
                    WHEN classe_rendimento = 'Total' THEN NULL
                    WHEN classe_rendimento LIKE 'Até%' THEN 0.0
                    ELSE valores[1] / {MINIMUM_WAGE_2018}
                END AS limite_inferior_salarios_minimos,
                CASE
                    WHEN classe_rendimento LIKE 'Até%' THEN valores[1] / {MINIMUM_WAGE_2018}
                    WHEN len(valores) = 2 THEN valores[2] / {MINIMUM_WAGE_2018}
                END AS limite_superior_salarios_minimos,
                gasto_cafe_fora_domicilio,
                gasto_lanches_fora_domicilio,
                gasto_cafe_moido,
                gasto_alimentacao_fora_domicilio
            FROM limites
        """
