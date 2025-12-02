#!/bin/bash
# =============================================================================
# 🤟 MENÚ PRINCIPAL - Traductor de Lenguaje de Señas Peruano
# =============================================================================

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Banner
show_banner() {
    clear
    echo -e "${CYAN}"
    echo "  ═══════════════════════════════════════════════════════════════"
    echo "  ║                                                             ║"
    echo "  ║      🤟  TRADUCTOR DE LENGUAJE DE SEÑAS PERUANO 🤟        ║"
    echo "  ║                                                             ║"
    echo "  ║                    Versión 2.1.0                           ║"
    echo "  ║                                                             ║"
    echo "  ═══════════════════════════════════════════════════════════════"
    echo -e "${NC}"
}

# Verificar entorno virtual
check_venv() {
    if [ ! -d "venv_translator" ]; then
        echo -e "${RED}❌ Error: No se encontró el entorno virtual${NC}"
        echo -e "${YELLOW}Ejecuta: python3 -m venv venv_translator${NC}"
        echo -e "${YELLOW}         source venv_translator/bin/activate${NC}"
        echo -e "${YELLOW}         pip install -r requirements.txt${NC}"
        exit 1
    fi
}

# Activar entorno virtual
activate_venv() {
    echo -e "${BLUE}📦 Activando entorno virtual...${NC}"
    source venv_translator/bin/activate
}

