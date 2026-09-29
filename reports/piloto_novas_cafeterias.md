# Piloto: métricas para abertura de cafeterias em São Paulo

Data de referência: 29/09/2026. Recorte: distritos de **Pinheiros** (alta renda, polo de empregos) e **Itaquera** (Zona Leste, residencial e populoso), comparados com a mediana dos 96 distritos da capital.

Todos os valores foram gerados pelo pipeline em `main.py` a partir das fontes públicas listadas na seção de metodologia. Os valores de mercado são **potenciais**, não previsão de faturamento.

## Principais achados (gerados automaticamente em 29/09/2026)

Os achados são montados a partir dos marts a cada execução. A interpretação de negócio fica para a revisão de quem lê.

1. **Mercado e concorrência direta.** Itaquera tem mercado potencial de R$ 1,9 milhão/mês, 20 cafeterias ativas (0,8 por 10 mil pessoas) e R$ 93,7 mil/mês por cafeteria; Pinheiros tem mercado potencial de R$ 2,6 milhões/mês, 129 cafeterias ativas (6,2 por 10 mil pessoas) e R$ 20,3 mil/mês por cafeteria.
2. **Concorrência somando lanchonetes e padarias.** Itaquera soma 796 pontos de venda de café (cafeterias, lanchonetes e padarias), com R$ 2,4 mil/mês por ponto, acima de 12,6% dos distritos; Pinheiros soma 695 pontos de venda de café (cafeterias, lanchonetes e padarias), com R$ 3,8 mil/mês por ponto, acima de 70,5% dos distritos.
3. **Rotatividade e sobrevivência.** Itaquera abriu 2 e fechou 3 cafeterias em 24 meses, com sobrevivência em 3 anos de 61,4%; Pinheiros abriu 40 e fechou 34 cafeterias em 24 meses, com sobrevivência em 3 anos de 71,2%. A mediana da cidade é 64,9%.
4. **Custo do ponto (m² comercial no ITBI).** Itaquera: R$ 2.500/m² (7 vendas), amostra pequena para leitura com cautela; Pinheiros: R$ 10.600/m² (47 vendas).
5. **Endereços-exemplo num raio de 500 m.** **Avenida Campanella, 1000 (Itaquera):** 0 cafeterias (0 abertas em 24 meses), 41 lanchonetes e padarias, 674 empregos formais e 4,4 mil viagens atraídas por dia útil; **Rua dos Pinheiros, 800 (Pinheiros):** 17 cafeterias (8 abertas em 24 meses), 87 lanchonetes e padarias, 27,8 mil empregos formais e 27,6 mil viagens atraídas por dia útil.
6. **Margem do insumo.** Em 12 meses, o arábica variou -29,1%, o café moído -18,7% no IPCA e o cafezinho +7,0%.
7. **Ranking de oportunidade.** Itaquera em 75º; Pinheiros em 36º. Os 5 primeiros são Campo Grande, Barra Funda, Butantã, Morumbi, Liberdade.
8. **Fluxo de pessoas (Pesquisa OD 2023).** Itaquera atrai 172,9 mil viagens por dia útil (0,8 por morador), 74,4 mil a trabalho, e suas estações somam 67,8 mil passageiros por dia; Pinheiros atrai 239,2 mil viagens por dia útil (3,7 por morador), 167,3 mil a trabalho, e suas estações somam 324,0 mil passageiros por dia. A mediana da cidade é 0,8 viagem por morador.
9. **Versão oficial (Pesquisa OD) × versão RAIS.** Correlação de 0,94 entre as posições. A maior subida com a Pesquisa OD é de Bela Vista (+22 posições) e a maior queda é de Sé (-30).

## 1. Ficha comparativa dos distritos

"Mercado potencial" é o gasto mensal estimado das pessoas da região com café e lanches fora de casa. Ele combina o gasto por faixa de renda da POF com a renda domiciliar de cada setor censitário e a quantidade de domicílios em 2022, corrigido pelo IPCA do cafezinho e do lanche. A metade do consumo é atribuída ao local de moradia e a outra metade, o consumo fora de casa, é distribuída pelas viagens atraídas de cada distrito na Pesquisa OD 2023 (versão oficial desde 29/09/2026). As linhas "versão RAIS" mostram o cálculo anterior, que distribuía essa segunda metade pelos empregos formais (ver seção 7).

