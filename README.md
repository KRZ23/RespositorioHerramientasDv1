# 🤟 Traductor de Lenguaje de Señas Peruano

¡Bienvenido al sistema de traducción de lenguaje de señas peruano en tiempo real!

Este proyecto utiliza inteligencia artificial y visión por computadora para detectar y traducir señas de la mano en tiempo real, con un enfoque específico en el lenguaje de señas peruano.

## 🌟 Características Principales

- ✨ **Detección en tiempo real**: Reconocimiento instantáneo de señas usando MediaPipe
- 🧠 **IA Avanzada**: Múltiples algoritmos de clasificación (coseno, euclidiano, correlación)
- 📚 **Señas preconfiguradas**: 10 señas básicas incluidas (HOLA, GRACIAS, SÍ, NO, etc.)
- 🎯 **Entrenamiento personalizado**: Entrena el sistema con tus propias señas
- 📊 **Sistema de confianza**: Muestra el nivel de certeza de cada traducción
- 🔄 **Estabilidad temporal**: Suavizado de predicciones para mayor precisión
- 🎨 **Interfaz moderna**: GUI intuitiva con indicadores visuales
- 📜 **Historial de traducciones**: Almacena automáticamente las traducciones detectadas
- 🔊 **Text-to-Speech**: Escucha las traducciones en voz alta (español)
- 💾 **Exportación**: Guarda el historial de traducciones a archivo de texto

## 🏗️ Arquitectura del Sistema

### Componentes Principales

1. **`sign_features.py`**: Extractor de características de landmarks de manos
2. **`peruvian_signs_dataset.py`**: Dataset de señas peruanas con patrones básicos
3. **`sign_classifier.py`**: Clasificador multicriteria con suavizado temporal
4. **`hand_detector.py`**: Detector de manos integrado con MediaPipe
5. **`main.py`**: Interfaz gráfica principal

### Señas Incluidas

| Seña | Descripción |
|------|-------------|
| HOLA | Mano abierta, movimiento de saludo |
| GRACIAS | Mano hacia el pecho, dedos juntos |
| SÍ | Puño cerrado, movimiento de asentimiento |
| NO | Índice extendido, movimiento lateral |
| BIEN | Pulgar arriba |
| MAL | Pulgar hacia abajo |
| AMOR | Índice y meñique extendidos |
| PAZ | Índice y medio extendidos (V de victoria) |
| AGUA | Mano formando copa |
| COMIDA | Dedos juntos hacia la boca |

## 🚀 Instalación y Uso

### Método Rápido (Recomendado)

```bash
# Clonar el repositorio
git clone <url-del-repo>
cd RespositorioHerramientasDv1

# Ejecutar script de inicio automático
./start_translator.sh
```

### Método Manual

```bash
# 1. Crear entorno virtual
python3 -m venv venv_translator
source venv_translator/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar pruebas (opcional)
python test_translator.py

# 4. Iniciar aplicación
python main.py
```

## 📋 Dependencias

- **OpenCV**: Procesamiento de imágenes y video
- **MediaPipe**: Detección de landmarks de manos
- **NumPy**: Cálculos numéricos
- **SciPy**: Algoritmos de similitud y estadística
- **Tkinter**: Interfaz gráfica (incluido con Python)

## 🎯 Cómo Usar

### Detección Básica

1. **Iniciar**: Presiona "▶️ Iniciar Detección"
2. **Posicionar**: Coloca tu mano frente a la cámara
3. **Traducir**: Las señas aparecerán en tiempo real
4. **Confianza**: Observa el nivel de certeza (colores: verde=alta, amarillo=media, naranja=baja)

### Entrenamiento de Nuevas Señas

1. **Escribir**: Ingresa el nombre de la nueva seña
2. **Entrenar**: Presiona "🎯 Entrenar"
3. **Demostrar**: Haz la seña frente a la cámara por 2-3 segundos
4. **Confirmar**: El sistema guardará automáticamente el patrón

