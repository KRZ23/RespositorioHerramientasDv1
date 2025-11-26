#!/usr/bin/env python3
"""
Iniciador para la interfaz simplificada de detección
"""
import sys
import os
import tkinter as tk

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.interfaces.simple_interface import SimpleTranslatorInterface

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleTranslatorInterface(root)
    root.mainloop()
