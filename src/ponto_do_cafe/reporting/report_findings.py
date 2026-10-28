from datetime import date

from ponto_do_cafe.infrastructure.analytical_database import AnalyticalDatabase
from ponto_do_cafe.reporting.brazilian_number_format import BrazilianNumberFormat
from ponto_do_cafe.infrastructure.data_directories import DataDirectories

NUMBER_FORMAT = BrazilianNumberFormat()
FINDINGS_RADIUS = 500
TOP_DISTRICTS = 5
SMALL_PROPERTY_SAMPLE = 10

type Row = dict[str, float | int | str | None]


class ReportFindings:
    def __init__(self, database: AnalyticalDatabase, directories: DataDirectories, pilot_district_codes: tuple[str, ...], reference_date: date) -> None:
        self._database = database
        self._directories = directories
        self._pilot_district_codes = pilot_district_codes
        self._reference_date = reference_date

    def render(self) -> str:
        districts = self._district_rows()
        city = self._city_row()
        findings = [
            self._market_finding(districts),
            self._sale_points_finding(districts),
            self._turnover_finding(districts, city),
            self._occupancy_cost_finding(districts),
            self._candidates_finding(),
            self._margin_finding(),
            self._ranking_finding(districts),
            self._mobility_finding(districts, city),
            self._method_finding(),
        ]
        numbered = [f"{position}. {finding}" for position, finding in enumerate(findings, start=1)]
        title = f"## Principais achados (gerados automaticamente em {self._reference_date.strftime('%d/%m/%Y')})"
        note = "Os achados são montados a partir dos marts a cada execução. A interpretação de negócio fica para a revisão de quem lê."
        return "\n\n".join([title, note, "\n".join(numbered)])

    def _frame_rows(self, query: str) -> list[Row]:
        frame = self._database.frame(query)
        return frame.to_dicts()

    def _district_rows(self) -> list[Row]:
        metrics = self._directories.marts_file("distritos_metricas.parquet")
        index = self._directories.marts_file("distritos_indice_oportunidade.parquet")
        comparison = self._directories.marts_file("distritos_comparacao_ranking.parquet")
        mobility = self._directories.marts_file("distritos_mobilidade.parquet")
        codes = ", ".join(f"'{code}'" for code in self._pilot_district_codes)
        return self._frame_rows(f"""
            WITH completo AS (
                SELECT
                    metricas.*,
                    percent_rank() OVER (ORDER BY metricas.mercado_mensal_por_ponto_de_venda) AS percentil_mercado_ponto_de_venda,
                    indice.posicao_ranking,
                    comparacao.posicao_ranking_rais,
                    mobilidade.viagens_atraidas_trabalho,
                    mobilidade.viagens_atraidas_por_morador,
                    mobilidade.demanda_estacoes_dias_uteis
                FROM '{metrics}' AS metricas
                JOIN '{index}' AS indice USING (codigo_distrito)
                JOIN '{comparison}' AS comparacao USING (codigo_distrito)
                JOIN '{mobility}' AS mobilidade USING (codigo_distrito)
            )
            SELECT * FROM completo WHERE codigo_distrito IN ({codes}) ORDER BY codigo_distrito
        """)

    def _city_row(self) -> Row:
        metrics = self._directories.marts_file("distritos_metricas.parquet")
        mobility = self._directories.marts_file("distritos_mobilidade.parquet")
        rows = self._frame_rows(f"""
            SELECT
                (SELECT median(sobrevivencia_3_anos) FROM '{metrics}') AS mediana_sobrevivencia_3_anos,
                (SELECT median(viagens_atraidas_por_morador) FROM '{mobility}') AS mediana_viagens_por_morador
        """)
        return rows[0]

    def _market_finding(self, districts: list[Row]) -> str:
        phrases = [
            f"{district['nome_distrito']} tem mercado potencial de {NUMBER_FORMAT.compact_currency(district['mercado_potencial_mensal'])}/mês, "
            f"{NUMBER_FORMAT.integer(district['cafeterias_ativas'])} cafeterias ativas ({NUMBER_FORMAT.decimal(district['cafeterias_por_10_mil_pessoas'])} por 10 mil pessoas) "
            f"e {NUMBER_FORMAT.compact_currency(district['mercado_mensal_por_cafeteria'])}/mês por cafeteria"
            for district in districts
        ]
        return "**Mercado e concorrência direta.** " + "; ".join(phrases) + "."

    def _sale_points_finding(self, districts: list[Row]) -> str:
        phrases = [
            f"{district['nome_distrito']} soma {NUMBER_FORMAT.integer(district['pontos_de_venda_cafe'])} pontos de venda de café "
            f"(cafeterias, lanchonetes e padarias), com {NUMBER_FORMAT.compact_currency(district['mercado_mensal_por_ponto_de_venda'])}/mês por ponto, "
            f"acima de {NUMBER_FORMAT.percentage(district['percentil_mercado_ponto_de_venda'])} dos distritos"
            for district in districts
        ]
        return "**Concorrência somando lanchonetes e padarias.** " + "; ".join(phrases) + "."

    def _turnover_finding(self, districts: list[Row], city: Row) -> str:
        phrases = [
            f"{district['nome_distrito']} abriu {NUMBER_FORMAT.integer(district['cafeterias_abertas_24_meses'])} e fechou "
            f"{NUMBER_FORMAT.integer(district['cafeterias_fechadas_24_meses'])} cafeterias em 24 meses, "
            f"com sobrevivência em 3 anos de {NUMBER_FORMAT.percentage(district['sobrevivencia_3_anos'])}"
            for district in districts
        ]
        median = NUMBER_FORMAT.percentage(city["mediana_sobrevivencia_3_anos"])
        return "**Rotatividade e sobrevivência.** " + "; ".join(phrases) + f". A mediana da cidade é {median}."

    def _occupancy_cost_finding(self, districts: list[Row]) -> str:
        phrases = [self._occupancy_cost_phrase(district) for district in districts]
        return "**Custo do ponto (m² comercial no ITBI).** " + "; ".join(phrases) + "."

    def _occupancy_cost_phrase(self, district: Row) -> str:
        transactions = district["transacoes_comerciais"]
        phrase = f"{district['nome_distrito']}: {NUMBER_FORMAT.rounded_currency(district['preco_mediano_m2_comercial'])}/m² ({NUMBER_FORMAT.integer(transactions)} vendas)"
        if transactions is None or transactions >= SMALL_PROPERTY_SAMPLE:
            return phrase
        return phrase + ", amostra pequena para leitura com cautela"

    def _candidates_finding(self) -> str:
        areas = self._directories.marts_file("areas_influencia.parquet")
        candidates = self._frame_rows(f"SELECT * FROM '{areas}' WHERE raio_metros = {FINDINGS_RADIUS} ORDER BY endereco_candidato")
        phrases = [
            f"**{candidate['endereco_candidato']}:** {NUMBER_FORMAT.integer(candidate['cafeterias_ativas'])} cafeterias "
            f"({NUMBER_FORMAT.integer(candidate['cafeterias_abertas_24_meses'])} abertas em 24 meses), "
            f"{NUMBER_FORMAT.integer(candidate['lanchonetes_ativas'] + candidate['padarias_ativas'])} lanchonetes e padarias, "
            f"{NUMBER_FORMAT.compact_integer(candidate['vinculos_formais'])} empregos formais e "
            f"{NUMBER_FORMAT.compact_integer(candidate['viagens_atraidas_nao_residenciais'])} viagens atraídas por dia útil"
            for candidate in candidates
        ]
        return f"**Endereços-exemplo num raio de {FINDINGS_RADIUS} m.** " + "; ".join(phrases) + "."

    def _margin_finding(self) -> str:
        prices = self._directories.staging_file("ipca", "variacao_mensal_rmsp.parquet")
        arabica = self._directories.staging_file("cepea", "arabica.parquet")
        rows = self._frame_rows(f"""
            WITH limite AS (SELECT max(mes) AS mes FROM '{prices}'),
            ipca AS (
                SELECT item, exp(sum(ln(1 + variacao_mensal_percentual / 100))) - 1 AS variacao
                FROM '{prices}' AS precos, limite
                WHERE precos.mes > limite.mes - 100
                GROUP BY item
            )
            SELECT
                (SELECT last(preco_saca_60kg ORDER BY data) / first(preco_saca_60kg ORDER BY data) - 1 FROM '{arabica}') AS arabica,
                (SELECT variacao FROM ipca WHERE item ILIKE '%moído%') AS cafe_moido,
                (SELECT variacao FROM ipca WHERE item ILIKE '%cafezinho%') AS cafezinho
        """)
        values = rows[0]
        return (
            f"**Margem do insumo.** Em 12 meses, o arábica variou {NUMBER_FORMAT.signed_percentage(values['arabica'])}, "
            f"o café moído {NUMBER_FORMAT.signed_percentage(values['cafe_moido'])} no IPCA e o cafezinho {NUMBER_FORMAT.signed_percentage(values['cafezinho'])}."
        )

    def _ranking_finding(self, districts: list[Row]) -> str:
        index = self._directories.marts_file("distritos_indice_oportunidade.parquet")
        leaders = self._frame_rows(f"SELECT nome_distrito FROM '{index}' ORDER BY posicao_ranking LIMIT {TOP_DISTRICTS}")
        leader_names = ", ".join(str(leader["nome_distrito"]) for leader in leaders)
        positions = "; ".join(f"{district['nome_distrito']} em {district['posicao_ranking']}º" for district in districts)
        return f"**Ranking de oportunidade.** {positions}. Os {TOP_DISTRICTS} primeiros são {leader_names}."

    def _mobility_finding(self, districts: list[Row], city: Row) -> str:
        phrases = [
            f"{district['nome_distrito']} atrai {NUMBER_FORMAT.compact_integer(district['viagens_atraidas_nao_residenciais'])} viagens por dia útil "
            f"({NUMBER_FORMAT.decimal(district['viagens_atraidas_por_morador'])} por morador), "
            f"{NUMBER_FORMAT.compact_integer(district['viagens_atraidas_trabalho'])} a trabalho, e suas estações somam "
            f"{NUMBER_FORMAT.compact_integer(district['demanda_estacoes_dias_uteis'])} passageiros por dia"
            for district in districts
        ]
        median = NUMBER_FORMAT.decimal(city["mediana_viagens_por_morador"])
        return "**Fluxo de pessoas (Pesquisa OD 2023).** " + "; ".join(phrases) + f". A mediana da cidade é {median} viagem por morador."

    def _method_finding(self) -> str:
        comparison = self._directories.marts_file("distritos_comparacao_ranking.parquet")
        rows = self._frame_rows(f"""
            SELECT
                corr(posicao_ranking_rais, posicao_ranking_od) AS correlacao,
                arg_max(nome_distrito, posicoes_ganhas_com_od) AS maior_subida,
                max(posicoes_ganhas_com_od) AS posicoes_subida,
                arg_min(nome_distrito, posicoes_ganhas_com_od) AS maior_queda,
                min(posicoes_ganhas_com_od) AS posicoes_queda
            FROM '{comparison}'
        """)
        values = rows[0]
        correlation = f"{values['correlacao']:.2f}".replace(".", ",")
        return (
            f"**Versão oficial (Pesquisa OD) × versão RAIS.** Correlação de {correlation} entre as posições. "
            f"A maior subida com a Pesquisa OD é de {values['maior_subida']} ({values['posicoes_subida']:+d} posições) "
            f"e a maior queda é de {values['maior_queda']} ({values['posicoes_queda']:+d})."
        )
