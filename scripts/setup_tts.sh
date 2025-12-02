#!/bin/bash
# Script para configurar opciones de TTS

set -e

VENV_PATH="venv_translator"

echo "================================="
echo "🎙️ CONFIGURACIÓN DE TTS"
echo "================================="
echo ""

# Verificar venv
if [ ! -d "$VENV_PATH" ]; then
    echo "❌ Error: No se encuentra el entorno virtual en $VENV_PATH"
    exit 1
fi

# Activar venv
source "$VENV_PATH/bin/activate"

echo "Selecciona el motor TTS que deseas usar:"
echo ""
echo "1) Edge TTS (Microsoft) - 🌟 RECOMENDADO"
echo "   - Gratis, sin API key"
echo "   - Alta calidad, voces naturales"
echo "   - Requiere internet"
echo ""
echo "2) gTTS (Google) - Ya instalado"
echo "   - Gratis, simple"
echo "   - Calidad media"
echo "   - Puede tener entrecortes"
echo ""
echo "3) pyttsx3 (Offline)"
echo "   - Completamente offline"
echo "   - Usa voces del sistema"
echo "   - Calidad depende del sistema"
echo ""
echo "4) Coqui TTS (Local, IA)"
echo "   - Open source, local"
echo "   - Alta calidad"
echo "   - Requiere ~2GB descarga de modelo"
echo ""
echo "5) ElevenLabs (Premium)"
echo "   - Máxima calidad"
echo "   - Requiere API key (pago)"
echo ""

read -p "Opción [1]: " choice
choice=${choice:-1}

case $choice in
    1)
        echo "📦 Instalando Edge TTS..."
        pip install edge-tts
        echo "✅ Edge TTS instalado"
        echo ""
        echo "Voces disponibles en español:"
        echo "  - es-ES-AlvaroNeural (Hombre, España)"
        echo "  - es-ES-ElviraNeural (Mujer, España)"
        echo "  - es-MX-DaliaNeural (Mujer, México)"
        echo "  - es-MX-JorgeNeural (Hombre, México)"
        echo "  - es-AR-ElenaNeural (Mujer, Argentina)"
        echo ""
        ;;
    2)
        echo "✅ gTTS ya está instalado (requirements.txt)"
        ;;
    3)
        echo "📦 Instalando pyttsx3..."
        pip install pyttsx3
        
        # Instalar dependencias del sistema
        echo "Instalando dependencias del sistema..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get install -y espeak espeak-data libespeak1 libespeak-dev
        elif command -v pacman &> /dev/null; then
            sudo pacman -S --noconfirm espeak
        fi
        echo "✅ pyttsx3 instalado"
        ;;
    4)
        echo "📦 Instalando Coqui TTS..."
        echo "⚠️ Esto descargará ~2GB de modelos"
        read -p "¿Continuar? (s/n) [s]: " confirm
        confirm=${confirm:-s}
        
        if [ "$confirm" = "s" ] || [ "$confirm" = "S" ]; then
            pip install TTS
            echo "✅ Coqui TTS instalado"
        else
            echo "❌ Instalación cancelada"
        fi
        ;;
    5)
        echo "📦 Instalando ElevenLabs..."
        pip install elevenlabs
        echo "✅ ElevenLabs instalado"
        echo ""
        echo "⚠️ Requiere API key:"
        echo "1. Regístrate en https://elevenlabs.io"
        echo "2. Obtén tu API key"
        echo "3. Configura: export ELEVENLABS_API_KEY='tu_api_key'"
        echo ""
        ;;
    *)
        echo "❌ Opción inválida"
        exit 1
        ;;
esac

echo ""
echo "================================="
echo "✅ Configuración completada"
echo "================================="
echo ""
echo "Para pre-generar todos los audios:"
echo "  python scripts/pregenerate_audio.py"
echo ""
