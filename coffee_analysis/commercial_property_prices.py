import re
from pathlib import Path

import fastexcel
import polars

from coffee_analysis.analytical_database import AnalyticalDatabase
from coffee_analysis.data_directories import DataDirectories

SELECTED_COLUMNS = {
    "CEP": "cep",
    "Natureza de Transação": "natureza_transacao",
    "Valor de Transação (declarado pelo contribuinte)": "valor_transacao",
    "Proporção Transmitida (%)": "proporcao_transmitida",
    "Área Construída (m2)": "area_construida",
    "Descrição do uso (IPTU)": "descricao_uso",
    "Descrição do padrão (IPTU)": "descricao_padrao",
}
MISSPELLED_COLUMNS = {"Descrição do pardão (IPTU)": "Descrição do padrão (IPTU)"}
MINIMUM_BUILT_AREA = 15
MONTH_SHEET_PATTERN = re.compile(r"^[A-Z]{3}-\d{4}$")


class CommercialPropertyPrices:
    def __init__(self, database: AnalyticalDatabase, directories: DataDirectories) -> None:
        self._database = database
        self._directories = directories

    def build(self) -> Path:
        transactions = self._read_transactions()
        self._database.register_frame("transacoes_itbi", transactions)
        return self._database.export_parquet(
            self._district_prices_query(),
            self._directories.processed_file("itbi_preco_m2_comercial.parquet"),
        )

    def _read_transactions(self) -> polars.DataFrame:
        source = self._directories.raw_file("itbi", "guias_itbi_2026.xlsx")
        workbook = fastexcel.read_excel(source)
        month_sheets = [name for name in workbook.sheet_names if MONTH_SHEET_PATTERN.match(name)]
        frames = [self._read_sheet(workbook, sheet_name) for sheet_name in month_sheets]
        return polars.concat(frames, how="vertical_relaxed")

    def _read_sheet(self, workbook: fastexcel.ExcelReader, sheet_name: str) -> polars.DataFrame:
        sheet = workbook.load_sheet_by_name(sheet_name, dtypes="string")
        frame = sheet.to_polars()
        corrected = frame.rename(MISSPELLED_COLUMNS, strict=False)
        selected = corrected.select(list(SELECTED_COLUMNS))
        renamed = selected.rename(SELECTED_COLUMNS)
        month_label = polars.lit(sheet_name)
        return renamed.with_columns(month_label.alias("mes_referencia"))

    def _district_prices_query(self) -> str:
        postal_codes = self._directories.processed_file("cep_distrito.parquet")
        return f"""
            WITH transacoes AS (
                SELECT
                    lpad(regexp_replace(cep, '\\.0$', ''), 8, '0') AS cep,
                    TRY_CAST(valor_transacao AS DOUBLE) AS valor_transacao,
                    TRY_CAST(proporcao_transmitida AS DOUBLE) AS proporcao_transmitida,
                    TRY_CAST(area_construida AS DOUBLE) AS area_construida,
                    descricao_uso
                FROM transacoes_itbi
                WHERE natureza_transacao LIKE '1.%'
                    AND (descricao_uso LIKE 'LOJA%' OR trim(descricao_padrao) = 'COMERCIAL HORIZONTAL')
            ),
            validas AS (
                SELECT transacoes.*, cep_distrito.codigo_distrito, valor_transacao / area_construida AS preco_m2
                FROM transacoes
                JOIN '{postal_codes}' AS cep_distrito USING (cep)
                WHERE proporcao_transmitida = 100 AND area_construida >= {MINIMUM_BUILT_AREA} AND valor_transacao > 0
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