### Demanda

| Métrica | Itaquera | Pinheiros | Mediana dos 96 distritos | Fonte |
| --- | --- | --- | --- | --- |
| População residente (2022) | 210.960 | 65.145 | 103.612 | Censo 2022 |
| Densidade (hab/km²) | 14.352 | 7.877 | 10.885 | Censo 2022 |
| Empregos formais no distrito | 30.608 | 142.771 | 30.534 | RAIS 2025 |
| Renda média domiciliar (salários mínimos) | 4,1 | 17,5 | 5,9 | Censo 2010 |
| Gasto com café fora de casa por domicílio (R$/mês) | R$ 6,46 | R$ 22,68 | R$ 8,89 | POF 2017-18 + IPCA |
| Gasto com café + lanches fora de casa por domicílio (R$/mês) | R$ 21,71 | R$ 74,14 | R$ 27,67 | POF 2017-18 + IPCA |
| Mercado potencial de café fora de casa (R$/mês) | R$ 570.541 | R$ 807.274 | R$ 411.205 | Derivada |
| Mercado potencial café + lanches (R$/mês) | R$ 1.874.723 | R$ 2.621.681 | R$ 1.293.080 | Derivada |
| Mercado potencial café + lanches, versão RAIS (R$/mês) | R$ 1.001.061 | R$ 2.024.813 | R$ 878.323 | Derivada |

### Fluxo de pessoas

| Métrica | Itaquera | Pinheiros | Mediana dos 96 distritos | Fonte |
| --- | --- | --- | --- | --- |
| Viagens diárias atraídas (trabalho, estudo, compras, serviços e lazer) | 172.898 | 239.189 | 100.987 | Pesquisa OD 2023 |
| Viagens diárias atraídas por trabalho | 74.362 | 167.278 | 43.907 | Pesquisa OD 2023 |
| Viagens diárias atraídas por compras e serviços | 25.831 | 19.889 | 12.064 | Pesquisa OD 2023 |
| Viagens diárias atraídas por lazer e refeição | 14.897 | 26.415 | 4.684 | Pesquisa OD 2023 |
| Viagens atraídas por morador | 0,8 | 3,7 | 0,8 | Derivada |
| Viagens entrevistadas na amostra | 492 | 1.431 | 314 | Pesquisa OD 2023 |
| Pessoas que trabalham no distrito (formais e informais) | 78.390 | 182.968 | 53.921 | Pesquisa OD 2023 |
| Estações de metrô e trem (contadas por linha) | 3 | 8 | 1 | GeoSampa |
| Estações sem dado de demanda (CPTM) | 2 | 0 | 0 | GeoSampa |
| Demanda média das estações em dias úteis | 67.833 | 324.038 | 0 | Metrô e Motiva, 12 meses |

### Concorrência

| Métrica | Itaquera | Pinheiros | Mediana dos 96 distritos | Fonte |
| --- | --- | --- | --- | --- |
| Cafeterias ativas | 20 | 129 | 10 | CNPJ |
| Lanchonetes ativas (concorrência indireta) | 631 | 477 | 298 | CNPJ |
| Padarias ativas (concorrência indireta) | 145 | 89 | 66 | CNPJ |
| Cafeterias por 10 mil pessoas (residentes + empregos) | 0,8 | 6,2 | 0,7 | Derivada |
| Mercado café + lanches por cafeteria (R$/mês) | R$ 93.736 | R$ 20.323 | R$ 106.562 | Derivada |
| Mercado café + lanches por ponto de venda (R$/mês) | R$ 2.355 | R$ 3.772 | R$ 3.269 | Derivada |
| Mercado café + lanches por ponto de venda, versão RAIS (R$/mês) | R$ 1.258 | R$ 2.913 | R$ 2.253 | Derivada |
| Cafeterias abertas nos últimos 12 meses | 0 | 20 | 1 | CNPJ |
| Cafeterias abertas nos últimos 24 meses | 2 | 40 | 2 | CNPJ |
| Cafeterias fechadas nos últimos 24 meses | 3 | 34 | 3 | CNPJ |
| Saldo de cafeterias em 24 meses | -1 | 6 | 0 | CNPJ |
| Novas cafeterias em 24 meses / cafeterias ativas | 10,0% | 31,0% | 24,2% | CNPJ |

