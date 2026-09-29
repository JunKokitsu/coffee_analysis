import plotly.graph_objects as graph_objects
import polars

from coffee_analysis.dashboard.chart_palette import ChartPalette

SAO_PAULO_CENTER = {"lat": -23.65, "lon": -46.60}
MOVERS_PER_SIDE = 8
POSITION_TICKS = [1, 20, 40, 60, 80, 96]


class DashboardCharts:
    def __init__(self, palette: ChartPalette) -> None:
        self._palette = palette

    def _figure(self, traces: list[graph_objects.BaseTraceType], height: int) -> graph_objects.Figure:
        figure = graph_objects.Figure(traces)
        figure.update_layout(**self._palette.layout(), height=height)
        return figure

    def opportunity_map(self, ranking: polars.DataFrame, shapes: dict[str, object]) -> graph_objects.Figure:
        trace = graph_objects.Choroplethmap(
            geojson=shapes,
            featureidkey="properties.codigo_distrito",
            locations=ranking["codigo_distrito"].to_list(),
            z=ranking["indice_oportunidade"].to_list(),
            customdata=ranking.select("nome_distrito", "posicao_ranking").rows(),
            colorscale=self._palette.sequential_scale(),
            marker={"line": {"width": 0.6, "color": self._palette.surface}, "opacity": 0.9},
            colorbar={"title": {"text": "Índice", "font": {"color": self._palette.secondary_ink}}, "tickfont": {"color": self._palette.muted_ink}, "thickness": 12, "outlinewidth": 0},
            hovertemplate="<b>%{customdata[0]}</b><br>Índice %{z:.1f}<br>%{customdata[1]}º lugar<extra></extra>",
        )
        figure = self._figure([trace], 560)
        figure.update_layout(map={"style": self._palette.map_style, "center": SAO_PAULO_CENTER, "zoom": 8.9})
        return figure

    def ranking_bars(self, ranking: polars.DataFrame, count: int) -> graph_objects.Figure:
        leaders = ranking.head(count).reverse()
        labels = [f"{position}º {name}" for position, name in zip(leaders["posicao_ranking"], leaders["nome_distrito"])]
        trace = graph_objects.Bar(
            x=leaders["indice_oportunidade"].to_list(),
            y=labels,
            orientation="h",
            marker={"color": self._palette.highlight, "cornerradius": 4},
            width=0.6,
            text=[f"{value:.1f}".replace(".", ",") for value in leaders["indice_oportunidade"]],
            textposition="outside",
            textfont={"color": self._palette.secondary_ink},
            hovertemplate="<b>%{y}</b><br>Índice %{x:.1f}<extra></extra>",
        )
        figure = self._figure([trace], 28 * count + 40)
        figure.update_xaxes(range=[0, 100], title={"text": "Índice de oportunidade (0 a 100)"})
        figure.update_yaxes(gridcolor="rgba(0,0,0,0)")
        return figure

    def position_changes(self, comparison: polars.DataFrame) -> graph_objects.Figure:
        ordered = comparison.sort("posicoes_ganhas_com_od")
        movers = polars.concat([ordered.head(MOVERS_PER_SIDE), ordered.tail(MOVERS_PER_SIDE)]).unique(maintain_order=True)
        gains = movers["posicoes_ganhas_com_od"].to_list()
        colors = [self._color_for_change(gain) for gain in gains]
        trace = graph_objects.Bar(
            x=gains,
            y=movers["nome_distrito"].to_list(),
            orientation="h",
            marker={"color": colors, "cornerradius": 4},
            width=0.6,
            text=[f"{gain:+d}" for gain in gains],
            textposition="outside",
            textfont={"color": self._palette.secondary_ink},
            customdata=movers.select("posicao_ranking_rais", "posicao_ranking_od").rows(),
            hovertemplate="<b>%{y}</b><br>RAIS: %{customdata[0]}º → OD: %{customdata[1]}º<br>%{x:+d} posições<extra></extra>",
        )
        figure = self._figure([trace], 28 * len(gains) + 40)
        figure.update_xaxes(title={"text": "Posições ganhas ao trocar RAIS pela Pesquisa OD"}, zeroline=True, zerolinewidth=1)
        figure.update_yaxes(gridcolor="rgba(0,0,0,0)")
        return figure

    def _color_for_change(self, gain: int) -> str:
        if gain < 0:
            return self._palette.negative
        return self._palette.highlight

    def position_scatter(self, comparison: polars.DataFrame, highlighted_codes: tuple[str, ...]) -> graph_objects.Figure:
        is_highlighted = polars.col("codigo_distrito").is_in(list(highlighted_codes))
        others = comparison.filter(~is_highlighted)
        highlighted = comparison.filter(is_highlighted)
        diagonal = graph_objects.Scatter(x=[1, 96], y=[1, 96], mode="lines", line={"color": self._palette.baseline, "width": 1, "dash": "dot"}, hoverinfo="skip")
        traces = [diagonal, self._scatter_trace(others, self._palette.recessive_mark, "markers"), self._scatter_trace(highlighted, self._palette.highlight, "markers+text")]
        figure = self._figure(traces, 460)
        figure.update_xaxes(title={"text": "Posição na versão RAIS"}, range=[98, -1], tickvals=POSITION_TICKS)
        figure.update_yaxes(title={"text": "Posição na versão oficial (Pesquisa OD)"}, range=[98, -1], tickvals=POSITION_TICKS)
        return figure

    def _scatter_trace(self, frame: polars.DataFrame, color: str, mode: str) -> graph_objects.Scatter:
        return graph_objects.Scatter(
            x=frame["posicao_ranking_rais"].to_list(),
            y=frame["posicao_ranking_od"].to_list(),
            mode=mode,
            text=frame["nome_distrito"].to_list(),
            textposition="top center",
            textfont={"color": self._palette.primary_ink},
            marker={"color": color, "size": 10, "line": {"width": 2, "color": self._palette.surface}},
            hovertemplate="<b>%{text}</b><br>RAIS: %{x}º<br>OD: %{y}º<extra></extra>",
        )
