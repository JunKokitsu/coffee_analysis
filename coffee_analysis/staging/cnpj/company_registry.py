import io
import zipfile
from collections.abc import Callable
from pathlib import Path

from coffee_analysis.infrastructure.analytical_database import AnalyticalDatabase
from coffee_analysis.infrastructure.data_directories import DataDirectories

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


class CompanyRegistry:
    def __init__(self, database: AnalyticalDatabase, directories: DataDirectories) -> None:
        self._database = database
        self._directories = directories

    def build(self) -> Path:
        competence = self._directories.raw_competence("cnpj")
        establishment_parts = [self._filter_establishments(archive) for archive in sorted(competence.glob("Estabelecimentos*.zip"))]
        self._database.execute(self._union_view("estabelecimentos_alimentacao", establishment_parts))
        company_codes = self._company_codes()
        company_parts = [self._filter_companies(archive, company_codes) for archive in sorted(competence.glob("Empresas*.zip"))]
        self._database.execute(self._companies_view(company_parts))
        self._database.export_parquet(self._companies_query(), self._directories.staging_file("cnpj", "empresas_alimentacao.parquet"))
        return self._database.export_parquet(self._establishments_query(), self._directories.staging_file("cnpj", "estabelecimentos_alimentacao.parquet"))

    def _parts_directory(self) -> Path:
        competence = self._directories.raw_competence("cnpj")
        directory = self._directories.temporary_directory() / "cnpj" / competence.name
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def _union_view(self, name: str, parts: list[Path]) -> str:
        files = ", ".join(f"'{part}'" for part in parts)
        return f"CREATE OR REPLACE VIEW {name} AS SELECT * FROM read_parquet([{files}])"

    def _companies_view(self, parts: list[Path]) -> str:
        if not parts:
            return "CREATE OR REPLACE VIEW empresas_alimentacao AS SELECT NULL::VARCHAR AS cnpj_basico, NULL::VARCHAR AS razao_social, NULL::VARCHAR AS capital_social WHERE false"
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
        destination = self._parts_directory() / f"cnpj_{archive.stem}.parquet"
        if destination.exists():
            return destination
        extracted = self._extract(archive, self._is_sao_paulo_line)
        self._database.export_parquet(self._establishment_part_query(extracted), destination)
        extracted.unlink()
        return destination

    def _filter_companies(self, archive: Path, company_codes: frozenset[str]) -> Path:
        destination = self._parts_directory() / f"cnpj_{archive.stem}.parquet"
        if destination.exists():
            return destination
        extracted = self._extract(archive, lambda line: line[1:9] in company_codes)
        self._database.export_parquet(self._company_part_query(extracted), destination)
        extracted.unlink()
        return destination

    def _company_codes(self) -> frozenset[str]:
        codes = self._database.frame("SELECT DISTINCT cnpj_basico FROM estabelecimentos_alimentacao")
        return frozenset(codes["cnpj_basico"].to_list())

    def _csv_reader(self, source: Path, columns: list[str]) -> str:
        column_types = ", ".join(f"'{column}': 'VARCHAR'" for column in columns)
        return f"read_csv('{source}', delim=';', quote='\"', header=false, columns={{{column_types}}}, strict_mode=false, ignore_errors=true)"

    def _establishment_part_query(self, source: Path) -> str:
        return f"""
            SELECT *
            FROM {self._csv_reader(source, ESTABLISHMENT_COLUMNS)}
            WHERE municipio = '{RECEITA_SAO_PAULO_MUNICIPALITY_CODE}'
                AND cnae_principal IN ({FOOD_SERVICE_ACTIVITIES})
        """

    def _company_part_query(self, source: Path) -> str:
        return f"""
            SELECT empresas.cnpj_basico, empresas.razao_social, empresas.capital_social
            FROM {self._csv_reader(source, COMPANY_COLUMNS)} AS empresas
        """

    def _companies_query(self) -> str:
        return """
            SELECT cnpj_basico, any_value(razao_social) AS razao_social, any_value(TRY_CAST(replace(capital_social, ',', '.') AS DOUBLE)) AS capital_social
            FROM empresas_alimentacao
            GROUP BY cnpj_basico
        """

    def _establishments_query(self) -> str:
        return """
            SELECT
                cnpj_basico || cnpj_ordem || cnpj_digito AS cnpj,
                cnpj_basico,
                nome_fantasia,
                cnae_principal AS cnae,
                TRY_CAST(situacao_cadastral AS INTEGER) AS situacao_cadastral,
                TRY_STRPTIME(data_inicio_atividade, '%Y%m%d')::DATE AS data_inicio_atividade,
                TRY_STRPTIME(data_situacao_cadastral, '%Y%m%d')::DATE AS data_situacao_cadastral,
                lpad(cep, 8, '0') AS cep,
                TRY_CAST(regexp_extract(numero, '[0-9]+') AS INTEGER) AS numero,
                logradouro,
                bairro
            FROM estabelecimentos_alimentacao
        """
