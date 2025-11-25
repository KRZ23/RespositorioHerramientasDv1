#!/usr/bin/env python3
"""
Demostración visual del sistema mejorado de traducción 3D
Muestra las mejoras en la visualización con colores por dedo
"""

from landmarks_3d_manager import Landmarks3DManager, SignTo3DTranslator
from hand_3d_visualizer import Hand3DVisualizer
import sys


def demo_visual_improvements():
    """Demuestra las mejoras visuales"""
    print("=" * 60)
    print("🎨 DEMOSTRACIÓN DE MEJORAS VISUALES 3D")
    print("=" * 60)
    print()
    print("✨ Nuevas características:")
    print("   • Colores por dedo:")
    print("     - 🔴 Pulgar: Rojo")
    print("     - 🟠 Índice: Naranja")
    print("     - 🟢 Medio: Verde")
    print("     - 🔵 Anular: Azul")
    print("     - 🟣 Meñique: Púrpura")
    print("     - ⚪ Palma: Gris")
    print()
    print("   • Articulaciones destacadas:")
    print("     - Muñeca: Grande y negra")
    print("     - Bases: Medianas")
    print("     - Puntas: Coloreadas")
    print()
    print("   • Soporte para 2 manos:")
    print("     - Detección automática de 1 o 2 manos")
    print("     - Visualización simultánea")
    print()
    print("   • Líneas más gruesas y visibles")
    print("   • Bordes blancos para mejor contraste")
    print()
    print("=" * 60)
    print()
    
    # Cargar manager
    manager = Landmarks3DManager()
    signs = manager.get_all_signs()
    
    if not signs:
        print("⚠️  No hay señas en el dataset para visualizar")
        print("   Entrena algunas señas primero: python main.py")
        return
    
    print(f"✓ {len(signs)} seña(s) disponible(s) para visualización mejorada")
    print()
    
    # Mostrar menú
    print("¿Qué quieres hacer?")
    print("1. Ver una seña específica (visualización mejorada)")
    print("2. Ver todas las señas secuencialmente")
    print("3. Animar texto completo")
    print()
    
    choice = input("Opción (1-3): ").strip()
    
    visualizer = Hand3DVisualizer()
    
    if choice == "1":
        # Ver seña específica
        print()
        print("Señas disponibles:")
        for i, sign in enumerate(sorted(signs), 1):
            sign_type = manager.get_sign_type(sign)
            sign_data = manager.get_sign_landmarks(sign)
            num_hands = sign_data.get('num_hands', 1)
            hands_text = f"{num_hands} mano(s)"
            print(f"  {i}. {sign} ({sign_type}) - {hands_text}")
        print()
        
        sign_name = input("Nombre de la seña: ").strip().upper()
        
        sign_data = manager.get_sign_landmarks(sign_name)
        if sign_data:
            num_hands = sign_data.get('num_hands', 1)
            print()
            print(f"📊 Mostrando: {sign_name}")
            print(f"   Tipo: {sign_data.get('type', 'unknown')}")
            print(f"   Manos: {num_hands}")
            print()
            print("💡 Observa:")
            print("   • Cada dedo tiene un color diferente")
            print("   • Las articulaciones tienen diferentes tamaños")
            print("   • Las líneas son más gruesas y visibles")
            if num_hands > 1:
                print("   • Dos manos se muestran simultáneamente")
            print()
        
        visualizer.show_sign(sign_name, manager)
        visualizer.show()
        
    elif choice == "2":
        # Ver todas las señas
        print()
        print("🎬 Mostrando todas las señas secuencialmente...")
        print("   Presiona Enter para continuar a la siguiente")
        print()
        
        import matplotlib.pyplot as plt
        plt.ion()
        
        for i, sign in enumerate(sorted(signs), 1):
            sign_data = manager.get_sign_landmarks(sign)
            num_hands = sign_data.get('num_hands', 1)
            sign_type = sign_data.get('type', 'unknown')
            
            print(f"{i}/{len(signs)}: {sign} ({sign_type}) - {num_hands} mano(s)")
            visualizer.show_sign(sign, manager)
            input("   Presiona Enter para continuar...")
        
        plt.ioff()
        visualizer.show()
        
    elif choice == "3":
        # Animar texto
        print()
        text = input("Texto a traducir: ").strip()
        
        translator = SignTo3DTranslator(manager)
        
        print()
        print(f"🎬 Animando: {text}")
        print("   Observa cómo cada seña se muestra con colores distintos")
        print()
        
        visualizer.animate_text(text, translator)
        visualizer.show()
    
    else:
        print("❌ Opción inválida")
    
    visualizer.close()


if __name__ == "__main__":
    demo_visual_improvements()
