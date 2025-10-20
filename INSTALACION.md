# 📦 Guía de Instalación - Traductor de Señas Peruano v2.1

## 🔧 Requisitos del Sistema

### Sistema Operativo
- **Linux** (probado en Arch Linux)
- **Python 3.11** (requerido para compatibilidad con MediaPipe)

### Dependencias del Sistema

#### En Arch Linux:
```bash
sudo pacman -S espeak-ng tk tcl
```

#### En Ubuntu/Debian:
```bash
sudo apt install espeak-ng python3-tk
```

## 🚀 Instalación Paso a Paso

### 1. Clonar el Repositorio
```bash
git clone https://github.com/KRZ23/RespositorioHerramientasDv1.git
cd RespositorioHerramientasDv1
```

### 2. Instalar Python 3.11

#### Usando mise (recomendado):
```bash
# Instalar mise si no lo tienes
curl https://mise.run | sh

# Instalar Python 3.11
mise install python@3.11
```

#### Alternativa con pyenv:
```bash
pyenv install 3.11.13
pyenv local 3.11.13
```

### 3. Crear Entorno Virtual
```bash
python3.11 -m venv .venv311
source .venv311/bin/activate  # En Linux/Mac
```

### 4. Instalar Dependencias de Python

**IMPORTANTE**: Usar las versiones específicas probadas:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 📋 Versiones Probadas

Las siguientes versiones han sido probadas y son compatibles:

| Paquete | Versión | Notas |
|---------|---------|-------|
| Python | 3.11.13 | Requerido |
| opencv-python | 4.10.0.84 | Estable |
| opencv-contrib-python | 4.10.0.84 | Requerido por MediaPipe |
| mediapipe | 0.10.14 | Última versión compatible con Python 3.11 |
| numpy | 1.26.4 | Compatible con OpenCV y MediaPipe |
| scipy | 1.13.1 | Estable |
| pyttsx3 | 2.90 | Text-to-Speech |
| jax | 0.4.23 | Requerido por MediaPipe |
| jaxlib | 0.4.23 | Compatible con numpy 1.26.4 |

## ⚠️ Problemas Comunes y Soluciones

### Error: "No module named numpy._core._multiarray_umath"
**Solución**: Reinstalar numpy con la versión correcta
```bash
pip uninstall numpy
pip install numpy==1.26.4
```

### Error: "recursion is detected during loading of cv2"
**Solución**: Desinstalar versiones conflictivas de OpenCV
```bash
pip uninstall opencv-python opencv-contrib-python
pip install opencv-python==4.10.0.84 opencv-contrib-python==4.10.0.84
```

### Error: "espeak or espeak-ng not installed"
**Solución**: Instalar motor de voz del sistema
```bash
# Arch Linux
sudo pacman -S espeak-ng

# Ubuntu/Debian
sudo apt install espeak-ng
```

### Error: "cannot import cv2"
**Causas posibles**:
1. Múltiples versiones de OpenCV instaladas
2. Conflicto entre opencv-python y opencv-contrib-python

**Solución**:
```bash
# Limpiar todo
pip uninstall -y opencv-python opencv-contrib-python opencv-python-headless

# Reinstalar solo las necesarias
pip install opencv-python==4.10.0.84 opencv-contrib-python==4.10.0.84
```

### Error: Tkinter no funciona
**Solución**: Instalar paquetes Tk del sistema
```bash
# Arch Linux
sudo pacman -S tk tcl

# Ubuntu/Debian
sudo apt install python3-tk
```

## 🎯 Verificar Instalación

Ejecuta este script para verificar que todo está instalado correctamente:

```python
# test_instalacion.py
import sys
print(f"Python: {sys.version}")

try:
    import cv2
    print(f"✅ OpenCV: {cv2.__version__}")
except ImportError as e:
    print(f"❌ OpenCV: {e}")

try:
    import mediapipe as mp
    print(f"✅ MediaPipe: {mp.__version__}")
except ImportError as e:
    print(f"❌ MediaPipe: {e}")

try:
    import numpy as np
    print(f"✅ NumPy: {np.__version__}")
except ImportError as e:
    print(f"❌ NumPy: {e}")

try:
    import scipy
    print(f"✅ SciPy: {scipy.__version__}")
except ImportError as e:
    print(f"❌ SciPy: {e}")

try:
    import pyttsx3
    engine = pyttsx3.init()
    print(f"✅ pyttsx3: OK")
except Exception as e:
    print(f"❌ pyttsx3: {e}")

try:
    import tkinter
    print(f"✅ Tkinter: {tkinter.TkVersion}")
except ImportError as e:
    print(f"❌ Tkinter: {e}")

print("\n🎉 ¡Todas las dependencias están instaladas correctamente!")
```

## 🏃 Ejecutar el Programa

```bash
# Activar entorno virtual
source .venv311/bin/activate

# Ejecutar
python main.py
```

## 🔄 Actualización

Para actualizar a la última versión:

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

## 💡 Consejos

1. **Siempre usa el entorno virtual**: No instales las dependencias globalmente
2. **Versiones específicas**: No uses `pip install --upgrade` sin verificar compatibilidad
3. **Python 3.11**: MediaPipe no funciona con Python 3.12+
4. **Cámara**: Asegúrate que tu cámara no esté siendo usada por otra aplicación

## 🆘 Soporte

Si encuentras problemas:

1. Verifica que estés usando **Python 3.11**
2. Asegúrate de tener **todas las dependencias del sistema** instaladas
3. Revisa los logs de error completos
4. Consulta el archivo `CHANGELOG.md` para cambios recientes

---

**Última actualización**: 20 de Octubre 2025
**Versión del programa**: 2.1
**Python requerido**: 3.11.x
