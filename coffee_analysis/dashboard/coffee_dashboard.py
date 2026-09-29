from datetime import datetime

import polars
import streamlit

from coffee_analysis.brazilian_number_format import BrazilianNumberFormat
from coffee_analysis.dashboard.dashboard_charts import DashboardCharts
from coffee_analysis.dashboard.dashboard_data import DashboardData
from coffee_analysis.dashboard.index_version import IndexVersion

NUMBER_FORMAT = BrazilianNumberFormat()
RANKING_SIZES = (10, 15, 20, 30)
TABLE_ROW_HEIGHT = 35
PROFILE_METRICS = (
    ("Mercado potencial café + lanches (R$/mês)", "mercado_potencial_mensal", NUMBER_FORMAT.rounded_currency),
    ("Mercado por ponto de venda (R$/mês)", "mercado_mensal_por_ponto_de_venda", NUMBER_FORMAT.rounded_currency),
    ("População residente (2022)", "populacao_2022", NUMBER_FORMAT.integer),
    ("Viagens atraídas por dia útil", "viagens_atraidas_nao_residenciais", NUMBER_FORMAT.integer),
    ("Cafeterias ativas", "cafeterias_ativas", NUMBER_FORMAT.integer),
    ("Pontos de venda de café", "pontos_de_venda_cafe", NUMBER_FORMAT.integer),
    ("Cafeterias abertas em 24 meses", "cafeterias_abertas_24_meses", NUMBER_FORMAT.integer),
    ("Cafeterias fechadas em 24 meses", "cafeterias_fechadas_24_meses", NUMBER_FORMAT.integer),
    ("Sobrevivência em 3 anos", "sobrevivencia_3_anos", NUMBER_FORMAT.percentage),
    ("Preço mediano do m² comercial (R$)", "preco_mediano_m2_comercial", NUMBER_FORMAT.rounded_currency),
    ("Demanda das estações por dia útil", "demanda_estacoes_dias_uteis", NUMBER_FORMAT.integer),
    ("Índice de oportunidade", "indice_oportunidade", NUMBER_FORMAT.decimal),
)
AREA_METRICS = (
    ("População residente", "populacao_residente", NUMBER_FORMAT.integer),
    ("Empregos formais", "vinculos_formais", NUMBER_FORMAT.integer),
    ("Viagens atraídas por dia útil", "viagens_atraidas_nao_residenciais", NUMBER_FORMAT.integer),
    ("Viagens entrevistadas na amostra", "viagens_atraidas_amostra", NUMBER_FORMAT.integer),
    ("Mercado potencial, versão RAIS (R$/mês)", "mercado_potencial_mensal", NUMBER_FORMAT.rounded_currency),
    ("Mercado potencial, versão Pesquisa OD (R$/mês)", "mercado_potencial_mensal_od", NUMBER_FORMAT.rounded_currency),
    ("Cafeterias ativas", "cafeterias_ativas", NUMBER_FORMAT.integer),
    ("Lanchonetes ativas", "lanchonetes_ativas", NUMBER_FORMAT.integer),
    ("Padarias ativas", "padarias_ativas", NUMBER_FORMAT.integer),
    ("Cafeterias abertas em 24 meses", "cafeterias_abertas_24_meses", NUMBER_FORMAT.integer),
    ("Estações de metrô e trem", "estacoes_metro_trem", NUMBER_FORMAT.integer),
)