### Risco e custos

| Métrica | Itaquera | Pinheiros | Mediana dos 96 distritos | Fonte |
| --- | --- | --- | --- | --- |
| Sobrevivência em 3 anos (cafeterias + lanchonetes) | 61,4% | 71,2% | 64,9% | CNPJ |
| Amostra usada na sobrevivência em 3 anos | 952 | 857 | 470 | CNPJ |
| Empregados por lanchonete/cafeteria (mediana) | 3,5 | 5,0 | 3,0 | RAIS 2025 |
| Preço mediano do m² comercial (R$) | R$ 2.500 | R$ 10.600 | R$ 3.805 | ITBI 2026 |
| Transações comerciais usadas no m² | 7 | 47 | 11 | ITBI 2026 |

### Índice de oportunidade

| Métrica | Itaquera | Pinheiros | Mediana dos 96 distritos | Fonte |
| --- | --- | --- | --- | --- |
| Percentil do mercado por ponto de venda | 12,6% | 70,5% | 50,0% | Derivada |
| Percentil da sobrevivência em 3 anos | 11,7% | 88,3% | 50,0% | Derivada |
| Percentil da pressão de entrada | 20,0% | 67,8% | 50,0% | Derivada |
| Percentil do custo do m² | 12,5% | 94,4% | 50,0% | Derivada |
| **Índice de oportunidade (0 a 100)** | 37,5 | 56,2 | 52,7 | Derivada |
| **Posição no ranking (de 96 distritos)** | 75 | 36 | 48 | Derivada |
| Índice de oportunidade, versão RAIS (0 a 100) | 36,2 | 57,9 | 53,5 | Derivada |
| Posição no ranking, versão RAIS | 74 | 35 | 48 | Derivada |

## 2. Sobrevivência dos negócios

Coortes de CNPJs abertos desde 2012. Um negócio conta como fechado quando está baixado, inapto ou suspenso e a data dessa situação é anterior ao horizonte. Como a Receita demora a registrar baixas, as taxas tendem a ser **otimistas**.

| Recorte | Categoria | Anos após abertura | Negócios na amostra | Ainda ativos |
| --- | --- | --- | --- | --- |
| Cidade de São Paulo | Cafeterias | 1 | 3.866 | 89,6% |
| Cidade de São Paulo | Cafeterias | 2 | 3.588 | 77,5% |
| Cidade de São Paulo | Cafeterias | 3 | 3.273 | 66,4% |
| Cidade de São Paulo | Cafeterias | 5 | 2.675 | 51,2% |
| Cidade de São Paulo | Cafeterias + lanchonetes | 1 | 61.096 | 86,2% |
| Cidade de São Paulo | Cafeterias + lanchonetes | 2 | 55.981 | 77,6% |
| Cidade de São Paulo | Cafeterias + lanchonetes | 3 | 51.130 | 65,6% |
| Cidade de São Paulo | Cafeterias + lanchonetes | 5 | 41.861 | 49,0% |
| Itaquera | Cafeterias | 1 | 24 | 83,3% |
| Itaquera | Cafeterias | 2 | 22 | 68,2% |
| Itaquera | Cafeterias | 3 | 18 | 50,0% |
| Itaquera | Cafeterias | 5 | 14 | 42,9% |
| Itaquera | Cafeterias + lanchonetes | 1 | 1.158 | 83,2% |
| Itaquera | Cafeterias + lanchonetes | 2 | 1.053 | 74,4% |
| Itaquera | Cafeterias + lanchonetes | 3 | 952 | 61,4% |
| Itaquera | Cafeterias + lanchonetes | 5 | 750 | 46,0% |
| Pinheiros | Cafeterias | 1 | 215 | 94,0% |
| Pinheiros | Cafeterias | 2 | 195 | 79,5% |
| Pinheiros | Cafeterias | 3 | 179 | 71,5% |
| Pinheiros | Cafeterias | 5 | 137 | 53,3% |
| Pinheiros | Cafeterias + lanchonetes | 1 | 976 | 92,5% |
| Pinheiros | Cafeterias + lanchonetes | 2 | 913 | 80,7% |
| Pinheiros | Cafeterias + lanchonetes | 3 | 857 | 71,2% |
| Pinheiros | Cafeterias + lanchonetes | 5 | 710 | 53,9% |

