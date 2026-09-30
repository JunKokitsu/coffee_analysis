from pathlib import Path

import pytest

from coffee_analysis.infrastructure.data_directories import DataDirectories
from coffee_analysis.staging.ibge.ibge_download import IbgeDownload
from tests.recording_archive_extractor import RecordingArchiveExtractor
from tests.recording_download_client import RecordingDownloadClient


def test_ibge_download_downloads_all_files(tmp_path: Path) -> None:
    client = RecordingDownloadClient()
    extractor = RecordingArchiveExtractor()
    directories = DataDirectories(tmp_path, "2026-09")

    download = IbgeDownload(client, extractor, directories)
    download.build()

    assert len(client.download_calls) == 4
    assert client.download_calls[0][0] == "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/malha_com_atributos/setores/gpkg/UF/SP/SP_setores_CD2022.gpkg"
    assert client.download_calls[0][1] == tmp_path / "data" / "raw" / "ibge" / "SP_setores_CD2022.gpkg"
    assert client.download_calls[1][0] == "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/malha_com_atributos/distritos/gpkg/UF/SP/SP_distritos_CD2022.gpkg"
    assert client.download_calls[1][1] == tmp_path / "data" / "raw" / "ibge" / "SP_distritos_CD2022.gpkg"
    assert client.download_calls[2][0] == "https://ftp.ibge.gov.br/Cadastro_Nacional_de_Enderecos_para_Fins_Estatisticos/Censo_Demografico_2022/Arquivos_CNEFE/CSV/Municipio/35_SP/3550308_SAO_PAULO.zip"
    assert client.download_calls[2][1] == tmp_path / "data" / "raw" / "ibge" / "3550308_SAO_PAULO.zip"
    assert client.download_calls[3][0] == "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2010/Resultados_do_Universo/Agregados_por_Setores_Censitarios/SP_Capital_20260615.zip"
    assert client.download_calls[3][1] == tmp_path / "data" / "raw" / "ibge" / "SP_Capital_20260615.zip"


def test_ibge_download_extracts_cnefe_when_csv_missing(tmp_path: Path) -> None:
    client = RecordingDownloadClient()
    extractor = RecordingArchiveExtractor()
    directories = DataDirectories(tmp_path, "2026-09")

    download = IbgeDownload(client, extractor, directories)
    download.build()

    assert len(extractor.unzip_calls) == 2
    assert extractor.unzip_calls[0][0] == tmp_path / "data" / "raw" / "ibge" / "3550308_SAO_PAULO.zip"
    assert extractor.unzip_calls[0][1] == tmp_path / "data" / "raw" / "ibge"
    assert extractor.unzip_calls[0][2] == ()
    assert extractor.unzip_calls[0][3] is False


def test_ibge_download_extracts_censo_2010_with_patterns(tmp_path: Path) -> None:
    client = RecordingDownloadClient()
    extractor = RecordingArchiveExtractor()
    directories = DataDirectories(tmp_path, "2026-09")

    download = IbgeDownload(client, extractor, directories)
    download.build()

    assert len(extractor.unzip_calls) == 2
    assert extractor.unzip_calls[1][0] == tmp_path / "data" / "raw" / "ibge" / "SP_Capital_20260615.zip"
    assert extractor.unzip_calls[1][1] == tmp_path / "data" / "raw" / "ibge"
    assert extractor.unzip_calls[1][2] == ("*/CSV/Basico_SP1.csv", "*/CSV/DomicilioRenda_SP1.csv")
    assert extractor.unzip_calls[1][3] is True


def test_ibge_download_skips_cnefe_extraction_when_csv_exists(tmp_path: Path) -> None:
    client = RecordingDownloadClient()
    extractor = RecordingArchiveExtractor()
    directories = DataDirectories(tmp_path, "2026-09")
    ibge_directory = tmp_path / "data" / "raw" / "ibge"
    ibge_directory.mkdir(parents=True)

    extracted_file = ibge_directory / "3550308_SAO_PAULO.csv"
    extracted_file.write_bytes(b"data")

    download = IbgeDownload(client, extractor, directories)
    download.build()

    cnefe_calls = [call for call in extractor.unzip_calls if "3550308_SAO_PAULO.zip" in str(call[0])]
    assert len(cnefe_calls) == 0


def test_ibge_download_skips_censo_2010_extraction_when_csv_exists(tmp_path: Path) -> None:
    client = RecordingDownloadClient()
    extractor = RecordingArchiveExtractor()
    directories = DataDirectories(tmp_path, "2026-09")
    ibge_directory = tmp_path / "data" / "raw" / "ibge"
    ibge_directory.mkdir(parents=True)

    extracted_file = ibge_directory / "Basico_SP1.csv"
    extracted_file.write_bytes(b"data")

    download = IbgeDownload(client, extractor, directories)
    download.build()

    censo_calls = [call for call in extractor.unzip_calls if "SP_Capital_20260615.zip" in str(call[0])]
    assert len(censo_calls) == 0


def test_ibge_download_returns_ibge_directory(tmp_path: Path) -> None:
    client = RecordingDownloadClient()
    extractor = RecordingArchiveExtractor()
    directories = DataDirectories(tmp_path, "2026-09")

    download = IbgeDownload(client, extractor, directories)
    result = download.build()

    assert result == tmp_path / "data" / "raw" / "ibge"
