import ftplib
from pathlib import Path

import pytest

from ponto_do_cafe.infrastructure.ftp_client import FtpClient
from tests.fake_ftp_connection import FAKE_FTP_FILE_CONTENT, FakeFtpConnection


def reset_created_connections() -> None:
    FakeFtpConnection.created_connections = []


def test_download_writes_content_from_retrbinary_callback(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    reset_created_connections()
    monkeypatch.setattr(ftplib, "FTP", FakeFtpConnection)
    destination = tmp_path / "arquivo.7z"
    FtpClient().download("ftp.mtps.gov.br", "/pdet/microdados/RAIS/2025/RAIS_ESTAB_PUB.7z", destination)
    assert destination.read_bytes() == FAKE_FTP_FILE_CONTENT
    connection = FakeFtpConnection.created_connections[0]
    assert connection.host == "ftp.mtps.gov.br"
    assert connection.login_call_count == 1
    assert connection.retrbinary_commands == ["RETR /pdet/microdados/RAIS/2025/RAIS_ESTAB_PUB.7z"]


def test_download_creates_parent_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    reset_created_connections()
    monkeypatch.setattr(ftplib, "FTP", FakeFtpConnection)
    destination = tmp_path / "rais" / "2025" / "arquivo.7z"
    FtpClient().download("ftp.mtps.gov.br", "/pdet/microdados/RAIS/2025/arquivo.7z", destination)
    assert destination.exists()


def test_download_is_idempotent_and_does_not_open_connection(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    reset_created_connections()
    monkeypatch.setattr(ftplib, "FTP", FakeFtpConnection)
    destination = tmp_path / "arquivo.7z"
    destination.write_bytes(b"ja baixado")
    FtpClient().download("ftp.mtps.gov.br", "/pdet/microdados/RAIS/2025/RAIS_ESTAB_PUB.7z", destination)
    assert destination.read_bytes() == b"ja baixado"
    assert FakeFtpConnection.created_connections == []
