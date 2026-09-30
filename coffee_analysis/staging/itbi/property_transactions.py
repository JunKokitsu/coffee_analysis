import re
from pathlib import Path

import fastexcel
import polars

from coffee_analysis.infrastructure.analytical_database import AnalyticalDatabase
from coffee_analysis.infrastructure.data_directories import DataDirectories

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
MONTH_SHEET_PATTERN = re.compile(r"^[A-Z]{3}-\d{4}$")


class PropertyTransactions:
    def __init__(self, database: AnalyticalDatabase, directories: DataDirectories) -> None:
        self._database = database
        self._directories = directories

    def build(self) -> Path:
        self._database.register_frame("transacoes_itbi_bruto", self._read_transactions())
        destination = self._directories.staging_file("itbi", "transacoes.parquet")
        return self._database.export_parquet(self._typed_query(), destination)

    def _read_transactions(self) -> polars.DataFrame:
        source = self._directories.raw_competence_file("itbi", "guias_itbi.xlsx")
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

    def _typed_query(self) -> str:
        return """
            SELECT
                lpad(regexp_replace(cep, '\\.0$', ''), 8, '0') AS cep,
                natureza_transacao,
                TRY_CAST(valor_transacao AS DOUBLE) AS valor_transacao,
                TRY_CAST(proporcao_transmitida AS DOUBLE) AS proporcao_transmitida,
                TRY_CAST(area_construida AS DOUBLE) AS area_construida,
                trim(descricao_uso) AS descricao_uso,
                trim(descricao_padrao) AS descricao_padrao,
                mes_referencia
            FROM transacoes_itbi_bruto
        """
