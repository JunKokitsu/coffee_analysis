# Análise de mercado para novas cafeterias (São Paulo)

Pipeline do piloto descrito em `PLANEJAMENTO_NOVAS_CAFETERIAS.md`.

## Como executar

```bash
uv sync
./scripts/baixar_fontes.sh
uv run python main.py
```

O relatório é gerado em `reports/piloto_novas_cafeterias.md` e as tabelas intermediárias ficam em `data/processed/`.

Para rodar apenas algumas etapas, passe seus nomes na ordem desejada:

```bash
uv run python main.py metricas indice area_influencia relatorio
```

Etapas disponíveis: `enderecos`, `censo`, `ipca`, `pof`, `renda`, `cepea`, `rais`, `itbi`, `cnpj`, `sobrevivencia`, `metricas`, `indice`, `area_influencia`, `relatorio`.

Os endereços analisados e os distritos do piloto são configurados em `main.py`.
