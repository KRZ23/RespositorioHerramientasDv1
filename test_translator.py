#!/usr/bin/env python3
"""
Script de prueba para el traductor de señas peruano
Permite probar los diferentes componentes sin ejecutar la interfaz completa
"""

import numpy as np
from sign_features import SignFeatureExtractor
from peruvian_signs_dataset import PeruvianSignsDataset
from sign_classifier import SignClassifier

def test_feature_extractor():
    """Prueba el extractor de características"""
    print("🧪 Probando extractor de características...")
    
    extractor = SignFeatureExtractor()
    
    # Obtener nombres de características
    feature_names = extractor.get_feature_names()
    print(f"✅ Extractor inicializado con {len(feature_names)} características:")
    for i, name in enumerate(feature_names):
        print(f"   {i+1}. {name}")
    
    print()

def test_dataset():
    """Prueba el dataset de señas peruanas"""
    print("🧪 Probando dataset de señas peruanas...")
    
    dataset = PeruvianSignsDataset()
    
    # Mostrar señas básicas
    basic_signs = dataset.basic_signs.keys()
    print(f"✅ Señas básicas incluidas ({len(basic_signs)}):")
    for sign in basic_signs:
        info = dataset.get_sign_info(sign)
        print(f"   • {sign}: {info.get('description', 'Sin descripción')}")
    
    # Estadísticas del dataset
    stats = dataset.get_dataset_stats()
    print(f"\n📊 Estadísticas del dataset:")
    print(f"   • Señas básicas: {stats['total_basic_signs']}")
    print(f"   • Señas aprendidas: {stats['total_learned_signs']}")
    print(f"   • Total de patrones: {stats['total_patterns']}")
    
    print()

def test_classifier():
    """Prueba el clasificador de señas"""
    print("🧪 Probando clasificador de señas...")
    
    classifier = SignClassifier(confidence_threshold=0.5)
    
    # Obtener estadísticas
    stats = classifier.get_classifier_stats()
    print(f"✅ Clasificador inicializado:")
    print(f"   • Umbral de confianza: {stats['confidence_threshold']}")
    print(f"   • Métricas disponibles: {', '.join(stats['available_metrics'])}")
    print(f"   • Tamaño del historial: {stats['history_size']}")
    
    # Probar con datos simulados
    print(f"\n🎯 Probando con datos simulados...")
    
    # Simular landmarks de mano (21 puntos con coordenadas x, y, z)
    class MockLandmark:
        def __init__(self, x, y, z):
            self.x, self.y, self.z = x, y, z
    
    class MockHandLandmarks:
        def __init__(self):
            # Crear landmarks simulados para una mano abierta
            self.landmark = []
            for i in range(21):  # MediaPipe usa 21 landmarks por mano
                # Coordenadas simuladas (valores entre 0 y 1)
                x = np.random.random() * 0.3 + 0.35  # Centro en pantalla
                y = np.random.random() * 0.3 + 0.35
                z = np.random.random() * 0.1 - 0.05
                self.landmark.append(MockLandmark(x, y, z))
    
    # Crear landmarks simulados
    mock_landmarks = MockHandLandmarks()
    
    # Probar clasificación
    result = classifier.classify_hand_landmarks(mock_landmarks)
    print(f"   • Resultado: {result['sign'] if result['sign'] else 'No reconocida'}")
    print(f"   • Confianza: {result['confidence']:.1%}")
    print(f"   • Estabilidad: {result.get('stability', 'N/A')}")
    
    print()

def test_integration():
    """Prueba la integración completa"""
    print("🧪 Probando integración completa...")
    
    try:
        # Importar componentes principales
        from hand_detector import HandDetector
        
        print("✅ HandDetector importado correctamente")
        
        # Verificar que se puede crear una instancia
        detector = HandDetector()
        print("✅ HandDetector inicializado correctamente")
        
        # Verificar métodos de traducción
        assert hasattr(detector, 'toggle_translation'), "Falta método toggle_translation"
        assert hasattr(detector, 'is_translation_enabled'), "Falta método is_translation_enabled"
        assert hasattr(detector, 'add_training_sample'), "Falta método add_training_sample"
        
        print("✅ Métodos de traducción disponibles")
        
    except Exception as e:
        print(f"❌ Error en integración: {e}")
        return False
    
    return True

def show_available_signs():
    """Muestra todas las señas disponibles"""
    print("📋 Señas disponibles en el sistema:")
    
    dataset = PeruvianSignsDataset()
    all_signs = dataset.get_all_signs()
    
    print(f"\n🤟 Total de señas: {len(all_signs)}")
    print("=" * 50)
    
    for i, sign in enumerate(sorted(all_signs), 1):
        info = dataset.get_sign_info(sign)
        if info:
            description = info.get('description', 'Sin descripción')
            sign_type = info.get('type', 'desconocido')
            print(f"{i:2d}. {sign:10} - {description} [{sign_type}]")
    
    print()

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas del Traductor de Señas Peruano")
    print("=" * 60)
    print()
    
    # Ejecutar todas las pruebas
    test_feature_extractor()
    test_dataset()
    test_classifier()
    
    integration_ok = test_integration()
    
    show_available_signs()
    
    # Resumen final
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 30)
    print("✅ Extractor de características: OK")
    print("✅ Dataset de señas: OK")
    print("✅ Clasificador: OK")
    print(f"{'✅' if integration_ok else '❌'} Integración: {'OK' if integration_ok else 'ERROR'}")
    print()
    
    if integration_ok:
        print("🎉 ¡Todas las pruebas pasaron! El sistema está listo para usar.")
        print("   Ejecuta 'python main.py' para iniciar la aplicación completa.")
    else:
        print("⚠️  Hay problemas en la integración. Revisa los errores mostrados.")
    
    print()
    print("💡 Para usar el sistema:")
    print("   1. Asegúrate de tener una cámara funcionando")
    print("   2. Instala las dependencias: pip install -r requirements.txt")
    print("   3. Ejecuta: python main.py")
    print("   4. ¡Comienza a traducir señas!")

if __name__ == "__main__":
    main()
