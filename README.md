# 🤟 Traductor de Lenguaje de Señas Peruano (LSP)

Sistema avanzado de traducción bidireccional de Lenguaje de Señas Peruano con visualización 3D realista.

## ✨ Características Principales

- 🎥 **Detección en tiempo real** con MediaPipe (21 landmarks 3D por mano)
- 🖐️ **Soporte para 1 o 2 manos** simultáneamente
- 📝 **Traducción Texto → Señas** con animación 3D realista
- 🎭 **Visualización 3D con superficies** usando mallas poligonales
- 🗣️ **Síntesis de voz** con gTTS y pygame
- 🎨 **Múltiples interfaces gráficas** con Tkinter
- 💾 **Sistema de entrenamiento** para nuevas señas

## 🏗️ Estructura del Proyecto

```
RespositorioHerramientasDv1/
├── src/                          # Código fuente principal
│   ├── core/                     # Módulos principales
│   │   ├── hand_detector.py      # Detección de manos con MediaPipe
│   │   ├── sign_classifier.py    # Clasificación de señas
│   │   ├── landmarks_3d_manager.py # Gestión de landmarks 3D
│   │   ├── movement_analyzer.py  # Análisis de movimientos
│   │   └── sign_features.py      # Extracción de características
│   ├── visualizers/              # Visualizadores 3D
│   │   ├── realistic_hand_visualizer.py  # Renderizado realista con mallas
│   │   └── hand_3d_visualizer.py         # Visualización con líneas
│   ├── interfaces/               # Interfaces gráficas
│   │   ├── text_to_sign_interface.py  # GUI Texto → Señas
│   │   ├── simple_interface.py        # GUI simplificada
│   │   └── main.py                    # Interfaz principal
│   └── utils/                    # Utilidades y datasets
│       ├── dynamic_signs_dataset.py   # Dataset de señas dinámicas
│       └── peruvian_signs_dataset.py  # Dataset de señas estáticas
├── data/                         # Datos y datasets
│   ├── signs_dataset.json        # Dataset de características
│   └── landmarks_3d_dataset.json # Dataset de landmarks 3D
├── tests/                        # Tests unitarios
│   ├── test_3d_translation.py    # Tests del sistema 3D
│   └── test_translator.py        # Tests del traductor
├── scripts/                      # Scripts auxiliares
│   ├── migrate_to_3d.py          # Migración a formato 3D
│   ├── demo_3d_system.py         # Demo del sistema
│   └── start_3d_translator.sh    # Script de inicio
├── docs/                         # Documentación
│   ├── README_3D_TRANSLATION.md  # Doc del sistema 3D
│   ├── INSTALACION.md            # Guía de instalación
│   └── CHANGELOG.md              # Registro de cambios
├── requirements.txt              # Dependencias Python
└── README.md                     # Este archivo

```

## 🚀 Instalación Rápida

### 1. Clonar el repositorio

```bash
git clone https://github.com/KRZ23/RespositorioHerramientasDv1.git
cd RespositorioHerramientasDv1
```

### 2. Crear entorno virtual

```bash
python3 -m venv venv_translator
source venv_translator/bin/activate  # Linux/Mac
# o en Windows: venv_translator\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la interfaz principal

```bash
# Interfaz Texto → Señas 3D
python -m src.interfaces.text_to_sign_interface

# O interfaz completa con detección
python -m src.interfaces.main
```

## 📋 Dependencias Principales

- **Python** >= 3.8
- **OpenCV** >= 4.10.0 - Procesamiento de video
- **MediaPipe** >= 0.10.14 - Detección de landmarks
- **NumPy** >= 1.26.4 - Operaciones matemáticas
- **Matplotlib** >= 3.7.0 - Visualización 3D
- **Tkinter** - Interfaces gráficas (incluido con Python)
- **gTTS** - Síntesis de voz
- **pygame** - Reproducción de audio

## 🎯 Uso del Sistema

### Modo 1: Traducción Texto → Señas 3D

```python
from src.interfaces.text_to_sign_interface import TextToSignTranslator

# Iniciar interfaz
app = TextToSignTranslator()
app.mainloop()
```

**Características:**
- Escribe texto en español
- Visualización 3D realista con mallas poligonales
- Animación suave con interpolación
- Soporte para múltiples señas en secuencia

### Modo 2: Detección en Tiempo Real

```python
from src.interfaces.simple_interface import SimpleTranslatorInterface

