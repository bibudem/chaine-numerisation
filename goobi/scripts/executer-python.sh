#!/bin/bash

# Script qui exécute un script Python en lui passant ses propres paramètres

# Vérifier qu'au moins un argument est fourni (le nom du script Python)
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 script-python.py [param1 param2 param3 ...]" >&2
    exit 1
fi

# Trouver le chemin du script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Récupérer le nom du script Python et supprimer le premier argument
SCRIPT_PYTHON="$SCRIPT_DIR/$1"
shift  # Supprime $1 et décale les autres paramètres

# Définir le chemin de l'environnement virtuel
VENV_DIR="$SCRIPT_DIR/.venv"

# Vérifier si l'environnement virtuel existe
if [ ! -d "$VENV_DIR" ]; then
    echo "L'environnement virtuel $VENV_DIR n'existe pas. Veuillez le créer." >&2
    exit 1
fi

# Vérifier si le fichier Python existe
if [ ! -f "$SCRIPT_PYTHON" ]; then
    echo "Le fichier $SCRIPT_PYTHON n'existe pas." >&2
    exit 1
fi

# Activer l'environnement virtuel
source "$VENV_DIR/bin/activate"

# Exécuter le script Python avec les paramètres et rediriger correctement stdout et stderr
exec python "$SCRIPT_PYTHON" "$@"
