#!/usr/bin/env python3
"""
Test del sistema SmartTTS (Sistema de caché para TTS sin entrecortes)
"""

import sys
import os
import time
import tempfile

# Agregar src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("\n" + "="*70)
print("🧪 TEST DEL SISTEMA SMARTTTS")
print("="*70 + "\n")

# Test básico de gTTS (fallback)
print("📝 Test 1: gTTS + pygame (sistema base)")
try:
    from gtts import gTTS
    from pygame import mixer
    
    mixer.init()
    print("✅ gTTS y pygame disponibles")
    
    # Test rápido
    text = "Prueba"
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
        temp_file = fp.name
    
    tts = gTTS(text=text, lang='es', slow=False)
    tts.save(temp_file)
    os.unlink(temp_file)
    print("✅ Generación de audio funcional")
except Exception as e:
    print(f"❌ Error con gTTS: {e}")

# Test SmartTTS
print("\n📝 Test 2: SmartTTS con caché")
try:
    from src.utils.smart_tts import SmartTTS
    
    tts_smart = SmartTTS(engine="gtts", cache_dir="test_cache")
    print("✅ SmartTTS inicializado")
    
    # Primera generación (con caché)
    test_text = "HOLA"
    start = time.time()
    audio_path = tts_smart.speak(test_text)
    elapsed1 = time.time() - start
    print(f"✅ Primera generación: {elapsed1:.2f}s → {audio_path}")
    
    # Segunda generación (desde caché)
    start = time.time()
    audio_path = tts_smart.speak(test_text)
    elapsed2 = time.time() - start
    print(f"⚡ Desde caché: {elapsed2:.4f}s (mejora: {elapsed1/max(elapsed2, 0.001):.1f}x)")
    
    # Limpiar
    import shutil
    if os.path.exists("test_cache"):
        shutil.rmtree("test_cache")
    print("✅ SmartTTS funciona correctamente")
    
except Exception as e:
    print(f"❌ Error con SmartTTS: {e}")

print("\n" + "="*70)
print("✅ TESTS COMPLETADOS")
print("="*70)
print("\nPróximos pasos:")
print("1. Instalar Edge TTS: pip install edge-tts")
print("2. Pre-generar audio: python scripts/pregenerate_audio.py")
print("3. Probar: ./run.sh (Opción 2, activar VOZ)")
print()
