import polars

from coffee_analysis.quality_result import QualityResult


class QualityResults:
    def __init__(self, results: tuple[QualityResult, ...]) -> None:
        self._results = results

    def frame(self, competence: str) -> polars.DataFrame:
        return polars.DataFrame([result.as_row(competence) for result in self._results])

    def failure_lines(self) -> list[str]:
        return [result.failure_line() for result in self._results if not result.passed]
