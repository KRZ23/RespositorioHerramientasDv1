#!/usr/bin/env python3
"""
Script de verificación de instalación
Traductor de Señas Peruano v2.1
"""

import sys

def check_python_version():
    """Verifica la versión de Python"""
    version = sys.version_info
    print(f"\n🐍 Python: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor == 11:
        print("   ✅ Versión correcta (Python 3.11)")
        return True
    else:
        print(f"   ⚠️  Se recomienda Python 3.11 (tienes {version.major}.{version.minor})")
        return False

def check_package(package_name, import_name=None, get_version=None):
    """Verifica si un paquete está instalado"""
    if import_name is None:
        import_name = package_name
    
    try:
        module = __import__(import_name)
        
        # Intentar obtener versión
        version = "OK"
        if get_version:
            version = get_version(module)
        elif hasattr(module, '__version__'):
            version = module.__version__
        
        print(f"   ✅ {package_name}: {version}")
        return True
    except ImportError as e:
        print(f"   ❌ {package_name}: No instalado - {e}")
        return False
    except Exception as e:
        print(f"   ⚠️  {package_name}: Error - {e}")
        return False

def check_system_dependencies():
    """Verifica dependencias del sistema"""
    print("\n🔧 Verificando dependencias del sistema:")
    
    # Tkinter
    try:
        import tkinter
        print(f"   ✅ Tkinter: {tkinter.TkVersion}")
    except ImportError:
        print("   ❌ Tkinter: No disponible (instala python3-tk)")
    
    # eSpeak
    try:
        import pyttsx3
        engine = pyttsx3.init()
        print("   ✅ eSpeak/pyttsx3: OK")
        engine.stop()
    except Exception as e:
        print(f"   ❌ eSpeak: No disponible - {e}")
        print("      Instala: sudo pacman -S espeak-ng  # Arch")
        print("      O:       sudo apt install espeak-ng  # Ubuntu/Debian")

def main():
    print("=" * 60)
    print("🔍 VERIFICACIÓN DE INSTALACIÓN")
    print("   Traductor de Señas Peruano v2.1")
    print("=" * 60)
    
    # Verificar Python
    python_ok = check_python_version()
    
    # Verificar paquetes principales
    print("\n📦 Verificando paquetes de Python:")
    
    packages = [
        ('OpenCV', 'cv2', lambda m: m.__version__),
        ('MediaPipe', 'mediapipe', lambda m: m.__version__),
        ('NumPy', 'numpy', lambda m: m.__version__),
        ('SciPy', 'scipy', lambda m: scipy.__version__),
        ('pyttsx3', 'pyttsx3', lambda m: 'OK'),
        ('JAX', 'jax', lambda m: m.__version__),
        ('JAXlib', 'jaxlib', lambda m: m.__version__),
    ]
    
    all_ok = True
    for package_name, import_name, version_getter in packages:
        if not check_package(package_name, import_name, version_getter):
            all_ok = False
    
    # Verificar dependencias del sistema
    check_system_dependencies()
    
    # Resumen
    print("\n" + "=" * 60)
    if all_ok and python_ok:
        print("✅ ¡INSTALACIÓN COMPLETA!")
        print("   Puedes ejecutar: python main.py")
    else:
        print("⚠️  HAY PROBLEMAS CON LA INSTALACIÓN")
        print("   Revisa los errores arriba y consulta INSTALACION.md")
    print("=" * 60)
    
    return 0 if (all_ok and python_ok) else 1

if __name__ == "__main__":
    sys.exit(main())
