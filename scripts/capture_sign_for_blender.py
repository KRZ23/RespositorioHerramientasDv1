#!/usr/bin/env python3
"""
Script de captura rápida: Entrena UNA seña estática para Blender
Captura landmarks 3D REALES con profundidad
"""

import sys
import os
import cv2

# Agregar ruta del proyecto (directorio padre del script)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.core.hand_detector import HandDetector
from src.core.landmarks_3d_manager import Landmarks3DManager

def capture_sign_for_blender():
    """Captura una seña estática con landmarks 3D reales"""
    
    print("\n" + "="*70)
    print("📸 CAPTURA RÁPIDA DE SEÑA PARA BLENDER")
    print("="*70)
    print("\nInstrucciones:")
    print("1. Muestra tu mano haciendo una seña (ej: pulgar arriba 👍)")
    print("2. Mantén la mano quieta")
    print("3. Presiona ESPACIO para capturar")
    print("4. Se capturarán 3 muestras")
    print("5. Presiona ESC para salir\n")
    
    sign_name = input("📝 Nombre de la seña (ej: THUMBS_UP, PEACE, OK): ").strip().upper()
    
    if not sign_name:
        print("❌ Nombre inválido")
        return
    
    print(f"\n✅ Capturando seña: {sign_name}")
    print("🎥 Iniciando cámara...\n")
    
    # Inicializar detector
    detector = HandDetector()
    
    # Abrir cámara
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Error: No se pudo abrir la cámara")
        return
    
    samples_captured = 0
    target_samples = 3
    capturing = False
    
    print("📹 Cámara activa. Presiona ESPACIO para capturar, ESC para salir")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Procesar frame
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = detector.hands.process(frame_rgb)
        
        # Dibujar landmarks si se detecta mano
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                detector.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    detector.mp_hands.HAND_CONNECTIONS
                )
            
            # Mostrar instrucción
            if samples_captured < target_samples:
                cv2.putText(frame, f"Muestras: {samples_captured}/{target_samples}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, "Presiona ESPACIO para capturar", 
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            else:
                cv2.putText(frame, "CAPTURA COMPLETA! Presiona ESC", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "No se detecta mano", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Mostrar frame
        cv2.imshow('Captura de Seña para Blender', frame)
        
        # Capturar al presionar ESPACIO
        key = cv2.waitKey(1) & 0xFF
        
        if key == 32 and samples_captured < target_samples:  # ESPACIO
            if results.multi_hand_landmarks:
                # Obtener landmarks 3D
                hand_landmarks = results.multi_hand_landmarks[0]
                landmarks_3d = detector.landmarks_3d_manager.extract_landmarks_3d(hand_landmarks)
                
                # Guardar
                detector.landmarks_3d_manager.save_static_sign(
                    sign_name=sign_name,
                    hand_landmarks=[hand_landmarks],
                    description=f"Seña capturada para Blender - Muestra {samples_captured + 1}",
                    num_hands=1
                )
                
                samples_captured += 1
                print(f"✅ Muestra {samples_captured}/{target_samples} capturada!")
                
                # Mostrar profundidad Z
                print(f"   Profundidad Z: min={min(p[2] for p in landmarks_3d):.4f}, "
                      f"max={max(p[2] for p in landmarks_3d):.4f}")
                
                if samples_captured >= target_samples:
                    print(f"\n🎉 ¡Captura completa! Seña '{sign_name}' guardada")
                    print("📊 Ahora puedes visualizarla en Blender")
                    break
            else:
                print("⚠️ No se detectó mano, intenta de nuevo")
        
        elif key == 27:  # ESC
            print("\n❌ Captura cancelada")
            break
    
    # Liberar recursos
    cap.release()
    cv2.destroyAllWindows()
    
    if samples_captured > 0:
        print(f"\n✅ Seña '{sign_name}' guardada con {samples_captured} muestras")
        print(f"\n📝 Para visualizar en Blender, ejecuta:")
        print(f"   blender -b -P scripts/blender/visualize_sign.py -- {sign_name}")
    else:
        print("\n❌ No se capturó ninguna muestra")


if __name__ == "__main__":
    capture_sign_for_blender()