## 3. Salários de referência (lanchonetes e cafeterias da capital, RAIS 2025, jornada de 40 horas ou mais)

| Ocupação | Vínculos em tempo integral | Percentil 25 | Mediana | Percentil 75 | Mediana dos admitidos em 2025 |
| --- | --- | --- | --- | --- | --- |
| Atendente de lanchonete | 21.887 | R$ 1.515,76 | R$ 1.813,02 | R$ 2.182,80 | R$ 1.635,18 |
| Auxiliar nos serviços de alimentação | 6.665 | R$ 1.922,28 | R$ 2.180,91 | R$ 2.465,50 | R$ 2.070,51 |
| Cozinheiro geral | 5.177 | R$ 2.174,58 | R$ 2.433,14 | R$ 2.967,76 | R$ 2.357,25 |
| Gerente de restaurante | 3.597 | R$ 2.777,72 | R$ 3.655,54 | R$ 4.954,35 | R$ 3.560,05 |
| Garçom | 3.398 | R$ 2.145,50 | R$ 2.351,45 | R$ 2.866,23 | R$ 2.271,99 |
| Operador de caixa | 1.551 | R$ 2.040,67 | R$ 2.285,38 | R$ 2.645,92 | R$ 2.197,00 |

## 4. Preços e margem

| Indicador | Variação em 12 meses | Variação desde jan/2018 |
| --- | --- | --- |
| IPCA RMSP - Cafezinho (até 202608) | +7,0% | +125,9% |
| IPCA RMSP - Índice geral (até 202608) | +4,5% | +57,4% |
| IPCA RMSP - Café moído (até 202608) | -18,7% | +138,4% |
| IPCA RMSP - Lanche (até 202608) | +7,0% | +101,8% |
| Café arábica CEPEA/ESALQ (saca de 60 kg) | -29,1% | n/d |

| Data | Arábica CEPEA/ESALQ (R$/saca de 60 kg) |
| --- | --- |
| 22/09/2025 | R$ 2.133,08 |
| 22/10/2025 | R$ 2.323,66 |
| 21/11/2025 | R$ 2.181,70 |
| 22/12/2025 | R$ 2.159,06 |
| 22/01/2026 | R$ 2.107,84 |
| 20/02/2026 | R$ 1.806,48 |
| 20/03/2026 | R$ 1.962,67 |
| 22/04/2026 | R$ 1.770,08 |
| 22/05/2026 | R$ 1.612,87 |
| 22/06/2026 | R$ 1.472,20 |
| 22/07/2026 | R$ 1.701,33 |
| 21/08/2026 | R$ 1.803,76 |
| 22/09/2026 | R$ 1.511,31 |

Quando o grão cai e o cafezinho sobe, o custo do insumo principal alivia enquanto o preço de venda continua subindo. É uma janela favorável de margem para quem abre agora, mas o preço do grão é volátil e pode inverter rápido.

## 5. Área de influência dos endereços-exemplo

Cálculo por raio em torno do endereço. A população vem da área de cada setor censitário que cai dentro do círculo. Cafeterias e empregos são contados pelo endereço ou, na falta dele, pelo centro do CEP. Viagens atraídas vêm dos destinos entrevistados na Pesquisa OD 2023, e estações são as que ficam dentro do raio.

### Avenida Campanella, 1000 (Itaquera)

