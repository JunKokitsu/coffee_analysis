from pathlib import Path

from coffee_analysis.infrastructure.analytical_database import AnalyticalDatabase
from coffee_analysis.infrastructure.data_directories import DataDirectories
from coffee_analysis.staging.ibge.sidra_table import SidraTable

METROPOLITAN_REGION_SAO_PAULO = "3501"
COFFEE_ITEMS = "7169,7392,7435,7438"


class ConsumerPriceIndex:
    def __init__(self, database: AnalyticalDatabase, directories: DataDirectories) -> None:
        self._database = database
        self._directories = directories

    def build(self) -> Path:
        older_series = SidraTable(
            f"t/1419/n7/{METROPOLITAN_REGION_SAO_PAULO}/v/63/p/all/c315/{COFFEE_ITEMS}",
            self._directories.current_raw_file("ipca", "ipca_1419_rmsp.json"),
        )
        recent_series = SidraTable(
            f"t/7060/n7/{METROPOLITAN_REGION_SAO_PAULO}/v/63/p/all/c315/{COFFEE_ITEMS}",
            self._directories.current_raw_file("ipca", "ipca_7060_rmsp.json"),
        )
        older_file = older_series.download()
        recent_file = recent_series.download()
        return self._database.export_parquet(
            self._monthly_variation_query(older_file, recent_file),
            self._directories.staging_file("ipca", "variacao_mensal_rmsp.parquet"),
        )

    def _monthly_variation_query(self, older_file: Path, recent_file: Path) -> str:
        return f"""
            WITH bruto AS (
                SELECT D3C AS mes, D4C AS codigo_item, D4N AS item, V AS valor
                FROM read_json_auto(['{older_file}', '{recent_file}'])
                WHERE NC <> 'Nível Territorial (Código)'
            )
            SELECT
                CAST(mes AS INTEGER) AS mes,
                codigo_item,
                regexp_replace(item, '^[0-9]+\\.', '') AS item,
                TRY_CAST(valor AS DOUBLE) AS variacao_mensal_percentual
            FROM bruto
            WHERE TRY_CAST(valor AS DOUBLE) IS NOT NULL
            ORDER BY codigo_item, mes
        """
