#!/bin/bash

# Script de inicio para el Traductor de Señas Peruano
# Creado para facilitar el uso del sistema

echo "🚀 Iniciando Traductor de Señas Peruano..."
echo "=" * 50

# Verificar si existe el entorno virtual
if [ ! -d "venv_translator" ]; then
    echo "❌ No se encontró el entorno virtual. Creándolo..."
    # Usar Python 3.11 para compatibilidad con MediaPipe
    ~/.local/share/mise/installs/python/3.11.13/bin/python -m venv venv_translator
    echo "✅ Entorno virtual creado con Python 3.11"
fi

# Activar entorno virtual
echo "🔄 Activando entorno virtual..."
source venv_translator/bin/activate

# Verificar/instalar dependencias
echo "📦 Verificando dependencias..."
pip install -q -r requirements.txt

echo "✅ Dependencias instaladas"
echo ""

# Mostrar información del sistema
echo "📋 INFORMACIÓN DEL SISTEMA"
echo "=" * 30
echo "🤟 Señas básicas disponibles:"
echo "   • HOLA, GRACIAS, SI, NO"
echo "   • BIEN, MAL, AMOR, PAZ"
echo "   • AGUA, COMIDA"
echo ""
echo "🎯 Funcionalidades:"
echo "   • Detección en tiempo real"
echo "   • Entrenamiento personalizado"
echo "   • Sistema de confianza"
echo "   • Historial de patrones"
echo ""

# Preguntar si quiere ejecutar pruebas
read -p "¿Ejecutar pruebas del sistema primero? (s/N): " run_tests

if [[ $run_tests =~ ^[SsYy]$ ]]; then
    echo ""
    echo "🧪 Ejecutando pruebas del sistema..."
    python test_translator.py
    echo ""
fi

# Preguntar si quiere iniciar la aplicación
read -p "¿Iniciar la aplicación gráfica? (S/n): " start_app

if [[ ! $start_app =~ ^[Nn]$ ]]; then
    echo ""
    echo "🎉 Iniciando aplicación..."
    echo "💡 Consejos para mejor rendimiento:"
    echo "   • Usa buena iluminación"
    echo "   • Mantén la mano frente a la cámara"
    echo "   • Mantén las señas por 2-3 segundos"
    echo "   • Para entrenar: escribe el nombre y haz la seña"
    echo ""
    echo "Presiona Ctrl+C para cerrar la aplicación"
    echo ""
    
    # Iniciar la aplicación principal
    python main.py
else
    echo ""
    echo "📝 Para iniciar manualmente:"
    echo "   1. source venv_translator/bin/activate"
    echo "   2. python main.py"
    echo ""
    echo "📖 Para ver ayuda:"
    echo "   python test_translator.py"
fi

echo ""
echo "👋 ¡Gracias por usar el Traductor de Señas Peruano!"
