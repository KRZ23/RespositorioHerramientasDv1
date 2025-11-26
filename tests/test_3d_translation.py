#!/usr/bin/env python3
"""
Script de prueba para el sistema de traducción texto → señas 3D

Prueba:
1. Carga del dataset de landmarks 3D
2. Traducción de texto a secuencia de landmarks
3. Visualización 3D básica
"""

from landmarks_3d_manager import Landmarks3DManager, SignTo3DTranslator
from hand_3d_visualizer import Hand3DVisualizer


def test_landmarks_manager():
    """Prueba el gestor de landmarks 3D"""
    print("=" * 50)
    print("TEST 1: Gestor de Landmarks 3D")
    print("=" * 50)
    
    manager = Landmarks3DManager()
    signs = manager.get_all_signs()
    
    print(f"\n✓ Señas en dataset 3D: {len(signs)}")
    
    if signs:
        print("\nSeñas disponibles:")
        for sign in signs:
            sign_type = manager.get_sign_type(sign)
            sign_data = manager.get_sign_landmarks(sign)
            frame_count = len(sign_data.get('frames', []))
            print(f"  • {sign} ({sign_type}) - {frame_count} frame(s)")
    else:
        print("\n⚠ No hay señas en el dataset 3D")
        print("   Entrena algunas señas usando la interfaz principal primero")
    
    return manager


def test_translator(manager):
    """Prueba el traductor texto → landmarks"""
    print("\n" + "=" * 50)
    print("TEST 2: Traductor Texto → Landmarks")
    print("=" * 50)
    
    translator = SignTo3DTranslator(manager)
    
    # Texto de prueba
    test_texts = [
        "HOLA",
        "HOLA OKEY",
        "SILENCIO",
        "PALABRA_NO_EXISTE"
    ]
    
    for text in test_texts:
        print(f"\n📝 Texto: '{text}'")
        sequence = translator.text_to_landmarks_sequence(text)
        
        if sequence:
            print(f"   ✓ Secuencia generada: {len(sequence)} seña(s)")
            for i, sign_data in enumerate(sequence, 1):
                sign = sign_data['sign']
                sign_type = sign_data['type']
                duration = sign_data['duration']
                has_frames = sign_data['frames'] is not None
                print(f"     {i}. {sign} ({sign_type}) - {duration}s - Frames: {has_frames}")
        else:
            print("   ✗ No se pudo generar secuencia")
    
    return translator


def test_visualization(manager):
    """Prueba la visualización 3D"""
    print("\n" + "=" * 50)
    print("TEST 3: Visualización 3D")
    print("=" * 50)
    
    signs = manager.get_all_signs()
    
    if not signs:
        print("\n⚠ No hay señas para visualizar")
        return
    
    print(f"\n✓ Se pueden visualizar {len(signs)} seña(s)")
    print("\nPara visualizar:")
    print("  1. Ejecuta: python hand_3d_visualizer.py")
    print("  2. O ejecuta: python text_to_sign_interface.py (interfaz completa)")


def main():
    """Función principal de pruebas"""
    print("\n🎭 PRUEBA DEL SISTEMA DE TRADUCCIÓN TEXTO → SEÑAS 3D\n")
    
    try:
        # Test 1: Manager
        manager = test_landmarks_manager()
        
        # Test 2: Translator
        translator = test_translator(manager)
        
        # Test 3: Visualization
        test_visualization(manager)
        
        print("\n" + "=" * 50)
        print("RESUMEN")
        print("=" * 50)
        
        signs = manager.get_all_signs()
        print(f"\n✓ Sistema de traducción 3D operativo")
        print(f"✓ {len(signs)} seña(s) disponible(s) para animación")
        
        if signs:
            print("\n🎬 Para usar el traductor:")
            print("   python text_to_sign_interface.py")
            print("\n📊 Para visualizar señas individuales:")
            print("   python hand_3d_visualizer.py")
        else:
            print("\n⚠ ACCIÓN REQUERIDA:")
            print("   1. Ejecuta: python main.py")
            print("   2. Entrena algunas señas (estáticas o dinámicas)")
            print("   3. Los landmarks 3D se guardarán automáticamente")
            print("   4. Luego ejecuta: python text_to_sign_interface.py")
        
        print("\n✅ Pruebas completadas\n")
        
    except Exception as e:
        print(f"\n❌ Error en pruebas: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