# Menú principal
show_menu() {
    echo ""
    echo -e "${WHITE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${WHITE}║                    MENÚ PRINCIPAL                         ║${NC}"
    echo -e "${WHITE}╠════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${WHITE}║                                                            ║${NC}"
    echo -e "${WHITE}║  ${GREEN}1)${NC} 🎥  Interfaz Principal Completa                      ${WHITE}║${NC}"
    echo -e "${WHITE}║      ${CYAN}→ Detección + Entrenamiento + TTS${NC}                   ${WHITE}║${NC}"
    echo -e "${WHITE}║                                                            ║${NC}"
    echo -e "${WHITE}║  ${GREEN}2)${NC} 📱  Interfaz Simplificada                            ${WHITE}║${NC}"
    echo -e "${WHITE}║      ${CYAN}→ Detección básica en tiempo real${NC}                   ${WHITE}║${NC}"
    echo -e "${WHITE}║                                                            ║${NC}"
    echo -e "${WHITE}║  ${GREEN}3)${NC} 📝  Traductor Texto → Señas 3D                       ${WHITE}║${NC}"
    echo -e "${WHITE}║      ${CYAN}→ Animación 3D de señas desde texto${NC}                 ${WHITE}║${NC}"
    echo -e "${WHITE}║                                                            ║${NC}"
    echo -e "${WHITE}║  ${YELLOW}4)${NC} 🎓  Entrenar Nueva Seña                             ${WHITE}║${NC}"
    echo -e "${WHITE}║      ${CYAN}→ Capturar y entrenar señas personalizadas${NC}          ${WHITE}║${NC}"
    echo -e "${WHITE}║                                                            ║${NC}"
    echo -e "${WHITE}║  ${YELLOW}5)${NC} 📊  Ver Señas Disponibles                           ${WHITE}║${NC}"
    echo -e "${WHITE}║      ${CYAN}→ Lista de señas en el dataset${NC}                      ${WHITE}║${NC}"
    echo -e "${WHITE}║                                                            ║${NC}"
    echo -e "${WHITE}║  ${MAGENTA}6)${NC} 🎨  Visualización Blender                           ${WHITE}║${NC}"
    echo -e "${WHITE}║      ${CYAN}→ Renderizar señas en 3D con Blender${NC}               ${WHITE}║${NC}"
    echo -e "${WHITE}║                                                            ║${NC}"
    echo -e "${WHITE}║  ${MAGENTA}7)${NC} 🐳  Ejecutar con Docker                             ${WHITE}║${NC}"
    echo -e "${WHITE}║      ${CYAN}→ Lanzar en contenedor${NC}                              ${WHITE}║${NC}"
    echo -e "${WHITE}║                                                            ║${NC}"
    echo -e "${WHITE}║  ${BLUE}8)${NC} 🧪  Ejecutar Tests                                   ${WHITE}║${NC}"
    echo -e "${WHITE}║      ${CYAN}→ Pruebas unitarias del sistema${NC}                     ${WHITE}║${NC}"
    echo -e "${WHITE}║                                                            ║${NC}"
    echo -e "${WHITE}║  ${BLUE}9)${NC} 📚  Abrir Documentación                              ${WHITE}║${NC}"
    echo -e "${WHITE}║      ${CYAN}→ Ver README y guías${NC}                                ${WHITE}║${NC}"
    echo -e "${WHITE}║                                                            ║${NC}"
    echo -e "${WHITE}║  ${GREEN}A)${NC} 🎙️  Configurar TTS con IA                          ${WHITE}║${NC}"
    echo -e "${WHITE}║      ${CYAN}→ Instalar motores de voz (sin entrecortes)${NC}        ${WHITE}║${NC}"
    echo -e "${WHITE}║                                                            ║${NC}"
    echo -e "${WHITE}║  ${GREEN}B)${NC} ⚡  Pre-generar Audio de Señas                      ${WHITE}║${NC}"
    echo -e "${WHITE}║      ${CYAN}→ Cachear todas las voces para reproducción instantánea${NC}${WHITE}║${NC}"
    echo -e "${WHITE}║                                                            ║${NC}"
    echo -e "${WHITE}║  ${RED}0)${NC} 🚪  Salir                                            ${WHITE}║${NC}"
    echo -e "${WHITE}║                                                            ║${NC}"
    echo -e "${WHITE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Función 1: Interfaz Principal
run_main_interface() {
    echo -e "${GREEN}🎥 Iniciando Interfaz Principal Completa...${NC}"
    echo ""
    activate_venv
    python start_main.py
}

# Función 2: Interfaz Simplificada
run_simple_interface() {
    echo -e "${GREEN}📱 Iniciando Interfaz Simplificada...${NC}"
    echo ""
    activate_venv
    python start_simple.py
}

# Función 3: Texto → Señas 3D
run_text_to_sign() {
    echo -e "${GREEN}📝 Iniciando Traductor Texto → Señas 3D...${NC}"
    echo ""
    activate_venv
    python start_text_to_sign.py
}

# Función 4: Entrenar Nueva Seña
train_new_sign() {
    echo -e "${YELLOW}🎓 Entrenamiento de Nueva Seña${NC}"
    echo ""
    echo -e "${CYAN}Instrucciones:${NC}"
    echo "1. Se abrirá la cámara"
    echo "2. Presiona 'T' para iniciar entrenamiento"
    echo "3. Ingresa el nombre de la seña"
    echo "4. Sigue las instrucciones en pantalla"
    echo ""
    read -p "Presiona ENTER para continuar..."
    activate_venv
    python start_main.py
}

# Función 5: Ver Señas
show_signs() {
    echo -e "${YELLOW}📊 Señas Disponibles en el Dataset${NC}"
    echo ""
    activate_venv
    python -c "
import json
import os

dataset_path = 'data/signs_dataset.json'
if os.path.exists(dataset_path):
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print('╔═══════════════════════════════════════════╗')
    print('║          SEÑAS DISPONIBLES                ║')
    print('╠═══════════════════════════════════════════╣')
    for i, (name, info) in enumerate(sorted(data.items()), 1):
        tipo = info.get('type', 'N/A')
        count = info.get('count', 0)
        print(f'║ {i:2d}. {name:25s} [{tipo:7s}] x{count}  ║')
    print('╚═══════════════════════════════════════════╝')
    print(f'\nTotal: {len(data)} señas')
else:
    print('❌ No se encontró el dataset')
    
print('\nSeñas 3D disponibles:')
dataset_3d = 'data/landmarks_3d_dataset.json'
if os.path.exists(dataset_3d):
    with open(dataset_3d, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f'Total: {len(data)} señas con landmarks 3D')
    for name in sorted(data.keys()):
        print(f'  • {name}')
"
    echo ""
    read -p "Presiona ENTER para volver al menú..."
}

# Función 6: Blender
run_blender_viz() {
    echo -e "${MAGENTA}🎨 Visualización con Blender${NC}"
    echo ""
    
    # Verificar Blender
    if ! command -v blender &> /dev/null; then
        echo -e "${RED}❌ Error: Blender no está instalado${NC}"
        echo -e "${YELLOW}Instala con: sudo pacman -S blender${NC}"
        read -p "Presiona ENTER para volver..."
        return
    fi
    
    echo -e "${CYAN}Señas disponibles para visualizar:${NC}"
    python -c "
import json
with open('data/landmarks_3d_dataset.json', 'r') as f:
    data = json.load(f)
for i, name in enumerate(sorted(data.keys()), 1):
    print(f'  {i}. {name}')
"
    echo ""
    read -p "Nombre de la seña a visualizar: " sign_name
    
    if [ -z "$sign_name" ]; then
        echo -e "${RED}❌ Nombre vacío${NC}"
        read -p "Presiona ENTER para volver..."
        return
    fi
    
    echo -e "${BLUE}🎬 Renderizando ${sign_name}...${NC}"
    blender -b -P scripts/blender/visualize_sign.py -- ${sign_name^^}
    
    output_file="output/${sign_name^^}_3D.png"
    if [ -f "$output_file" ]; then
        echo -e "${GREEN}✅ Render completado: $output_file${NC}"
        read -p "¿Abrir imagen? (s/n): " open_img
        if [ "$open_img" = "s" ] || [ "$open_img" = "S" ]; then
            xdg-open "$output_file" &
        fi
    fi
    
    read -p "Presiona ENTER para volver..."
}

# Función 7: Docker
run_docker() {
    echo -e "${MAGENTA}🐳 Menú Docker${NC}"
    echo ""
    echo "1) Interfaz Principal (translator)"
    echo "2) Interfaz Simplificada (translator-simple)"
    echo "3) Texto → Señas 3D (translator-3d)"
    echo "4) Construir imágenes"
    echo "5) Detener contenedores"
    echo "6) Ver logs"
    echo "0) Volver"
    echo ""
    read -p "Selecciona opción: " docker_opt
    
    case $docker_opt in
        1)
            echo -e "${BLUE}Ejecutando con Docker...${NC}"
            xhost +local:docker
            docker-compose up --build translator
            ;;
        2)
            echo -e "${BLUE}Ejecutando versión simple...${NC}"
            xhost +local:docker
            docker-compose --profile simple up --build translator-simple
            ;;
        3)
            echo -e "${BLUE}Ejecutando traductor 3D...${NC}"
            xhost +local:docker
            docker-compose --profile 3d up --build translator-3d
            ;;
        4)
            echo -e "${BLUE}Construyendo imágenes...${NC}"
            docker-compose build
            ;;
        5)
            echo -e "${YELLOW}Deteniendo contenedores...${NC}"
            docker-compose down
            ;;
        6)
            echo -e "${BLUE}Mostrando logs...${NC}"
            docker-compose logs -f
            ;;
    esac
    
    read -p "Presiona ENTER para volver..."
}

