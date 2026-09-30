from coffee_analysis.staging.rais.rais_releases import RaisReleases


class FixedRaisReleases(RaisReleases):
    def __init__(self, year: str) -> None:
        super().__init__()
        self._year = year

    def latest_year(self) -> str:
        return self._year
