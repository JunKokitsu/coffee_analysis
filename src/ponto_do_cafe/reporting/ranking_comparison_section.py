from ponto_do_cafe.infrastructure.analytical_database import AnalyticalDatabase
from ponto_do_cafe.reporting.brazilian_number_format import BrazilianNumberFormat
from ponto_do_cafe.infrastructure.data_directories import DataDirectories
from ponto_do_cafe.reporting.markdown_table import MarkdownTable

TOP_POSITIONS = 10
LARGEST_MOVES = 5
NUMBER_FORMAT = BrazilianNumberFormat()
HEADERS = [
    "Distrito",
    "Posição (RAIS)",
    "Posição (OD)",
    "Posições ganhas",
    "Índice (RAIS)",
    "Índice (OD)",
    "Mercado por ponto de venda (RAIS)",
    "Mercado por ponto de venda (OD)",
]
SELECTED_COLUMNS = """
    nome_distrito,
    posicao_ranking_rais,
    posicao_ranking_od,
    posicoes_ganhas_com_od,
    indice_oportunidade_rais,
    indice_oportunidade_od,
    mercado_mensal_por_ponto_de_venda_rais,
    mercado_mensal_por_ponto_de_venda_od
"""


class RankingComparisonSection:
    def __init__(self, database: AnalyticalDatabase, directories: DataDirectories, pilot_district_codes: tuple[str, ...], note: str) -> None:
        self._database = database
        self._comparison = directories.marts_file("distritos_comparacao_ranking.parquet")
        self._pilot_district_codes = pilot_district_codes
        self._note = note

    def render(self) -> str:
        return "\n\n".join(
            [
                "## 7. Comparação: ranking oficial (Pesquisa OD) × versão RAIS",
                self._note,
                self._summary(),
                "### 10 primeiros em qualquer das versões + distritos do piloto",
                self._table(self._leaders_query()),
                f"### {LARGEST_MOVES} maiores subidas e {LARGEST_MOVES} maiores quedas com a Pesquisa OD",
                self._table(self._largest_moves_query()),
            ]
        )

    def _summary(self) -> str:
        summary = self._database.frame(f"""
            SELECT
                corr(posicao_ranking_rais, posicao_ranking_od) AS correlacao_posicoes,
                avg(abs(posicoes_ganhas_com_od)) AS mudanca_media,
                count(*) FILTER (WHERE posicao_ranking_rais <= {TOP_POSITIONS} AND posicao_ranking_od <= {TOP_POSITIONS}) AS mantidos_no_topo
            FROM '{self._comparison}'
        """)
        correlation, average_move, kept_on_top = summary.row(0)
        correlation_text = f"{correlation:.2f}".replace(".", ",")
        return (
            f"Correlação entre as posições nas duas versões: **{correlation_text}**. "
            f"Em média, um distrito muda **{NUMBER_FORMAT.decimal(average_move)} posições**, "
            f"e {kept_on_top} dos {TOP_POSITIONS} primeiros continuam no topo."
        )

    def _leaders_query(self) -> str:
        codes = ", ".join(f"'{code}'" for code in self._pilot_district_codes)
        return f"""
            SELECT {SELECTED_COLUMNS}
            FROM '{self._comparison}'
            WHERE posicao_ranking_od <= {TOP_POSITIONS} OR posicao_ranking_rais <= {TOP_POSITIONS} OR codigo_distrito IN ({codes})
            ORDER BY posicao_ranking_od
        """

    def _largest_moves_query(self) -> str:
        return f"""
            (SELECT {SELECTED_COLUMNS} FROM '{self._comparison}' ORDER BY posicoes_ganhas_com_od DESC LIMIT {LARGEST_MOVES})
            UNION ALL
            (SELECT {SELECTED_COLUMNS} FROM '{self._comparison}' ORDER BY posicoes_ganhas_com_od LIMIT {LARGEST_MOVES})
        """

    def _table(self, query: str) -> str:
        frame = self._database.frame(query)
        rows = [self._row(row) for row in frame.iter_rows()]
        table = MarkdownTable(HEADERS, rows)
        return table.render()

    def _row(self, row: tuple[str, int, int, int, float, float, float, float]) -> list[str]:
        return [
            row[0],
            str(row[1]),
            str(row[2]),
            f"{row[3]:+d}",
            NUMBER_FORMAT.decimal(row[4]),
            NUMBER_FORMAT.decimal(row[5]),
            NUMBER_FORMAT.rounded_currency(row[6]),
            NUMBER_FORMAT.rounded_currency(row[7]),
        ]