# Iniciar interfaz
app = SimpleTranslatorInterface()
app.mainloop()
```

**Características:**
- Detección en tiempo real con cámara
- Clasificación automática de señas
- Síntesis de voz de las señas detectadas
- Modo entrenamiento para nuevas señas

### Modo 3: Entrenamiento de Señas

```python
from src.core.hand_detector import HandDetector

detector = HandDetector()
detector.train_sign("NUEVA_SEÑA", is_static=True, num_samples=5)
```

## 🎨 Sistema de Visualización 3D

### Visualizador Realista

El `RealisticHand3DVisualizer` crea manos 3D con superficies sólidas:

```python
from src.visualizers.realistic_hand_visualizer import RealisticHand3DVisualizer

visualizer = RealisticHand3DVisualizer(figsize=(10, 8))
visualizer.draw_realistic_hand(landmarks_3d, hand_color='skin')
```

**Características técnicas:**
- Mallas cilíndricas para dedos (8 segmentos)
- Palma triangulada con Poly3DCollection
- Colores personalizables: 'skin', 'blue', 'lightblue'
- Transparencia alpha=0.8 para profundidad
- Bordes con edgecolor='#8B7355'

## 📊 Dataset de Señas

### Señas Disponibles (13 señas migradas a 3D)

**Estáticas:**
- HOLA, OKEY, SILENCIO, DESPIERTO

**Dinámicas:**
- LUSER, BARRER, LLAMAME, FLOJO, ABRAZO, TE VEO, BESAR, LLORAR, CONFEZAR

### Estructura del Dataset

```json
{
  "NOMBRE_SEÑA": {
    "type": "static" | "dynamic",
    "description": "Descripción de la seña",
    "frames": [[[x,y,z], ...21 puntos], ...],
    "num_hands": 1 | 2,
    "count": 1,
    "frame_count": N,
    "fps": 30
  }
}
```

## 🔧 Arquitectura del Sistema

### Flujo de Datos

```
ENTRADA (Texto o Video)
    ↓
[HandDetector] → Captura landmarks con MediaPipe
    ↓
[SignClassifier] → Clasifica características
    ↓
[Landmarks3DManager] → Gestiona landmarks 3D
    ↓
[RealisticHand3DVisualizer] → Renderiza mallas 3D
    ↓
SALIDA (Visualización 3D o Clasificación)
```

### Componentes Principales

1. **Core (`src/core/`)**
   - `HandDetector`: Detección con MediaPipe
   - `SignClassifier`: Clasificación con múltiples métricas
   - `Landmarks3DManager`: Gestión de datos 3D
   - `MovementAnalyzer`: Análisis de movimientos dinámicos

2. **Visualizers (`src/visualizers/`)**
   - `RealisticHand3DVisualizer`: Renderizado con Poly3DCollection
   - `Hand3DVisualizer`: Visualización con líneas coloreadas

3. **Interfaces (`src/interfaces/`)**
   - `TextToSignInterface`: GUI Texto → Señas
   - `SimpleInterface`: GUI detección en tiempo real
   - `main`: Interfaz principal completa

## 📚 Documentación Adicional

- [Instalación Detallada](docs/INSTALACION.md)
- [Sistema 3D](docs/README_3D_TRANSLATION.md)
- [Integración Completa](docs/INTEGRACION_COMPLETA.md)
- [Changelog](docs/CHANGELOG.md)

## 🧪 Tests

```bash
# Test del sistema 3D
python -m tests.test_3d_translation

# Test del traductor
python -m tests.test_translator

# Test de instalación
python -m tests.test_instalacion
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add: AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

**Cristopher Rivera** - [@KRZ23](https://github.com/KRZ23)

## 🙏 Agradecimientos

- **MediaPipe** por la tecnología de detección de manos
- **OpenCV** por el procesamiento de video
- **Matplotlib** por las capacidades de visualización 3D
- Comunidad de Lenguaje de Señas Peruano

## 📧 Contacto

Para preguntas o sugerencias, abre un issue en el repositorio.

---

**Versión:** 2.1.0  
**Última actualización:** Noviembre 2025
