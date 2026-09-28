from datetime import date


class ReportTexts:
    def header(self, reference_date: date) -> str:
        return f"""# Piloto: métricas para abertura de cafeterias em São Paulo

Data de referência: {reference_date.strftime("%d/%m/%Y")}. Recorte: distritos de **Pinheiros** (alta renda, polo de empregos) e **Itaquera** (Zona Leste, residencial e populoso), comparados com a mediana dos 96 distritos da capital.

Todos os valores foram gerados pelo pipeline em `main.py` a partir das fontes públicas listadas na seção de metodologia. Os valores de mercado são **potenciais**, não previsão de faturamento."""

    def findings(self) -> str:
        return """## Principais achados (leitura do piloto em 23/09/2026)

1. **Pinheiros tem o dobro de mercado, mas quase 8 vezes mais cafeterias por pessoa.** O mercado potencial de café + lanches é de cerca de R$ 2,0 milhões/mês, contra R$ 1,0 milhão em Itaquera. Porém são 129 cafeterias ativas (6,2 por 10 mil pessoas) contra 20 (0,8). O mercado por cafeteria cai para cerca de R$ 16 mil/mês, contra R$ 50 mil em Itaquera.
2. **Somando lanchonetes e padarias, Itaquera é mais disputada.** Os 796 pontos de venda de café de Itaquera deixam R$ 1,3 mil/mês por ponto, o 10º percentil mais baixo da cidade. Pinheiros tem R$ 2,9 mil. A falta de cafeterias em Itaquera é uma oportunidade de diferenciação, não de mercado vazio.
3. **Pinheiros tem alta rotatividade.** Em 24 meses abriram 41 cafeterias e fecharam 34. Ainda assim, a sobrevivência em 3 anos (71%) está acima da mediana da cidade (65%). Itaquera fica abaixo (62%) e teve saldo negativo de cafeterias.
4. **O ponto custa 4 vezes mais em Pinheiros**: R$ 10,6 mil/m² contra R$ 2,5 mil em Itaquera. O valor de Itaquera vem de apenas 7 vendas e deve ser lido com cautela.
5. **Os endereços-exemplo mostram perfis opostos.** Num raio de 500 m:
   - **Rua dos Pinheiros, 800:** 17 cafeterias, 8 abertas nos últimos 24 meses, e 27,8 mil empregos formais. O fluxo de trabalho é alto e a saturação também.
   - **Av. Campanella, 1000:** nenhuma cafeteria e 41 lanchonetes/padarias. É uma demanda de bairro, sensível a preço.
6. **A margem do insumo está favorável.** Em 12 meses o arábica caiu 29% e o café moído caiu 19% no IPCA, enquanto o cafezinho subiu 7%.
7. **No ranking, nenhum dos dois distritos está no topo.** Pinheiros ficou em 34º e Itaquera em 74º. Os primeiros colocados combinam mercado por ponto de venda acima da média, boa sobrevivência e m² moderado: Jaguaré, Morumbi, Campo Grande, Barra Funda e Butantã.
8. **A Pesquisa OD confirma Pinheiros como polo de destino** (incluído em 28/09/2026). O distrito atrai 239 mil viagens por dia útil, ou 3,7 por morador, sendo 167 mil a trabalho. Suas estações somam 324 mil passageiros por dia. Itaquera atrai 173 mil viagens, 0,8 por morador, igual à mediana, com mais peso de compras e serviços (26 mil contra 20 mil em Pinheiros). No raio de 500 m, a Rua dos Pinheiros recebe 27,6 mil viagens por dia, contra 4,4 mil na Av. Campanella."""

    def district_note(self) -> str:
        return """"Mercado potencial" é o gasto mensal estimado das pessoas da região com café e lanches fora de casa. Ele combina o gasto por faixa de renda da POF com a renda domiciliar de cada setor censitário, a quantidade de domicílios em 2022 e os empregos formais do distrito, corrigido pelo IPCA do cafezinho e do lanche. A metade do consumo é atribuída ao local de moradia e a outra metade ao local de trabalho."""

    def survival_note(self) -> str:
        return """Coortes de CNPJs abertos desde 2012. Um negócio conta como fechado quando está baixado, inapto ou suspenso e a data dessa situação é anterior ao horizonte. Como a Receita demora a registrar baixas, as taxas tendem a ser **otimistas**."""

    def price_note(self) -> str:
        return """Quando o grão cai e o cafezinho sobe, o custo do insumo principal alivia enquanto o preço de venda continua subindo. É uma janela favorável de margem para quem abre agora, mas o preço do grão é volátil e pode inverter rápido."""

    def influence_area_note(self) -> str:
        return """Cálculo por raio em torno do endereço. A população vem da área de cada setor censitário que cai dentro do círculo. Cafeterias e empregos são contados pelo endereço ou, na falta dele, pelo centro do CEP. Viagens atraídas vêm dos destinos entrevistados na Pesquisa OD 2023, e estações são as que ficam dentro do raio."""

    def methodology(self) -> str:
        return """## 7. Metodologia e fontes

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

Distritos com menos de 30 negócios na amostra de sobrevivência ou com menos de 5 vendas comerciais no ITBI recebem percentil neutro (50%) nesse componente, para que amostras pequenas não distorçam o ranking. Os pesos são uma proposta inicial e devem ser calibrados."""

    def limitations(self) -> str:
        return """## 8. Limitações conhecidas

- **Renda de 2010**: o Censo 2022 ainda não publicou a renda por setor. Bairros que mudaram muito de perfil desde 2010 ficam distorcidos.
- **A POF subestima o consumo fora de casa**: o café costuma ser registrado junto com o lanche e as despesas pequenas são subdeclaradas. Os valores absolutos de mercado ficam abaixo do faturamento real do setor. Por isso servem para **comparar regiões**, não para projetar receita.
- **Empregos pela sede**: a RAIS registra os vínculos no CEP do estabelecimento declarante. Sedes de grandes empresas concentram empregos que, na prática, estão espalhados pela cidade.
- **CNPJ ativo não significa operando**: há atraso nas baixas, então a concorrência e a sobrevivência ficam superestimadas.
- **Classificação por nome**: cafeterias sem "café" no nome entram como lanchonetes, e lanchonetes com "café" no nome entram como cafeterias.
- **ITBI com poucas transações** em distritos periféricos. A amostra aparece na ficha e medianas com menos de 10 transações devem ser lidas com cautela.
- **Parâmetro de 50% do consumo no trabalho**: é uma suposição, não uma medição. A Pesquisa Origem-Destino já está integrada, mas ainda não substitui esse parâmetro no mercado potencial.
- **Pesquisa OD é amostral**: nos raios de 300 m a amostra tem poucas dezenas de viagens entrevistadas. A linha "Viagens entrevistadas na amostra" mostra quantas, e valores com menos de 30 entrevistas devem ser lidos só como ordem de grandeza.
- **Demanda das estações incompleta**: a CPTM (linhas 7, 10, 11, 12 e 13) e a Linha 6-Laranja ainda não têm fonte integrada. Distritos atendidos por essas linhas, como Itaquera, ficam com a demanda subestimada. A linha "Estações sem dado de demanda" mostra quantas faltam.
- **Transferências contadas nas estações de integração**: a demanda publicada soma entradas e transferências, então quem troca de linha é contado de novo. Isso ainda é fluxo de pessoas passando pelo local, mas infla um pouco os polos de integração."""

    def next_steps(self) -> str:
        return """## 9. Próximos passos sugeridos

1. Validar a classificação de cafeterias com uma amostra manual (ex.: 50 CNPJs por distrito comparados com o Google Maps).
2. Usar as viagens atraídas da Pesquisa Origem-Destino no lugar da proxy de empregos formais no mercado potencial, e incluir a demanda por estação da CPTM.
3. Incluir o valor venal do IPTU (cobertura total dos lotes) para complementar o ITBI nos distritos com poucas vendas.
4. Calibrar os pesos do índice contra a sobrevivência observada das cafeterias abertas entre 2019 e 2022.
5. Abrir a análise por endereço para qualquer ponto informado pelo cliente (o código já aceita novos endereços em `main.py`)."""
