from pathlib import Path

from ponto_do_cafe.staging.rais.rais_releases import RaisReleases

FIXTURES_DIRECTORY = Path(__file__).parent / "fixtures"


def rais_listing() -> list[str]:
    text = (FIXTURES_DIRECTORY / "rais_listing.txt").read_text(encoding="utf-8")
    return [line for line in text.splitlines() if line]


def test_latest_year_among_ignores_partial_and_non_numeric_entries() -> None:
    assert RaisReleases().latest_year_among(rais_listing()) == "2025"


def test_latest_year_among_uses_only_the_last_path_segment() -> None:
    names = [f"/pdet/microdados/RAIS/{name}" for name in rais_listing()]
    assert RaisReleases().latest_year_among(names) == "2025"
