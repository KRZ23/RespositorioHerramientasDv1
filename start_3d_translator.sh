#!/bin/bash
# Script para iniciar el sistema de traducción texto → señas 3D

echo "🎭 Iniciando Sistema de Traducción Texto → Señas 3D..."
echo ""

# Activar entorno virtual
if [ -d "venv_translator" ]; then
    source venv_translator/bin/activate
    echo "✓ Entorno virtual activado"
else
    echo "⚠️  Entorno virtual no encontrado. Creando..."
    python3 -m venv venv_translator
    source venv_translator/bin/activate
    pip install -r requirements.txt
fi

echo ""
echo "Selecciona qué quieres hacer:"
echo ""
echo "1. 🎬 Traductor Texto → Señas (Interfaz Completa)"
echo "2. 📊 Visualizador de Señas Individuales"
echo "3. 🎓 Entrenar Nuevas Señas (con landmarks 3D)"
echo "4. 🔍 Probar Sistema"
echo "5. 📚 Ver Documentación"
echo ""
read -p "Opción (1-5): " choice

case $choice in
    1)
        echo ""
        echo "🎬 Iniciando traductor completo..."
        python text_to_sign_interface.py
        ;;
    2)
        echo ""
        echo "📊 Iniciando visualizador..."
        python hand_3d_visualizer.py
        ;;
    3)
        echo ""
        echo "🎓 Iniciando sistema de entrenamiento..."
        python main.py
        ;;
    4)
        echo ""
        echo "🔍 Ejecutando pruebas..."
        python test_3d_translation.py
        ;;
    5)
        echo ""
        echo "📚 Mostrando documentación..."
        cat README_3D_TRANSLATION.md | less
        ;;
    *)
        echo ""
        echo "❌ Opción inválida"
        ;;
esac
