from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class MetricDefinition:
    label: str
    column: str
    formatter: Callable[[float | None], str]
    source: str

    def row(self, values: dict[str, tuple[float | None, ...]]) -> list[str]:
        metric_values = values.get(self.column, ())
        formatted = [self.formatter(value) for value in metric_values]
        return [self.label, *formatted, self.source]
