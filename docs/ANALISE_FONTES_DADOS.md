# Fontes de dados sobre consumo de café no Brasil (foco em São Paulo)

> Observação: a mensagem colada não trazia, de fato, uma lista de fontes — apenas um
> parágrafo genérico dizendo que seria necessário recorrer a bases governamentais e de
> institutos de pesquisa. Por isso, a etapa 1 deste trabalho foi pesquisar e validar,
> agora em setembro/2026, quais fontes brasileiras gratuitas realmente existem, estão
> ativas e são úteis para o objetivo. A lista abaixo é o resultado dessa pesquisa.

## 1. Objetivo da análise

Mapear negócios e comportamentos ligados ao consumo de café no Brasil, com recorte para
o estado de São Paulo, cruzando dados de:
- **produção** (quanto café é plantado/colhido),
- **indústria/varejo** (quantos negócios existem, onde, e como crescem/encolhem),
- **consumo domiciliar** (quanto e como as famílias consomem/gastam),
- **preço** (o que pressiona oferta e demanda).

O cruzamento entre essas quatro camadas é o que permite ir de "dados soltos" para
"insight de negócio" (ex.: em quais municípios de SP a densidade de cafeterias cresce
mais rápido que a população, e isso é compatível com renda/consumo local?).

## 2. Fontes selecionadas e avaliação de confiabilidade

