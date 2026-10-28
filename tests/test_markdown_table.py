from ponto_do_cafe.reporting.markdown_table import MarkdownTable


def test_render_builds_header_separator_and_rows() -> None:
    table = MarkdownTable(["Distrito", "Posição"], [["Pinheiros", "37"], ["Itaquera", "74"]])
    assert table.render() == "| Distrito | Posição |\n| --- | --- |\n| Pinheiros | 37 |\n| Itaquera | 74 |"
