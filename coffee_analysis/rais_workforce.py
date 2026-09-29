from pathlib import Path

from coffee_analysis.analytical_database import AnalyticalDatabase
from coffee_analysis.data_directories import DataDirectories

SNACK_BAR_ACTIVITY = "5611203"
FULL_TIME_WEEKLY_HOURS = 40


class RaisWorkforce:
    def __init__(self, database: AnalyticalDatabase, directories: DataDirectories) -> None:
        self._database = database
        self._directories = directories

    def build(self) -> Path:
        self._database.export_parquet(self._district_jobs_query(), self._directories.marts_file("distritos_empregos_formais.parquet"))
        self._database.export_parquet(self._establishment_jobs_query(), self._directories.marts_file("empregos_formais_cep.parquet"))
        return self._database.export_parquet(self._wages_query(), self._directories.marts_file("salarios_lanchonetes.parquet"))

    def _located_establishments(self) -> str:
        establishments = self._directories.staging_file("rais", "estabelecimentos.parquet")
        postal_codes = self._directories.staging_file("cnefe", "cep_distrito.parquet")
        return f"""
            SELECT estabelecimentos.*, cep_distrito.codigo_distrito, cep_distrito.latitude, cep_distrito.longitude
            FROM '{establishments}' AS estabelecimentos
            JOIN '{postal_codes}' AS cep_distrito USING (cep)
        """

    def _establishment_jobs_query(self) -> str:
        return f"""
            SELECT cep, codigo_distrito, latitude, longitude, sum(vinculos_ativos) AS vinculos_ativos
            FROM ({self._located_establishments()})
            GROUP BY ALL
        """

    def _district_jobs_query(self) -> str:
        return f"""
            SELECT
                codigo_distrito,
                sum(vinculos_ativos) AS vinculos_ativos_total,
                count(*) FILTER (WHERE cnae = '{SNACK_BAR_ACTIVITY}' AND vinculos_ativos > 0) AS lanchonetes_com_empregados,
                avg(vinculos_ativos) FILTER (WHERE cnae = '{SNACK_BAR_ACTIVITY}' AND vinculos_ativos > 0) AS media_vinculos_por_lanchonete,
                median(vinculos_ativos) FILTER (WHERE cnae = '{SNACK_BAR_ACTIVITY}' AND vinculos_ativos > 0) AS mediana_vinculos_por_lanchonete
            FROM ({self._located_establishments()})
            GROUP BY codigo_distrito
        """

    def _wages_query(self) -> str:
        links = self._directories.staging_file("rais", "vinculos_alimentacao.parquet")
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
                SELECT codigo_ocupacao, remuneracao_media, mes_admissao
                FROM '{links}'
                WHERE cnae = '{SNACK_BAR_ACTIVITY}' AND ativo_31_dezembro AND horas_contratadas >= {FULL_TIME_WEEKLY_HOURS}
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
