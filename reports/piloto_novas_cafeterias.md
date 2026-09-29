# Piloto: métricas para abertura de cafeterias em São Paulo

Data de referência: 23/09/2026. Recorte: distritos de **Pinheiros** (alta renda, polo de empregos) e **Itaquera** (Zona Leste, residencial e populoso), comparados com a mediana dos 96 distritos da capital.

Todos os valores foram gerados pelo pipeline em `main.py` a partir das fontes públicas listadas na seção de metodologia. Os valores de mercado são **potenciais**, não previsão de faturamento.

## Principais achados (leitura do piloto em 23/09/2026)

1. **Pinheiros tem o dobro de mercado, mas quase 8 vezes mais cafeterias por pessoa.** O mercado potencial de café + lanches é de cerca de R$ 2,0 milhões/mês, contra R$ 1,0 milhão em Itaquera. Porém são 129 cafeterias ativas (6,2 por 10 mil pessoas) contra 20 (0,8). O mercado por cafeteria cai para cerca de R$ 16 mil/mês, contra R$ 50 mil em Itaquera.
2. **Somando lanchonetes e padarias, Itaquera é mais disputada.** Os 796 pontos de venda de café de Itaquera deixam R$ 1,3 mil/mês por ponto, o 10º percentil mais baixo da cidade. Pinheiros tem R$ 2,9 mil. A falta de cafeterias em Itaquera é uma oportunidade de diferenciação, não de mercado vazio.
3. **Pinheiros tem alta rotatividade.** Em 24 meses abriram 41 cafeterias e fecharam 34. Ainda assim, a sobrevivência em 3 anos (71%) está acima da mediana da cidade (65%). Itaquera fica abaixo (62%) e teve saldo negativo de cafeterias.
4. **O ponto custa 4 vezes mais em Pinheiros**: R$ 10,6 mil/m² contra R$ 2,5 mil em Itaquera. O valor de Itaquera vem de apenas 7 vendas e deve ser lido com cautela.
5. **Os endereços-exemplo mostram perfis opostos.** Num raio de 500 m:
   - **Rua dos Pinheiros, 800:** 17 cafeterias, 8 abertas nos últimos 24 meses, e 27,8 mil empregos formais. O fluxo de trabalho é alto e a saturação também.
   - **Av. Campanella, 1000:** nenhuma cafeteria e 41 lanchonetes/padarias. É uma demanda de bairro, sensível a preço.
6. **A margem do insumo está favorável.** Em 12 meses o arábica caiu 29% e o café moído caiu 19% no IPCA, enquanto o cafezinho subiu 7%.
7. **No ranking, nenhum dos dois distritos está no topo.** Pinheiros ficou em 34º e Itaquera em 74º. Os primeiros colocados combinam mercado por ponto de venda acima da média, boa sobrevivência e m² moderado: Jaguaré, Morumbi, Campo Grande, Barra Funda e Butantã.
8. **A Pesquisa OD confirma Pinheiros como polo de destino** (incluído em 28/09/2026). O distrito atrai 239 mil viagens por dia útil, ou 3,7 por morador, sendo 167 mil a trabalho. Suas estações somam 324 mil passageiros por dia. Itaquera atrai 173 mil viagens, 0,8 por morador, igual à mediana, com mais peso de compras e serviços (26 mil contra 20 mil em Pinheiros). No raio de 500 m, a Rua dos Pinheiros recebe 27,6 mil viagens por dia, contra 4,4 mil na Av. Campanella.
9. **Medir o consumo fora de casa pela Pesquisa OD muda pouco o topo, mas corrige distritos com sedes de empresas** (incluído em 29/09/2026). Os dois rankings têm correlação de 0,94. Jaguaré cai do 1º para o 27º lugar e a Sé do 15º para o 45º, porque a RAIS registra ali mais empregos do que as pessoas que de fato trabalham no distrito: 78 mil vínculos contra 33 mil trabalhadores no Jaguaré. Sobem distritos com muitas viagens de trabalho informal, compras e estudo, como Freguesia do Ó (+23) e Bela Vista (+21). Na versão OD, Campo Grande assume o 1º lugar. Pinheiros vai para 37º e Itaquera para 75º. O mercado de Itaquera quase dobra (R$ 1,9 milhão/mês), mas os outros distritos também sobem e a posição não muda.

