#!/usr/bin/env python3
"""
Script para pre-generar audio de todas las señas
Ejecutar una vez para tener todo en caché
"""

import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.smart_tts import SmartTTS, pregenerate_all_signs
import json


def main():
    print("\n" + "="*70)
    print("🎙️ PRE-GENERACIÓN DE AUDIO PARA TRADUCTOR DE SEÑAS")
    print("="*70 + "\n")
    
    # Seleccionar motor
    print("Motores TTS disponibles:")
    print("1) edge-tts   - Microsoft Edge TTS (Recomendado)")
    print("2) gtts       - Google TTS (Simple)")
    print("3) pyttsx3    - TTS Offline")
    print("4) coqui      - Coqui TTS (IA Local)")
    print("5) elevenlabs - ElevenLabs (Premium)")
    
    choice = input("\nSelecciona motor [1]: ").strip() or "1"
    
    engines = {
        "1": "edge-tts",
        "2": "gtts",
        "3": "pyttsx3",
        "4": "coqui",
        "5": "elevenlabs"
    }
    
    engine = engines.get(choice, "edge-tts")
    
    print(f"\n✅ Motor seleccionado: {engine}")
    
    # Dataset path
    dataset_path = "data/signs_dataset.json"
    
    if not os.path.exists(dataset_path):
        print(f"❌ No se encuentra el dataset: {dataset_path}")
        return
    
    # Pre-generar todo
    pregenerate_all_signs(dataset_path, engine)
    
    # Mostrar estadísticas
    print("\n" + "="*70)
    print("📊 ESTADÍSTICAS")
    print("="*70)
    
    audio_cache_dir = "audio_cache"
    if os.path.exists(audio_cache_dir):
        files = [f for f in os.listdir(audio_cache_dir) if f.endswith('.mp3')]
        total_size = sum(os.path.getsize(os.path.join(audio_cache_dir, f)) for f in files)
        
        print(f"📁 Archivos generados: {len(files)}")
        print(f"💾 Tamaño total: {total_size / 1024 / 1024:.2f} MB")
        print(f"📍 Ubicación: {os.path.abspath(audio_cache_dir)}")
    
    print("\n✅ ¡Listo! Ahora las traducciones serán instantáneas sin entrecortes")


if __name__ == "__main__":
    main()
