# Análise de mercado para novas cafeterias (São Paulo)

Pipeline descrito em `PLANEJAMENTO_NOVAS_CAFETERIAS.md`.

## Como executar localmente

```bash
uv sync
uv run python main.py --competencia 2026-09
uv run streamlit run dashboard_app.py
```

O relatório é gerado em `reports/piloto_novas_cafeterias.md`. Os dados seguem três camadas:

- `data/raw/<fonte>/<competência>/`: arquivos como vieram da fonte, nunca alterados;
- `data/staging/<fonte>/`: limpeza e padronização de uma única fonte;
- `data/marts/`: tabelas que cruzam fontes e alimentam o relatório e o dashboard.

Os resultados de qualidade ficam em `data/quality/`.

- **Download:** `uv run python main.py baixar_<fonte> --competencia AAAA-MM`, uma etapa por fonte
  (`baixar_cnpj`, `baixar_ibge`, `baixar_rais`, `baixar_itbi`, `baixar_pesquisa_od`, `baixar_metro`,
  `baixar_motiva`, `baixar_geosampa`). Cada etapa descobre sozinha a versão mais recente até a
  competência (último mês do CNPJ, último ano da RAIS, arquivo mais recente do ITBI) e não baixa de
  novo se o arquivo já existe na pasta da competência.
- **Etapas:** `uv run python main.py [etapa ...] --competencia AAAA-MM [--data-referencia AAAA-MM-DD]`.
  Sem etapas, o `main.py` roda todas na ordem, dos downloads ao relatório. A lista está em
  `uv run python main.py --help`, e as dependências entre elas ficam em
  `coffee_analysis/pipeline/pipeline_graph.py`.
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

## Organização do código

```
coffee_analysis/
├── infrastructure/   banco analítico (DuckDB), diretórios de dados e competência
├── pipeline/         etapas do pipeline e grafo de dependências (lido pela DAG)
├── staging/<fonte>/  limpeza e padronização de uma única fonte (cnpj, ibge, rais, itbi, cepea, mobility)
├── quality/          validação da staging, que bloqueia os marts em caso de falha
├── marts/            tabelas que cruzam fontes: métricas, índice, sobrevivência, áreas de influência
├── reporting/        relatório em Markdown e achados automáticos
└── dashboard/        dashboard em Streamlit
dags/                 DAG mensal do Airflow
tests/                testes unitários
```
