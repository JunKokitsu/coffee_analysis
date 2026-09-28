# Análise de mercado para novas cafeterias (São Paulo)

Pipeline do piloto descrito em `PLANEJAMENTO_NOVAS_CAFETERIAS.md`.

## Como executar

```bash
uv sync
./scripts/baixar_fontes.sh
uv run python main.py
```

O relatório é gerado em `reports/piloto_novas_cafeterias.md`. As fontes novas seguem as camadas `data/raw/<fonte>/<competência>/`, `data/staging/<fonte>/` e `data/marts/`. As etapas anteriores ainda gravam em `data/processed/` até a migração (ver seção 9.2 do planejamento).

Para rodar apenas algumas etapas, passe seus nomes na ordem desejada:

```bash
uv run python main.py metricas indice area_influencia relatorio
```

Etapas disponíveis: `enderecos`, `censo`, `ipca`, `pof`, `renda`, `cepea`, `rais`, `itbi`, `cnpj`, `sobrevivencia`, `metricas`, `indice`, `pesquisa_od`, `demanda_metro`, `demanda_motiva`, `estacoes`, `fluxo_estacoes`, `mobilidade`, `area_influencia`, `relatorio`.

O download das fontes mensais usa a competência atual (`AAAA-MM`). Para baixar outra, defina `COMPETENCIA=2026-09 ./scripts/baixar_fontes.sh`.

Os endereços analisados e os distritos do piloto são configurados em `main.py`.
