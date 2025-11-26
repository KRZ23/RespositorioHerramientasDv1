# 🎭 Sistema de Traducción Texto → Señas 3D

Sistema completo para traducir texto a lengua de señas animada en 3D, utilizando los landmarks capturados durante el entrenamiento.

## 📋 Características

✅ **Guardado automático de landmarks 3D** durante el entrenamiento  
✅ **Animación 3D** de señas estáticas y dinámicas  
✅ **Traductor texto → señas** con interpolación suave  
✅ **Visualizador interactivo** con Matplotlib embebido  
✅ **Interfaz gráfica** completa con Tkinter  

## 🏗️ Arquitectura

### Nuevos Archivos

1. **`landmarks_3d_manager.py`** (332 líneas)
   - Gestión de dataset de landmarks 3D
   - Guardado de señas estáticas y dinámicas
   - Interpolación de frames para animación suave
   - Traductor de texto a secuencia de landmarks

2. **`hand_3d_visualizer.py`** (232 líneas)
   - Visualizador 3D con Matplotlib
   - Animación de secuencias de landmarks
   - Demo interactivo desde terminal

3. **`text_to_sign_interface.py`** (350 líneas)
   - Interfaz gráfica completa
   - Visualización 3D embebida
   - Lista de señas disponibles
   - Control de animación en tiempo real

4. **`test_3d_translation.py`** (145 líneas)
   - Suite de pruebas del sistema
   - Verificación de componentes
   - Guía de uso

### Modificaciones

- **`hand_detector.py`**:
  - Integración de `Landmarks3DManager`
  - Guardado automático de landmarks 3D durante entrenamiento
  - Captura de landmarks para señas estáticas y dinámicas

## 🚀 Uso

### 1. Entrenar Señas (Captura Landmarks 3D)

```bash
python main.py
```

Cuando entrenes señas (estáticas o dinámicas), el sistema automáticamente:
- Guarda las características en `signs_dataset.json` (para detección)
- Guarda los landmarks 3D en `landmarks_3d_dataset.json` (para animación)

### 2. Verificar Sistema

```bash
python test_3d_translation.py
```

Esto te mostrará:
- Señas disponibles en el dataset 3D
- Pruebas de traducción texto → landmarks
- Estado del sistema

### 3. Visualizar Señas Individuales

```bash
python hand_3d_visualizer.py
```

Opciones:
- Ver una seña específica
- Animar texto completo
- Ver todas las señas secuencialmente

### 4. Traductor Texto → Señas (Interfaz Completa)

```bash
python text_to_sign_interface.py
```

Interfaz gráfica con:
- Campo de texto para entrada
- Visualización 3D embebida
- Lista de señas disponibles
- Control de reproducción (play/stop)

## 📊 Formato de Datos

### Dataset de Landmarks 3D (`landmarks_3d_dataset.json`)

```json
{
  "HOLA": {
    "type": "static",
    "description": "Seña estática entrenada por usuario",
    "frames": [
      [
        [0.5, 0.6, 0.0],  // Landmark 0 (muñeca): [x, y, z]
        [0.45, 0.55, 0.01],  // Landmark 1
        // ... 19 landmarks más
      ]
    ],
    "count": 1
  },
  "ADIOS": {
    "type": "dynamic",
    "description": "Seña dinámica entrenada por usuario",
    "frames": [
      [...],  // Frame 1
      [...],  // Frame 2
      // ... más frames
    ],
    "frame_count": 90,
    "fps": 30
  }
}
```

### Landmarks de MediaPipe (21 puntos)

```
0: Muñeca (WRIST)
1-4: Pulgar (THUMB_CMC, MCP, IP, TIP)
5-8: Índice (INDEX_FINGER_MCP, PIP, DIP, TIP)
9-12: Medio (MIDDLE_FINGER_MCP, PIP, DIP, TIP)
13-16: Anular (RING_FINGER_MCP, PIP, DIP, TIP)
17-20: Meñique (PINKY_MCP, PIP, DIP, TIP)
```

## 🎨 Componentes Técnicos

### Landmarks3DManager

```python
from landmarks_3d_manager import Landmarks3DManager

manager = Landmarks3DManager()

# Guardar seña estática
manager.save_static_sign("HOLA", hand_landmarks, "Saludo")

# Guardar seña dinámica
manager.save_dynamic_sign("ADIOS", [landmarks1, landmarks2, ...], "Despedida")

# Obtener landmarks
sign_data = manager.get_sign_landmarks("HOLA")

# Interpolar frames (para animación suave)
smooth_frames = manager.interpolate_frames(frames, target_fps=60)
```

### SignTo3DTranslator

```python
from landmarks_3d_manager import SignTo3DTranslator

translator = SignTo3DTranslator(manager)

# Traducir texto a secuencia
sequence = translator.text_to_landmarks_sequence("HOLA COMO ESTAS")
# Retorna: [{"sign": "HOLA", "type": "static", "frames": [...], "duration": 0.8}, ...]

# Obtener secuencia completa interpolada
all_frames = translator.get_complete_animation_sequence("HOLA OKEY", smooth=True)
```

### Hand3DVisualizer

