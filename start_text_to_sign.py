#!/usr/bin/env python3
"""
Iniciador para la interfaz de traducción Texto → Señas 3D
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.interfaces.text_to_sign_interface import TextToSignTranslator

if __name__ == "__main__":
    app = TextToSignTranslator()
    app.mainloop()
