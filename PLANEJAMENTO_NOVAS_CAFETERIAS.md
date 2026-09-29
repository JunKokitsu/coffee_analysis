# Planejamento: métricas de localização e mercado para novas cafeterias (SP)

> Versão reorientada do `ANALISE_FONTES_DADOS.md`. O público agora é um só: quem vai
> **abrir uma cafeteria** no estado de São Paulo, com foco na capital. Fontes que só
> servem para produção agrícola, exportação ou outros negócios da cadeia saíram do escopo.

## 1. Objetivo

Entregar ao empreendedor, para cada **endereço candidato** (ou bairro/distrito), um
conjunto de métricas com valores concretos que respondam:

1. **Tem demanda aqui?** Quantas pessoas moram e circulam na região, e qual é a renda delas.
2. **Quanta concorrência já existe?** Quantas cafeterias há e se a região está saturada.
3. **Cafeterias sobrevivem aqui?** Taxa de sobrevivência histórica dos negócios da região.
4. **Quanto vai custar operar?** Referências de folha salarial, ocupação e insumo.
5. **Quanto dá para cobrar?** Evolução do preço do cafezinho na região metropolitana.
6. **Posso abrir aqui?** Se o zoneamento permite a atividade no lote.

## 2. Unidade de análise

| Nível | Quando usar | Observação |
|---|---|---|
| **Área de influência** (raio de 300 m, 500 m e 1 km em torno do endereço) | Padrão na capital | Exige georreferenciar os CNPJs (ver 5.2) |
| **Distrito / subprefeitura** | Comparar regiões da capital | 96 distritos, compatível com SEADE e Pesquisa OD |
| **Município** | Interior de SP | Onde não há dado intraurbano disponível |

## 3. Métricas entregues

### 3.1 Demanda

| Métrica | Cálculo | Fonte |
|---|---|---|
| População residente na área | Soma dos setores censitários dentro do raio | IBGE Censo 2022 (agregados por setor) |
| Renda média domiciliar da área | Média ponderada pelos domicílios dos setores | IBGE Censo 2022 / SEADE (verificar disponibilidade da renda por setor em 2022; alternativa: Censo 2010) |
| População flutuante | Viagens com destino na zona por motivo trabalho/estudo/compras | Pesquisa Origem-Destino do Metrô (edição mais recente) |
| Fluxo de transporte próximo | Entradas diárias médias nas estações de metrô/trem do raio | Dados abertos Metrô SP / CPTM |
| **Mercado potencial (xícaras/dia)** | (residentes + flutuantes ponderados) × consumo per capita × participação do consumo fora do lar ÷ 365 ÷ gramas por xícara | ABIC (per capita), POF 2017-18 (fração fora do lar em SP) |

### 3.2 Concorrência

| Métrica | Cálculo | Fonte |
|---|---|---|
| Cafeterias ativas no raio | Contagem de CNPJs ativos com CNAE de cafeteria | Receita Federal (CNPJ) + alvarás da Prefeitura |
| Concorrentes indiretos | Padarias e lanchonetes que vendem café | CNPJ (CNAEs `4721-1/02`, `5611-2/03` e correlatos; validar na CONCLA) |
| Densidade | Cafeterias por 10 mil habitantes (residentes + flutuantes) | Derivada |
| **Mercado potencial por cafeteria** | Mercado potencial ÷ (cafeterias + peso × concorrentes indiretos) | Derivada |
| Ritmo de entrada | Novas cafeterias abertas nos últimos 12/24 meses no raio | CNPJ (data de início de atividade) |
| Presença de redes | Participação de CNPJs ligados a redes/franquias (mesmo CNPJ básico, várias filiais) | CNPJ |

### 3.3 Risco / sobrevivência

| Métrica | Cálculo | Fonte |
|---|---|---|
| Taxa de sobrevivência em 1, 2, 3 e 5 anos | Para cada coorte de abertura, fração ainda ativa após N anos | CNPJ (datas de abertura e de situação cadastral) |
| Tempo mediano até o fechamento | Curva de Kaplan-Meier por distrito/município | CNPJ |
| Saldo líquido | Aberturas − baixas nos últimos 24 meses | CNPJ |
| Comparação com a média | Sobrevivência da região vs. média da capital/estado | Derivada |