```python
from hand_3d_visualizer import Hand3DVisualizer

visualizer = Hand3DVisualizer()

# Mostrar una seña
visualizer.show_sign("HOLA", landmarks_manager)

# Animar secuencia de frames
visualizer.animate_frames(frames, title="HOLA")

# Animar texto completo
visualizer.animate_text("HOLA OKEY", translator)

visualizer.show()
```

## 🔄 Flujo de Trabajo

```
1. Usuario entrena señas
   ↓
2. HandDetector guarda:
   • Features en signs_dataset.json (detección)
   • Landmarks 3D en landmarks_3d_dataset.json (animación)
   ↓
3. Usuario ingresa texto en text_to_sign_interface.py
   ↓
4. SignTo3DTranslator convierte texto → secuencia de landmarks
   ↓
5. Hand3DVisualizer anima los landmarks en 3D
   ↓
6. Usuario ve la traducción animada
```

## 📈 Interpolación de Frames

Para animación suave, el sistema interpola entre frames:

```python
# Original: 30 FPS
frames_30fps = [...90 frames...]

# Interpolado: 60 FPS
frames_60fps = manager.interpolate_frames(frames_30fps, target_fps=60)
# Retorna: ~180 frames interpolados
```

Algoritmo de interpolación:
- Interpolación lineal entre frames consecutivos
- Mantiene la naturalidad del movimiento
- Configurable para diferentes FPS objetivo

## 🎯 Casos de Uso

### 1. Educación
- Aprender lengua de señas
- Visualizar la forma correcta de cada seña
- Practicar con traducciones

### 2. Comunicación
- Traducir mensajes a señas
- Generar contenido en lengua de señas
- Asistencia para personas con discapacidad auditiva

### 3. Investigación
- Análisis de movimientos de manos
- Estudio de patrones de señas
- Desarrollo de IA para lengua de señas

## ⚙️ Configuración

### Ajustar duración de señas estáticas

En `landmarks_3d_manager.py`, línea ~172:

```python
duration = 0.8  # Segundos que se mantiene la seña estática
```

### Ajustar FPS de interpolación

En `landmarks_3d_manager.py`, línea ~235:

```python
interpolated = self.landmarks_manager.interpolate_frames(frames, target_fps=60)
```

### Ajustar pausa entre señas

En `landmarks_3d_manager.py`, línea ~256:

```python
for _ in range(5):  # 5 frames de pausa (0.16s a 30 FPS)
    all_frames.append(pause_frame)
```

## 🐛 Solución de Problemas

### "No hay señas guardadas en el dataset 3D"

**Solución**: Entrena señas usando `main.py` primero. Los landmarks 3D se guardan automáticamente.

### "Error guardando landmarks 3D"

**Causa**: Problema con permisos o formato de datos.

**Solución**:
```bash
# Verificar permisos
ls -la landmarks_3d_dataset.json

# Si no existe, se creará automáticamente
python main.py
```

### La animación se ve entrecortada

**Solución**: Aumenta la interpolación en `text_to_sign_interface.py`:

```python
# Cambiar smooth=True y ajustar FPS
sequence = self.translator.get_complete_animation_sequence(text, smooth=True)
```

## 📦 Dependencias

Ya incluidas en `requirements.txt`:
- `mediapipe` - Detección de landmarks
- `opencv-python` - Procesamiento de video
- `numpy` - Cálculos numéricos
- `matplotlib` - Visualización 3D
- `tkinter` - Interfaz gráfica (viene con Python)

## 🎓 Ejemplo Completo

```python
#!/usr/bin/env python3
from landmarks_3d_manager import Landmarks3DManager, SignTo3DTranslator
from hand_3d_visualizer import Hand3DVisualizer

# Inicializar
manager = Landmarks3DManager()
translator = SignTo3DTranslator(manager)
visualizer = Hand3DVisualizer()

# Traducir y animar
text = "HOLA COMO ESTAS"
visualizer.animate_text(text, translator)
visualizer.show()
```

## 📝 Notas Técnicas

- **Coordenadas normalizadas**: Los landmarks usan coordenadas normalizadas (0-1)
- **Sistema de coordenadas**: 
  - X: izquierda (0) a derecha (1)
  - Y: arriba (0) a abajo (1) [invertido en visualización]
  - Z: profundidad relativa a la muñeca
- **Formato JSON**: UTF-8, pretty-printed para legibilidad

## 🚀 Mejoras Futuras

Posibles extensiones del sistema:

1. **Exportación**:
   - Exportar animación a video (MP4)
   - Exportar a formato BVH (motion capture)
   - Exportar a formatos 3D (FBX, GLTF)

2. **Visualización**:
   - Modelo 3D realista de mano
   - Skin/textura de mano
   - Múltiples vistas simultáneas

3. **Interactividad**:
   - Control de velocidad de reproducción
   - Pausar/reanudar en frame específico
   - Comparar señas lado a lado

4. **Web**:
   - Versión web con Three.js
   - Streaming de animaciones
   - Compartir traducciones

## 📄 Licencia

Mismo que el proyecto principal.

## 👥 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el repositorio
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

---

**¿Preguntas?** Abre un issue en el repositorio.

**¡Disfruta traduciendo texto a señas en 3D! 🎭🙌**