## 1. Ficha comparativa dos distritos

"Mercado potencial" é o gasto mensal estimado das pessoas da região com café e lanches fora de casa. Ele combina o gasto por faixa de renda da POF com a renda domiciliar de cada setor censitário, a quantidade de domicílios em 2022 e os empregos formais do distrito, corrigido pelo IPCA do cafezinho e do lanche. A metade do consumo é atribuída ao local de moradia e a outra metade ao local de trabalho. As linhas "versão Pesquisa OD" distribuem essa segunda metade pelas viagens atraídas de cada distrito, e não pelos empregos formais (ver seção 7).

### Demanda

| Métrica | Itaquera | Pinheiros | Mediana dos 96 distritos | Fonte |
| --- | --- | --- | --- | --- |
| População residente (2022) | 210.960 | 65.145 | 103.612 | Censo 2022 |
| Densidade (hab/km²) | 14.352 | 7.877 | 10.885 | Censo 2022 |
| Empregos formais no distrito | 30.608 | 143.394 | 30.534 | RAIS 2025 |
| Renda média domiciliar (salários mínimos) | 4,1 | 17,5 | 5,9 | Censo 2010 |
| Gasto com café fora de casa por domicílio (R$/mês) | R$ 6,46 | R$ 22,68 | R$ 8,89 | POF 2017-18 + IPCA |
| Gasto com café + lanches fora de casa por domicílio (R$/mês) | R$ 21,71 | R$ 74,14 | R$ 27,67 | POF 2017-18 + IPCA |
| Mercado potencial de café fora de casa (R$/mês) | R$ 300.092 | R$ 623.684 | R$ 270.266 | Derivada |
| Mercado potencial café + lanches (R$/mês) | R$ 1.001.061 | R$ 2.028.608 | R$ 878.323 | Derivada |
| Mercado potencial café + lanches, fora de casa pela Pesquisa OD (R$/mês) | R$ 1.874.723 | R$ 2.621.681 | R$ 1.293.080 | Derivada |

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
| Lanchonetes ativas (concorrência indireta) | 631 | 477 | 297 | CNPJ |
| Padarias ativas (concorrência indireta) | 145 | 89 | 66 | CNPJ |
| Cafeterias por 10 mil pessoas (residentes + empregos) | 0,8 | 6,2 | 0,7 | Derivada |
| Mercado café + lanches por cafeteria (R$/mês) | R$ 50.053 | R$ 15.726 | R$ 76.163 | Derivada |
| Mercado café + lanches por ponto de venda (R$/mês) | R$ 1.258 | R$ 2.919 | R$ 2.257 | Derivada |
| Mercado café + lanches por ponto de venda, versão Pesquisa OD (R$/mês) | R$ 2.355 | R$ 3.772 | R$ 3.266 | Derivada |
| Cafeterias abertas nos últimos 12 meses | 0 | 20 | 1 | CNPJ |
| Cafeterias abertas nos últimos 24 meses | 2 | 41 | 2 | CNPJ |
| Cafeterias fechadas nos últimos 24 meses | 3 | 34 | 3 | CNPJ |
| Saldo de cafeterias em 24 meses | -1 | 7 | 0 | CNPJ |
| Novas cafeterias em 24 meses / cafeterias ativas | 10,0% | 31,8% | 24,2% | CNPJ |

### Risco e custos

| Métrica | Itaquera | Pinheiros | Mediana dos 96 distritos | Fonte |
| --- | --- | --- | --- | --- |
| Sobrevivência em 3 anos (cafeterias + lanchonetes) | 61,6% | 71,1% | 65,0% | CNPJ |
| Amostra usada na sobrevivência em 3 anos | 948 | 856 | 470 | CNPJ |
| Empregados por lanchonete/cafeteria (mediana) | 3,5 | 5,0 | 3,0 | RAIS 2025 |
| Preço mediano do m² comercial (R$) | R$ 2.500 | R$ 10.600 | R$ 3.805 | ITBI 2026 |
| Transações comerciais usadas no m² | 7 | 47 | 11 | ITBI 2026 |