### 3.4 Custos de operação

| Métrica | Cálculo | Fonte |
|---|---|---|
| Salário médio de admissão de atendente/barista | Média do salário de admissão no CNAE de cafeteria, por município | Novo CAGED (filtrar CBO de atendentes/baristas; validar código) |
| Porte típico da equipe | Distribuição de estabelecimentos por faixa de vínculos | RAIS (tabela de estabelecimentos por tamanho) |
| Custo de ocupação (proxy) | Valor venal médio do m² dos lotes comerciais no raio | Cadastro do IPTU (Prefeitura de SP, dados abertos) |
| Tendência de custo do grão | Variação do indicador de preço do arábica em 3/6/12 meses | CEPEA/ESALQ |

### 3.5 Preço

| Métrica | Cálculo | Fonte |
|---|---|---|
| Inflação do cafezinho | Variação acumulada em 12 meses do subitem "cafezinho" na RM de SP | IBGE IPCA/SIDRA (confirmar código do subitem) |
| Inflação do café moído | Mesmo cálculo para o subitem "café moído" | IBGE IPCA/SIDRA |
| Margem pressionada? | Variação do grão (CEPEA) − variação do cafezinho (IPCA) | Derivada |

### 3.6 Viabilidade legal

| Métrica | Cálculo | Fonte |
|---|---|---|
| Zoneamento permite a atividade | Zona do lote × usos permitidos | GeoSampa (Prefeitura de SP) |

## 4. Entregável

**Relatório por endereço candidato**, com:

1. Ficha resumo com os valores de cada métrica da seção 3.
2. **Índice de oportunidade** de 0 a 100, combinando, com pesos documentados:
   - mercado potencial por cafeteria (maior = melhor);
   - sobrevivência em 3 anos (maior = melhor);
   - ritmo de entrada de concorrentes (maior = pior);
   - custo de ocupação (maior = pior).
3. Posição do endereço no ranking dos distritos da capital (ou municípios do estado).
4. Mapa da área de influência com concorrentes, estações e setores censitários.
5. Comparação com até 3 endereços alternativos informados pelo cliente.

## 5. Fontes

### 5.1 Mantidas do plano anterior

| Fonte | Uso agora |
|---|---|
| Receita Federal – CNPJ | Concorrência, ritmo de entrada, sobrevivência (base central) |
| Prefeitura de SP – alvarás / vigilância sanitária | Confirmar se a cafeteria está operando e seu endereço real |
| RAIS / Novo CAGED | Porte da equipe e salário de admissão |
| SEADE | Renda e população por município/distrito |
| ABIC | Consumo per capita (entrada do mercado potencial) |
| IBGE POF 2017-18 | Fração do consumo fora do lar em SP |
| CEPEA/ESALQ | Tendência de custo do grão |
| Base dos Dados | Atalho de ETL para CNPJ, RAIS e IBGE |

### 5.2 Novas

| Fonte | Uso |
|---|---|
| IBGE Censo 2022 – agregados por setor censitário | População e domicílios em escala de quarteirão |
| IBGE CNEFE 2022 | Coordenadas de endereços, para georreferenciar os CNPJs sem geocodificador pago |
| Pesquisa Origem-Destino (Metrô SP) | População flutuante por zona |
| Metrô SP / CPTM – demanda por estação | Fluxo de pessoas perto do ponto |
| IPTU – cadastro de imóveis (Prefeitura de SP) | Proxy do custo de ocupação |
| GeoSampa | Zoneamento e camadas geográficas da capital |
| IBGE IPCA (SIDRA) | Preço do cafezinho e do café moído |

### 5.3 Removidas

| Fonte | Motivo |
|---|---|
| IBGE PAM, CONAB, USDA | Produção e exportação não influenciam a decisão de onde abrir uma cafeteria |
| Cadastur | Cadastro voluntário; o CNPJ e os alvarás já cobrem o universo |

## 6. Etapas de execução