# Función 8: Tests
run_tests() {
    echo -e "${BLUE}🧪 Ejecutando Tests${NC}"
    echo ""
    echo "1) Test del sistema 3D"
    echo "2) Test del traductor"
    echo "3) Test de instalación"
    echo "4) Todos los tests"
    echo ""
    read -p "Selecciona opción: " test_opt
    
    activate_venv
    
    case $test_opt in
        1)
            python -m tests.test_3d_translation
            ;;
        2)
            python -m tests.test_translator
            ;;
        3)
            python -m tests.test_instalacion
            ;;
        4)
            python -m pytest tests/ -v
            ;;
    esac
    
    echo ""
    read -p "Presiona ENTER para volver..."
}

# Función 9: Documentación
show_docs() {
    echo -e "${BLUE}📚 Documentación${NC}"
    echo ""
    echo "1) README principal"
    echo "2) Guía de instalación"
    echo "3) Sistema 3D"
    echo "4) Changelog"
    echo "5) TTS sin entrecortes (NUEVO)"
    echo "6) Abrir carpeta docs/"
    echo ""
    read -p "Selecciona opción: " doc_opt
    
    case $doc_opt in
        1) xdg-open README.md & ;;
        2) xdg-open docs/INSTALACION.md & ;;
        3) xdg-open docs/README_3D_TRANSLATION.md & ;;
        4) xdg-open docs/CHANGELOG.md & ;;
        5) xdg-open docs/TTS_IA_SIN_ENTRECORTES.md & ;;
        6) xdg-open docs/ & ;;
    esac
    
    sleep 1
}

