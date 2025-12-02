#!/usr/bin/env python3
"""
Script para Re-entrenar Señas con Múltiples Muestras
Mejora el reconocimiento capturando varias versiones de cada seña
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cv2
import json
from src.core.hand_detector import HandDetector
from src.core.sign_features import SignFeatureExtractor
import time

class SignRetrainer:
    def __init__(self):
        self.detector = HandDetector(show_window=False)
        self.feature_extractor = SignFeatureExtractor()
        self.dataset_path = "data/signs_dataset.json"
        
    def load_dataset(self):
        """Carga el dataset existente"""
        if os.path.exists(self.dataset_path):
            with open(self.dataset_path, 'r') as f:
                return json.load(f)
        return {}
    
    def save_dataset(self, data):
        """Guarda el dataset"""
        with open(self.dataset_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def capture_samples(self, sign_name, num_samples=5):
        """Captura múltiples muestras de una seña"""
        print(f"\n{'='*70}")
        print(f"📸 CAPTURANDO {num_samples} MUESTRAS DE: {sign_name}")
        print(f"{'='*70}\n")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Error: No se puede abrir la cámara")
            return []
        
        samples = []
        captured = 0
        
        print("Instrucciones:")
        print(f"  • Haz la seña '{sign_name}' frente a la cámara")
        print(f"  • Presiona ESPACIO para capturar cada muestra ({num_samples} en total)")
        print("  • Varía ligeramente la posición, ángulo o distancia")
        print("  • Presiona ESC para cancelar")
        print("\n⏳ Preparando cámara...")
        
        # Inicializar MediaPipe
        if not self.detector.mp_hands:
            self.detector._init_mediapipe()
        
        time.sleep(1)
        print("✅ Cámara lista. ¡Empieza!\n")
        
        while captured < num_samples:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Procesar frame
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.detector.hands.process(frame_rgb)
            
            # Dibujar landmarks si hay manos
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.detector.mp_draw.draw_landmarks(
                        frame,
                        hand_landmarks,
                        self.detector.mp_hands.HAND_CONNECTIONS
                    )
            
            # Mostrar estado
            status_text = f"Muestras: {captured}/{num_samples} - ESPACIO para capturar | ESC para salir"
            cv2.putText(frame, status_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            if results.multi_hand_landmarks:
                cv2.putText(frame, "MANO DETECTADA", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "Sin mano", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            cv2.imshow(f'Re-entrenar: {sign_name}', frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            # ESPACIO: capturar
            if key == 32 and results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                feature_vector = self.feature_extractor.extract_features(hand_landmarks)
                
                if feature_vector is not None:
                    samples.append(feature_vector.tolist())
                    captured += 1
                    print(f"  ✅ Muestra {captured}/{num_samples} capturada")
                    
                    # Feedback visual
                    frame_copy = frame.copy()
                    cv2.putText(frame_copy, "CAPTURADO!", (frame.shape[1]//2 - 100, frame.shape[0]//2),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                    cv2.imshow(f'Re-entrenar: {sign_name}', frame_copy)
                    cv2.waitKey(500)  # Pausa de 0.5s
                else:
                    print("  ⚠️  Error extrayendo características, inténtalo de nuevo")
            
            # ESC: cancelar
            elif key == 27:
                print("\n⚠️  Captura cancelada")
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        if captured == num_samples:
            print(f"\n✅ {captured} muestras capturadas exitosamente")
        else:
            print(f"\n⚠️  Solo se capturaron {captured}/{num_samples} muestras")
        
        return samples
    
    def retrain_sign(self, sign_name, num_samples=5):
        """Re-entrena una seña específica"""
        # Capturar muestras
        samples = self.capture_samples(sign_name, num_samples)
        
        if not samples:
            print(f"❌ No se capturaron muestras para {sign_name}")
            return False
        
        # Cargar dataset
        data = self.load_dataset()
        
        # Actualizar o agregar seña
        if sign_name in data:
            # Mantener descripción existente si hay
            description = data[sign_name].get('description', f'Seña re-entrenada con {len(samples)} muestras')
        else:
            description = f'Seña entrenada con {len(samples)} muestras'
        
        data[sign_name] = {
            'patterns': samples,
            'description': description,
            'count': len(samples)
        }
        
        # Guardar
        self.save_dataset(data)
        
        print(f"\n✅ {sign_name} actualizada con {len(samples)} muestras")
        return True
    
    def retrain_all_signs(self, num_samples=5):
        """Re-entrena todas las señas del dataset"""
        data = self.load_dataset()
        signs = list(data.keys())
        
        if not signs:
            print("❌ No hay señas en el dataset")
            return
        
        print(f"\n{'='*70}")
        print(f"🎯 RE-ENTRENAMIENTO COMPLETO")
        print(f"{'='*70}")
        print(f"\nTotal de señas: {len(signs)}")
        print(f"Muestras por seña: {num_samples}")
        print(f"\nEsto tomará aproximadamente {len(signs) * num_samples * 5} segundos")
        print(f"({'~' + str(len(signs) * num_samples * 5 // 60)} minutos)\n")
        
        response = input("¿Continuar? (s/n) [s]: ").strip().lower()
        if response not in ['', 's', 'si', 'y', 'yes']:
            print("❌ Cancelado")
            return
        
        success_count = 0
        
        for i, sign in enumerate(signs, 1):
            print(f"\n[{i}/{len(signs)}] Procesando: {sign}")
            if self.retrain_sign(sign, num_samples):
                success_count += 1
        
        print(f"\n{'='*70}")
        print(f"✅ RE-ENTRENAMIENTO COMPLETADO")
        print(f"{'='*70}")
        print(f"\nSeñas actualizadas: {success_count}/{len(signs)}")
        print(f"\nAhora prueba: ./run.sh (Opción 2)")


def main():
    """Función principal"""
    print("\n" + "="*70)
    print("🎓 RE-ENTRENAMIENTO DE SEÑAS")
    print("="*70 + "\n")
    
    retrainer = SignRetrainer()
    data = retrainer.load_dataset()
    signs = list(data.keys())
    
    if not signs:
        print("❌ No hay señas en el dataset para re-entrenar")
        print("   Primero entrena algunas señas con: ./run.sh (Opción 4)")
        return
    
    print("Opciones:\n")
    print("1) Re-entrenar UNA seña específica")
    print("2) Re-entrenar TODAS las señas")
    print("0) Cancelar\n")
    
    choice = input("Selecciona opción [1]: ").strip() or "1"
    
    if choice == "1":
        # Mostrar señas disponibles
        print("\nSeñas disponibles:\n")
        for i, sign in enumerate(signs, 1):
            count = data[sign].get('count', 0)
            print(f"  {i:2d}. {sign:15s} (muestras actuales: {count})")
        
        print()
        sign_input = input("Nombre de la seña a re-entrenar: ").strip().upper()
        
        if sign_input not in signs:
            print(f"❌ '{sign_input}' no existe en el dataset")
            return
        
        num_samples = input("¿Cuántas muestras capturar? [5]: ").strip() or "5"
        try:
            num_samples = int(num_samples)
        except:
            num_samples = 5
        
        retrainer.retrain_sign(sign_input, num_samples)
        
    elif choice == "2":
        num_samples = input("¿Cuántas muestras por seña? [5]: ").strip() or "5"
        try:
            num_samples = int(num_samples)
        except:
            num_samples = 5
        
        retrainer.retrain_all_signs(num_samples)
    
    else:
        print("❌ Cancelado")


if __name__ == "__main__":
    main()
