#!/bin/bash
# Script para iniciar el traductor texto → señas 3D

# Cambiar al directorio del proyecto
cd "$(dirname "$0")/.." || exit

# Activar entorno virtual
source venv_translator/bin/activate

# Ejecutar la interfaz
python -m src.interfaces.text_to_sign_interface
