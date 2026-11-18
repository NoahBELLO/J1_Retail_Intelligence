#!/usr/bin/env bash
# Lance le pipeline Raw -> Silver -> Gold du TP Jour 3, dans l'ordre, un notebook a la fois.
#
# Usage (depuis n'importe quel dossier) :
#   ./run_pipeline.sh              etapes 4 a 9 (nettoyage -> controles qualite)
#   ./run_pipeline.sh --formats    ajoute l'etape 8 (comparaison CSV / JSON / Parquet)
#
# Parametres : config/parametres.json. Journaux : outputs/logs/.
set -euo pipefail

RACINE="$(cd "$(dirname "$0")" && pwd)"
JUPYTER="$RACINE/../.venv/bin/jupyter"
PYTHON="$RACINE/../.venv/bin/python"
LOGS="$RACINE/outputs/logs"
HORODATAGE="$(date +%Y%m%d_%H%M%S)"
JOURNAL="$LOGS/pipeline_$HORODATAGE.log"
mkdir -p "$LOGS"

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') | pipeline | $*" | tee -a "$JOURNAL"; }

# Ordre d'execution : chaque notebook lit ce que le precedent a ecrit
NOTEBOOKS=(
  "transformations/cleaning/nettoyage_silver.ipynb"          # Raw -> Silver (+ rejets)
  "transformations/enrichment/enrichissement_ventes.ipynb"   # Silver -> silver/sales_enriched
  "transformations/aggregation/agregations_gold.ipynb"       # sales_enriched -> Gold
  "tests/controles_silver.ipynb"                             # controles techniques Silver
  "tests/controles_qualite.ipynb"                            # rapport de qualite Silver + Gold
)
[[ "${1:-}" == "--formats" ]] && NOTEBOOKS+=("notebooks/comparaison_formats.ipynb")

[[ -x "$JUPYTER" ]] || { log "ERREUR : $JUPYTER introuvable (environnement .venv de tp3_lolo)"; exit 1; }

# Parametres lus dans config/parametres.json
param() { "$PYTHON" -c "import json,os,sys; p=json.load(open('$RACINE/config/parametres.json')); v=p
for k in sys.argv[1].split('.'): v=v[k]
print(os.path.expanduser(str(v)))" "$1"; }

# Echantillon de store_sales : cree une seule fois, sans Spark (leger)
if [[ "$(param echantillon.actif)" == "True" ]]; then
  ECHANTILLON="$RACINE/$(param chemins.echantillon_ventes)"
  if [[ ! -f "$ECHANTILLON" ]]; then
    MODULO="$(param echantillon.modulo_ticket)"
    SOURCE_VENTES="$(param chemins.source_tpcxbb)/store_sales/store_sales.dat"
    log "creation de l'echantillon (tickets multiples de $MODULO) depuis $SOURCE_VENTES"
    mkdir -p "$(dirname "$ECHANTILLON")"
    awk -F'|' -v m="$MODULO" '$10 % m == 0' "$SOURCE_VENTES" > "$ECHANTILLON"
  fi
  log "echantillon : $ECHANTILLON ($(wc -l < "$ECHANTILLON") lignes)"
else
  log "echantillon desactive : store_sales complet"
fi

log "debut : ${#NOTEBOOKS[@]} notebook(s)"
for NB in "${NOTEBOOKS[@]}"; do
  NOM="$(basename "$NB" .ipynb)"
  DEBUT=$SECONDS
  log "-> $NB"
  # Execution sur place : le notebook garde ses sorties (preuves). nice : laisse la main au reste du PC
  if (cd "$RACINE/$(dirname "$NB")" && nice -n 10 "$JUPYTER" nbconvert --to notebook --execute --inplace \
        --ExecutePreprocessor.timeout=1800 "$(basename "$NB")") > "$LOGS/${NOM}_$HORODATAGE.out" 2>&1; then
    log "   OK ($((SECONDS - DEBUT)) s)"
  else
    log "   ECHEC ($((SECONDS - DEBUT)) s) : voir $LOGS/${NOM}_$HORODATAGE.out"
    exit 1
  fi
done
log "fin : pipeline termine. Resultats dans data/silver, data/gold et outputs/"
