import shutil
import subprocess
import zipfile
from pathlib import Path

import pytest

from ponto_do_cafe.infrastructure.archive_extractor import ArchiveExtractor

SEVEN_ZIP_BINARY = shutil.which("7z") or shutil.which("7zz")


def build_sample_zip(archive_path: Path) -> Path:
    with zipfile.ZipFile(archive_path, "w") as zip_file:
        zip_file.writestr("top.txt", "conteudo do topo")
        zip_file.writestr("CSV/Basico_SP1.csv", "coluna_a;coluna_b\n1;2\n")
        zip_file.writestr("CSV/Outro.csv", "x;y\n3;4\n")
    return archive_path


def test_unzip_extracts_everything_preserving_structure(tmp_path: Path) -> None:
    archive_path = build_sample_zip(tmp_path / "sample.zip")
    destination = tmp_path / "extracted"
    ArchiveExtractor().unzip(archive_path, destination)
    assert (destination / "top.txt").read_text() == "conteudo do topo"
    assert (destination / "CSV" / "Basico_SP1.csv").exists()
    assert (destination / "CSV" / "Outro.csv").exists()


def test_unzip_extracts_only_matching_pattern(tmp_path: Path) -> None:
    archive_path = build_sample_zip(tmp_path / "sample.zip")
    destination = tmp_path / "extracted"
    ArchiveExtractor().unzip(archive_path, destination, member_patterns=("CSV/Basico_SP1.csv",))
    assert (destination / "CSV" / "Basico_SP1.csv").exists()
    assert not (destination / "CSV" / "Outro.csv").exists()
    assert not (destination / "top.txt").exists()


def test_unzip_flattens_matching_members(tmp_path: Path) -> None:
    archive_path = build_sample_zip(tmp_path / "sample.zip")
    destination = tmp_path / "extracted"
    ArchiveExtractor().unzip(archive_path, destination, member_patterns=("*/Basico_SP1.csv",), flatten=True)
    assert (destination / "Basico_SP1.csv").read_text() == "coluna_a;coluna_b\n1;2\n"
    assert not (destination / "CSV").exists()


def test_extract_seven_zip_raises_when_binary_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda name: None)
    archive_path = tmp_path / "sample.7z"
    archive_path.write_bytes(b"nao importa")
    with pytest.raises(FileNotFoundError):
        ArchiveExtractor().extract_seven_zip(archive_path, tmp_path / "extracted")


@pytest.mark.skipif(SEVEN_ZIP_BINARY is None, reason="binário 7z/7zz não disponível")
def test_extract_seven_zip_extracts_real_archive(tmp_path: Path) -> None:
    source_directory = tmp_path / "source"
    source_directory.mkdir()
    (source_directory / "arquivo.txt").write_text("conteudo compactado")
    archive_path = tmp_path / "sample.7z"
    subprocess.run(
        [SEVEN_ZIP_BINARY, "a", "-y", str(archive_path), str(source_directory / "arquivo.txt")],
        check=True,
        capture_output=True,
    )
    destination = tmp_path / "extracted"
    ArchiveExtractor().extract_seven_zip(archive_path, destination)
    assert (destination / "arquivo.txt").read_text() == "conteudo compactado"
