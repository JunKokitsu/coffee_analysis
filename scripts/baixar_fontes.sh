#!/bin/bash
set -euo pipefail

RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
BRUTO="$RAIZ/data/raw"
COMPETENCIA="${COMPETENCIA:-$(date +%Y-%m)}"
TOKEN_RECEITA="gn672Ad4CF8N6TK"
RECEITA_CNPJ="https://arquivos.receitafederal.gov.br/public.php/webdav/Dados/Cadastros/CNPJ"
TAMANHO_PARTE=67108864
FONTES_DISPONIVEIS=(cnpj ibge rais itbi pesquisa_od metro motiva geosampa)
DESCOMPACTADOR_7Z="$(command -v 7z || command -v 7zz || true)"

baixar() {
    local destino="$1" endereco="$2"
    [ -s "$destino" ] && return 0
    mkdir -p "$(dirname "$destino")"
    curl -s -f -L --retry 5 -A "Mozilla/5.0" -o "$destino" "$endereco"
}

ultimo_mes_cnpj() {
    curl -s -u "$TOKEN_RECEITA:" -X PROPFIND -H "Depth: 1" "$RECEITA_CNPJ/" \
        | grep -oE '/CNPJ/[0-9]{4}-[0-9]{2}/' \
        | grep -oE '[0-9]{4}-[0-9]{2}' \
        | awk -v limite="$COMPETENCIA" '$0 <= limite' \
        | sort | tail -1
}

tamanho_remoto_receita() {
    local mes="$1" arquivo="$2"
    curl -s -u "$TOKEN_RECEITA:" -X PROPFIND -H "Depth: 0" "$RECEITA_CNPJ/$mes/$arquivo" \
        | grep -oE '<d:getcontentlength>[0-9]+' | grep -oE '[0-9]+'
}

baixar_parte_receita() {
    local mes="$1" arquivo="$2" inicio="$3" fim="$4"
    local parte="$BRUTO/cnpj/$mes/partes/$arquivo.$(printf %012d "$inicio")"
    local esperado=$((fim - inicio + 1))
    for _ in $(seq 1 400); do
        local obtido
        obtido=$(stat -c %s "$parte" 2>/dev/null || echo 0)
        [ "$obtido" -ge "$esperado" ] && return 0
        curl -s -u "$TOKEN_RECEITA:" --speed-limit 100000 --speed-time 20 --connect-timeout 20 --max-time 900 \
            -r $((inicio + obtido))-"$fim" "$RECEITA_CNPJ/$mes/$arquivo" >> "$parte" || true
    done
    return 1
}

baixar_arquivo_receita() {
    local mes="$1" arquivo="$2"
    local destino="$BRUTO/cnpj/$mes/$arquivo"
    [ -s "$destino" ] && return 0
    mkdir -p "$BRUTO/cnpj/$mes/partes"
    local total
    total=$(tamanho_remoto_receita "$mes" "$arquivo")
    for ((inicio = 0; inicio < total; inicio += TAMANHO_PARTE)); do
        local fim=$((inicio + TAMANHO_PARTE - 1))
        [ "$fim" -ge "$total" ] && fim=$((total - 1))
        baixar_parte_receita "$mes" "$arquivo" "$inicio" "$fim"
    done
    cat "$BRUTO/cnpj/$mes/partes/$arquivo".* > "$destino"
    rm -f "$BRUTO/cnpj/$mes/partes/$arquivo".*
}

baixar_cnpj() {
    local mes
    mes="${MES_CNPJ:-$(ultimo_mes_cnpj)}"
    [ -n "$mes" ] || { echo "nenhuma publicação do CNPJ até $COMPETENCIA" >&2; return 1; }
    echo "CNPJ: publicação $mes"
    for numero in 0 1 2 3 4 5 6 7 8 9; do
        baixar_arquivo_receita "$mes" "Estabelecimentos$numero.zip"
        baixar_arquivo_receita "$mes" "Empresas$numero.zip"
    done
}

baixar_ibge() {
    local setores="https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios"
    local cnefe="https://ftp.ibge.gov.br/Cadastro_Nacional_de_Enderecos_para_Fins_Estatisticos/Censo_Demografico_2022/Arquivos_CNEFE"
    local censo_2010="https://ftp.ibge.gov.br/Censos/Censo_Demografico_2010/Resultados_do_Universo/Agregados_por_Setores_Censitarios"
    baixar "$BRUTO/ibge/SP_setores_CD2022.gpkg" "$setores/malha_com_atributos/setores/gpkg/UF/SP/SP_setores_CD2022.gpkg"
    baixar "$BRUTO/ibge/SP_distritos_CD2022.gpkg" "$setores/malha_com_atributos/distritos/gpkg/UF/SP/SP_distritos_CD2022.gpkg"
    baixar "$BRUTO/ibge/3550308_SAO_PAULO.zip" "$cnefe/CSV/Municipio/35_SP/3550308_SAO_PAULO.zip"
    baixar "$BRUTO/ibge/SP_Capital_20260615.zip" "$censo_2010/SP_Capital_20260615.zip"
    [ -s "$BRUTO/ibge/3550308_SAO_PAULO.csv" ] || unzip -o -q "$BRUTO/ibge/3550308_SAO_PAULO.zip" -d "$BRUTO/ibge/"
    [ -s "$BRUTO/ibge/Basico_SP1.csv" ] || unzip -o -j -q "$BRUTO/ibge/SP_Capital_20260615.zip" "*/CSV/Basico_SP1.csv" "*/CSV/DomicilioRenda_SP1.csv" -d "$BRUTO/ibge/"
}

