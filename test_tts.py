#!/usr/bin/env python3
"""
Test rápido de Text-to-Speech con gTTS + pygame
"""

import tempfile
import os
import time
from gtts import gTTS
from pygame import mixer

print("🔊 Probando Text-to-Speech...")

try:
    # Inicializar pygame mixer
    mixer.init()
    print("✅ Pygame mixer inicializado")
    
    # Crear audio de prueba
    text = "Hola, esto es una prueba del sistema de texto a voz"
    print(f"📝 Generando audio: '{text}'")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
        temp_file = fp.name
    
    tts = gTTS(text=text, lang='es', slow=False)
    tts.save(temp_file)
    print(f"✅ Audio generado: {temp_file}")
    
    # Reproducir
    print("🔊 Reproduciendo...")
    mixer.music.load(temp_file)
    mixer.music.play()
    
    # Esperar a que termine
    while mixer.music.get_busy():
        time.sleep(0.1)
    
    print("✅ Reproducción completada")
    
    # Limpiar
    os.remove(temp_file)
    print("🗑️ Archivo temporal eliminado")
    
    print("\n🎉 ¡TTS funcionando correctamente!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
