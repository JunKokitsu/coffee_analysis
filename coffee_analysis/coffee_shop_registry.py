import io
import zipfile
from collections.abc import Callable
from pathlib import Path

from coffee_analysis.analytical_database import AnalyticalDatabase
from coffee_analysis.data_directories import DataDirectories

RECEITA_SAO_PAULO_MUNICIPALITY_CODE = "7107"
MUNICIPALITY_MARKER = f';"{RECEITA_SAO_PAULO_MUNICIPALITY_CODE}";'
ESTABLISHMENT_COLUMNS = [
    "cnpj_basico",
    "cnpj_ordem",
    "cnpj_digito",
    "identificador_matriz_filial",
    "nome_fantasia",
    "situacao_cadastral",
    "data_situacao_cadastral",
    "motivo_situacao_cadastral",
    "nome_cidade_exterior",
    "pais",
    "data_inicio_atividade",
    "cnae_principal",
    "cnae_secundaria",
    "tipo_logradouro",
    "logradouro",
    "numero",
    "complemento",
    "bairro",
    "cep",
    "uf",
    "municipio",
    "ddd_1",
    "telefone_1",
    "ddd_2",
    "telefone_2",
    "ddd_fax",
    "fax",
    "email",
    "situacao_especial",
    "data_situacao_especial",
]
COMPANY_COLUMNS = [
    "cnpj_basico",
    "razao_social",
    "natureza_juridica",
    "qualificacao_responsavel",
    "capital_social",
    "porte_empresa",
    "ente_federativo",
]
FOOD_SERVICE_ACTIVITIES = "'5611201', '5611203', '5611204', '5611205', '4721102', '1091102', '1081302'"
BAKERY_NAME_PATTERN = r"(^|[^A-Z])(PADARIA|PANIFICADORA|PANIFICACAO|PAES|PAO|BAKERY|BOULANGERIE)([^A-Z]|$)"
COFFEE_NAME_PATTERN = r"(^|[^A-Z])(CAFE|CAFES|CAFETERIA|COFFEE|ESPRESSO|EXPRESSO|BARISTA|TORREFACAO|TORRA)([^A-Z]|$)"