| Métrica | Raio de 300 m | Raio de 500 m | Raio de 1000 m | Fonte |
| --- | --- | --- | --- | --- |
| População residente | 4.388 | 12.217 | 37.480 | Censo 2022 |
| Empregos formais | 267 | 674 | 3.247 | RAIS 2025 |
| Mercado potencial café + lanches, versão RAIS (R$/mês, referência nos raios) | R$ 19.115 | R$ 53.196 | R$ 167.001 | Derivada |
| Mercado potencial café + lanches, versão Pesquisa OD (R$/mês) | R$ 31.241 | R$ 75.881 | R$ 511.693 | Derivada |
| Viagens diárias atraídas (exceto volta para casa) | 2.243 | 4.369 | 59.443 | Pesquisa OD 2023 |
| Viagens diárias atraídas por trabalho | 1.037 | 1.050 | 26.628 | Pesquisa OD 2023 |
| Viagens entrevistadas na amostra | 10 | 17 | 159 | Pesquisa OD 2023 |
| Estações de metrô e trem (por linha) | 0 | 0 | 2 | GeoSampa |
| Demanda média das estações em dias úteis | 0 | 0 | 67.833 | Metrô e Motiva, 12 meses |
| Cafeterias ativas | 0 | 0 | 2 | CNPJ |
| Lanchonetes ativas | 9 | 28 | 106 | CNPJ |
| Padarias ativas | 3 | 13 | 25 | CNPJ |
| Cafeterias abertas em 24 meses | 0 | 0 | 0 | CNPJ |
| Mercado por cafeteria (R$/mês) | n/d | n/d | R$ 83.501 | Derivada |
| Mercado por ponto de venda, versão RAIS (R$/mês, referência nos raios) | R$ 1.593 | R$ 1.297 | R$ 1.256 | Derivada |
| Mercado por ponto de venda, versão Pesquisa OD (R$/mês) | R$ 2.603 | R$ 1.851 | R$ 3.847 | Derivada |

### Rua dos Pinheiros, 800 (Pinheiros)

| Métrica | Raio de 300 m | Raio de 500 m | Raio de 1000 m | Fonte |
| --- | --- | --- | --- | --- |
| População residente | 3.875 | 10.285 | 30.641 | Censo 2022 |
| Empregos formais | 4.893 | 27.812 | 81.455 | RAIS 2025 |
| Mercado potencial café + lanches, versão RAIS (R$/mês, referência nos raios) | R$ 100.702 | R$ 356.164 | R$ 1.064.226 | Derivada |
| Mercado potencial café + lanches, versão Pesquisa OD (R$/mês) | R$ 134.778 | R$ 355.680 | R$ 1.221.348 | Derivada |
| Viagens diárias atraídas (exceto volta para casa) | 10.419 | 27.552 | 106.551 | Pesquisa OD 2023 |
| Viagens diárias atraídas por trabalho | 8.630 | 17.733 | 77.857 | Pesquisa OD 2023 |
| Viagens entrevistadas na amostra | 70 | 188 | 626 | Pesquisa OD 2023 |
| Estações de metrô e trem (por linha) | 1 | 1 | 2 | GeoSampa |
| Demanda média das estações em dias úteis | 19.619 | 19.619 | 54.753 | Metrô e Motiva, 12 meses |
| Cafeterias ativas | 8 | 17 | 67 | CNPJ |
| Lanchonetes ativas | 19 | 73 | 271 | CNPJ |
| Padarias ativas | 3 | 14 | 40 | CNPJ |
| Cafeterias abertas em 24 meses | 4 | 8 | 21 | CNPJ |
| Mercado por cafeteria (R$/mês) | R$ 12.588 | R$ 20.951 | R$ 15.884 | Derivada |
| Mercado por ponto de venda, versão RAIS (R$/mês, referência nos raios) | R$ 3.357 | R$ 3.425 | R$ 2.815 | Derivada |
| Mercado por ponto de venda, versão Pesquisa OD (R$/mês) | R$ 4.493 | R$ 3.420 | R$ 3.231 | Derivada |

## 6. Ranking do índice de oportunidade (10 primeiros + distritos do piloto)

