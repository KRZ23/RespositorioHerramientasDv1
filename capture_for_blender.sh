#!/bin/bash
# Script de captura de señas para Blender
# Uso: ./capture_for_blender.sh

cd "$(dirname "$0")"

# Activar entorno virtual
source venv_translator/bin/activate

# Ejecutar script de captura
python scripts/capture_sign_for_blender.py

# Desactivar entorno
deactivate