### Índice de oportunidade

| Métrica | Itaquera | Pinheiros | Mediana dos 96 distritos | Fonte |
| --- | --- | --- | --- | --- |
| Percentil do mercado por ponto de venda | 9,5% | 74,7% | 50,0% | Derivada |
| Percentil da sobrevivência em 3 anos | 14,9% | 88,3% | 50,0% | Derivada |
| Percentil da pressão de entrada | 20,0% | 67,8% | 50,0% | Derivada |
| Percentil do custo do m² | 12,5% | 94,4% | 50,0% | Derivada |
| **Índice de oportunidade (0 a 100)** | 37,0 | 57,9 | 53,5 | Derivada |
| **Posição no ranking (de 96 distritos)** | 74 | 34 | 48 | Derivada |
| Índice de oportunidade, versão Pesquisa OD (0 a 100) | 37,9 | 56,2 | 52,5 | Derivada |
| Posição no ranking, versão Pesquisa OD | 75 | 37 | 48 | Derivada |

## 2. Sobrevivência dos negócios

Coortes de CNPJs abertos desde 2012. Um negócio conta como fechado quando está baixado, inapto ou suspenso e a data dessa situação é anterior ao horizonte. Como a Receita demora a registrar baixas, as taxas tendem a ser **otimistas**.

| Recorte | Categoria | Anos após abertura | Negócios na amostra | Ainda ativos |
| --- | --- | --- | --- | --- |
| Cidade de São Paulo | Cafeterias | 1 | 3.863 | 89,6% |
| Cidade de São Paulo | Cafeterias | 2 | 3.580 | 77,4% |
| Cidade de São Paulo | Cafeterias | 3 | 3.266 | 66,3% |
| Cidade de São Paulo | Cafeterias | 5 | 2.673 | 51,1% |
| Cidade de São Paulo | Cafeterias + lanchonetes | 1 | 60.998 | 86,2% |
| Cidade de São Paulo | Cafeterias + lanchonetes | 2 | 55.895 | 77,6% |
| Cidade de São Paulo | Cafeterias + lanchonetes | 3 | 51.047 | 65,6% |
| Cidade de São Paulo | Cafeterias + lanchonetes | 5 | 41.754 | 49,1% |
| Itaquera | Cafeterias | 1 | 24 | 83,3% |
| Itaquera | Cafeterias | 2 | 22 | 68,2% |
| Itaquera | Cafeterias | 3 | 18 | 50,0% |
| Itaquera | Cafeterias | 5 | 14 | 42,9% |
| Itaquera | Cafeterias + lanchonetes | 1 | 1.152 | 83,3% |
| Itaquera | Cafeterias + lanchonetes | 2 | 1.047 | 74,4% |
| Itaquera | Cafeterias + lanchonetes | 3 | 948 | 61,6% |
| Itaquera | Cafeterias + lanchonetes | 5 | 745 | 46,2% |
| Pinheiros | Cafeterias | 1 | 215 | 94,0% |
| Pinheiros | Cafeterias | 2 | 194 | 79,4% |
| Pinheiros | Cafeterias | 3 | 179 | 71,5% |
| Pinheiros | Cafeterias | 5 | 137 | 53,3% |
| Pinheiros | Cafeterias + lanchonetes | 1 | 973 | 92,5% |
| Pinheiros | Cafeterias + lanchonetes | 2 | 912 | 80,7% |
| Pinheiros | Cafeterias + lanchonetes | 3 | 856 | 71,1% |
| Pinheiros | Cafeterias + lanchonetes | 5 | 709 | 54,0% |

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
| Mercado potencial café + lanches (R$/mês) | R$ 19.115 | R$ 53.196 | R$ 167.001 | Derivada |
| Mercado potencial café + lanches, fora de casa pela Pesquisa OD (R$/mês) | R$ 31.241 | R$ 75.881 | R$ 511.693 | Derivada |
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
| Mercado por ponto de venda (R$/mês) | R$ 1.593 | R$ 1.297 | R$ 1.256 | Derivada |
| Mercado por ponto de venda, versão Pesquisa OD (R$/mês) | R$ 2.603 | R$ 1.851 | R$ 3.847 | Derivada |

