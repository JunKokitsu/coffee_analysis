from pathlib import Path

import pytest

from coffee_analysis.infrastructure.data_directories import DataDirectories


def test_raw_competence_picks_latest_folder_up_to_competence(tmp_path: Path) -> None:
    for folder in ("2025", "2026-08-27", "2026-10-02"):
        tmp_path.joinpath("data", "raw", "fonte", folder).mkdir(parents=True)
    assert DataDirectories(tmp_path, "2026-09").raw_competence("fonte").name == "2026-08-27"
    assert DataDirectories(tmp_path, "2026-01").raw_competence("fonte").name == "2025"


def test_raw_competence_fails_without_folder(tmp_path: Path) -> None:
    tmp_path.joinpath("data", "raw", "fonte", "2027").mkdir(parents=True)
    with pytest.raises(FileNotFoundError):
        DataDirectories(tmp_path, "2026-09").raw_competence("fonte")