| Posição | Distrito | Índice | Mercado por ponto de venda (R$/mês) | Sobrevivência 3 anos | Cafeterias ativas | m² comercial (R$) |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Campo Grande | 76,7 | R$ 4.657 | 68,3% | 19 | R$ 3.481 |
| 2 | Barra Funda | 75,8 | R$ 5.425 | 73,9% | 38 | R$ 5.688 |
| 3 | Butantã | 75,6 | R$ 5.933 | 70,0% | 24 | R$ 5.414 |
| 4 | Morumbi | 74,7 | R$ 8.587 | 69,6% | 21 | R$ 11.522 |
| 5 | Liberdade | 71,6 | R$ 3.776 | 74,6% | 51 | R$ 3.731 |
| 6 | Vila Mariana | 70,1 | R$ 6.063 | 70,0% | 91 | R$ 10.523 |
| 7 | Campo Belo | 69,8 | R$ 5.234 | 69,8% | 38 | R$ 5.525 |
| 8 | Moema | 69,3 | R$ 7.444 | 73,6% | 79 | R$ 15.385 |
| 9 | Saúde | 68,3 | R$ 4.602 | 68,7% | 51 | R$ 5.808 |
| 10 | Raposo Tavares | 67,6 | R$ 3.132 | 65,5% | 4 | R$ 1.946 |
| 36 | Pinheiros | 56,2 | R$ 3.772 | 71,2% | 129 | R$ 10.600 |
| 75 | Itaquera | 37,5 | R$ 2.355 | 61,4% | 20 | R$ 2.500 |

## 7. Comparação: ranking oficial (Pesquisa OD) × versão RAIS

As duas versões usam o mesmo índice e os mesmos pesos. Muda só a metade do mercado potencial atribuída ao consumo fora de casa:

- **Pesquisa OD (versão oficial):** o gasto fora de casa da cidade é distribuído entre os distritos na proporção das viagens atraídas em dia útil (trabalho, estudo, compras, serviços, lazer e refeição). Isso inclui trabalhadores informais, estudantes e clientes, e usa o endereço onde a pessoa realmente está, não a sede da empresa.
- **RAIS (versão anterior, mantida para comparação):** empregos formais do distrito × gasto médio por habitante da cidade.

Na versão OD, a soma dos distritos é igual ao gasto total dos moradores da cidade (R$ 139,5 milhões/mês). Na versão RAIS, a soma fica em R$ 97,3 milhões, porque só entram os empregos formais. Por isso os valores absolutos da versão OD são maiores. Para comparar as duas versões, use a posição no ranking.

Correlação entre as posições nas duas versões: **0,94**. Em média, um distrito muda **6,7 posições**, e 8 dos 10 primeiros continuam no topo.

### 10 primeiros em qualquer das versões + distritos do piloto

| Distrito | Posição (RAIS) | Posição (OD) | Posições ganhas | Índice (RAIS) | Índice (OD) | Mercado por ponto de venda (RAIS) | Mercado por ponto de venda (OD) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Campo Grande | 3 | 1 | +2 | 74,2 | 76,7 | R$ 3.500 | R$ 4.657 |
| Barra Funda | 4 | 2 | +2 | 74,1 | 75,8 | R$ 3.874 | R$ 5.425 |
| Butantã | 5 | 3 | +2 | 73,5 | 75,6 | R$ 4.014 | R$ 5.933 |
| Morumbi | 2 | 4 | -2 | 74,7 | 74,7 | R$ 6.871 | R$ 8.587 |
| Liberdade | 13 | 5 | +8 | 67,4 | 71,6 | R$ 2.434 | R$ 3.776 |
| Vila Mariana | 9 | 6 | +3 | 68,8 | 70,1 | R$ 4.284 | R$ 6.063 |
| Campo Belo | 6 | 7 | -1 | 71,0 | 69,8 | R$ 4.450 | R$ 5.234 |
| Moema | 8 | 8 | +0 | 69,3 | 69,3 | R$ 5.507 | R$ 7.444 |
| Saúde | 11 | 9 | +2 | 67,9 | 68,3 | R$ 3.777 | R$ 4.602 |
| Raposo Tavares | 7 | 10 | -3 | 70,6 | 67,6 | R$ 2.377 | R$ 3.132 |
| Cambuci | 10 | 21 | -11 | 68,3 | 64,1 | R$ 2.994 | R$ 3.647 |
| Jaguaré | 1 | 27 | -26 | 76,8 | 61,2 | R$ 4.436 | R$ 3.344 |
| Pinheiros | 35 | 36 | -1 | 57,9 | 56,2 | R$ 2.913 | R$ 3.772 |
| Itaquera | 74 | 75 | -1 | 36,2 | 37,5 | R$ 1.258 | R$ 2.355 |

