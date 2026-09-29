from datetime import date

from coffee_analysis.competence import Competence


def test_competence_of_day_uses_year_and_month() -> None:
    assert Competence.of(date(2026, 10, 20)) == Competence("2026-10")


def test_reference_date_is_today_inside_the_month() -> None:
    assert Competence("2026-09").reference_date(date(2026, 9, 23)) == date(2026, 9, 23)


def test_reference_date_is_last_day_for_past_months() -> None:
    assert Competence("2026-02").reference_date(date(2026, 9, 23)) == date(2026, 2, 28)
