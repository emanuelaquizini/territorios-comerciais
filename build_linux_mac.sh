#!/bin/sh
# Gera o executável ContatosTerritorio em dist/ContatosTerritorio/
set -e
cd "$(dirname "$0")"

python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller

DEST=dist/ContatosTerritorio
rm -rf "$DEST"
pyinstaller --noconfirm --clean --onefile --console --name ContatosTerritorio \
  --distpath "$DEST" executar.py

mkdir -p "$DEST/dados"
cp config.json "$DEST/"
cp dados/territorios_exemplo.geojson dados/territorios.geojson dados/bloqueio.csv \
   dados/amostra_osm_ficticia.json "$DEST/dados/"
cp docs/GUIA_DO_VOLUNTARIO.md "$DEST/"

echo "Pronto! Executável em $DEST"
