import calendar
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Competence:
    month: str

    @classmethod
    def of(cls, day: date) -> "Competence":
        return cls(day.strftime("%Y-%m"))

    def reference_date(self, today: date) -> date:
        year, month = (int(part) for part in self.month.split("-"))
        last_day = date(year, month, calendar.monthrange(year, month)[1])
        return min(today, last_day)