| Fonte | Camada | Confiabilidade | Granularidade | Atualização |
|---|---|---|---|---|
| [IBGE – POF](https://www.ibge.gov.br/pof2024/) | Consumo domiciliar | Muito alta (oficial, amostral robusto) | Grande região / UF (não desce a município) | A cada ~7 anos (2017-18; 2024-25 em campo, ainda sem microdados públicos) |
| [IBGE – PAM/SIDRA](https://www.ibge.gov.br/estatisticas/economicas/agricultura-e-pecuaria/9119-producao-agricola-municipal-cereais-leguminosas-e-oleaginosas.html) | Produção agrícola | Muito alta (censo administrativo) | Município | Anual |
| [CONAB – Série Histórica Café](https://www.conab.gov.br/info-agro/safras/serie-historica-das-safras) | Produção/oferta | Muito alta (agência oficial de abastecimento) | Nacional / UF, por tipo (Arábica/Conilon) | A cada safra (levantamentos mensais) |
| [ABIC – Indicadores da Indústria de Café](https://www.abic.com.br/) | Consumo aparente | Alta, mas é dado de associação setorial (autorreportado pelas indústrias associadas) | Nacional (per capita Brasil) | Anual |
| [USDA FAS – Coffee Annual/Semi-annual (Brazil)](https://www.fas.usda.gov/data/brazil-coffee-annual-10) | Produção/consumo/exportação | Alta (fonte independente, cruza com CONAB/ABIC) | Nacional | Semestral |
| [Receita Federal – Dados Abertos de CNPJ](https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/dados-abertos) | Negócios (varejo/indústria) | Muito alta (registro administrativo completo) | Estabelecimento (endereço, CNAE, data de abertura, situação cadastral) | Mensal |
| [Prefeitura de SP – Portal de Dados Abertos](https://dados.prefeitura.sp.gov.br/) | Negócios (município SP) | Alta (dado administrativo municipal) | Estabelecimento/alvará, dentro do município de SP | Variável por dataset |
| [RAIS/CAGED – PDET/MTE](https://acesso.trabalho.gov.br/portal-pdet/o-pdet/portifolio-de-produtos/bases-de-dados.htm) | Emprego formal no setor | Muito alta (registro administrativo trabalhista) | Município, por CNAE | Mensal (CAGED) / Anual (RAIS) |
| [SEADE / Governo Aberto SP](https://dadosabertos.sp.gov.br/) | Contexto socioeconômico | Muito alta (fundação estatística estadual) | Município do estado de SP | Variável (a maioria anual) |
| [Base dos Dados (basedosdados.org)](https://basedosdados.org/) | Camada de integração | Alta (trata dados oficiais, não é fonte primária) | Depende da tabela original | Depende da tabela original |
| [dados.turismo.gov.br – Cadastur Restaurantes/Cafeterias/Bares](https://dados.turismo.gov.br/) | Negócios (turismo) | Média-alta (cadastro voluntário, cobertura parcial) | Estabelecimento | Trimestral |
| [dados.agr.br / CEPEA-ESALQ](https://www.dados.agr.br/cafe/) | Preço e agregação | Alta como painel de consulta; não é fonte primária (reagrega IBGE/CONAB/CEPEA) | Município (produção) / diário (preço) | Diária (preço) |

## 3. Chaves de cruzamento entre as bases

Para relacionar as fontes é preciso um vocabulário comum. As três chaves que aparecem
repetidamente são:

1. **Geografia** — código de município do IBGE (7 dígitos) ou sigla de UF. Presente em
   PAM/SIDRA, RAIS/CAGED, CNPJ (endereço do estabelecimento), SEADE, Prefeitura de SP.
   A POF só desce a nível de região/UF em microdados públicos, então ela entra no
   cruzamento apenas no nível estadual, não municipal.
2. **CNAE (setor de atividade)** — é o elo entre "existe um negócio" (CNPJ, alvará,
   Cadastur) e "existe emprego formal nesse negócio" (RAIS/CAGED). Os códigos relevantes
   precisam ser mapeados com cuidado, por exemplo:
   - `5611-2/01` e `5611-2/03` — restaurantes e lanchonetes/casas de chá/cafeterias;
   - `4721-1/02` — padaria com predominância de revenda de café e produtos de padaria;
   - `4634-6/02` — comércio atacadista de café em grão/torrado/moído/solúvel;
   - códigos de indústria de torrefação e moagem de café (verificar subclasse exata na
     CONCLA/IBGE antes de filtrar, pois há mais de um candidato próximo).
3. **Tempo** — atenção: CONAB, ABIC e USDA trabalham em **ano-safra** (ex.: nov/2024 a
   out/2025), enquanto IBGE, RAIS/CAGED e CNPJ trabalham em **ano civil**. Qualquer
   cruzamento temporal exige converter uma das duas convenções antes de comparar.

Cadeia lógica de cruzamento (produção → indústria/varejo → consumo):

```
IBGE PAM / CONAB (produção por município/UF, ano-safra)
        │
        ▼
CEPEA/dados.agr.br (preço Arábica/Robusta, diário)
        │
        ▼
CNPJ Receita Federal + RAIS/CAGED (negócios e empregos por CNAE e município, ano civil)
        │
        ▼
Prefeitura de SP / Cadastur (confirmação municipal e turística dos negócios)
        │
        ▼
ABIC + USDA (consumo aparente nacional, ano-safra) ── cruza com ──▶ IBGE POF (consumo domiciliar por UF)
        │
        ▼
SEADE (renda, população, urbanização por município de SP) ── explica variação regional
```

## 4. Plano de análise aprofundada por fonte

### 4.1 IBGE — POF (Pesquisa de Orçamentos Familiares)
- **O que extrair**: despesa média mensal com café (em grão/moído/solúvel) e com
  "alimentação fora do domicílio" (cafeterias), por UF, faixa de renda e área
  urbana/rural.
- **Como acessar**: microdados da POF 2017-2018 já publicados; buscar tabelas tratadas
  em [Base dos Dados](https://basedosdados.org/dataset/a1b6d2b6-4aa6-47e7-a517-8a21b28b7254)
  para evitar lidar com os arquivos brutos de pesos amostrais do IBGE.
- **Limitação crítica**: a edição 2024-2025 ainda está em campo/tabulação — os
  microdados públicos mais recentes hoje são de 2017-18, ou seja, defasados ~8 anos.
  Qualquer conclusão de consumo domiciliar precisa citar essa defasagem.
- **Passo a passo**: (1) baixar tabela de despesas por UF; (2) filtrar rubricas de café
  e de bares/lanchonetes/restaurantes; (3) calcular gasto per capita por UF; (4) comparar
  SP contra a média nacional e contra ABIC (per capita em kg).

### 4.2 IBGE — PAM/SIDRA (Produção Agrícola Municipal)
- **O que extrair**: área plantada, área colhida, quantidade produzida e valor da
  produção de café, por município, desde 1974 (dados anuais, granularidade municipal).
- **Como acessar**: SIDRA (tabela 1613) ou via agregador
  [dados.agr.br/cafe](https://www.dados.agr.br/cafe/), que já filtra apenas municípios
  com pelo menos 1 ha cultivado e 1 t produzida — reduz ruído de municípios irrelevantes.
- **Uso no cruzamento**: dá o lado da **oferta regional** dentro de SP (municípios
  produtores, ex. região de Franca/Garça), útil para separar "SP produtor" de "SP
  consumidor/varejista", que são histórias diferentes dentro do mesmo estado.

### 4.3 CONAB — Série Histórica de Safras de Café
- **O que extrair**: produção nacional e por UF, por tipo (Arábica/Conilon), evolução
  safra a safra, estimativas de área e produtividade.
- **Como acessar**: [Portal de Informações Agropecuárias](https://portaldeinformacoes.conab.gov.br/safra-serie-historica-cafe.html)
  (download direto de planilha) ou página de séries históricas em conab.gov.br.
- **Uso no cruzamento**: validar/cruzar a série do IBGE PAM (que é mais granular
  geograficamente, mas mais lenta a publicar) com a série da CONAB (mais rápida e focada
  em política de abastecimento).

### 4.4 ABIC — Indicadores da Indústria de Café
- **O que extrair**: consumo per capita anual (kg/habitante/ano, cru e torrado/moído),
  consumo total em sacas, variação ano a ano, participação de associados x
  não-associados.
- **Como acessar**: relatório anual em PDF, ex.
  [Indicadores da Indústria 2025](https://www.abic.com.br/wp-content/uploads/2026/01/2026.02.Indicadores-da-Industria-2025_-Site.pdf).
  Como só existe em PDF, será necessário extrair as tabelas manualmente ou com
  ferramenta de parsing de PDF.
- **Cuidado de confiabilidade**: é dado autorreportado por uma associação setorial —
  ótimo como indicador de tendência nacional, mas deve ser **sempre cruzado** com a
  fonte independente do USDA (item 4.5) antes de virar premissa de negócio.

### 4.5 USDA FAS — Coffee Annual / Semi-annual (Brazil)
- **O que extrair**: produção, consumo doméstico e exportação em sacas de 60 kg, por
  ano-safra, com metodologia consistente internacionalmente (permite comparar o Brasil
  com outros países consumidores).
- **Como acessar**: [relatórios em PDF no FAS/USDA](https://www.fas.usda.gov/data/brazil-coffee-annual-10).
- **Uso no cruzamento**: contraponto independente aos números da ABIC; também traz
  contexto de exportação, que a ABIC não cobre.

### 4.6 Receita Federal — Dados Abertos de CNPJ
- **O que extrair**: todos os estabelecimentos ativos com CNAE de cafeteria/restaurante/
  torrefação/atacado de café, com endereço, município, data de abertura, situação
  cadastral e capital social.
- **Como acessar**: arquivos completos em [dadosabertos.rfb.gov.br](https://dadosabertos.rfb.gov.br/),
  atualizados mensalmente; como os arquivos nacionais são grandes (dezenas de GB), vale
  usar uma ferramenta pronta de ETL como o
  [projeto aphonsoar/Receita_Federal_do_Brasil_-_Dados_Publicos_CNPJ](https://github.com/aphonsoar/Receita_Federal_do_Brasil_-_Dados_Publicos_CNPJ)
  no GitHub para carregar em banco local e já filtrar por UF=SP e CNAE de interesse.
- **Uso no cruzamento**: é a base que permite contar **quantos negócios existem**, onde
  nasceram e quando fecharam — o dado estrutural para "densidade de cafeterias por
  município" citado na cadeia lógica da seção 3.
- **Limitação**: situação cadastral "ativa" não garante que o negócio está de fato
  funcionando (defasagem de baixas); tratar como teto superior, não como contagem exata.

### 4.7 Prefeitura de São Paulo — Portal de Dados Abertos
- **O que extrair**: alvarás de funcionamento e licenciamento sanitário de
  estabelecimentos de alimentação dentro do município de SP — permite geolocalizar
  cafeterias na capital com mais precisão que o CNPJ nacional (que às vezes só tem
  endereço fiscal, não o de operação).
- **Como acessar**: [dados.prefeitura.sp.gov.br](https://dados.prefeitura.sp.gov.br/),
  buscar datasets de alvarás/vigilância sanitária.
- **Uso no cruzamento**: validação cruzada em nível de bairro/subprefeitura da capital,
  complementando o CNPJ (que não desce abaixo de município).

### 4.8 RAIS/CAGED — Ministério do Trabalho (PDET)
- **O que extrair**: número de vínculos formais, admissões/desligamentos e massa
  salarial no CNAE 56 (alimentação), por município e mês.
- **Como acessar**: [Bases de Dados do PDET](https://acesso.trabalho.gov.br/portal-pdet/o-pdet/portifolio-de-produtos/bases-de-dados.htm).
- **Uso no cruzamento**: mede o **tamanho real da operação** de cada negócio (uma
  cafeteria com 1 CNPJ pode ter 2 ou 20 funcionários) — complementa a contagem simples
  de CNPJs com uma proxy de porte/atividade econômica.

### 4.9 SEADE / Governo Aberto SP
- **O que extrair**: renda domiciliar, população, taxa de urbanização e outros
  indicadores socioeconômicos por município do estado de SP.
- **Como acessar**: [dadosabertos.sp.gov.br](https://dadosabertos.sp.gov.br/), catálogo
  da fundação Seade.
- **Uso no cruzamento**: variável explicativa — testar se a densidade/crescimento de
  cafeterias (CNPJ) em um município correlaciona com renda e urbanização locais.

### 4.10 Base dos Dados (basedosdados.org)
- **Papel**: não é fonte primária, é uma camada de integração em BigQuery que já
  padroniza IBGE, RAIS, CNPJ e outras bases com o mesmo formato de chave geográfica.
  Cota gratuita de 1 TB de processamento/mês, sem cartão de crédito.
- **Uso recomendado**: usar como atalho para não reescrever o ETL de RAIS/CNPJ/IBGE do
  zero — mas sempre documentar que a fonte primária é a listada nas seções acima,
  pois a Base dos Dados pode atrasar a atualização em relação à fonte oficial.

### 4.11 Cadastur (dados.turismo.gov.br)
- **O que extrair**: cadastro de restaurantes/cafeterias/bares como prestadores de
  serviço turístico.
- **Limitação**: cadastro é voluntário — cobre bem estabelecimentos voltados a turismo,
  mas subestima o universo total (uma cafeteria de bairro comum não costuma se
  cadastrar). Usar como complemento qualitativo, não como contagem total.

## 5. O que esse cruzamento permite responder

- **Onde o consumo fora do lar está crescendo em SP**: crescimento de CNPJs ativos de
  CNAE 5611-2/03 por município, cruzado com RAIS/CAGED (emprego formal no setor) e com
  SEADE (renda/urbanização) para explicar o padrão regional.
- **Se o crescimento de negócios acompanha o consumo real**: comparar a curva de
  abertura de CNPJs de cafeteria com o per capita da ABIC e com a despesa domiciliar da
  POF — se negócios crescem mas consumo per capita cai (como ocorreu em 2025 segundo a
  ABIC), é sinal de fragmentação/competição, não de mercado em expansão.
- **Se SP é mais produtor ou mais consumidor/varejista**: cruzar IBGE PAM/CONAB
  (produção municipal) com CNPJ (negócios de varejo/torrefação) para separar os
  municípios de SP que são polos agrícolas dos que são polos de consumo urbano.
- **Pressão de preço sobre o varejo**: usar a série diária de preço do CEPEA/dados.agr.br
  para testar se picos de preço do grão antecedem fechamentos de CNPJ (baixas) no setor.

## 6. Riscos e cuidados gerais

- **Ano-safra x ano civil**: sempre converter antes de comparar (ver seção 3).
- **CNAE mal filtrado**: os códigos de café se sobrepõem com padaria/restaurante
  genérico; validar a subclasse exata na CONCLA antes de qualquer contagem.
- **POF defasada**: a edição mais atual com microdados públicos é 2017-18; tratar
  qualquer número domiciliar como referência histórica, não atual.
- **ABIC é dado de associação setorial**: sempre cruzar com USDA antes de usar como
  verdade absoluta.
- **CNPJ "ativo" ≠ "operando"**: tratar contagens de CNPJ como teto superior.

## 7. Próximos passos sugeridos

1. Baixar e validar uma amostra pequena de cada fonte (ex.: só município de SP capital)
   antes de baixar as bases nacionais completas (CNPJ é pesado).
2. Definir a lista final de códigos CNAE de interesse com apoio da CONCLA/IBGE.
3. Montar a chave geográfica única (código de município IBGE) como padrão de junção
   entre todas as tabelas.
4. Priorizar Base dos Dados para RAIS/CNPJ/IBGE (evita ETL do zero) e reservar tempo
   manual só para ABIC/USDA (PDFs sem API).