### 5 maiores subidas e 5 maiores quedas com a Pesquisa OD

| Distrito | Posição (RAIS) | Posição (OD) | Posições ganhas | Índice (RAIS) | Índice (OD) | Mercado por ponto de venda (RAIS) | Mercado por ponto de venda (OD) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Bela Vista | 37 | 15 | +22 | 57,8 | 65,8 | R$ 2.470 | R$ 4.205 |
| Freguesia do Ó | 38 | 17 | +21 | 56,7 | 65,5 | R$ 2.124 | R$ 3.668 |
| São Mateus | 61 | 42 | +19 | 44,7 | 54,8 | R$ 1.678 | R$ 3.289 |
| Vila Prudente | 30 | 12 | +18 | 60,4 | 67,6 | R$ 2.421 | R$ 4.025 |
| Penha | 67 | 51 | +16 | 42,5 | 52,2 | R$ 1.993 | R$ 3.590 |
| Sé | 16 | 46 | -30 | 66,7 | 53,2 | R$ 3.342 | R$ 3.044 |
| Jaguaré | 1 | 27 | -26 | 76,8 | 61,2 | R$ 4.436 | R$ 3.344 |
| Vila Matilde | 53 | 74 | -21 | 49,5 | 38,2 | R$ 2.525 | R$ 2.897 |
| Parque do Carmo | 32 | 52 | -20 | 59,8 | 52,2 | R$ 2.241 | R$ 2.725 |
| Bom Retiro | 39 | 58 | -19 | 56,7 | 49,1 | R$ 1.731 | R$ 2.309 |

## 8. Metodologia e fontes

| Fonte | Uso no piloto | Referência |
| --- | --- | --- |
| Receita Federal – CNPJ (set/2026) | Cafeterias, lanchonetes e padarias ativas; aberturas, fechamentos e sobrevivência | CNAEs 5611-2/01, 5611-2/03, 5611-2/04, 5611-2/05, 4721-1/02, 1091-1/02, 1081-3/02 |
| IBGE – Censo 2022 (setores) | População e domicílios, por setor e por distrito | Malha com atributos, SP |
| IBGE – CNEFE 2022 | Coordenadas de endereços e mapeamento CEP → distrito | Município de São Paulo |
| IBGE – Censo 2010 (universo) | Renda domiciliar média por setor | Único dado de renda por setor disponível |
| IBGE – POF 2017-18 (tabela 6972) | Gasto mensal familiar com café e lanches fora de casa, por faixa de renda, em SP | Categorias 3.2 e 3.5 |
| IBGE – IPCA RMSP (tabelas 1419 e 7060) | Correção dos gastos até 2026; variação do cafezinho, do lanche e do café moído | Subitens 1201009, 1201003, 1114022 |
| RAIS 2025 (MTE/PDET) | Empregos formais por distrito (pelo CEP do estabelecimento); porte das lanchonetes; salários | CNAE 5611-2/03 |
| Prefeitura de SP – guias de ITBI 2026 | Preço mediano do m² de imóveis comerciais | Compra e venda de lojas ou imóveis de padrão comercial horizontal |
| CEPEA/ESALQ (via Notícias Agrícolas) | Preço do café arábica | Indicador diário, um ponto por mês |
| Metrô SP – Pesquisa Origem-Destino 2023 | Viagens atraídas por motivo (trabalho, estudo, compras, serviços, lazer, refeição) e pessoas que trabalham em cada distrito ou raio | Microdados com coordenadas do destino, expandidos pelo fator de viagem; dia útil típico |
| Metrô SP – portal da transparência | Demanda média das estações em dias úteis (entradas + transferências) | Linhas 1, 2, 3 e 15; média dos últimos 12 meses |
| Motiva (ViaQuatro e ViaMobilidade) | Demanda média das estações em dias úteis | Linhas 4, 5, 8 e 9; média dos últimos 12 meses |
| Prefeitura de SP – GeoSampa | Localização das estações de metrô e trem em operação | Camadas `estacao_metro` e `estacao_trem` |

