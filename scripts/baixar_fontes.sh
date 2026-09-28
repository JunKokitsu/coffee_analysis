#!/bin/bash
set -euo pipefail

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
BRUTO="$RAIZ/data/raw"
MES_CNPJ="${MES_CNPJ:-2026-09}"
COMPETENCIA="${COMPETENCIA:-$(date +%Y-%m)}"
TOKEN_RECEITA="gn672Ad4CF8N6TK"
ENDERECO_RECEITA="https://arquivos.receitafederal.gov.br/public.php/webdav/Dados/Cadastros/CNPJ/$MES_CNPJ"
TAMANHO_PARTE=67108864

baixar() {
    local destino="$1" endereco="$2"
    [ -s "$destino" ] && return 0
    mkdir -p "$(dirname "$destino")"
    curl -s -f -L --retry 5 -A "Mozilla/5.0" -o "$destino" "$endereco"
}

tamanho_remoto_receita() {
    curl -s -u "$TOKEN_RECEITA:" -X PROPFIND -H "Depth: 0" "$ENDERECO_RECEITA/$1" \
        | grep -oE '<d:getcontentlength>[0-9]+' | grep -oE '[0-9]+'
}

baixar_parte_receita() {
    local arquivo="$1" inicio="$2" fim="$3"
    local parte="$BRUTO/cnpj/partes/$arquivo.$(printf %012d "$inicio")"
    local esperado=$((fim - inicio + 1))
    for _ in $(seq 1 400); do
        local obtido
        obtido=$(stat -c %s "$parte" 2>/dev/null || echo 0)
        [ "$obtido" -ge "$esperado" ] && return 0
        curl -s -u "$TOKEN_RECEITA:" --speed-limit 100000 --speed-time 20 --connect-timeout 20 --max-time 900 \
            -r $((inicio + obtido))-"$fim" "$ENDERECO_RECEITA/$arquivo" >> "$parte" || true
    done
    return 1
}

baixar_arquivo_receita() {
    local arquivo="$1"
    [ -s "$BRUTO/cnpj/$arquivo" ] && return 0
    mkdir -p "$BRUTO/cnpj/partes"
    local total
    total=$(tamanho_remoto_receita "$arquivo")
    for ((inicio = 0; inicio < total; inicio += TAMANHO_PARTE)); do
        local fim=$((inicio + TAMANHO_PARTE - 1))
        [ "$fim" -ge "$total" ] && fim=$((total - 1))
        baixar_parte_receita "$arquivo" "$inicio" "$fim"
    done
    cat "$BRUTO/cnpj/partes/$arquivo".* > "$BRUTO/cnpj/$arquivo"
    rm -f "$BRUTO/cnpj/partes/$arquivo".*
}

for numero in 0 1 2 3 4 5 6 7 8 9; do
    baixar_arquivo_receita "Estabelecimentos$numero.zip"
    baixar_arquivo_receita "Empresas$numero.zip"
done

IBGE_SETORES="https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios"
IBGE_CNEFE="https://ftp.ibge.gov.br/Cadastro_Nacional_de_Enderecos_para_Fins_Estatisticos/Censo_Demografico_2022/Arquivos_CNEFE"
IBGE_2010="https://ftp.ibge.gov.br/Censos/Censo_Demografico_2010/Resultados_do_Universo/Agregados_por_Setores_Censitarios"
baixar "$BRUTO/ibge/SP_setores_CD2022.gpkg" "$IBGE_SETORES/malha_com_atributos/setores/gpkg/UF/SP/SP_setores_CD2022.gpkg"
baixar "$BRUTO/ibge/SP_distritos_CD2022.gpkg" "$IBGE_SETORES/malha_com_atributos/distritos/gpkg/UF/SP/SP_distritos_CD2022.gpkg"
baixar "$BRUTO/ibge/3550308_SAO_PAULO.zip" "$IBGE_CNEFE/CSV/Municipio/35_SP/3550308_SAO_PAULO.zip"
baixar "$BRUTO/ibge/SP_Capital_20260615.zip" "$IBGE_2010/SP_Capital_20260615.zip"
unzip -o -q "$BRUTO/ibge/3550308_SAO_PAULO.zip" -d "$BRUTO/ibge/"
unzip -o -j -q "$BRUTO/ibge/SP_Capital_20260615.zip" "*/CSV/Basico_SP1.csv" "*/CSV/DomicilioRenda_SP1.csv" -d "$BRUTO/ibge/"