### Rua dos Pinheiros, 800 (Pinheiros)

| Métrica | Raio de 300 m | Raio de 500 m | Raio de 1000 m | Fonte |
| --- | --- | --- | --- | --- |
| População residente | 3.875 | 10.285 | 30.641 | Censo 2022 |
| Empregos formais | 4.893 | 27.812 | 81.455 | RAIS 2025 |
| Mercado potencial café + lanches (R$/mês) | R$ 100.702 | R$ 356.164 | R$ 1.064.226 | Derivada |
| Mercado potencial café + lanches, fora de casa pela Pesquisa OD (R$/mês) | R$ 134.778 | R$ 355.680 | R$ 1.221.348 | Derivada |
| Viagens diárias atraídas (exceto volta para casa) | 10.419 | 27.552 | 106.551 | Pesquisa OD 2023 |
| Viagens diárias atraídas por trabalho | 8.630 | 17.733 | 77.857 | Pesquisa OD 2023 |
| Viagens entrevistadas na amostra | 70 | 188 | 626 | Pesquisa OD 2023 |
| Estações de metrô e trem (por linha) | 1 | 1 | 2 | GeoSampa |
| Demanda média das estações em dias úteis | 19.619 | 19.619 | 54.753 | Metrô e Motiva, 12 meses |
| Cafeterias ativas | 8 | 17 | 67 | CNPJ |
| Lanchonetes ativas | 19 | 73 | 271 | CNPJ |
| Padarias ativas | 3 | 14 | 40 | CNPJ |
| Cafeterias abertas em 24 meses | 4 | 8 | 22 | CNPJ |
| Mercado por cafeteria (R$/mês) | R$ 12.588 | R$ 20.951 | R$ 15.884 | Derivada |
| Mercado por ponto de venda (R$/mês) | R$ 3.357 | R$ 3.425 | R$ 2.815 | Derivada |
| Mercado por ponto de venda, versão Pesquisa OD (R$/mês) | R$ 4.493 | R$ 3.420 | R$ 3.231 | Derivada |

## 6. Ranking do índice de oportunidade, versão RAIS (10 primeiros + distritos do piloto)

| Posição | Distrito | Índice | Mercado por ponto de venda (R$/mês) | Sobrevivência 3 anos | Cafeterias ativas | m² comercial (R$) |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Jaguaré | 76,3 | R$ 4.436 | 68,3% | 8 | R$ 2.650 |
| 2 | Morumbi | 74,7 | R$ 6.794 | 69,6% | 21 | R$ 11.522 |
| 3 | Campo Grande | 74,7 | R$ 3.500 | 68,5% | 19 | R$ 3.481 |
| 4 | Barra Funda | 74,3 | R$ 3.874 | 73,8% | 38 | R$ 5.688 |
| 5 | Butantã | 74,0 | R$ 4.014 | 70,0% | 24 | R$ 5.414 |
| 6 | Campo Belo | 71,3 | R$ 4.450 | 69,8% | 38 | R$ 5.525 |
| 7 | Raposo Tavares | 70,6 | R$ 2.377 | 65,8% | 4 | R$ 1.946 |
| 8 | Moema | 69,2 | R$ 5.507 | 73,6% | 79 | R$ 15.385 |
| 9 | Vila Mariana | 68,9 | R$ 4.286 | 69,9% | 91 | R$ 10.523 |
| 10 | Cambuci | 68,5 | R$ 2.994 | 68,0% | 16 | R$ 3.185 |
| 34 | Pinheiros | 57,9 | R$ 2.919 | 71,1% | 129 | R$ 10.600 |
| 74 | Itaquera | 37,0 | R$ 1.258 | 61,6% | 20 | R$ 2.500 |

## 7. Ranking com o mercado pela Pesquisa OD (comparação lado a lado)

