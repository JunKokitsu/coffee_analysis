# Análise de mercado para novas cafeterias (São Paulo)

Pipeline descrito em `PLANEJAMENTO_NOVAS_CAFETERIAS.md`.

## Como executar localmente

```bash
uv sync
COMPETENCIA=2026-09 ./scripts/baixar_fontes.sh
uv run python main.py --competencia 2026-09
uv run streamlit run dashboard_app.py
```

O relatório é gerado em `reports/piloto_novas_cafeterias.md`. Os dados seguem três camadas:

- `data/raw/<fonte>/<competência>/`: arquivos como vieram da fonte, nunca alterados;
- `data/staging/<fonte>/`: limpeza e padronização de uma única fonte;
- `data/marts/`: tabelas que cruzam fontes e alimentam o relatório e o dashboard.

Os resultados de qualidade ficam em `data/quality/`.

- **Download:** `./scripts/baixar_fontes.sh [fonte ...]` baixa todas as fontes ou só as indicadas
  (`cnpj`, `ibge`, `rais`, `itbi`, `pesquisa_od`, `metro`, `motiva`, `geosampa`). Ele descobre
  sozinho a última publicação do CNPJ até a competência, o último ano da RAIS e o arquivo mais
  recente do ITBI.
- **Etapas:** `uv run python main.py [etapa ...] --competencia AAAA-MM [--data-referencia AAAA-MM-DD]`.
  Sem etapas, roda todas na ordem. A lista está em `uv run python main.py --help`, e as
  dependências entre elas ficam em `coffee_analysis/pipeline_graph.py`.
- **Qualidade:** a etapa `qualidade` valida a staging e bloqueia os marts se alguma verificação falhar.
- **Testes:** `uv run pytest`.

## Execução mensal com Airflow

```bash
docker compose up -d airflow dashboard
```

- A DAG `atualizacao_mensal_cafeterias` roda todo dia 20 às 6h. A interface fica em
  `localhost:8080`, com usuário e senha gerados pelo `airflow standalone` e mostrados em
  `docker compose logs airflow`.
- O dashboard fica em `localhost:8501`.
- Para reprocessar uma competência, dispare a DAG manualmente com o parâmetro `competencia`.

Os endereços analisados e os distritos do piloto são configurados em `main.py`.