1. **Definir os CNAEs** de cafeteria e de concorrentes indiretos com a CONCLA/IBGE.
2. **Carregar o CNPJ** (UF = SP, CNAEs definidos, incluindo os baixados, para calcular sobrevivência).
3. **Georreferenciar** os estabelecimentos pelo CNEFE (endereço → coordenada), com fallback pelo centroide do CEP.
4. **Carregar as camadas de demanda**: setores censitários, zonas OD e estações.
5. **Calcular as métricas por distrito** da capital e validar com uma amostra checada manualmente (ex.: 2 distritos, comparando com alvarás e Google Maps).
6. **Calcular as métricas por raio** para endereços arbitrários.
7. **Calibrar o índice de oportunidade**: checar se distritos com índice alto têm, de fato, maior sobrevivência histórica.
8. **Gerar o relatório** por endereço.

## 7. Limitações que o relatório deve declarar

- **Mercado potencial é estimativa**, não previsão de vendas: depende do per capita nacional da ABIC e da POF, que está defasada (2017-18) e só desce até o nível de estado.
- **"CNPJ ativo" não significa "operando"**: baixas chegam atrasadas, então a concorrência fica superestimada e a sobrevivência também. Os alvarás reduzem esse viés na capital.
- **CNAE impreciso**: muitas cafeterias se registram como lanchonete ou padaria; a contagem de concorrentes diretos tem erro.
- **Valor venal do IPTU não é aluguel**: serve só para comparar regiões.
- **Sem dado de faturamento, ticket médio ou preferências**: o produto aponta onde abrir, não quanto a cafeteria vai vender.
- **Intraurbano só na capital**: no interior a análise fica no nível de município.

## 8. Próximos passos

1. ~~Validar a disponibilidade e o formato de Censo 2022 por setor, CNEFE, Pesquisa OD e IPTU.~~ Censo 2022 e CNEFE validados e integrados; Pesquisa OD e IPTU pendentes (ver seção 10).
2. ~~Montar um piloto com 2 distritos da capital, com perfis bem diferentes.~~ Feito em 23/09/2026 (Pinheiros × Itaquera): `reports/piloto_novas_cafeterias.md`.
3. Revisar os pesos do índice de oportunidade com os resultados do piloto.

## 9. Engenharia de dados

Decisões registradas em 26/09/2026. O objetivo é transformar o pipeline do piloto num projeto de
engenharia de dados que consome e cruza fontes diferentes, atualizado mensalmente.

### 9.1 Decisões

| Tema | Decisão | Situação |
|---|---|---|
| Versionamento | Git, repositório **privado** no GitHub pessoal (conta `JunKokitsu`). Dados (`data/`) ficam fora do repositório | Em andamento |
| Armazenamento | DuckDB local + arquivos Parquet. Sem warehouse/lakehouse por enquanto | Mantido |
| Camadas de dados | Três camadas no disco (ver 9.2) | A implementar |
| Orquestração | Apache Airflow, uma DAG com execução **mensal** | A implementar |
| Qualidade de dados | Testes e validações automatizadas (ver 9.4) | **Lembrete: implementar mais tarde** |

### 9.2 Camadas

| Camada | Pasta | Conteúdo | Regra |
|---|---|---|---|
| Bruta (raw) | `data/raw/<fonte>/<competência>/` | Arquivo exatamente como veio da fonte (zip, csv, html, pdf) | Nunca é alterada; cada carga mensal ganha sua própria pasta de competência |
| Intermediária (staging) | `data/staging/<fonte>/` | Uma tabela Parquet por entidade da fonte, com tipos corretos, nomes de coluna padronizados em português e chaves de cruzamento normalizadas | Só limpeza e padronização: sem regra de negócio e sem cruzar fontes |
| Analítica (marts) | `data/marts/` | Tabelas que cruzam fontes: métricas por distrito, sobrevivência, índice de oportunidade, áreas de influência | Lê apenas da staging; é o que alimenta o relatório |

Chaves de cruzamento padronizadas na staging:

- `codigo_distrito` (9 dígitos, IBGE 2022) e `codigo_setor` (15 dígitos);
- `cep` (8 dígitos, texto, sem hífen);
- `cnae` (7 dígitos, texto, sem pontuação);
- `competencia` (primeiro dia do mês, tipo `DATE`) em todas as séries temporais;
- coordenadas sempre em `EPSG:4326` na staging (a projeção métrica fica na camada analítica).