ultimo_ano_rais() {
    curl -s --max-time 120 --list-only "ftp://ftp.mtps.gov.br/pdet/microdados/RAIS/" \
        | tr -d '\r' | grep -E '^[0-9]{4}$' | sort | tail -1
}

baixar_rais() {
    local ano
    ano="${ANO_RAIS:-$(ultimo_ano_rais)}"
    echo "RAIS: ano-base $ano"
    local pasta="$BRUTO/rais/$ano"
    baixar "$pasta/RAIS_ESTAB_PUB.7z" "ftp://ftp.mtps.gov.br/pdet/microdados/RAIS/$ano/RAIS_ESTAB_PUB.7z"
    baixar "$pasta/RAIS_VINC_PUB_SP.7z" "ftp://ftp.mtps.gov.br/pdet/microdados/RAIS/$ano/RAIS_VINC_PUB_SP.7z"
    [ -s "$pasta/RAIS_ESTAB_PUB.COMT" ] || (cd "$pasta" && "$DESCOMPACTADOR_7Z" e -y RAIS_ESTAB_PUB.7z > /dev/null)
    [ -s "$pasta/RAIS_VINC_PUB_SP.COMT" ] || (cd "$pasta" && "$DESCOMPACTADOR_7Z" e -y RAIS_VINC_PUB_SP.7z > /dev/null)
}

ultimo_arquivo_itbi() {
    curl -s -L -A "Mozilla/5.0" --max-time 120 "https://prefeitura.sp.gov.br/web/fazenda/w/acesso_a_informacao/31501" \
        | grep -oE 'guias-de-itbi-pagas-[0-9]{8}-xls-xlsx' \
        | sort -u \
        | awk '{ data = substr($0, 21, 8); print substr(data, 5, 4) substr(data, 3, 2) substr(data, 1, 2), $0 }' \
        | sort | tail -1 | cut -d' ' -f2
}

baixar_itbi() {
    local arquivo
    arquivo="$(ultimo_arquivo_itbi)"
    [ -n "$arquivo" ] || { echo "arquivo do ITBI não encontrado na página da Prefeitura" >&2; return 1; }
    local data="${arquivo:20:8}"
    local publicacao="${data:4:4}-${data:2:2}-${data:0:2}"
    echo "ITBI: publicação $publicacao"
    baixar "$BRUTO/itbi/$publicacao/guias_itbi.xlsx" "https://prefeitura.sp.gov.br/documents/d/fazenda/$arquivo"
}

baixar_pesquisa_od() {
    local pasta="$BRUTO/pesquisa_od/2023"
    baixar "$pasta/Site_190225_PesquisaOD2023.zip" "https://transparencia.metrosp.com.br/sites/default/files/Site_190225_PesquisaOD2023.zip"
    [ -d "$pasta/Site_190225" ] || unzip -o -q "$pasta/Site_190225_PesquisaOD2023.zip" -d "$pasta/"
}

endereco_demanda_metro() {
    local ano="$1" transparencia="https://transparencia.metrosp.com.br"
    curl -s -A "Mozilla/5.0" "$transparencia/dataset/demanda" \
        | grep -oE "/dataset/demanda/resource/[a-f0-9-]+\"[^>]*title=\"Demanda de Passageiros por Estação - Média Dias Úteis - $ano\"" \
        | grep -oE '/dataset/demanda/resource/[a-f0-9-]+' \
        | while read -r recurso; do
            curl -s -A "Mozilla/5.0" "$transparencia$recurso" | grep -oE "$transparencia/sites/default/files/[^\"]+\.csv" || true
        done \
        | head -1
}

baixar_metro() {
    local ano_competencia="${COMPETENCIA%-*}"
    for ano in $((ano_competencia - 1)) "$ano_competencia"; do
        baixar "$BRUTO/metro/$COMPETENCIA/demanda_estacoes_$ano.csv" "$(endereco_demanda_metro "$ano")"
    done
}

baixar_demanda_motiva() {
    local pagina="$1" pasta="$2" motiva="https://trilhos.motiva.com.br"
    curl -s -L -A "Mozilla/5.0" "$motiva/$pagina/historico-de-pessoas-transportadas/" \
        | grep -oE '/content/dam/[^"]*/entrada-de-passageiros-por-estacao/[^"]*\.pdf' \
        | sort -u \
        | while read -r caminho; do
            baixar "$BRUTO/motiva/$COMPETENCIA/$pasta/$(basename "$caminho")" "$motiva$caminho"
        done
}

baixar_motiva() {
    baixar_demanda_motiva "linha-4-amarela" "linha-4"
    baixar_demanda_motiva "linha-5-lilas" "linha-5"
    baixar_demanda_motiva "viamobilidade8e9" "linha-8-e-9"
}

baixar_geosampa() {
    local wfs="https://wfs.geosampa.prefeitura.sp.gov.br/geoserver/ows?service=WFS&version=2.0.0&request=GetFeature&outputFormat=application/json&srsName=EPSG:4326"
    for camada in estacao_metro estacao_trem; do
        baixar "$BRUTO/geosampa/$COMPETENCIA/$camada.json" "$wfs&typeNames=geoportal:$camada"
    done
}

fontes=("$@")
[ ${#fontes[@]} -gt 0 ] || fontes=("${FONTES_DISPONIVEIS[@]}")
for fonte in "${fontes[@]}"; do
    [[ " ${FONTES_DISPONIVEIS[*]} " == *" $fonte "* ]] || { echo "fonte desconhecida: $fonte" >&2; exit 2; }
    echo "baixando $fonte (competência $COMPETENCIA)"
    "baixar_$fonte"
done