### Controles Disponibles

- **▶️ Iniciar/Parar Detección**: Controla la cámara
- **🇪🇸 Traducción ON/OFF**: Activa/desactiva el clasificador
- **🎯 Entrenar**: Añade nuevas señas al sistema

## 📊 Características Técnicas

### Extractor de Características (17 dimensiones)

- **Distancias**: 5 distancias desde muñeca a cada dedo
- **Ángulos**: 4 ángulos entre dedos adyacentes
- **Flexión**: 5 ratios de extensión de dedos
- **Orientación**: 2 componentes de orientación (sin/cos)
- **Apertura**: 1 medida de apertura general de la mano

### Algoritmos de Clasificación

1. **Similitud Coseno**: Comparación de vectores normalizados
2. **Distancia Euclidiana**: Distancia geométrica en espacio de características
3. **Correlación de Pearson**: Correlación lineal entre patrones
4. **Patrones Básicos**: Coincidencia directa con reglas heurísticas

### Sistema de Estabilidad

- **Historial**: 5 predicciones recientes
- **Consenso**: 3 predicciones consistentes para confirmación
- **Suavizado**: Promediado de confianza temporal

## 🔬 Pruebas y Validación

```bash
# Ejecutar suite completa de pruebas
python test_translator.py

# Probar solo un componente
python -c "from test_translator import test_classifier; test_classifier()"
```

## 📁 Estructura del Proyecto

```
RespositorioHerramientasDv1/
├── 📄 main.py                    # Interfaz principal
├── 🤖 hand_detector.py          # Detector de manos
├── 🔍 sign_classifier.py        # Clasificador de señas
├── 📊 sign_features.py          # Extractor de características
├── 📚 peruvian_signs_dataset.py # Dataset de señas
├── 🧪 test_translator.py        # Suite de pruebas
├── 🚀 start_translator.sh       # Script de inicio
├── 📋 requirements.txt          # Dependencias
├── 📖 README.md                 # Este archivo
├── 🗂️ venv_translator/          # Entorno virtual
└── 📄 signs_dataset.json        # Dataset persistente (generado)
```

## 🛠️ Desarrollo y Contribución

### Añadir Nuevas Señas Básicas

Edita `peruvian_signs_dataset.py` en la sección `_initialize_basic_signs()`:

```python
"NUEVA_SEÑA": {
    "description": "Descripción de la seña",
    "pattern": {
        "fingers_extended": [True, False, True, False, True],
        "hand_openness": 0.6,
        "confidence_threshold": 0.7
    }
}
```

### Mejorar Algoritmos

- **Características**: Modifica `SignFeatureExtractor` en `sign_features.py`
- **Clasificación**: Añade nuevas métricas en `SignClassifier`
- **Dataset**: Expande patrones en `PeruvianSignsDataset`

## 🎨 Personalización

### Configuración de Confianza

```python
# Ajustar umbral de confianza
classifier = SignClassifier(confidence_threshold=0.8)  # Más estricto
```

### Configuración de Estabilidad

```python
# Modificar en SignClassifier.__init__()
self.history_size = 10      # Más historial
self.stable_frames = 5      # Más frames para estabilidad
```

## 🤝 Créditos

- **MediaPipe**: Google - Framework de ML para detección de manos
- **OpenCV**: Biblioteca de visión por computadora
- **SciPy**: Comunidad científica de Python

## 📞 Soporte

¿Problemas o preguntas?

1. **Ejecutar pruebas**: `python test_translator.py`
2. **Verificar cámara**: Asegúrate de que funcione con otras apps
3. **Revisar logs**: Observa los mensajes en la interfaz
4. **Reinstalar**: `rm -rf venv_translator && ./start_translator.sh`

---

🇵🇪 **Hecho con ❤️ para la comunidad peruana sorda**

> *"La tecnología debe ser accesible para todos"*
