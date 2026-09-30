from coffee_analysis.reporting.markdown_table import MarkdownTable
from coffee_analysis.reporting.metric_definition import MetricDefinition


class MetricDefinitions:
    def __init__(self, definitions: tuple[MetricDefinition, ...]) -> None:
        self._definitions = definitions

    def columns(self) -> list[str]:
        return [definition.column for definition in self._definitions]

    def table(self, headers: list[str], values: dict[str, tuple[float | None, ...]]) -> MarkdownTable:
        rows = [definition.row(values) for definition in self._definitions]
        return MarkdownTable(headers, rows)
