from pathlib import Path

from ponto_do_cafe.infrastructure.data_directories import DataDirectories
from ponto_do_cafe.staging.rais.rais_download import RAIS_DIRECTORY, RAIS_HOST, RaisDownload
from tests.fake_rais_ftp_client import FakeRaisFtpClient
from tests.fake_seven_zip_extractor import FakeSevenZipExtractor
from tests.fixed_rais_releases import FixedRaisReleases


def build_directories(tmp_path: Path) -> DataDirectories:
    return DataDirectories(tmp_path, "2026-09")


def test_build_downloads_both_files_and_extracts_when_marker_missing(tmp_path: Path) -> None:
    ftp_client = FakeRaisFtpClient()
    extractor = FakeSevenZipExtractor()
    releases = FixedRaisReleases("2025")
    download = RaisDownload(ftp_client, releases, extractor, build_directories(tmp_path))
    result = download.build()
    assert len(ftp_client.download_calls) == 2
    assert len(extractor.extract_seven_zip_calls) == 2
    assert result == tmp_path / "data" / "raw" / "rais" / "2025"


def test_build_uses_expected_host_and_remote_path(tmp_path: Path) -> None:
    ftp_client = FakeRaisFtpClient()
    extractor = FakeSevenZipExtractor()
    releases = FixedRaisReleases("2025")
    download = RaisDownload(ftp_client, releases, extractor, build_directories(tmp_path))
    download.build()
    host, remote_path, destination = ftp_client.download_calls[0]
    assert host == RAIS_HOST
    assert remote_path == f"{RAIS_DIRECTORY}/2025/RAIS_ESTAB_PUB.7z"
    assert destination == tmp_path / "data" / "raw" / "rais" / "2025" / "RAIS_ESTAB_PUB.7z"


def test_build_skips_extraction_when_marker_already_exists(tmp_path: Path) -> None:
    ftp_client = FakeRaisFtpClient()
    extractor = FakeSevenZipExtractor()
    releases = FixedRaisReleases("2025")
    directories = build_directories(tmp_path)
    marker = directories.raw_file("rais", "2025", "RAIS_ESTAB_PUB.COMT")
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_bytes(b"conteudo")
    RaisDownload(ftp_client, releases, extractor, directories).build()
    extracted_archives = [archive for archive, _ in extractor.extract_seven_zip_calls]
    assert directories.raw_file("rais", "2025", "RAIS_ESTAB_PUB.7z") not in extracted_archives
    assert directories.raw_file("rais", "2025", "RAIS_VINC_PUB_SP.7z") in extracted_archives