As duas versões usam o mesmo índice e os mesmos pesos. Muda só a metade do mercado potencial atribuída ao consumo fora de casa:

- **RAIS (versão atual):** empregos formais do distrito × gasto médio por habitante da cidade.
- **Pesquisa OD:** o gasto fora de casa da cidade é distribuído entre os distritos na proporção das viagens atraídas em dia útil (trabalho, estudo, compras, serviços, lazer e refeição). Isso inclui trabalhadores informais, estudantes e clientes, e usa o endereço onde a pessoa realmente está, não a sede da empresa.

Na versão OD, a soma dos distritos é igual ao gasto total dos moradores da cidade (R$ 139,5 milhões/mês). Na versão RAIS, a soma fica em R$ 97,3 milhões, porque só entram os empregos formais. Por isso os valores absolutos da versão OD são maiores. Para comparar as duas versões, use a posição no ranking.

Correlação entre as posições nas duas versões: **0,94**. Em média, um distrito muda **6,7 posições**, e 8 dos 10 primeiros continuam no topo.

### 10 primeiros em qualquer das versões + distritos do piloto

| Distrito | Posição (RAIS) | Posição (OD) | Posições ganhas | Índice (RAIS) | Índice (OD) | Mercado por ponto de venda (RAIS) | Mercado por ponto de venda (OD) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Campo Grande | 3 | 1 | +2 | 74,7 | 77,2 | R$ 3.500 | R$ 4.657 |
| Butantã | 5 | 2 | +3 | 74,0 | 76,1 | R$ 4.014 | R$ 5.933 |
| Barra Funda | 4 | 3 | +1 | 74,3 | 76,0 | R$ 3.874 | R$ 5.425 |
| Morumbi | 2 | 4 | -2 | 74,7 | 74,7 | R$ 6.794 | R$ 8.448 |
| Liberdade | 12 | 5 | +7 | 67,6 | 71,9 | R$ 2.431 | R$ 3.776 |
| Vila Mariana | 9 | 6 | +3 | 68,9 | 70,2 | R$ 4.286 | R$ 6.063 |
| Campo Belo | 6 | 7 | -1 | 71,3 | 70,0 | R$ 4.450 | R$ 5.234 |
| Moema | 8 | 8 | +0 | 69,2 | 69,2 | R$ 5.507 | R$ 7.444 |
| Saúde | 11 | 9 | +2 | 67,7 | 68,1 | R$ 3.769 | R$ 4.593 |
| Raposo Tavares | 7 | 10 | -3 | 70,6 | 67,6 | R$ 2.377 | R$ 3.132 |
| Cambuci | 10 | 20 | -10 | 68,5 | 64,3 | R$ 2.994 | R$ 3.647 |
| Jaguaré | 1 | 27 | -26 | 76,3 | 60,7 | R$ 4.436 | R$ 3.344 |
| Pinheiros | 34 | 37 | -3 | 57,9 | 56,2 | R$ 2.919 | R$ 3.772 |
| Itaquera | 74 | 75 | -1 | 37,0 | 37,9 | R$ 1.258 | R$ 2.355 |

### 5 maiores subidas e 5 maiores quedas com a Pesquisa OD

| Distrito | Posição (RAIS) | Posição (OD) | Posições ganhas | Índice (RAIS) | Índice (OD) | Mercado por ponto de venda (RAIS) | Mercado por ponto de venda (OD) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Freguesia do Ó | 40 | 17 | +23 | 56,4 | 65,3 | R$ 2.124 | R$ 3.668 |
| Bela Vista | 35 | 14 | +21 | 57,8 | 65,8 | R$ 2.470 | R$ 4.205 |
| São Mateus | 62 | 42 | +20 | 44,9 | 54,6 | R$ 1.670 | R$ 3.275 |
| Vila Prudente | 36 | 18 | +18 | 57,8 | 65,0 | R$ 2.421 | R$ 4.025 |
| Penha | 67 | 52 | +15 | 42,0 | 51,7 | R$ 1.993 | R$ 3.590 |
| Sé | 15 | 45 | -30 | 67,0 | 53,5 | R$ 3.334 | R$ 3.037 |
| Jaguaré | 1 | 27 | -26 | 76,3 | 60,7 | R$ 4.436 | R$ 3.344 |
| Parque do Carmo | 31 | 51 | -20 | 59,4 | 51,8 | R$ 2.232 | R$ 2.713 |
| Vila Matilde | 54 | 74 | -20 | 49,3 | 37,9 | R$ 2.525 | R$ 2.897 |
| Marsilac | 60 | 79 | -19 | 45,6 | 35,5 | R$ 1.892 | R$ 2.377 |

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

