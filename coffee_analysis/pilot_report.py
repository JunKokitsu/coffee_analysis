from datetime import date
from pathlib import Path

import polars

from coffee_analysis.analytical_database import AnalyticalDatabase
from coffee_analysis.brazilian_number_format import BrazilianNumberFormat
from coffee_analysis.data_directories import DataDirectories
from coffee_analysis.markdown_table import MarkdownTable
from coffee_analysis.metric_definition import MetricDefinition
from coffee_analysis.metric_definitions import MetricDefinitions
from coffee_analysis.ranking_comparison_section import RankingComparisonSection
from coffee_analysis.report_findings import ReportFindings
from coffee_analysis.report_texts import ReportTexts

NUMBER_FORMAT = BrazilianNumberFormat()
DEMAND_METRICS = MetricDefinitions(
    (
        MetricDefinition("População residente (2022)", "populacao_2022", NUMBER_FORMAT.integer, "Censo 2022"),
        MetricDefinition("Densidade (hab/km²)", "densidade_demografica", NUMBER_FORMAT.integer, "Censo 2022"),
        MetricDefinition("Empregos formais no distrito", "vinculos_formais", NUMBER_FORMAT.integer, "RAIS 2025"),
        MetricDefinition("Renda média domiciliar (salários mínimos)", "renda_media_domiciliar_salarios_minimos", NUMBER_FORMAT.decimal, "Censo 2010"),
        MetricDefinition("Gasto com café fora de casa por domicílio (R$/mês)", "gasto_cafe_fora_por_domicilio_atual", NUMBER_FORMAT.currency, "POF 2017-18 + IPCA"),
        MetricDefinition("Gasto com café + lanches fora de casa por domicílio (R$/mês)", "gasto_cesta_cafeteria_por_domicilio_atual", NUMBER_FORMAT.currency, "POF 2017-18 + IPCA"),
        MetricDefinition("Mercado potencial de café fora de casa (R$/mês)", "mercado_cafe_mensal", NUMBER_FORMAT.rounded_currency, "Derivada"),
        MetricDefinition("Mercado potencial café + lanches (R$/mês)", "mercado_potencial_mensal", NUMBER_FORMAT.rounded_currency, "Derivada"),
        MetricDefinition("Mercado potencial café + lanches, versão RAIS (R$/mês)", "mercado_potencial_mensal_rais", NUMBER_FORMAT.rounded_currency, "Derivada"),
    )
)
MOBILITY_METRICS = MetricDefinitions(
    (
        MetricDefinition("Viagens diárias atraídas (trabalho, estudo, compras, serviços e lazer)", "viagens_atraidas_nao_residenciais", NUMBER_FORMAT.integer, "Pesquisa OD 2023"),
        MetricDefinition("Viagens diárias atraídas por trabalho", "viagens_atraidas_trabalho", NUMBER_FORMAT.integer, "Pesquisa OD 2023"),
        MetricDefinition("Viagens diárias atraídas por compras e serviços", "viagens_atraidas_compras_e_servicos", NUMBER_FORMAT.integer, "Pesquisa OD 2023"),
        MetricDefinition("Viagens diárias atraídas por lazer e refeição", "viagens_atraidas_lazer_e_refeicao", NUMBER_FORMAT.integer, "Pesquisa OD 2023"),
        MetricDefinition("Viagens atraídas por morador", "viagens_atraidas_por_morador", NUMBER_FORMAT.decimal, "Derivada"),
        MetricDefinition("Viagens entrevistadas na amostra", "viagens_atraidas_amostra", NUMBER_FORMAT.integer, "Pesquisa OD 2023"),
        MetricDefinition("Pessoas que trabalham no distrito (formais e informais)", "trabalhadores_no_distrito", NUMBER_FORMAT.integer, "Pesquisa OD 2023"),
        MetricDefinition("Estações de metrô e trem (contadas por linha)", "estacoes_metro_trem", NUMBER_FORMAT.integer, "GeoSampa"),
        MetricDefinition("Estações sem dado de demanda (CPTM)", "estacoes_sem_demanda", NUMBER_FORMAT.integer, "GeoSampa"),
        MetricDefinition("Demanda média das estações em dias úteis", "demanda_estacoes_dias_uteis", NUMBER_FORMAT.integer, "Metrô e Motiva, 12 meses"),
    )
)
COMPETITION_METRICS = MetricDefinitions(
    (
        MetricDefinition("Cafeterias ativas", "cafeterias_ativas", NUMBER_FORMAT.integer, "CNPJ"),
        MetricDefinition("Lanchonetes ativas (concorrência indireta)", "lanchonetes_ativas", NUMBER_FORMAT.integer, "CNPJ"),
        MetricDefinition("Padarias ativas (concorrência indireta)", "padarias_ativas", NUMBER_FORMAT.integer, "CNPJ"),
        MetricDefinition("Cafeterias por 10 mil pessoas (residentes + empregos)", "cafeterias_por_10_mil_pessoas", NUMBER_FORMAT.decimal, "Derivada"),
        MetricDefinition("Mercado café + lanches por cafeteria (R$/mês)", "mercado_mensal_por_cafeteria", NUMBER_FORMAT.rounded_currency, "Derivada"),
        MetricDefinition("Mercado café + lanches por ponto de venda (R$/mês)", "mercado_mensal_por_ponto_de_venda", NUMBER_FORMAT.rounded_currency, "Derivada"),
        MetricDefinition("Mercado café + lanches por ponto de venda, versão RAIS (R$/mês)", "mercado_mensal_por_ponto_de_venda_rais", NUMBER_FORMAT.rounded_currency, "Derivada"),
        MetricDefinition("Cafeterias abertas nos últimos 12 meses", "cafeterias_abertas_12_meses", NUMBER_FORMAT.integer, "CNPJ"),
        MetricDefinition("Cafeterias abertas nos últimos 24 meses", "cafeterias_abertas_24_meses", NUMBER_FORMAT.integer, "CNPJ"),
        MetricDefinition("Cafeterias fechadas nos últimos 24 meses", "cafeterias_fechadas_24_meses", NUMBER_FORMAT.integer, "CNPJ"),
        MetricDefinition("Saldo de cafeterias em 24 meses", "saldo_cafeterias_24_meses", NUMBER_FORMAT.integer, "CNPJ"),
        MetricDefinition("Novas cafeterias em 24 meses / cafeterias ativas", "crescimento_oferta_24_meses", NUMBER_FORMAT.percentage, "CNPJ"),
    )
)
RISK_AND_COST_METRICS = MetricDefinitions(
    (
        MetricDefinition("Sobrevivência em 3 anos (cafeterias + lanchonetes)", "sobrevivencia_3_anos", NUMBER_FORMAT.percentage, "CNPJ"),
        MetricDefinition("Amostra usada na sobrevivência em 3 anos", "amostra_sobrevivencia_3_anos", NUMBER_FORMAT.integer, "CNPJ"),
        MetricDefinition("Empregados por lanchonete/cafeteria (mediana)", "mediana_vinculos_por_lanchonete", NUMBER_FORMAT.decimal, "RAIS 2025"),
        MetricDefinition("Preço mediano do m² comercial (R$)", "preco_mediano_m2_comercial", NUMBER_FORMAT.rounded_currency, "ITBI 2026"),
        MetricDefinition("Transações comerciais usadas no m²", "transacoes_comerciais", NUMBER_FORMAT.integer, "ITBI 2026"),
    )
)
INDEX_METRICS = MetricDefinitions(
    (
        MetricDefinition("Percentil do mercado por ponto de venda", "percentil_mercado", NUMBER_FORMAT.percentage, "Derivada"),
        MetricDefinition("Percentil da sobrevivência em 3 anos", "percentil_sobrevivencia", NUMBER_FORMAT.percentage, "Derivada"),
        MetricDefinition("Percentil da pressão de entrada", "percentil_pressao_entrada", NUMBER_FORMAT.percentage, "Derivada"),
        MetricDefinition("Percentil do custo do m²", "percentil_custo_ocupacao", NUMBER_FORMAT.percentage, "Derivada"),
        MetricDefinition("**Índice de oportunidade (0 a 100)**", "indice_oportunidade", NUMBER_FORMAT.decimal, "Derivada"),
        MetricDefinition("**Posição no ranking (de 96 distritos)**", "posicao_ranking", NUMBER_FORMAT.integer, "Derivada"),
        MetricDefinition("Índice de oportunidade, versão RAIS (0 a 100)", "indice_oportunidade_rais", NUMBER_FORMAT.decimal, "Derivada"),
        MetricDefinition("Posição no ranking, versão RAIS", "posicao_ranking_rais", NUMBER_FORMAT.integer, "Derivada"),
    )
)
INFLUENCE_AREA_METRICS = MetricDefinitions(
    (
        MetricDefinition("População residente", "populacao_residente", NUMBER_FORMAT.integer, "Censo 2022"),
        MetricDefinition("Empregos formais", "vinculos_formais", NUMBER_FORMAT.integer, "RAIS 2025"),
        MetricDefinition("Mercado potencial café + lanches, versão RAIS (R$/mês, referência nos raios)", "mercado_potencial_mensal", NUMBER_FORMAT.rounded_currency, "Derivada"),
        MetricDefinition("Mercado potencial café + lanches, versão Pesquisa OD (R$/mês)", "mercado_potencial_mensal_od", NUMBER_FORMAT.rounded_currency, "Derivada"),
        MetricDefinition("Viagens diárias atraídas (exceto volta para casa)", "viagens_atraidas_nao_residenciais", NUMBER_FORMAT.integer, "Pesquisa OD 2023"),
        MetricDefinition("Viagens diárias atraídas por trabalho", "viagens_atraidas_trabalho", NUMBER_FORMAT.integer, "Pesquisa OD 2023"),
        MetricDefinition("Viagens entrevistadas na amostra", "viagens_atraidas_amostra", NUMBER_FORMAT.integer, "Pesquisa OD 2023"),
        MetricDefinition("Estações de metrô e trem (por linha)", "estacoes_metro_trem", NUMBER_FORMAT.integer, "GeoSampa"),
        MetricDefinition("Demanda média das estações em dias úteis", "demanda_estacoes_dias_uteis", NUMBER_FORMAT.integer, "Metrô e Motiva, 12 meses"),
        MetricDefinition("Cafeterias ativas", "cafeterias_ativas", NUMBER_FORMAT.integer, "CNPJ"),
        MetricDefinition("Lanchonetes ativas", "lanchonetes_ativas", NUMBER_FORMAT.integer, "CNPJ"),
        MetricDefinition("Padarias ativas", "padarias_ativas", NUMBER_FORMAT.integer, "CNPJ"),
        MetricDefinition("Cafeterias abertas em 24 meses", "cafeterias_abertas_24_meses", NUMBER_FORMAT.integer, "CNPJ"),
        MetricDefinition("Mercado por cafeteria (R$/mês)", "mercado_mensal_por_cafeteria", NUMBER_FORMAT.rounded_currency, "Derivada"),
        MetricDefinition("Mercado por ponto de venda, versão RAIS (R$/mês, referência nos raios)", "mercado_mensal_por_ponto_de_venda", NUMBER_FORMAT.rounded_currency, "Derivada"),
        MetricDefinition("Mercado por ponto de venda, versão Pesquisa OD (R$/mês)", "mercado_mensal_por_ponto_de_venda_od", NUMBER_FORMAT.rounded_currency, "Derivada"),
    )
)