class CoffeeDashboard:
    def __init__(self, data: DashboardData, charts: DashboardCharts, pilot_district_codes: tuple[str, ...]) -> None:
        self._data = data
        self._charts = charts
        self._pilot_district_codes = pilot_district_codes

    def render(self) -> None:
        streamlit.title("Oportunidades para novas cafeterias em São Paulo")
        updated_at = datetime.fromtimestamp(self._data.updated_at())
        streamlit.caption(f"Dados atualizados em {updated_at.strftime('%d/%m/%Y %H:%M')}. Valores de mercado são potenciais, não previsão de faturamento.")
        overview, district, addresses, method = streamlit.tabs(["Visão geral", "Distrito", "Endereços", "Método e qualidade"])
        with overview:
            self._overview()
        with district:
            self._district()
        with addresses:
            self._addresses()
        with method:
            self._method()

    def _overview(self) -> None:
        versions = {version.label: version for version in (IndexVersion.official(), IndexVersion.employment())}
        filters = streamlit.columns([2, 1, 3])
        chosen_label = filters[0].segmented_control("Versão do índice", list(versions), default=IndexVersion.official().label)
        ranking_size = filters[1].selectbox("Distritos no ranking", RANKING_SIZES, index=1)
        ranking = self._data.ranking(versions[chosen_label or IndexVersion.official().label])
        self._headline_tiles(ranking)
        map_column, ranking_column = streamlit.columns([3, 2])
        map_column.subheader("Índice de oportunidade por distrito")
        map_column.plotly_chart(self._charts.opportunity_map(ranking, self._data.district_shapes()), width="stretch")
        ranking_column.subheader(f"{ranking_size} primeiros")
        ranking_column.plotly_chart(self._charts.ranking_bars(ranking, ranking_size), width="stretch")
        with streamlit.expander("Tabela completa do ranking"):
            streamlit.dataframe(self._ranking_table(ranking), hide_index=True, width="stretch")

    def _headline_tiles(self, ranking: polars.DataFrame) -> None:
        leader = ranking.row(0, named=True)
        tiles = streamlit.columns(4)
        tiles[0].metric("1º do ranking", str(leader["nome_distrito"]))
        tiles[0].caption(f"Índice de oportunidade {NUMBER_FORMAT.decimal(leader['indice_oportunidade'])}")
        tiles[1].metric("Mercado potencial da cidade (por mês)", NUMBER_FORMAT.compact_currency(ranking["mercado_potencial_mensal"].sum()))
        tiles[2].metric("Cafeterias ativas", NUMBER_FORMAT.integer(ranking["cafeterias_ativas"].sum()))
        tiles[3].metric("Pontos de venda de café", NUMBER_FORMAT.integer(ranking["pontos_de_venda_cafe"].sum()))

    def _ranking_table(self, ranking: polars.DataFrame) -> polars.DataFrame:
        return ranking.select(
            polars.col("posicao_ranking").alias("Posição"),
            polars.col("nome_distrito").alias("Distrito"),
            polars.col("indice_oportunidade").round(1).alias("Índice"),
            polars.col("mercado_mensal_por_ponto_de_venda").round(0).alias("Mercado por ponto de venda (R$/mês)"),
            polars.col("cafeterias_ativas").alias("Cafeterias ativas"),
            (polars.col("sobrevivencia_3_anos") * 100).round(1).alias("Sobrevivência 3 anos (%)"),
            polars.col("preco_mediano_m2_comercial").round(0).alias("m² comercial (R$)"),
        )

    def _district(self) -> None:
        profile = self._data.district_profile()
        names = profile["nome_distrito"].to_list()
        pilot_names = profile.filter(polars.col("codigo_distrito").is_in(list(self._pilot_district_codes)))["nome_distrito"].to_list()
        chosen = streamlit.selectbox("Distrito", names, index=names.index(pilot_names[0]))
        district = profile.filter(polars.col("nome_distrito") == chosen).row(0, named=True)
        tiles = streamlit.columns(4)
        tiles[0].metric("Posição no ranking", f"{district['posicao_ranking']}º de {profile.height}")
        tiles[1].metric("Mercado potencial (por mês)", NUMBER_FORMAT.compact_currency(district["mercado_potencial_mensal"]))
        tiles[2].metric("Cafeterias ativas", NUMBER_FORMAT.integer(district["cafeterias_ativas"]))
        tiles[3].metric("Sobrevivência em 3 anos", NUMBER_FORMAT.percentage(district["sobrevivencia_3_anos"]))
        rows = [{"Métrica": label, chosen: formatter(district[column]), "Mediana dos distritos": formatter(profile[column].median())} for label, column, formatter in PROFILE_METRICS]
        streamlit.dataframe(polars.DataFrame(rows), hide_index=True, width="stretch", height=self._table_height(len(rows)))

    def _table_height(self, rows: int) -> int:
        return (rows + 1) * TABLE_ROW_HEIGHT + 3

    def _addresses(self) -> None:
        areas = self._data.influence_areas()
        streamlit.caption("Nas áreas de influência a referência é a versão RAIS: nos raios de 300 m e 500 m a Pesquisa OD tem poucas viagens entrevistadas.")
        for candidate in areas["endereco_candidato"].unique(maintain_order=True).to_list():
            streamlit.subheader(candidate)
            candidate_rows = areas.filter(polars.col("endereco_candidato") == candidate)
            streamlit.dataframe(self._area_table(candidate_rows), hide_index=True, width="stretch", height=self._table_height(len(AREA_METRICS)))

    def _area_table(self, candidate_rows: polars.DataFrame) -> polars.DataFrame:
        radii = candidate_rows["raio_metros"].to_list()
        rows = [
            {"Métrica": label, **{f"Raio de {radius} m": formatter(value) for radius, value in zip(radii, candidate_rows[column].to_list())}}
            for label, column, formatter in AREA_METRICS
        ]
        return polars.DataFrame(rows)

    def _method(self) -> None:
        comparison = self._data.comparison()
        streamlit.subheader("Versão oficial (Pesquisa OD) × versão RAIS")
        streamlit.caption("A versão oficial distribui o consumo fora de casa pelas viagens atraídas da Pesquisa OD 2023. A versão RAIS usa os empregos formais, que concentram vínculos nas sedes das empresas.")
        scatter_column, changes_column = streamlit.columns(2)
        scatter_column.plotly_chart(self._charts.position_scatter(comparison, self._pilot_district_codes), width="stretch")
        changes_column.plotly_chart(self._charts.position_changes(comparison), width="stretch")
        streamlit.subheader("Qualidade de dados da última execução")
        self._quality()

    def _quality(self) -> None:
        results = self._data.quality_results()
        if results.is_empty():
            streamlit.info("Ainda não há resultado de qualidade para esta competência.")
            return
        streamlit.markdown(self._quality_summary(results))
        labeled = results.with_columns(polars.col("aprovado").replace_strict({True: "✅ aprovado", False: "❌ reprovado"}, return_dtype=polars.String).alias("situacao"))
        streamlit.dataframe(labeled.select("tabela", "verificacao", "situacao", "detalhe"), hide_index=True, width="stretch")

    def _quality_summary(self, results: polars.DataFrame) -> str:
        failures = results.filter(~polars.col("aprovado")).height
        if failures == 0:
            return f"✅ **Aprovado:** {results.height} verificações sem falha."
        return f"❌ **Reprovado:** {failures} de {results.height} verificações falharam."
