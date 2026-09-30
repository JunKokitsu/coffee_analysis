from collections.abc import Iterator

from coffee_analysis.infrastructure.data_directories import DataDirectories
from coffee_analysis.quality.table_expectation import TableExpectation

COMPANY_REGISTRY_VOLUME_TOLERANCE = 0.1


class TableExpectations:
    def __init__(self, directories: DataDirectories) -> None:
        staging = directories.staging_file
        self._expectations = (
            TableExpectation(
                "cnefe/enderecos",
                staging("cnefe", "enderecos.parquet"),
                ("cep", "logradouro", "numero", "codigo_distrito", "latitude", "longitude"),
                not_null_columns=("cep",),
                unique_columns=("cep", "logradouro", "numero"),
                minimum_rows=500_000,
                district_column="codigo_distrito",
            ),
            TableExpectation(
                "cnefe/cep_distrito",
                staging("cnefe", "cep_distrito.parquet"),
                ("cep", "codigo_distrito", "latitude", "longitude"),
                not_null_columns=("cep", "codigo_distrito"),
                unique_columns=("cep",),
                minimum_rows=40_000,
                district_column="codigo_distrito",
            ),
            TableExpectation(
                "censo_2022/setores",
                staging("censo_2022", "setores.parquet"),
                ("codigo_setor", "codigo_distrito", "populacao", "domicilios_ocupados", "geometry"),
                not_null_columns=("codigo_setor", "codigo_distrito"),
                unique_columns=("codigo_setor",),
                minimum_rows=20_000,
                district_column="codigo_distrito",
            ),
            TableExpectation(
                "censo_2022/distritos",
                staging("censo_2022", "distritos.parquet"),
                ("codigo_distrito", "nome_distrito", "area_km2", "populacao_2022", "domicilios_2022", "geometry"),
                not_null_columns=("codigo_distrito", "populacao_2022"),
                unique_columns=("codigo_distrito",),
                minimum_rows=96,
            ),
            TableExpectation(
                "censo_2010/setores_renda",
                staging("censo_2010", "setores_renda.parquet"),
                ("codigo_setor", "codigo_distrito", "domicilios", "renda_total"),
                not_null_columns=("codigo_setor", "codigo_distrito"),
                unique_columns=("codigo_setor",),
                minimum_rows=15_000,
                district_column="codigo_distrito",
            ),
            TableExpectation(
                "ipca/variacao_mensal_rmsp",
                staging("ipca", "variacao_mensal_rmsp.parquet"),
                ("mes", "codigo_item", "item", "variacao_mensal_percentual"),
                not_null_columns=("mes", "codigo_item", "variacao_mensal_percentual"),
                unique_columns=("codigo_item", "mes"),
                minimum_rows=400,
            ),
            TableExpectation(
                "pof/gasto_cafe_sp",
                staging("pof", "gasto_cafe_sp.parquet"),
                ("classe_rendimento", "limite_inferior_salarios_minimos", "gasto_cafe_fora_domicilio", "gasto_lanches_fora_domicilio"),
                not_null_columns=("classe_rendimento",),
                unique_columns=("classe_rendimento",),
                minimum_rows=5,
            ),
            TableExpectation(
                "cepea/arabica",
                staging("cepea", "arabica.parquet"),
                ("data", "preco_saca_60kg"),
                not_null_columns=("data", "preco_saca_60kg"),
                unique_columns=("data",),
                minimum_rows=6,
            ),
            TableExpectation(
                "rais/estabelecimentos",
                staging("rais", "estabelecimentos.parquet"),
                ("cep", "cnae", "vinculos_ativos"),
                not_null_columns=("cep", "cnae"),
                minimum_rows=100_000,
            ),
            TableExpectation(
                "rais/vinculos_alimentacao",
                staging("rais", "vinculos_alimentacao.parquet"),
                ("cnae", "codigo_ocupacao", "remuneracao_media", "mes_admissao", "horas_contratadas", "ativo_31_dezembro"),
                not_null_columns=("cnae",),
                minimum_rows=10_000,
            ),
            TableExpectation(
                "itbi/transacoes",
                staging("itbi", "transacoes.parquet"),
                ("cep", "natureza_transacao", "valor_transacao", "proporcao_transmitida", "area_construida", "descricao_uso", "mes_referencia"),
                not_null_columns=("mes_referencia",),
                minimum_rows=10_000,
            ),
            TableExpectation(
                "cnpj/estabelecimentos_alimentacao",
                staging("cnpj", "estabelecimentos_alimentacao.parquet"),
                ("cnpj", "cnpj_basico", "nome_fantasia", "cnae", "situacao_cadastral", "data_inicio_atividade", "cep", "numero"),
                not_null_columns=("cnpj", "cnae", "situacao_cadastral"),
                unique_columns=("cnpj",),
                minimum_rows=50_000,
                volume_tolerance=COMPANY_REGISTRY_VOLUME_TOLERANCE,
            ),
            TableExpectation(
                "cnpj/empresas_alimentacao",
                staging("cnpj", "empresas_alimentacao.parquet"),
                ("cnpj_basico", "razao_social"),
                not_null_columns=("cnpj_basico",),
                unique_columns=("cnpj_basico",),
                minimum_rows=50_000,
                volume_tolerance=COMPANY_REGISTRY_VOLUME_TOLERANCE,
            ),
            TableExpectation(
                "pesquisa_od/viagens",
                staging("pesquisa_od", "viagens.parquet"),
                ("id_pessoa", "numero_viagem", "fator_expansao_viagem", "codigo_motivo_destino", "latitude_destino", "longitude_destino"),
                not_null_columns=("id_pessoa", "numero_viagem", "fator_expansao_viagem"),
                unique_columns=("id_pessoa", "numero_viagem"),
                minimum_rows=50_000,
            ),
            TableExpectation(
                "pesquisa_od/pessoas",
                staging("pesquisa_od", "pessoas.parquet"),
                ("id_pessoa", "fator_expansao_pessoa", "latitude_trabalho", "longitude_trabalho"),
                not_null_columns=("id_pessoa", "fator_expansao_pessoa"),
                unique_columns=("id_pessoa",),
                minimum_rows=50_000,
            ),
            TableExpectation(
                "metro/demanda_estacoes",
                staging("metro", "demanda_estacoes.parquet"),
                ("numero_linha", "nome_estacao", "chave_estacao", "competencia", "demanda_media_dias_uteis"),
                not_null_columns=("numero_linha", "chave_estacao", "competencia", "demanda_media_dias_uteis"),
                unique_columns=("numero_linha", "chave_estacao", "competencia"),
                minimum_rows=300,
            ),
            TableExpectation(
                "motiva/demanda_estacoes",
                staging("motiva", "demanda_estacoes.parquet"),
                ("numero_linha", "nome_estacao", "chave_estacao", "competencia", "demanda_media_dias_uteis"),
                not_null_columns=("numero_linha", "chave_estacao", "competencia", "demanda_media_dias_uteis"),
                unique_columns=("numero_linha", "chave_estacao", "competencia"),
                minimum_rows=300,
            ),
            TableExpectation(
                "geosampa/estacoes_metro_trem",
                staging("geosampa", "estacoes_metro_trem.parquet"),
                ("numero_linha", "nome_estacao", "chave_estacao", "latitude", "longitude"),
                not_null_columns=("numero_linha", "chave_estacao", "latitude", "longitude"),
                unique_columns=("numero_linha", "chave_estacao"),
                minimum_rows=100,
            ),
        )

    def __iter__(self) -> Iterator[TableExpectation]:
        return iter(self._expectations)
