# 🤟 Interfaz Simplificada - Traductor LSP

## Descripción

Interfaz minimalista del traductor de Lengua de Señas Peruana (LSP) con enfoque en usabilidad simple.

## Características

### 🎯 Vista Simple
- **Cámara embebida**: Vista en tiempo real directamente en la interfaz
- **5 botones principales**: Control sencillo e intuitivo
- **Área de texto**: Visualización clara de traducciones

### 🎮 Controles

1. **🚀 Iniciar**: Comienza la detección y traducción
2. **⏹️ Detener**: Detiene la cámara y traducción
3. **🔊 Modo Hablado**: Activa/desactiva síntesis de voz automática con delay
4. **🎓 Entrenamiento**: Cambia a modo de entrenamiento de nuevas señas
5. **🚪 Salir**: Cierra la aplicación

### 🔊 Modo Hablado Automático

Cuando está activado:
- Las señas detectadas se pronuncian automáticamente
- Delay configurable de 1.5 segundos entre pronunciaciones
- Evita repeticiones innecesarias de la misma seña
- Usa gTTS (Google Text-to-Speech) en español

## Ejecución

### Método 1: Script directo
```bash
./start_simple_translator.sh
```

### Método 2: Python directo
```bash
source venv_translator/bin/activate
python3 simple_interface.py
```

## Diferencias con la Interfaz Completa

| Característica | Interfaz Simple | Interfaz Completa |
|----------------|-----------------|-------------------|
| Vista de cámara | Embebida | Ventana separada |
| Controles | 5 botones | 20+ controles |
| Configuración | Básica | Avanzada |
| Estadísticas | No | Sí (tiempo real) |
| Exportación | No | Sí (traducciones) |
| Historial | Simple | Completo con timestamps |
| TTS | Auto con delay | Manual + auto configurable |
| Modo oscuro | No | Sí |
| Ayuda integrada | No | Sí (ventana detallada) |

## Requisitos

- Python 3.11+
- OpenCV 4.10.0+
- MediaPipe 0.10.14+
- gTTS 2.5.4+
- pygame (para reproducción de audio)
- tkinter (incluido en Python)

## Detección de Señas

### Señas Estáticas
- HOLA, ADIOS, GRACIAS, etc.
- Basadas en forma de mano y posición

### Señas Dinámicas (NUEVO)
- HOLA_MOVIMIENTO (movimiento zigzag)
- ADIOS (movimiento arriba-abajo)
- VEN_AQUI (movimiento hacia cámara)
- NO_NO (zigzag con índice)
- VAMOS (movimiento hacia adelante)
- LLAMAR (movimiento hacia oreja)
- ESPERAR (movimiento hacia abajo)
- RAPIDO (movimiento circular)
- DINERO (vibración rápida)
- PREGUNTAR (movimiento hacia arriba)

## Rendimiento

- **FPS esperado**: 22-27 FPS (con detección dinámica)
- **Latencia**: <50ms por frame
- **Uso de CPU**: Moderado (sin frameworks de ML pesados)
- **Uso de RAM**: ~300-400 MB

## Modo Entrenamiento

1. Clic en **🎓 Entrenamiento**
2. Ingresar nombre de la seña
3. Realizar la seña frente a la cámara
4. La muestra se guarda automáticamente
5. Repetir para agregar más señas personalizadas

## Solución de Problemas

### Cámara no se muestra
- Verificar que `/dev/video0` esté disponible
- Cerrar otras aplicaciones que usen la cámara
- Reiniciar la detección con el botón Detener → Iniciar

### Modo hablado no funciona
- Verificar instalación de `gTTS`: `pip install gtts`
- Verificar salida de audio del sistema
- Comprobar conectividad a internet (gTTS requiere conexión)

### Señas dinámicas no se detectan
- Realizar movimientos más amplios y claros
- Mantener la mano visible durante todo el movimiento
- Esperar ~0.5 segundos para que se acumule buffer de movimiento

## Arquitectura

```
simple_interface.py
├── SimpleTranslatorInterface (clase principal)
│   ├── _setup_ui() - Construcción de interfaz
│   ├── _start_translation() - Inicia detección
│   ├── _stop_translation() - Detiene detección
│   ├── _toggle_spoken_mode() - Activa/desactiva TTS auto
│   ├── _toggle_training_mode() - Cambia a modo entrenamiento
│   ├── _update_camera_feed() - Actualiza vista de cámara (hilo)
│   ├── _on_sign_detected() - Callback de seña detectada
│   ├── _speak_text() - Síntesis de voz con gTTS
│   └── _on_closing() - Limpieza al cerrar
└── HandDetector (de hand_detector.py)
    ├── Detección estática (SignClassifier)
    └── Detección dinámica (MovementAnalyzer)
```

## Créditos

- **Autor**: Cristopher Rivera
- **Versión**: 2.2 (con detección dinámica)
- **Fecha**: Enero 2025
- **Licencia**: MIT

## Ver También

- `main.py` - Interfaz completa con todas las características
- `hand_detector.py` - Motor de detección de señas
- `movement_analyzer.py` - Analizador de movimiento temporal
- `dynamic_signs_dataset.py` - Patrones de señas dinámicas
- `README.md` - Documentación completa del proyecto
