STAGING_LAYER = "staging"
QUALITY_LAYER = "qualidade"
MARTS_LAYER = "marts"
REPORT_LAYER = "relatorio"

STEP_LAYERS: dict[str, str] = {
    "enderecos": STAGING_LAYER,
    "censo": STAGING_LAYER,
    "renda_2010": STAGING_LAYER,
    "ipca": STAGING_LAYER,
    "pof": STAGING_LAYER,
    "cepea": STAGING_LAYER,
    "rais": STAGING_LAYER,
    "itbi": STAGING_LAYER,
    "cnpj": STAGING_LAYER,
    "pesquisa_od": STAGING_LAYER,
    "demanda_metro": STAGING_LAYER,
    "demanda_motiva": STAGING_LAYER,
    "estacoes": STAGING_LAYER,
    "qualidade": QUALITY_LAYER,
    "renda": MARTS_LAYER,
    "empregos": MARTS_LAYER,
    "preco_m2": MARTS_LAYER,
    "cafeterias": MARTS_LAYER,
    "sobrevivencia": MARTS_LAYER,
    "metricas_rais": MARTS_LAYER,
    "indice_rais": MARTS_LAYER,
    "fluxo_estacoes": MARTS_LAYER,
    "mobilidade": MARTS_LAYER,
    "metricas": MARTS_LAYER,
    "indice": MARTS_LAYER,
    "comparacao_ranking": MARTS_LAYER,
    "area_influencia": MARTS_LAYER,
    "relatorio": REPORT_LAYER,
}

MART_DEPENDENCIES: dict[str, tuple[str, ...]] = {
    "renda": ("qualidade",),
    "empregos": ("qualidade",),
    "preco_m2": ("qualidade",),
    "cafeterias": ("qualidade",),
    "fluxo_estacoes": ("qualidade",),
    "sobrevivencia": ("cafeterias",),
    "metricas_rais": ("renda", "empregos", "preco_m2", "cafeterias", "sobrevivencia"),
    "indice_rais": ("metricas_rais",),
    "mobilidade": ("fluxo_estacoes",),
    "metricas": ("metricas_rais", "mobilidade"),
    "indice": ("metricas",),
    "comparacao_ranking": ("indice", "indice_rais"),
    "area_influencia": ("metricas", "cafeterias", "empregos", "mobilidade"),
    "relatorio": ("comparacao_ranking", "area_influencia"),
}

DOWNLOAD_SOURCES: dict[str, str] = {
    "enderecos": "ibge",
    "censo": "ibge",
    "renda_2010": "ibge",
    "rais": "rais",
    "itbi": "itbi",
    "cnpj": "cnpj",
    "pesquisa_od": "pesquisa_od",
    "demanda_metro": "metro",
    "demanda_motiva": "motiva",
    "estacoes": "geosampa",
}


def staging_steps() -> list[str]:
    return [step for step, layer in STEP_LAYERS.items() if layer == STAGING_LAYER]


def step_dependencies(step: str) -> tuple[str, ...]:
    if STEP_LAYERS[step] == QUALITY_LAYER:
        return tuple(staging_steps())
    return MART_DEPENDENCIES.get(step, ())