**Classificação das cafeterias:** estabelecimentos com CNAE de alimentação cujo nome fantasia ou razão social contém CAFÉ, CAFETERIA, COFFEE, ESPRESSO, EXPRESSO, BARISTA ou TORRA. As demais lanchonetes (5611-2/03) e padarias contam como concorrência indireta. Padarias da CNAE 1091-1/02 só entram quando o nome indica padaria ou panificadora, para excluir confeitarias caseiras.

**Índice de oportunidade:** média ponderada dos percentis entre os 96 distritos. Pesos:

- mercado por ponto de venda (versão Pesquisa OD): 40%;
- sobrevivência em 3 anos: 25%;
- pressão de novas cafeterias: 15%, invertida;
- preço do m² comercial: 20%, invertido.

Distritos com menos de 30 negócios na amostra de sobrevivência ou com menos de 5 vendas comerciais no ITBI recebem percentil neutro (50%) nesse componente, para que amostras pequenas não distorçam o ranking. Os pesos são uma proposta inicial e devem ser calibrados.

## 9. Limitações conhecidas

- **Renda de 2010**: o Censo 2022 ainda não publicou a renda por setor. Bairros que mudaram muito de perfil desde 2010 ficam distorcidos.
- **A POF subestima o consumo fora de casa**: o café costuma ser registrado junto com o lanche e as despesas pequenas são subdeclaradas. Os valores absolutos de mercado ficam abaixo do faturamento real do setor. Por isso servem para **comparar regiões**, não para projetar receita.
- **Empregos pela sede**: a RAIS registra os vínculos no CEP do estabelecimento declarante. Sedes de grandes empresas concentram empregos que, na prática, estão espalhados pela cidade. Isso afeta a versão RAIS do ranking e as áreas de influência, mas não a versão oficial (Pesquisa OD).
- **CNPJ ativo não significa operando**: há atraso nas baixas, então a concorrência e a sobrevivência ficam superestimadas.
- **Classificação por nome**: cafeterias sem "café" no nome entram como lanchonetes, e lanchonetes com "café" no nome entram como cafeterias.
- **ITBI com poucas transações** em distritos periféricos. A amostra aparece na ficha e medianas com menos de 10 transações devem ser lidas com cautela.
- **Parâmetro de 50% do consumo fora de casa**: é uma suposição, não uma medição. A Pesquisa OD mede onde o consumo fora de casa acontece, mas não quanto dele acontece fora de casa. O parâmetro vale nas duas versões do ranking.
- **Mercado OD nos raios pequenos**: nos raios de 300 m e 500 m a versão OD se apoia em poucas viagens entrevistadas e oscila muito entre raios. Por isso, nas áreas de influência a referência continua sendo a versão RAIS, e a versão OD aparece como complemento.
- **Pesquisa OD é amostral**: nos raios de 300 m a amostra tem poucas dezenas de viagens entrevistadas. A linha "Viagens entrevistadas na amostra" mostra quantas, e valores com menos de 30 entrevistas devem ser lidos só como ordem de grandeza.
- **Demanda das estações incompleta**: a CPTM (linhas 7, 10, 11, 12 e 13) e a Linha 6-Laranja ainda não têm fonte integrada. Distritos atendidos por essas linhas, como Itaquera, ficam com a demanda subestimada. A linha "Estações sem dado de demanda" mostra quantas faltam.
- **Transferências contadas nas estações de integração**: a demanda publicada soma entradas e transferências, então quem troca de linha é contado de novo. Isso ainda é fluxo de pessoas passando pelo local, mas infla um pouco os polos de integração.

## 10. Próximos passos sugeridos

1. Validar a classificação de cafeterias com uma amostra manual (ex.: 50 CNPJs por distrito comparados com o Google Maps).
2. Incluir a demanda por estação da CPTM e da Linha 6-Laranja quando houver fonte aberta.
3. Incluir o valor venal do IPTU (cobertura total dos lotes) para complementar o ITBI nos distritos com poucas vendas.
4. Calibrar os pesos do índice contra a sobrevivência observada das cafeterias abertas entre 2019 e 2022.
5. Abrir a análise por endereço para qualquer ponto informado pelo cliente (o código já aceita novos endereços em `main.py`).
