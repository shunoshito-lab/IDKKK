#!/usr/bin/env bash
# Pacchettizza la Home e, se passi il nome del device, la installa e la avvia.
#   ./build.sh                 -> crea solo dist/com.shun.launcher_*.ipk
#   ./build.sh tv              -> pacchetto + install + launch sul device "tv"
set -euo pipefail
cd "$(dirname "$0")"
rm -f dist/*.ipk; mkdir -p dist
ares-package launcher -o dist
IPK=$(ls -t dist/*.ipk | head -1)
echo "pacchetto: $IPK"
if [ $# -ge 1 ]; then
  ares-install --device "$1" "$IPK"
  ares-launch  --device "$1" com.shun.launcher
  echo "avviata su '$1'. Log in tempo reale:  ares-inspect --device $1 --app com.shun.launcher"
fi