class PilotReport:
    def __init__(
        self,
        database: AnalyticalDatabase,
        directories: DataDirectories,
        pilot_district_codes: tuple[str, ...],
        reference_date: date,
    ) -> None:
        self._database = database
        self._directories = directories
        self._pilot_district_codes = pilot_district_codes
        self._reference_date = reference_date
        self._texts = ReportTexts()

    def build(self) -> Path:
        sections = [
            self._texts.header(self._reference_date),
            ReportFindings(self._database, self._directories, self._pilot_district_codes, self._reference_date).render(),
            self._district_section(),
            self._survival_section(),
            self._wage_section(),
            self._price_section(),
            self._influence_area_section(),
            self._ranking_section(),
            RankingComparisonSection(self._database, self._directories, self._pilot_district_codes, self._texts.ranking_comparison_note()).render(),
            self._texts.methodology(),
            self._texts.limitations(),
            self._texts.next_steps(),
        ]
        destination = self._directories.report_file("piloto_novas_cafeterias.md")
        destination.write_text("\n\n".join(sections) + "\n", encoding="utf-8")
        return destination

    def _district_names(self) -> list[str]:
        codes = ", ".join(f"'{code}'" for code in self._pilot_district_codes)
        metrics = self._directories.marts_file("distritos_metricas.parquet")
        names = self._database.frame(f"SELECT nome_distrito FROM '{metrics}' WHERE codigo_distrito IN ({codes}) ORDER BY codigo_distrito")
        return names["nome_distrito"].to_list()

    def _comparison_values(self) -> dict[str, tuple[float | None, ...]]:
        comparison = self._database.frame(self._comparison_query())
        return {row[0]: tuple(row[1:]) for row in comparison.iter_rows()}

    def _comparison_query(self) -> str:
        metrics = self._directories.marts_file("distritos_metricas.parquet")
        index = self._directories.marts_file("distritos_indice_oportunidade.parquet")
        mobility = self._directories.marts_file("distritos_mobilidade.parquet")
        ranking_comparison = self._directories.marts_file("distritos_comparacao_ranking.parquet")
        district_columns = ", ".join(
            f"max(valor) FILTER (WHERE codigo_distrito = '{code}') AS distrito_{position}"
            for position, code in enumerate(sorted(self._pilot_district_codes))
        )
        return f"""
            WITH completo AS (
                SELECT
                    metricas.*,
                    indice.* EXCLUDE (codigo_distrito, nome_distrito),
                    mobilidade.* EXCLUDE (codigo_distrito, viagens_atraidas_nao_residenciais),
                    comparacao.* EXCLUDE (codigo_distrito, nome_distrito)
                FROM '{metrics}' AS metricas
                JOIN '{index}' AS indice USING (codigo_distrito)
                JOIN '{mobility}' AS mobilidade USING (codigo_distrito)
                JOIN '{ranking_comparison}' AS comparacao USING (codigo_distrito)
            ),
            longo AS (
                UNPIVOT (SELECT codigo_distrito, COLUMNS(* EXCLUDE (codigo_distrito, nome_distrito))::DOUBLE FROM completo)
                ON COLUMNS(* EXCLUDE (codigo_distrito))
                INTO NAME metrica VALUE valor
            )
            SELECT metrica, {district_columns}, median(valor) AS mediana_cidade
            FROM longo
            GROUP BY metrica
        """

    def _district_section(self) -> str:
        values = self._comparison_values()
        headers = ["Métrica", *self._district_names(), "Mediana dos 96 distritos", "Fonte"]
        groups = [
            ("Demanda", DEMAND_METRICS),
            ("Fluxo de pessoas", MOBILITY_METRICS),
            ("Concorrência", COMPETITION_METRICS),
            ("Risco e custos", RISK_AND_COST_METRICS),
            ("Índice de oportunidade", INDEX_METRICS),
        ]
        tables = [self._metric_group(title, definitions, headers, values) for title, definitions in groups]
        return "## 1. Ficha comparativa dos distritos\n\n" + self._texts.district_note() + "\n\n" + "\n\n".join(tables)

    def _metric_group(
        self,
        title: str,
        definitions: MetricDefinitions,
        headers: list[str],
        values: dict[str, tuple[float | None, ...]],
    ) -> str:
        table = definitions.table(headers, values)
        return f"### {title}\n\n" + table.render()

    def _survival_section(self) -> str:
        survival = self._directories.marts_file("sobrevivencia_distritos.parquet")
        codes = ", ".join(f"'{code}'" for code in self._pilot_district_codes)
        frame = self._database.frame(f"""
            SELECT
                coalesce(distritos.nome_distrito, 'Cidade de São Paulo') AS recorte,
                sobrevivencia.categoria,
                sobrevivencia.anos,
                sobrevivencia.negocios_expostos,
                sobrevivencia.taxa_sobrevivencia
            FROM '{survival}' AS sobrevivencia
            LEFT JOIN (SELECT DISTINCT codigo_distrito, nome_distrito FROM '{self._directories.marts_file("distritos_metricas.parquet")}') AS distritos
                USING (codigo_distrito)
            WHERE (sobrevivencia.codigo_distrito IN ({codes}) OR sobrevivencia.codigo_distrito = 'cidade')
                AND sobrevivencia.categoria IN ('cafeteria', 'cafeteria_e_lanchonete')
            ORDER BY recorte, categoria, anos
        """)
        rows = [self._survival_row(row) for row in frame.iter_rows()]
        table = MarkdownTable(["Recorte", "Categoria", "Anos após abertura", "Negócios na amostra", "Ainda ativos"], rows)
        return "## 2. Sobrevivência dos negócios\n\n" + self._texts.survival_note() + "\n\n" + table.render()

    def _survival_row(self, row: tuple[str, str, int, int, float]) -> list[str]:
        category_labels = {"cafeteria": "Cafeterias", "lanchonete": "Lanchonetes", "cafeteria_e_lanchonete": "Cafeterias + lanchonetes"}
        return [row[0], category_labels.get(row[1], row[1]), str(row[2]), NUMBER_FORMAT.integer(row[3]), NUMBER_FORMAT.percentage(row[4])]

    def _wage_section(self) -> str:
        wages = self._database.frame(f"SELECT * FROM '{self._directories.marts_file('salarios_lanchonetes.parquet')}' ORDER BY vinculos DESC")
        rows = [self._wage_row(row) for row in wages.iter_rows(named=True)]
        table = MarkdownTable(["Ocupação", "Vínculos em tempo integral", "Percentil 25", "Mediana", "Percentil 75", "Mediana dos admitidos em 2025"], rows)
        return "## 3. Salários de referência (lanchonetes e cafeterias da capital, RAIS 2025, jornada de 40 horas ou mais)\n\n" + table.render()

    def _wage_row(self, row: dict[str, float | str]) -> list[str]:
        return [
            str(row["ocupacao"]),
            NUMBER_FORMAT.integer(float(row["vinculos"])),
            NUMBER_FORMAT.currency(float(row["remuneracao_percentil_25"])),
            NUMBER_FORMAT.currency(float(row["remuneracao_mediana"])),
            NUMBER_FORMAT.currency(float(row["remuneracao_percentil_75"])),
            NUMBER_FORMAT.currency(float(row["remuneracao_mediana_admitidos_no_ano"])),
        ]

    def _price_section(self) -> str:
        prices = self._database.frame(self._price_query())
        rows = [[str(row[0]), NUMBER_FORMAT.signed_percentage(row[1]), NUMBER_FORMAT.signed_percentage(row[2])] for row in prices.iter_rows()]
        table = MarkdownTable(["Indicador", "Variação em 12 meses", "Variação desde jan/2018"], rows)
        arabica = self._database.frame(self._arabica_query())
        arabica_rows = [[str(row[0]), NUMBER_FORMAT.currency(row[1])] for row in arabica.iter_rows()]
        arabica_table = MarkdownTable(["Data", "Arábica CEPEA/ESALQ (R$/saca de 60 kg)"], arabica_rows)
        return "## 4. Preços e margem\n\n" + table.render() + "\n\n" + arabica_table.render() + "\n\n" + self._texts.price_note()

    def _price_query(self) -> str:
        prices = self._directories.staging_file("ipca", "variacao_mensal_rmsp.parquet")
        arabica = self._directories.staging_file("cepea", "arabica.parquet")
        return f"""
            WITH ultimo AS (SELECT max(mes) AS mes FROM '{prices}'),
            limite AS (SELECT mes, CAST((mes // 100 - 1) * 100 + mes % 100 AS INTEGER) AS mes_ano_anterior FROM ultimo),
            variacoes AS (
                SELECT
                    'IPCA RMSP - ' || item || ' (até ' || limite.mes || ')' AS indicador,
                    exp(sum(ln(1 + variacao_mensal_percentual / 100)) FILTER (WHERE precos.mes > limite.mes_ano_anterior)) - 1 AS variacao_12_meses,
                    exp(sum(ln(1 + variacao_mensal_percentual / 100)) FILTER (WHERE precos.mes > 201801)) - 1 AS variacao_desde_2018
                FROM '{prices}' AS precos
                CROSS JOIN limite
                GROUP BY item, limite.mes
            ),
            grao AS (
                SELECT
                    'Café arábica CEPEA/ESALQ (saca de 60 kg)' AS indicador,
                    last(preco_saca_60kg ORDER BY data) / first(preco_saca_60kg ORDER BY data) - 1 AS variacao_12_meses,
                    NULL::DOUBLE AS variacao_desde_2018
                FROM '{arabica}'
            )
            SELECT * FROM variacoes
            UNION ALL
            SELECT * FROM grao
        """

    def _arabica_query(self) -> str:
        arabica = self._directories.staging_file("cepea", "arabica.parquet")
        return f"SELECT strftime(data, '%d/%m/%Y'), preco_saca_60kg FROM '{arabica}' ORDER BY data"

    def _influence_area_section(self) -> str:
        areas = self._database.frame(f"SELECT * FROM '{self._directories.marts_file('areas_influencia.parquet')}' ORDER BY endereco_candidato, raio_metros")
        candidates = areas["endereco_candidato"].unique(maintain_order=True)
        blocks = [self._influence_area_block(areas, candidate) for candidate in candidates.to_list()]
        return "## 5. Área de influência dos endereços-exemplo\n\n" + self._texts.influence_area_note() + "\n\n" + "\n\n".join(blocks)

    def _influence_area_block(self, areas: polars.DataFrame, candidate: str) -> str:
        candidate_rows = areas.filter(polars.col("endereco_candidato") == candidate)
        radii = candidate_rows["raio_metros"].to_list()
        values = {column: tuple(candidate_rows[column].to_list()) for column in INFLUENCE_AREA_METRICS.columns()}
        headers = ["Métrica", *[f"Raio de {radius} m" for radius in radii], "Fonte"]
        table = INFLUENCE_AREA_METRICS.table(headers, values)
        return f"### {candidate}\n\n" + table.render()

    def _ranking_section(self) -> str:
        index = self._directories.marts_file("distritos_indice_oportunidade.parquet")
        metrics = self._directories.marts_file("distritos_metricas.parquet")
        ranking = self._database.frame(f"""
            SELECT indice.posicao_ranking, indice.nome_distrito, indice.indice_oportunidade, metricas.mercado_mensal_por_ponto_de_venda,
                metricas.sobrevivencia_3_anos, metricas.cafeterias_ativas, metricas.preco_mediano_m2_comercial
            FROM '{index}' AS indice
            JOIN '{metrics}' AS metricas USING (codigo_distrito)
            WHERE indice.posicao_ranking <= 10 OR indice.codigo_distrito IN ({", ".join(f"'{code}'" for code in self._pilot_district_codes)})
            ORDER BY indice.posicao_ranking
        """)
        rows = [self._ranking_row(row) for row in ranking.iter_rows()]
        table = MarkdownTable(
            ["Posição", "Distrito", "Índice", "Mercado por ponto de venda (R$/mês)", "Sobrevivência 3 anos", "Cafeterias ativas", "m² comercial (R$)"],
            rows,
        )
        return "## 6. Ranking do índice de oportunidade (10 primeiros + distritos do piloto)\n\n" + table.render()

    def _ranking_row(self, row: tuple[int, str, float, float, float, int, float]) -> list[str]:
        return [
            str(row[0]),
            row[1],
            NUMBER_FORMAT.decimal(row[2]),
            NUMBER_FORMAT.rounded_currency(row[3]),
            NUMBER_FORMAT.percentage(row[4]),
            NUMBER_FORMAT.integer(row[5]),
            NUMBER_FORMAT.rounded_currency(row[6]),
        ]
