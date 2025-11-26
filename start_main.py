#!/usr/bin/env python3
"""
Iniciador para la interfaz principal de detección en tiempo real
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.interfaces.main import main

if __name__ == "__main__":
    main()