- mercado por ponto de venda: 40%;
- sobrevivência em 3 anos: 25%;
- pressão de novas cafeterias: 15%, invertida;
- preço do m² comercial: 20%, invertido.

Distritos com menos de 30 negócios na amostra de sobrevivência ou com menos de 5 vendas comerciais no ITBI recebem percentil neutro (50%) nesse componente, para que amostras pequenas não distorçam o ranking. Os pesos são uma proposta inicial e devem ser calibrados.

## 9. Limitações conhecidas

- **Renda de 2010**: o Censo 2022 ainda não publicou a renda por setor. Bairros que mudaram muito de perfil desde 2010 ficam distorcidos.
- **A POF subestima o consumo fora de casa**: o café costuma ser registrado junto com o lanche e as despesas pequenas são subdeclaradas. Os valores absolutos de mercado ficam abaixo do faturamento real do setor. Por isso servem para **comparar regiões**, não para projetar receita.
- **Empregos pela sede**: a RAIS registra os vínculos no CEP do estabelecimento declarante. Sedes de grandes empresas concentram empregos que, na prática, estão espalhados pela cidade.
- **CNPJ ativo não significa operando**: há atraso nas baixas, então a concorrência e a sobrevivência ficam superestimadas.
- **Classificação por nome**: cafeterias sem "café" no nome entram como lanchonetes, e lanchonetes com "café" no nome entram como cafeterias.
- **ITBI com poucas transações** em distritos periféricos. A amostra aparece na ficha e medianas com menos de 10 transações devem ser lidas com cautela.
- **Parâmetro de 50% do consumo fora de casa**: é uma suposição, não uma medição. A Pesquisa OD mede onde o consumo fora de casa acontece, mas não quanto dele acontece fora de casa. O parâmetro vale nas duas versões do ranking.
- **Mercado OD nos raios pequenos**: nos raios de 300 m e 500 m a versão OD se apoia em poucas viagens entrevistadas e oscila muito entre raios. Nesses casos, prefira a versão RAIS ou o raio de 1.000 m.
- **Pesquisa OD é amostral**: nos raios de 300 m a amostra tem poucas dezenas de viagens entrevistadas. A linha "Viagens entrevistadas na amostra" mostra quantas, e valores com menos de 30 entrevistas devem ser lidos só como ordem de grandeza.
- **Demanda das estações incompleta**: a CPTM (linhas 7, 10, 11, 12 e 13) e a Linha 6-Laranja ainda não têm fonte integrada. Distritos atendidos por essas linhas, como Itaquera, ficam com a demanda subestimada. A linha "Estações sem dado de demanda" mostra quantas faltam.
- **Transferências contadas nas estações de integração**: a demanda publicada soma entradas e transferências, então quem troca de linha é contado de novo. Isso ainda é fluxo de pessoas passando pelo local, mas infla um pouco os polos de integração.

## 10. Próximos passos sugeridos

1. Validar a classificação de cafeterias com uma amostra manual (ex.: 50 CNPJs por distrito comparados com o Google Maps).
2. Decidir qual versão do mercado potencial (RAIS ou Pesquisa OD) passa a ser a oficial do índice, e incluir a demanda por estação da CPTM.
3. Incluir o valor venal do IPTU (cobertura total dos lotes) para complementar o ITBI nos distritos com poucas vendas.
4. Calibrar os pesos do índice contra a sobrevivência observada das cafeterias abertas entre 2019 e 2022.
5. Abrir a análise por endereço para qualquer ponto informado pelo cliente (o código já aceita novos endereços em `main.py`).
