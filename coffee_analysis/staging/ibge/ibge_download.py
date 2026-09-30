from pathlib import Path

from coffee_analysis.infrastructure.archive_extractor import ArchiveExtractor
from coffee_analysis.infrastructure.data_directories import DataDirectories
from coffee_analysis.infrastructure.http_client import HttpClient


class IbgeDownload:
    def __init__(
        self,
        http_client: HttpClient,
        extractor: ArchiveExtractor,
        directories: DataDirectories,
    ) -> None:
        self._http_client = http_client
        self._extractor = extractor
        self._directories = directories

    def build(self) -> Path:
        ibge_raw_directory = self._directories.raw_file("ibge")
        self._download_all_files()
        self._extract_cnefe_if_needed(ibge_raw_directory)
        self._extract_censo_2010_if_needed(ibge_raw_directory)
        return ibge_raw_directory

    def _download_all_files(self) -> None:
        setores = "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios"
        cnefe = "https://ftp.ibge.gov.br/Cadastro_Nacional_de_Enderecos_para_Fins_Estatisticos/Censo_Demografico_2022/Arquivos_CNEFE"
        censo_2010 = "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2010/Resultados_do_Universo/Agregados_por_Setores_Censitarios"

        self._download_file(
            "SP_setores_CD2022.gpkg",
            f"{setores}/malha_com_atributos/setores/gpkg/UF/SP/SP_setores_CD2022.gpkg",
        )
        self._download_file(
            "SP_distritos_CD2022.gpkg",
            f"{setores}/malha_com_atributos/distritos/gpkg/UF/SP/SP_distritos_CD2022.gpkg",
        )
        self._download_file(
            "3550308_SAO_PAULO.zip",
            f"{cnefe}/CSV/Municipio/35_SP/3550308_SAO_PAULO.zip",
        )
        self._download_file(
            "SP_Capital_20260615.zip",
            f"{censo_2010}/SP_Capital_20260615.zip",
        )

    def _download_file(self, file_name: str, url: str) -> None:
        destination = self._directories.raw_file("ibge", file_name)
        self._http_client.download(url, destination)

    def _extract_cnefe_if_needed(self, ibge_raw_directory: Path) -> None:
        extracted_file = ibge_raw_directory / "3550308_SAO_PAULO.csv"
        if extracted_file.exists() and extracted_file.stat().st_size > 0:
            return
        archive = ibge_raw_directory / "3550308_SAO_PAULO.zip"
        self._extractor.unzip(archive, ibge_raw_directory)

    def _extract_censo_2010_if_needed(self, ibge_raw_directory: Path) -> None:
        extracted_file = ibge_raw_directory / "Basico_SP1.csv"
        if extracted_file.exists() and extracted_file.stat().st_size > 0:
            return
        archive = ibge_raw_directory / "SP_Capital_20260615.zip"
        member_patterns = ("*/CSV/Basico_SP1.csv", "*/CSV/DomicilioRenda_SP1.csv")
        self._extractor.unzip(archive, ibge_raw_directory, member_patterns, flatten=True)
