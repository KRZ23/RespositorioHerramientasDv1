#!/usr/bin/env python3
"""
Script de Diagnóstico y Mejora del Reconocimiento de Señas
Analiza el dataset y proporciona herramientas para mejorar la detección
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import numpy as np
from scipy.spatial.distance import cosine, euclidean

def analyze_dataset():
    """Analiza el dataset de señas"""
    print("\n" + "="*70)
    print("📊 ANÁLISIS DEL DATASET DE SEÑAS")
    print("="*70 + "\n")
    
    dataset_path = "data/signs_dataset.json"
    
    if not os.path.exists(dataset_path):
        print(f"❌ No se encuentra el dataset: {dataset_path}")
        return
    
    with open(dataset_path, 'r') as f:
        data = json.load(f)
    
    print(f"Total de señas: {len(data)}\n")
    
    # Análisis por seña
    issues = []
    
    for sign_name, sign_data in sorted(data.items()):
        count = sign_data.get('count', 0)
        patterns = sign_data.get('patterns', [])
        num_patterns = len(patterns)
        
        # Detectar problemas
        status = "✅"
        problem = None
        
        if num_patterns == 0:
            status = "❌"
            problem = "Sin patrones"
            issues.append((sign_name, problem))
        elif num_patterns < 3:
            status = "⚠️"
            problem = f"Pocas muestras ({num_patterns})"
            issues.append((sign_name, problem))
        elif num_patterns != count:
            status = "⚠️"
            problem = f"Inconsistencia: count={count}, patterns={num_patterns}"
        
        print(f"{status} {sign_name:15s} - Muestras: {num_patterns:2d} {f'({problem})' if problem else ''}")
    
    # Resumen de problemas
    print("\n" + "="*70)
    print("🔍 PROBLEMAS DETECTADOS")
    print("="*70 + "\n")
    
    if not issues:
        print("✅ No se detectaron problemas graves")
    else:
        print(f"Total de problemas: {len(issues)}\n")
        for sign, problem in issues:
            print(f"  • {sign}: {problem}")
    
    # Análisis de diversidad entre señas
    print("\n" + "="*70)
    print("📐 ANÁLISIS DE SIMILITUD ENTRE SEÑAS")
    print("="*70 + "\n")
    
    analyze_sign_similarity(data)
    
    # Recomendaciones
    print("\n" + "="*70)
    print("💡 RECOMENDACIONES")
    print("="*70 + "\n")
    
    if issues:
        print("1. ⚠️  Dataset insuficiente para reconocimiento robusto")
        print("   - Cada seña debería tener al menos 5-10 muestras")
        print("   - Actualmente la mayoría tiene solo 1 muestra")
        print()
        print("2. 🎯 Solución: Re-entrenar señas con más variaciones:")
        print("   - Diferentes ángulos de la cámara")
        print("   - Diferentes posiciones de la mano")
        print("   - Diferentes velocidades de ejecución")
        print()
        print("3. 🔧 Opciones para mejorar:")
        print("   a) Usar ./run.sh → Opción 4 (Entrenar Nueva Seña)")
        print("   b) Ejecutar: python scripts/retrain_signs.py")
        print("   c) Ajustar umbral de confianza (actualmente muy alto)")
        print()
        print("4. ⚡ Solución rápida: Reducir umbral de confianza")
        print("   - Editar src/core/hand_detector.py")
        print("   - Cambiar confidence_threshold de 0.7 a 0.4")


def analyze_sign_similarity(data):
    """Analiza similitud entre señas para detectar confusiones"""
    signs = list(data.keys())
    
    if len(signs) < 2:
        print("ℹ️  Necesitas al menos 2 señas para análisis de similitud")
        return
    
    # Calcular distancias entre primeros patrones de cada seña
    similarities = []
    
    for i, sign1 in enumerate(signs):
        for j, sign2 in enumerate(signs[i+1:], i+1):
            patterns1 = data[sign1].get('patterns', [])
            patterns2 = data[sign2].get('patterns', [])
            
            if patterns1 and patterns2:
                p1 = np.array(patterns1[0])
                p2 = np.array(patterns2[0])
                
                # Calcular similitud coseno
                sim = 1 - cosine(p1, p2)
                similarities.append((sign1, sign2, sim))
    
    # Mostrar señas más similares (posibles confusiones)
    similarities.sort(key=lambda x: x[2], reverse=True)
    
    print("Señas más similares (posible confusión):\n")
    
    for sign1, sign2, sim in similarities[:5]:
        status = "🔴" if sim > 0.9 else ("🟡" if sim > 0.8 else "🟢")
        print(f"  {status} {sign1:12s} ↔ {sign2:12s} : {sim:.3f}")
    
    if similarities and similarities[0][2] > 0.9:
        print(f"\n⚠️  ALERTA: {similarities[0][0]} y {similarities[0][1]} son muy similares")
        print("   Esto puede causar confusiones en el reconocimiento")


def suggest_improvements():
    """Sugiere mejoras específicas"""
    print("\n" + "="*70)
    print("🔧 AJUSTES RECOMENDADOS PARA MEJORAR DETECCIÓN")
    print("="*70 + "\n")
    
    print("1. 📉 REDUCIR UMBRAL DE CONFIANZA (Solución rápida)")
    print("   Archivo: src/core/hand_detector.py")
    print("   Cambiar: confidence_threshold=0.7")
    print("   Por:     confidence_threshold=0.4  # Más permisivo")
    print()
    
    print("2. 📊 REDUCIR FRAMES ESTABLES (Más sensible)")
    print("   Archivo: src/core/sign_classifier.py")
    print("   Cambiar: self.stable_frames = 3")
    print("   Por:     self.stable_frames = 2  # Confirma más rápido")
    print()
    
    print("3. 🎯 AJUSTAR PESOS DE MÉTRICAS")
    print("   Archivo: src/core/sign_classifier.py")
    print("   Si algunas señas tienen patrones muy distintos,")
    print("   aumentar peso de 'euclidean' y reducir 'cosine'")
    print()
    
    print("4. 📈 AUMENTAR TAMAÑO DE HISTORIAL")
    print("   Archivo: src/core/sign_classifier.py")
    print("   Cambiar: self.history_size = 5")
    print("   Por:     self.history_size = 8  # Más suavizado")
    print()


def quick_fix():
    """Aplica correcciones rápidas al sistema"""
    print("\n" + "="*70)
    print("⚡ APLICANDO CORRECCIONES RÁPIDAS")
    print("="*70 + "\n")
    
    # Leer hand_detector.py
    detector_path = "src/core/hand_detector.py"
    
    try:
        with open(detector_path, 'r') as f:
            content = f.read()
        
        # Verificar umbral actual
        if 'confidence_threshold=0.7' in content:
            print("📝 Ajustando umbral de confianza de 0.7 a 0.4...")
            new_content = content.replace(
                'confidence_threshold=0.7',
                'confidence_threshold=0.4'
            )
            
            # Hacer backup
            backup_path = detector_path + '.backup'
            with open(backup_path, 'w') as f:
                f.write(content)
            print(f"💾 Backup guardado: {backup_path}")
            
            # Guardar cambios
            with open(detector_path, 'w') as f:
                f.write(new_content)
            
            print("✅ Umbral ajustado correctamente")
            print("   Esto hará que el sistema sea más sensible")
            print("   y detecte más señas, aunque con menor precisión")
        else:
            print("ℹ️  El umbral ya fue modificado o no se encontró")
        
        # Ajustar stable_frames
        classifier_path = "src/core/sign_classifier.py"
        with open(classifier_path, 'r') as f:
            content = f.read()
        
        if 'self.stable_frames = 3' in content:
            print("\n📝 Ajustando frames estables de 3 a 2...")
            new_content = content.replace(
                'self.stable_frames = 3',
                'self.stable_frames = 2'
            )
            
            backup_path = classifier_path + '.backup'
            with open(backup_path, 'w') as f:
                f.write(content)
            
            with open(classifier_path, 'w') as f:
                f.write(new_content)
            
            print("✅ Frames estables ajustados")
        
        print("\n" + "="*70)
        print("✅ CORRECCIONES APLICADAS")
        print("="*70)
        print("\nPrueba ahora con: ./run.sh (Opción 2)")
        print("El sistema debería detectar más señas")
        
    except Exception as e:
        print(f"❌ Error al aplicar correcciones: {e}")


def main():
    """Función principal"""
    print("\n🔍 DIAGNÓSTICO DEL SISTEMA DE RECONOCIMIENTO DE SEÑAS\n")
    
    # Análisis
    analyze_dataset()
    suggest_improvements()
    
    # Preguntar si aplicar correcciones
    print("\n" + "="*70)
    response = input("\n¿Aplicar correcciones rápidas automáticamente? (s/n) [s]: ").strip().lower()
    
    if response in ['', 's', 'si', 'y', 'yes']:
        quick_fix()
    else:
        print("\n✅ Puedes aplicar las correcciones manualmente")
        print("   Consulta las recomendaciones arriba")
    
    print()


if __name__ == "__main__":
    main()