Migração: as tabelas atuais de `data/processed/` serão divididas entre staging (as que só
limpam uma fonte, como `cnpj_*`, `cepea_arabica`, `ipca_cafe_rmsp`, `setores_censo_2022`) e marts
(as que cruzam fontes, como `distritos_metricas`, `distritos_indice_oportunidade`,
`areas_influencia`). As fontes novas da seção 10 já nascem seguindo essas camadas.

### 9.3 Orquestração (Airflow)

- Uma DAG `atualizacao_mensal_cafeterias`, agendada para rodar **uma vez por mês**. O dia será
  definido depois da publicação mensal do CNPJ pela Receita, que é a fonte mais pesada.
- Uma tarefa de download e uma de staging por fonte, que rodam em paralelo entre fontes. As
  tarefas de marts dependem das tabelas de staging que usam, e o relatório vem por último.
- As tarefas são idempotentes: reexecutar uma competência sobrescreve só a pasta daquela
  competência.
- Fontes com publicação anual ou esporádica (Censo, POF, Pesquisa OD) têm tarefas que verificam se
  há versão nova e não baixam de novo se nada mudou.
- O Airflow roda localmente (Docker Compose ou `airflow standalone`) e chama as mesmas classes
  do pacote `coffee_analysis`. A lógica não fica nas DAGs.

### 9.4 Lembrete: qualidade de dados (implementar mais tarde)

> **Pendente.** Ainda não há nenhuma validação automatizada. Quando for implementar, cobrir:
>
> - testes unitários das transformações (pytest);
> - validação de esquema na staging (colunas, tipos, chaves não nulas e únicas);
> - checagens de volume entre competências (ex.: variação de mais de X% no número de CNPJs de SP
>   bloqueia a publicação dos marts);
> - integridade referencial das chaves de cruzamento (todo `codigo_distrito` existe na malha do
>   Censo, todo `cnae` existe na tabela da CONCLA);
> - uma tarefa de qualidade na DAG do Airflow entre staging e marts.

## 10. Integração de novas fontes (prioridade atual)

Ordem combinada: integrar as fontes novas primeiro, já seguindo as camadas da seção 9.2, e depois
migrar o restante do pipeline e montar a DAG do Airflow.

| Fonte | Métrica que destrava | Situação |
|---|---|---|
| Pesquisa Origem-Destino 2023 (Metrô SP) | População flutuante: viagens atraídas por motivo e pessoas que trabalham no distrito ou raio | **Integrada em 28/09/2026** (microdados com coordenadas, sem precisar das zonas OD) |
| Metrô SP – demanda por estação (linhas 1, 2, 3 e 15) | Fluxo de pessoas perto do ponto | **Integrada em 28/09/2026** (CSV do portal da transparência) |
| Motiva – demanda por estação (linhas 4, 5, 8 e 9) | Fluxo de pessoas perto do ponto | **Integrada em 28/09/2026** (PDFs mensais, lidos com `pypdf`) |
| CPTM – demanda por estação (linhas 7, 10, 11, 12 e 13) e Linha 6-Laranja | Fluxo de pessoas perto do ponto | Pendente: não foi encontrada publicação aberta por estação |
| GeoSampa – estações | Localização das estações de metrô e trem | **Integrada em 28/09/2026** (WFS) |
| GeoSampa – zoneamento | Se a zona permite a atividade | A integrar |
| Prefeitura de SP – alvarás / licenciamento | Confirmar se a cafeteria está operando | A integrar |
| IPTU – cadastro de imóveis | Custo de ocupação (complementa o ITBI) | A integrar |
| Novo CAGED | Salário de admissão de atendente/barista | A integrar |

Tabelas geradas pelas fontes integradas:

| Camada | Tabela | Conteúdo |
|---|---|---|
| staging | `pesquisa_od/viagens.parquet`, `pesquisa_od/pessoas.parquet` | Viagens com destino, motivo e fator de expansão; pessoas com local de trabalho (EPSG:4326) |
| staging | `metro/demanda_estacoes.parquet`, `motiva/demanda_estacoes.parquet` | Demanda média em dias úteis por linha, estação e competência |
| staging | `geosampa/estacoes_metro_trem.parquet` | Estações em operação com coordenadas e `chave_estacao` normalizada |
| marts | `estacoes_demanda.parquet` | Estação + demanda média dos últimos 12 meses + distrito |
| marts | `viagens_destino.parquet` | Destinos das viagens com categoria de motivo e distrito |
| marts | `distritos_mobilidade.parquet` | Viagens atraídas, trabalhadores, estações e demanda por distrito |
| marts | `distritos_metricas_od.parquet` | Métricas por distrito com o mercado potencial fora de casa distribuído pelas viagens atraídas da OD |
| marts | `distritos_indice_oportunidade_od.parquet` | Índice de oportunidade calculado sobre o mercado OD, com os mesmos pesos |
| marts | `distritos_comparacao_ranking.parquet` | Posição, índice e mercado por ponto de venda nas versões RAIS e OD, lado a lado |

### 10.1 Mercado potencial pela Pesquisa OD (29/09/2026, em avaliação)

A metade do mercado potencial atribuída ao consumo fora de casa continua em 50%. Na versão OD,
o gasto fora de casa da cidade é distribuído entre os distritos na proporção das viagens atraídas
não residenciais, em vez de empregos formais da RAIS × gasto per capita. O relatório mostra as
duas versões lado a lado (seção 7). Resultados:

- correlação de 0,94 entre as posições e mudança média de 6,7 posições. 8 dos 10 primeiros se mantêm;
- as maiores quedas são de distritos com sedes que inflam a RAIS: Jaguaré (1º → 27º, 78 mil vínculos
  contra 33 mil trabalhadores na OD) e Sé (15º → 45º);
- as maiores subidas são Freguesia do Ó (+23), Bela Vista (+21) e São Mateus (+20);
- Pinheiros vai de 34º para 37º e Itaquera de 74º para 75º.

**Decisão pendente:** qual versão passa a ser a oficial do índice. Nos raios de 300 m e 500 m a
versão OD tem amostra pequena. Nos raios, a versão RAIS continua sendo a referência.

## 11. Execução autônoma (próxima etapa)

Levantamento de 29/09/2026. Hoje o pipeline roda de ponta a ponta, mas não sozinho. É preciso
executar `scripts/baixar_fontes.sh` e `main.py` à mão, e há valores fixos que envelhecem a cada mês:

| Onde | Valor fixo | Efeito |
|---|---|---|
| `scripts/baixar_fontes.sh` | `MES_CNPJ=2026-09` como padrão | Continua baixando o CNPJ de setembro |
| `scripts/baixar_fontes.sh` | RAIS `2025` e URL do ITBI com data (`27082026`) | Não pega versões novas |
| `main.py` | `REFERENCE_DATE = date(2026, 9, 23)` | Aberturas, fechamentos e sobrevivência ficam presos a setembro |
| `coffee_analysis/report_texts.py` | "Principais achados" escritos à mão | Tabelas atualizadas com achados desatualizados |

Ordem de execução:

| Passo | Entrega | Situação |
|---|---|---|
| 1 | **Competência como parâmetro**: competência e data de referência recebidas de fora (linha de comando ou DAG); descoberta automática do último mês do CNPJ, do último ano da RAIS e do arquivo mais recente do ITBI | A implementar |
| 2 | **Qualidade de dados** (seção 9.4): validação da staging e checagem de volume entre competências que bloqueia a publicação dos marts | A implementar (sai do "lembrete para depois": sem ela a execução autônoma publica dados quebrados) |
| 3 | **DAG do Airflow** (seção 9.3): agendamento mensal, tarefas por fonte, tarefa de qualidade entre staging e marts | A implementar |
| 4 | **Achados automáticos**: achados do relatório gerados a partir dos marts, ou separados num texto de análise revisado por uma pessoa | A implementar |
| 5 | **Dashboard**: ferramenta a definir (Streamlit, Metabase, Power BI…) lendo os marts | A definir |

Fontes com publicação anual ou esporádica (Censo, POF, Pesquisa OD) continuam com verificação de
versão nova. A troca de versão dessas fontes pode exigir ajuste manual no código.
