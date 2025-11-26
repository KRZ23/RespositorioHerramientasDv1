#!/usr/bin/env python3
"""
Script para migrar señas existentes a formato 3D
Nota: Solo puede generar aproximaciones basadas en features,
no son los landmarks 3D reales capturados.
"""

import json
import numpy as np
from landmarks_3d_manager import Landmarks3DManager


def reconstruct_landmarks_from_features(features):
    """
    Intenta reconstruir landmarks 3D aproximados desde features
    
    NOTA: Esto es una APROXIMACIÓN. Los landmarks reales solo se obtienen
    durante el entrenamiento real con MediaPipe.
    
    Las features son distancias y ángulos, no coordenadas exactas,
    por lo que esta reconstrucción es solo ilustrativa.
    """
    # Features estructura:
    # 0-8: distancias entre puntos
    # 9-12: ángulos entre dedos
    # 13-16: información adicional
    
    # Crear una pose base (mano abierta)
    base_landmarks = np.array([
        [0.5, 0.5, 0.0],     # 0: Muñeca
        [0.45, 0.45, 0.02],  # 1-4: Pulgar
        [0.4, 0.4, 0.04],
        [0.35, 0.35, 0.05],
        [0.3, 0.3, 0.05],
        [0.5, 0.3, 0.0],     # 5-8: Índice
        [0.5, 0.2, 0.0],
        [0.5, 0.1, 0.0],
        [0.5, 0.05, 0.0],
        [0.55, 0.3, 0.0],    # 9-12: Medio
        [0.55, 0.18, 0.0],
        [0.55, 0.08, 0.0],
        [0.55, 0.03, 0.0],
        [0.6, 0.32, 0.0],    # 13-16: Anular
        [0.6, 0.22, 0.0],
        [0.6, 0.13, 0.0],
        [0.6, 0.08, 0.0],
        [0.65, 0.35, 0.0],   # 17-20: Meñique
        [0.65, 0.27, 0.0],
        [0.65, 0.20, 0.0],
        [0.65, 0.15, 0.0],
    ])
    
    # Modificar pose base usando features (simplificado)
    features = np.array(features)
    
    # Usar las primeras features (distancias) para ajustar posiciones
    scale_factors = features[:9] / 0.3  # Normalizar
    
    # Ajustar dedos según escalas
    finger_groups = [
        [1, 2, 3, 4],      # Pulgar
        [5, 6, 7, 8],      # Índice
        [9, 10, 11, 12],   # Medio
        [13, 14, 15, 16],  # Anular
        [17, 18, 19, 20],  # Meñique
    ]
    
    for i, group in enumerate(finger_groups):
        if i < len(scale_factors):
            scale = scale_factors[i]
            for idx in group:
                # Aplicar escala suave
                base_landmarks[idx] *= (1.0 + (scale - 1.0) * 0.3)
    
    # Normalizar para mantener en rango [0, 1]
    base_landmarks[:, :2] = np.clip(base_landmarks[:, :2], 0.0, 1.0)
    base_landmarks[:, 2] = np.clip(base_landmarks[:, 2], -0.3, 0.3)
    
    return base_landmarks.tolist()


def migrate_signs_to_3d():
    """Migra señas del dataset antiguo al formato 3D"""
    
    print("=" * 60)
    print("MIGRACIÓN DE SEÑAS A FORMATO 3D")
    print("=" * 60)
    print()
    print("⚠️  IMPORTANTE:")
    print("Este script genera APROXIMACIONES de landmarks 3D")
    print("Para obtener landmarks 3D REALES, entrena las señas nuevamente")
    print()
    
    # Cargar dataset antiguo
    try:
        with open('signs_dataset.json', 'r', encoding='utf-8') as f:
            old_dataset = json.load(f)
    except FileNotFoundError:
        print("❌ No se encontró signs_dataset.json")
        return
    
    if not old_dataset:
        print("❌ El dataset está vacío")
        return
    
    print(f"✓ Encontradas {len(old_dataset)} señas en signs_dataset.json\n")
    
    # Inicializar manager 3D
    manager = Landmarks3DManager()
    
    migrated_count = 0
    skipped_count = 0
    
    for sign_name, sign_data in old_dataset.items():
        patterns = sign_data.get('patterns', [])
        description = sign_data.get('description', '')
        
        if not patterns:
            print(f"⚠️  {sign_name}: Sin patrones, omitiendo")
            skipped_count += 1
            continue
        
        # Tomar el primer patrón (más entrenado)
        features = patterns[0]
        
        # Reconstruir landmarks aproximados
        try:
            landmarks_3d = reconstruct_landmarks_from_features(features)
            
            # Guardar en formato 3D (como seña estática)
            success = manager.save_static_sign(
                sign_name,
                # Convertir lista a objetos simulados con atributos x, y, z
                [type('Landmark', (), {'x': p[0], 'y': p[1], 'z': p[2]}) for p in landmarks_3d],
                f"{description} (migrada - aproximada)"
            )
            
            if success:
                print(f"✓ {sign_name}: Migrada exitosamente")
                migrated_count += 1
            else:
                print(f"✗ {sign_name}: Error al guardar")
                skipped_count += 1
                
        except Exception as e:
            print(f"✗ {sign_name}: Error - {e}")
            skipped_count += 1
    
    print()
    print("=" * 60)
    print("RESUMEN DE MIGRACIÓN")
    print("=" * 60)
    print(f"✓ Migradas exitosamente: {migrated_count}")
    print(f"⚠️  Omitidas: {skipped_count}")
    print()
    
    if migrated_count > 0:
        print("✅ Migración completada")
        print()
        print("NOTA: Los landmarks 3D generados son APROXIMACIONES")
        print("Para obtener animaciones de mejor calidad:")
        print("  1. Ejecuta: python main.py")
        print("  2. Re-entrena las señas importantes")
        print("  3. Los landmarks 3D reales se capturarán automáticamente")
        print()
        print("Ahora puedes probar:")
        print("  • python hand_3d_visualizer.py - Ver señas individuales")
        print("  • python text_to_sign_interface.py - Traductor completo")
    else:
        print("❌ No se pudo migrar ninguna seña")


if __name__ == "__main__":
    migrate_signs_to_3d()