PDET_RAIS="ftp://ftp.mtps.gov.br/pdet/microdados/RAIS/2025"
baixar "$BRUTO/rais/RAIS_ESTAB_PUB.7z" "$PDET_RAIS/RAIS_ESTAB_PUB.7z"
baixar "$BRUTO/rais/RAIS_VINC_PUB_SP.7z" "$PDET_RAIS/RAIS_VINC_PUB_SP.7z"
(cd "$BRUTO/rais" && 7z e -y RAIS_ESTAB_PUB.7z > /dev/null && 7z e -y RAIS_VINC_PUB_SP.7z > /dev/null)

baixar "$BRUTO/itbi/guias_itbi_2026.xlsx" "https://prefeitura.sp.gov.br/documents/d/fazenda/guias-de-itbi-pagas-27082026-xls-xlsx"

PESQUISA_OD="$BRUTO/pesquisa_od/2023"
baixar "$PESQUISA_OD/Site_190225_PesquisaOD2023.zip" "https://transparencia.metrosp.com.br/sites/default/files/Site_190225_PesquisaOD2023.zip"
unzip -o -q "$PESQUISA_OD/Site_190225_PesquisaOD2023.zip" -d "$PESQUISA_OD/"

METRO_TRANSPARENCIA="https://transparencia.metrosp.com.br"

endereco_demanda_metro() {
    local ano="$1"
    curl -s -A "Mozilla/5.0" "$METRO_TRANSPARENCIA/dataset/demanda" \
        | grep -oE "/dataset/demanda/resource/[a-f0-9-]+\"[^>]*title=\"Demanda de Passageiros por Estação - Média Dias Úteis - $ano\"" \
        | grep -oE '/dataset/demanda/resource/[a-f0-9-]+' \
        | while read -r recurso; do
            curl -s -A "Mozilla/5.0" "$METRO_TRANSPARENCIA$recurso" | grep -oE "$METRO_TRANSPARENCIA/sites/default/files/[^\"]+\.csv" || true
        done \
        | head -1
}

ANO_COMPETENCIA="${COMPETENCIA%-*}"
for ano in $((ANO_COMPETENCIA - 1)) "$ANO_COMPETENCIA"; do
    baixar "$BRUTO/metro/$COMPETENCIA/demanda_estacoes_$ano.csv" "$(endereco_demanda_metro "$ano")"
done

MOTIVA="https://trilhos.motiva.com.br"

baixar_demanda_motiva() {
    local pagina="$1" pasta="$2"
    curl -s -L -A "Mozilla/5.0" "$MOTIVA/$pagina/historico-de-pessoas-transportadas/" \
        | grep -oE '/content/dam/[^"]*/entrada-de-passageiros-por-estacao/[^"]*\.pdf' \
        | sort -u \
        | while read -r caminho; do
            baixar "$BRUTO/motiva/$COMPETENCIA/$pasta/$(basename "$caminho")" "$MOTIVA$caminho"
        done
}

baixar_demanda_motiva "linha-4-amarela" "linha-4"
baixar_demanda_motiva "linha-5-lilas" "linha-5"
baixar_demanda_motiva "viamobilidade8e9" "linha-8-e-9"

GEOSAMPA_WFS="https://wfs.geosampa.prefeitura.sp.gov.br/geoserver/ows?service=WFS&version=2.0.0&request=GetFeature&outputFormat=application/json&srsName=EPSG:4326"
for camada in estacao_metro estacao_trem; do
    baixar "$BRUTO/geosampa/$COMPETENCIA/$camada.json" "$GEOSAMPA_WFS&typeNames=geoportal:$camada"
done