# Función A: Configurar TTS
setup_tts() {
    echo -e "${GREEN}🎙️ Configuración de TTS con IA${NC}"
    echo ""
    echo -e "${CYAN}Este asistente te ayudará a instalar motores TTS avanzados${NC}"
    echo -e "${CYAN}para eliminar entrecortes en la reproducción de voz.${NC}"
    echo ""
    read -p "Presiona ENTER para continuar..."
    
    activate_venv
    ./scripts/setup_tts.sh
    
    read -p "Presiona ENTER para volver..."
}

# Función B: Pre-generar Audio
pregenerate_audio() {
    echo -e "${GREEN}⚡ Pre-generación de Audio${NC}"
    echo ""
    echo -e "${CYAN}Este proceso generará y cacheará el audio de todas las señas${NC}"
    echo -e "${CYAN}para reproducción instantánea sin entrecortes.${NC}"
    echo ""
    
    # Verificar si el caché ya existe
    if [ -d "audio_cache" ] && [ "$(ls -A audio_cache/*.mp3 2>/dev/null | wc -l)" -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Ya existen archivos de audio en caché${NC}"
        read -p "¿Regenerar todo? (s/n) [n]: " regenerate
        if [ "$regenerate" = "s" ] || [ "$regenerate" = "S" ]; then
            echo -e "${BLUE}🗑️  Limpiando caché anterior...${NC}"
            rm -rf audio_cache/
        else
            echo -e "${BLUE}Usando caché existente${NC}"
            read -p "Presiona ENTER para volver..."
            return
        fi
    fi
    
    activate_venv
    python scripts/pregenerate_audio.py
    
    echo ""
    echo -e "${GREEN}✅ Pre-generación completada${NC}"
    echo ""
    read -p "Presiona ENTER para volver..."
}

# Loop principal
main() {
    check_venv
    
    while true; do
        show_banner
        show_menu
        
        read -p "$(echo -e ${YELLOW}Selecciona una opción [0-9/A-B]: ${NC})" option
        
        case $option in
            1) run_main_interface ;;
            2) run_simple_interface ;;
            3) run_text_to_sign ;;
            4) train_new_sign ;;
            5) show_signs ;;
            6) run_blender_viz ;;
            7) run_docker ;;
            8) run_tests ;;
            9) show_docs ;;
            A|a) setup_tts ;;
            B|b) pregenerate_audio ;;
            0)
                echo ""
                echo -e "${GREEN}👋 ¡Hasta luego!${NC}"
                echo ""
                exit 0
                ;;
            *)
                echo -e "${RED}❌ Opción inválida${NC}"
                sleep 2
                ;;
        esac
    done
}

# Ejecutar
main