class CoffeeShopRegistry:
    def __init__(self, database: AnalyticalDatabase, directories: DataDirectories) -> None:
        self._database = database
        self._directories = directories

    def build(self) -> Path:
        establishment_parts = [self._filter_establishments(archive) for archive in self._directories.raw_files("cnpj", "Estabelecimentos*.zip")]
        self._database.execute(self._union_view("estabelecimentos_alimentacao", establishment_parts))
        company_codes = self._company_codes()
        company_parts = [self._filter_companies(archive, company_codes) for archive in self._directories.raw_files("cnpj", "Empresas*.zip")]
        self._database.execute(self._companies_view(company_parts))
        return self._database.export_parquet(
            self._classified_query(),
            self._directories.processed_file("estabelecimentos_cafe.parquet"),
        )

    def _union_view(self, name: str, parts: list[Path]) -> str:
        files = ", ".join(f"'{part}'" for part in parts)
        return f"CREATE OR REPLACE VIEW {name} AS SELECT * FROM read_parquet([{files}])"

    def _companies_view(self, parts: list[Path]) -> str:
        if not parts:
            return "CREATE OR REPLACE VIEW empresas_alimentacao AS SELECT NULL::VARCHAR AS cnpj_basico, NULL::VARCHAR AS razao_social WHERE false"
        return self._union_view("empresas_alimentacao", parts)

    def _extract(self, archive: Path, keep_line: Callable[[str], bool]) -> Path:
        extracted = self._directories.temporary_directory() / f"{archive.stem}.csv"
        with zipfile.ZipFile(archive) as compressed, compressed.open(compressed.namelist()[0]) as member:
            lines = io.TextIOWrapper(member, encoding="latin-1", newline="")
            kept_lines = (line for line in lines if keep_line(line))
            extracted.write_text("".join(kept_lines), encoding="utf-8")
        return extracted

    def _is_sao_paulo_line(self, line: str) -> bool:
        return MUNICIPALITY_MARKER in line

    def _filter_establishments(self, archive: Path) -> Path:
        destination = self._directories.processed_file(f"cnpj_{archive.stem}.parquet")
        if destination.exists():
            return destination
        extracted = self._extract(archive, self._is_sao_paulo_line)
        self._database.export_parquet(self._establishment_query(extracted), destination)
        extracted.unlink()
        return destination

    def _filter_companies(self, archive: Path, company_codes: frozenset[str]) -> Path:
        destination = self._directories.processed_file(f"cnpj_{archive.stem}.parquet")
        if destination.exists():
            return destination
        extracted = self._extract(archive, lambda line: line[1:9] in company_codes)
        self._database.export_parquet(self._company_query(extracted), destination)
        extracted.unlink()
        return destination

    def _company_codes(self) -> frozenset[str]:
        codes = self._database.frame("SELECT DISTINCT cnpj_basico FROM estabelecimentos_alimentacao")
        return frozenset(codes["cnpj_basico"].to_list())

    def _csv_reader(self, source: Path, columns: list[str]) -> str:
        column_types = ", ".join(f"'{column}': 'VARCHAR'" for column in columns)
        return f"read_csv('{source}', delim=';', quote='\"', header=false, columns={{{column_types}}}, strict_mode=false, ignore_errors=true)"

    def _establishment_query(self, source: Path) -> str:
        return f"""
            SELECT *
            FROM {self._csv_reader(source, ESTABLISHMENT_COLUMNS)}
            WHERE municipio = '{RECEITA_SAO_PAULO_MUNICIPALITY_CODE}'
                AND cnae_principal IN ({FOOD_SERVICE_ACTIVITIES})
        """

    def _company_query(self, source: Path) -> str:
        return f"""
            SELECT empresas.cnpj_basico, empresas.razao_social, empresas.capital_social
            FROM {self._csv_reader(source, COMPANY_COLUMNS)} AS empresas
        """

    def _classified_query(self) -> str:
        addresses = self._directories.processed_file("enderecos_cnefe.parquet")
        postal_codes = self._directories.processed_file("cep_distrito.parquet")
        return f"""
            WITH base AS (
                SELECT
                    estabelecimentos.cnpj_basico || estabelecimentos.cnpj_ordem || estabelecimentos.cnpj_digito AS cnpj,
                    estabelecimentos.nome_fantasia,
                    empresas.razao_social,
                    estabelecimentos.cnae_principal,
                    TRY_CAST(estabelecimentos.situacao_cadastral AS INTEGER) AS situacao_cadastral,
                    TRY_STRPTIME(estabelecimentos.data_inicio_atividade, '%Y%m%d')::DATE AS data_inicio_atividade,
                    TRY_STRPTIME(estabelecimentos.data_situacao_cadastral, '%Y%m%d')::DATE AS data_situacao_cadastral,
                    lpad(estabelecimentos.cep, 8, '0') AS cep,
                    TRY_CAST(regexp_extract(estabelecimentos.numero, '[0-9]+') AS INTEGER) AS numero,
                    estabelecimentos.logradouro,
                    estabelecimentos.bairro,
                    strip_accents(upper(coalesce(estabelecimentos.nome_fantasia, '') || ' ' || coalesce(empresas.razao_social, ''))) AS nome_normalizado
                FROM estabelecimentos_alimentacao AS estabelecimentos
                LEFT JOIN (SELECT DISTINCT cnpj_basico, razao_social FROM empresas_alimentacao) AS empresas USING (cnpj_basico)
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
                SELECT cep, numero, any_value(codigo_distrito) AS codigo_distrito, avg(latitude) AS latitude, avg(longitude) AS longitude
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
