class MarkdownTable:
    def __init__(self, headers: list[str], rows: list[list[str]]) -> None:
        self._headers = headers
        self._rows = rows

    def render(self) -> str:
        header_line = self._line(self._headers)
        separator_line = self._line(["---"] * len(self._headers))
        body_lines = [self._line(row) for row in self._rows]
        return "\n".join([header_line, separator_line, *body_lines])

    def _line(self, cells: list[str]) -> str:
        return "| " + " | ".join(cells) + " |"
