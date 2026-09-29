from dataclasses import dataclass


@dataclass(frozen=True)
class IndexVersion:
    label: str
    metrics_file: str
    index_file: str

    @classmethod
    def official(cls) -> "IndexVersion":
        return cls("Oficial (Pesquisa OD)", "distritos_metricas.parquet", "distritos_indice_oportunidade.parquet")

    @classmethod
    def employment(cls) -> "IndexVersion":
        return cls("RAIS (comparação)", "distritos_metricas_rais.parquet", "distritos_indice_oportunidade_rais.parquet")
