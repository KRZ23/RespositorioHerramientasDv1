# 🎙️ Sistema de Voz con IA - Sin Entrecortes

## 🌟 Problema Solucionado

**Antes:** La síntesis de voz se generaba en tiempo real con gTTS, causando:
- ⏳ Entrecortes y pausas molestas
- 🐌 Delay en la reproducción
- 📶 Dependencia de internet en cada reproducción

**Ahora:** Sistema de **caché inteligente** con múltiples motores TTS:
- ⚡ Reproducción instantánea (sin entrecortes)
- 🎯 Primera generación: se cachea el audio
- 🚀 Siguientes reproducciones: instantáneas desde caché
- 🔄 Múltiples motores disponibles (Edge TTS, gTTS, pyttsx3, Coqui, ElevenLabs)

---

## 📦 Instalación Rápida

### 1. Instalar Motor TTS (Recomendado: Edge TTS)

```bash
# Ejecutar script de configuración
chmod +x scripts/setup_tts.sh
./scripts/setup_tts.sh
```

El script te permite elegir entre:

| Motor | Calidad | Costo | Offline | Recomendado |
|-------|---------|-------|---------|-------------|
| **Edge TTS** | ⭐⭐⭐⭐⭐ | Gratis | ❌ | ✅ **SÍ** |
| gTTS | ⭐⭐⭐ | Gratis | ❌ | Instalado |
| pyttsx3 | ⭐⭐ | Gratis | ✅ | Para offline |
| Coqui TTS | ⭐⭐⭐⭐ | Gratis | ✅ | ~2GB descarga |
| ElevenLabs | ⭐⭐⭐⭐⭐ | Pago | ❌ | Premium |

### 2. Pre-generar Audio (Opcional pero Recomendado)

```bash
# Activar entorno virtual
source venv_translator/bin/activate

# Pre-generar audio para todas las señas
python scripts/pregenerate_audio.py
```

Esto generará y almacenará el audio de todas las señas en caché, asegurando reproducción instantánea.

---

## 🚀 Uso

### Automático (Ya Integrado)

Las interfaces ya usan el nuevo sistema automáticamente:

```bash
# Interfaz Simple (con botón de voz)
./run.sh  # Opción 2

# Interfaz Completa (con historial y TTS)
./run.sh  # Opción 1
```

### Manual (Desde Código)

```python
from src.utils.smart_tts import SmartTTS

# Inicializar con motor deseado
tts = SmartTTS(engine="edge-tts", cache_dir="audio_cache")

# Primera vez: genera y guarda en caché
tts.speak_and_play("HOLA")  # Tarda ~1-2 segundos

# Segunda vez: instantáneo desde caché
tts.speak_and_play("HOLA")  # <0.1 segundos ⚡
```

---

## 🎛️ Configuración Avanzada

### Cambiar Motor TTS

Edita los archivos de interfaz:

```python
# src/interfaces/simple_interface.py
self.tts = SmartTTS(
    engine="edge-tts",  # Cambiar aquí: "gtts", "pyttsx3", "coqui", "elevenlabs"
    cache_dir="audio_cache"
)
```

### Voces Disponibles (Edge TTS)

```python
# Voces en español
voices = {
    "es-ES-AlvaroNeural": "Hombre, España",
    "es-ES-ElviraNeural": "Mujer, España",
    "es-MX-DaliaNeural": "Mujer, México",
    "es-MX-JorgeNeural": "Hombre, México",
    "es-AR-ElenaNeural": "Mujer, Argentina"
}

# Usar voz específica
import asyncio
asyncio.run(tts.generate_audio_edge("Hola", "output.mp3", voice="es-MX-DaliaNeural"))
```

### Limpiar Caché

```bash
# Eliminar todos los audios cacheados
rm -rf audio_cache/

# Regenerar caché
python scripts/pregenerate_audio.py
```

---

## 📊 Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                     INTERFAZ DE USUARIO                      │
│  (Tkinter GUI - simple_interface.py / main.py)             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      SmartTTS Manager                        │
│  - Gestión de caché (audio_cache/)                          │
│  - Selección de motor TTS                                   │
│  - Generación bajo demanda                                  │
└────────┬───────────┬─────────┬──────────┬──────────────────┘
         │           │         │          │
    ┌────▼───┐  ┌───▼────┐ ┌──▼───┐  ┌──▼──────┐
    │Edge TTS│  │  gTTS  │ │pyttsx│  │ElevenLabs│
    └────┬───┘  └───┬────┘ └──┬───┘  └──┬──────┘
         │          │         │          │
         └──────────┴─────────┴──────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   audio_cache/        │
         │  ├── abc123.mp3       │
         │  ├── def456.mp3       │
         │  └── metadata.json    │
         └───────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   pygame.mixer        │
         │   (Reproducción)      │
         └───────────────────────┘
