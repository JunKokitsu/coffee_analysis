from pathlib import Path

from coffee_analysis.analytical_database import AnalyticalDatabase
from coffee_analysis.data_directories import DataDirectories

RAIS_SAO_PAULO_MUNICIPALITY_CODE = "355030"
SNACK_BAR_ACTIVITY = "5611203"
FULL_TIME_WEEKLY_HOURS = 40


class RaisWorkforce:
    def __init__(self, database: AnalyticalDatabase, directories: DataDirectories) -> None:
        self._database = database
        self._directories = directories

    def build(self) -> Path:
        self._database.export_parquet(
            self._district_jobs_query(),
            self._directories.processed_file("rais_distritos.parquet"),
        )
        self._database.export_parquet(
            self._establishment_jobs_query(),
            self._directories.processed_file("rais_estabelecimentos_cep.parquet"),
        )
        return self._database.export_parquet(
            self._wages_query(),
            self._directories.processed_file("rais_salarios_lanchonetes.parquet"),
        )

    def _establishments_source(self) -> str:
        source = self._directories.raw_file("rais", "RAIS_ESTAB_PUB.COMT")
        return f"""
            SELECT
                lpad(trim("CEP Estab"), 8, '0') AS cep,
                trim("CNAE 2.0 Subclasse - Codigo") AS cnae,
                TRY_CAST("Qtd Vínculos Ativos" AS INTEGER) AS vinculos_ativos
            FROM read_csv('{source}', delim=',', header=true, all_varchar=true, encoding='latin-1')
            WHERE "Município - Código" = '{RAIS_SAO_PAULO_MUNICIPALITY_CODE}'
        """

    def _establishment_jobs_query(self) -> str:
        postal_codes = self._directories.processed_file("cep_distrito.parquet")
        return f"""
            WITH estabelecimentos AS ({self._establishments_source()})
            SELECT
                estabelecimentos.cep,
                cep_distrito.codigo_distrito,
                cep_distrito.latitude,
                cep_distrito.longitude,
                sum(estabelecimentos.vinculos_ativos) AS vinculos_ativos
            FROM estabelecimentos
            JOIN '{postal_codes}' AS cep_distrito USING (cep)
            GROUP BY ALL
        """

    def _district_jobs_query(self) -> str:
        postal_codes = self._directories.processed_file("cep_distrito.parquet")
        return f"""
            WITH estabelecimentos AS ({self._establishments_source()}),
            localizados AS (
                SELECT estabelecimentos.*, cep_distrito.codigo_distrito
                FROM estabelecimentos
                JOIN '{postal_codes}' AS cep_distrito USING (cep)
            )
            SELECT
                codigo_distrito,
                sum(vinculos_ativos) AS vinculos_ativos_total,
                count(*) FILTER (WHERE cnae = '{SNACK_BAR_ACTIVITY}' AND vinculos_ativos > 0) AS lanchonetes_com_empregados,
                avg(vinculos_ativos) FILTER (WHERE cnae = '{SNACK_BAR_ACTIVITY}' AND vinculos_ativos > 0) AS media_vinculos_por_lanchonete,
                median(vinculos_ativos) FILTER (WHERE cnae = '{SNACK_BAR_ACTIVITY}' AND vinculos_ativos > 0) AS mediana_vinculos_por_lanchonete
            FROM localizados
            GROUP BY codigo_distrito
        """

    def _wages_query(self) -> str:
        source = self._directories.raw_file("rais", "RAIS_VINC_PUB_SP.COMT")
        return f"""
            WITH ocupacoes(codigo_ocupacao, ocupacao) AS (
                VALUES
                    ('513435', 'Atendente de lanchonete'),
                    ('513505', 'Auxiliar nos serviços de alimentação'),
                    ('513205', 'Cozinheiro geral'),
                    ('513405', 'Garçom'),
                    ('421125', 'Operador de caixa'),
                    ('141510', 'Gerente de restaurante')
            ),
            vinculos AS (
                SELECT
                    "CBO 2002 Ocupação - Código" AS codigo_ocupacao,
                    TRY_CAST(replace("Vl Rem Média Nom", ',', '.') AS DOUBLE) AS remuneracao_media,
                    TRY_CAST("Mês Admissão - Código" AS INTEGER) AS mes_admissao
                FROM read_csv('{source}', delim=',', header=true, all_varchar=true, encoding='latin-1')
                WHERE "Município - Código" = '{RAIS_SAO_PAULO_MUNICIPALITY_CODE}'
                    AND trim("CNAE 2.0 Subclasse - Codigo") = '{SNACK_BAR_ACTIVITY}'
                    AND "Ind Vínculo Ativo 31/12 - Código" = '1'
                    AND TRY_CAST("Qtd Hora Contr" AS INTEGER) >= {FULL_TIME_WEEKLY_HOURS}
            )
            SELECT
                ocupacoes.codigo_ocupacao,
                ocupacoes.ocupacao,
                count(*) AS vinculos,
                quantile_cont(vinculos.remuneracao_media, 0.25) AS remuneracao_percentil_25,
                median(vinculos.remuneracao_media) AS remuneracao_mediana,
                quantile_cont(vinculos.remuneracao_media, 0.75) AS remuneracao_percentil_75,
                median(vinculos.remuneracao_media) FILTER (WHERE vinculos.mes_admissao > 0) AS remuneracao_mediana_admitidos_no_ano
            FROM vinculos
            JOIN ocupacoes USING (codigo_ocupacao)
            WHERE vinculos.remuneracao_media > 0
            GROUP BY ALL
            ORDER BY vinculos DESC
        """
