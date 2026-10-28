from pathlib import Path

from ponto_do_cafe.infrastructure.analytical_database import AnalyticalDatabase
from ponto_do_cafe.infrastructure.data_directories import DataDirectories

RAIS_SAO_PAULO_MUNICIPALITY_CODE = "355030"
FOOD_SERVICE_ACTIVITY_PREFIX = "5611"


class RaisRegistry:
    def __init__(self, database: AnalyticalDatabase, directories: DataDirectories) -> None:
        self._database = database
        self._directories = directories

    def build(self) -> Path:
        self._database.export_parquet(self._establishments_query(), self._directories.staging_file("rais", "estabelecimentos.parquet"))
        return self._database.export_parquet(self._employment_links_query(), self._directories.staging_file("rais", "vinculos_alimentacao.parquet"))

    def _establishments_query(self) -> str:
        source = self._directories.raw_competence_file("rais", "RAIS_ESTAB_PUB.COMT")
        return f"""
            SELECT
                lpad(trim("CEP Estab"), 8, '0') AS cep,
                trim("CNAE 2.0 Subclasse - Codigo") AS cnae,
                TRY_CAST("Qtd Vínculos Ativos" AS INTEGER) AS vinculos_ativos
            FROM read_csv('{source}', delim=',', header=true, all_varchar=true, encoding='latin-1')
            WHERE "Município - Código" = '{RAIS_SAO_PAULO_MUNICIPALITY_CODE}'
        """

    def _employment_links_query(self) -> str:
        source = self._directories.raw_competence_file("rais", "RAIS_VINC_PUB_SP.COMT")
        return f"""
            SELECT
                trim("CNAE 2.0 Subclasse - Codigo") AS cnae,
                "CBO 2002 Ocupação - Código" AS codigo_ocupacao,
                TRY_CAST(replace("Vl Rem Média Nom", ',', '.') AS DOUBLE) AS remuneracao_media,
                TRY_CAST("Mês Admissão - Código" AS INTEGER) AS mes_admissao,
                TRY_CAST("Qtd Hora Contr" AS INTEGER) AS horas_contratadas,
                "Ind Vínculo Ativo 31/12 - Código" = '1' AS ativo_31_dezembro
            FROM read_csv('{source}', delim=',', header=true, all_varchar=true, encoding='latin-1')
            WHERE "Município - Código" = '{RAIS_SAO_PAULO_MUNICIPALITY_CODE}'
                AND starts_with(trim("CNAE 2.0 Subclasse - Codigo"), '{FOOD_SERVICE_ACTIVITY_PREFIX}')
        """