```

### Flujo de Ejecución

```
Usuario detecta seña → Sistema identifica "HOLA"
                              │
                              ▼
                    ¿Existe en caché?
                    │              │
                  SÍ ──┐           │ NO
                       │           ▼
                       │    Generar con TTS
                       │    (Edge TTS / gTTS / etc)
                       │           │
                       │           ▼
                       │    Guardar en caché
                       │    (audio_cache/hash.mp3)
                       │           │
                       └───────────┘
                              │
                              ▼
                    Reproducir con pygame
                    (⚡ Instantáneo, sin entrecortes)
```

---

## 🔧 Troubleshooting

### Error: "No module named 'edge_tts'"

```bash
pip install edge-tts
```

### Error: "espeak not found" (pyttsx3)

```bash
# Arch Linux
sudo pacman -S espeak

# Ubuntu/Debian
sudo apt-get install espeak espeak-data libespeak1
```

### Error: "ELEVENLABS_API_KEY no configurada"

```bash
# Obtener API key en https://elevenlabs.io
export ELEVENLABS_API_KEY='tu_api_key_aqui'
```

### Audio no se reproduce

```bash
# Verificar pygame
python -c "import pygame; pygame.mixer.init(); print('OK')"

# Verificar archivos de caché
ls -lh audio_cache/
```

### Regenerar todo el caché

```bash
# Limpiar y regenerar
rm -rf audio_cache/
python scripts/pregenerate_audio.py
```

---

## 📈 Comparativa de Rendimiento

| Método | Primera Reproducción | Segunda Reproducción | Calidad |
|--------|---------------------|---------------------|---------|
| **gTTS sin caché** | ~2-3s | ~2-3s | ⭐⭐⭐ |
| **SmartTTS + Edge** | ~1-2s | **<0.1s** ⚡ | ⭐⭐⭐⭐⭐ |
| **SmartTTS + Coqui** | ~1-2s | **<0.1s** ⚡ | ⭐⭐⭐⭐ |

**Mejora:** ~20-30x más rápido en reproducciones subsecuentes

---

## 📝 Ejemplo Completo

```python
from src.utils.smart_tts import SmartTTS

# 1. Inicializar
tts = SmartTTS(engine="edge-tts")

# 2. Generar y cachear todas las señas
signs = ["HOLA", "GRACIAS", "POR FAVOR", "ADIOS"]
for sign in signs:
    tts.speak(sign)  # Genera y cachea

# 3. Reproducir (instantáneo)
tts.speak_and_play("HOLA")  # ⚡ Sin entrecortes
tts.speak_and_play("GRACIAS")  # ⚡ Sin entrecortes

# 4. Verificar caché
audio_path = tts.cache.get_audio_path("HOLA")
print(f"Audio cacheado en: {audio_path}")
print(f"Existe: {audio_path.exists()}")
```

---

## 🎯 Beneficios del Sistema

1. **⚡ Velocidad:** Reproducción instantánea después de primera generación
2. **🔄 Sin entrecortes:** Audio pre-generado y listo para reproducir
3. **💾 Eficiencia:** Reutilización de audio (no regenera cada vez)
4. **🌐 Flexibilidad:** Múltiples motores TTS disponibles
5. **📦 Portabilidad:** Caché compartible entre ejecuciones
6. **🎨 Calidad:** Voces naturales con Edge TTS / ElevenLabs
7. **📴 Modo offline:** Compatible con pyttsx3 / Coqui TTS

---

## 🚀 Próximos Pasos

1. ✅ Instalar motor TTS preferido
2. ✅ Pre-generar audio con `python scripts/pregenerate_audio.py`
3. ✅ Ejecutar interfaz con `./run.sh`
4. 🎉 ¡Disfruta de traducciones sin entrecortes!

---

**Versión:** 2.2.0  
**Última actualización:** Noviembre 2025  
**Autor:** Sistema de Traducción LSP
