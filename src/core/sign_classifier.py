import numpy as np
from scipy.spatial.distance import cosine, euclidean
from scipy.stats import pearsonr
from src.core.sign_features import SignFeatureExtractor
from src.utils.peruvian_signs_dataset import PeruvianSignsDataset
import time

class SignClassifier:
    """
    Clasificador de señas del lenguaje de señas peruano.
    Utiliza múltiples métricas para clasificar vectores de características.
    """
    
    def __init__(self, confidence_threshold=0.7):
        """
        Inicializa el clasificador
        
        Args:
            confidence_threshold (float): Umbral mínimo de confianza para clasificar
        """
        self.feature_extractor = SignFeatureExtractor()
        self.dataset = PeruvianSignsDataset()
        self.confidence_threshold = confidence_threshold
        
        # Historial para suavizado temporal
        self.prediction_history = []
        self.history_size = 5
        self.stable_frames = 3  # Frames consistentes para confirmar una seña
        
        # Métricas de clasificación
        self.classification_metrics = {
            'cosine': self._cosine_similarity,
            'euclidean': self._euclidean_similarity,
            'correlation': self._correlation_similarity,
            'basic_pattern': self._basic_pattern_match
        }
        
        # Pesos para combinar diferentes métricas
        self.metric_weights = {
            'cosine': 0.3,
            'euclidean': 0.2,
            'correlation': 0.2,
            'basic_pattern': 0.3
        }
    
    def classify_hand_landmarks(self, hand_landmarks):
        """
        Clasifica una seña basada en los landmarks de la mano
        
        Args:
            hand_landmarks: Landmarks de MediaPipe
            
        Returns:
            dict: Resultado de la clasificación con confianza y detalles
        """
        if not hand_landmarks:
            return self._empty_result()
        
        # Extraer características
        feature_vector = self.feature_extractor.extract_features(hand_landmarks)
        if feature_vector is None:
            return self._empty_result()
        
        # Clasificar usando diferentes métricas
        classification_results = self._classify_with_all_metrics(feature_vector)
        
        # Combinar resultados
        final_result = self._combine_metric_results(classification_results)
        
        # Aplicar suavizado temporal
        smoothed_result = self._apply_temporal_smoothing(final_result)
        
        return smoothed_result
    
    def _classify_with_all_metrics(self, feature_vector):
        """Clasifica usando todas las métricas disponibles"""
        results = {}
        all_signs = self.dataset.get_all_signs()
        
        for metric_name, metric_func in self.classification_metrics.items():
            results[metric_name] = metric_func(feature_vector, all_signs)
        
        return results
    
    def _cosine_similarity(self, feature_vector, signs):
        """Clasificación basada en similitud coseno"""
        best_match = {"sign": None, "confidence": 0.0}
        
        for sign in signs:
            # Obtener patrones aprendidos
            pattern = self.dataset.get_sign_pattern(sign)
            if pattern is not None:
                similarity = 1 - cosine(feature_vector, pattern)
                if similarity > best_match["confidence"]:
                    best_match = {"sign": sign, "confidence": similarity}
        
        return best_match
    
    def _euclidean_similarity(self, feature_vector, signs):
        """Clasificación basada en distancia euclidiana normalizada"""
        best_match = {"sign": None, "confidence": 0.0}
        
        for sign in signs:
            pattern = self.dataset.get_sign_pattern(sign)
            if pattern is not None:
                # Normalizar distancia euclidiana a [0,1]
                distance = euclidean(feature_vector, pattern)
                max_possible_distance = np.linalg.norm(feature_vector) + np.linalg.norm(pattern)
                confidence = 1 - (distance / max_possible_distance) if max_possible_distance > 0 else 0
                
                if confidence > best_match["confidence"]:
                    best_match = {"sign": sign, "confidence": confidence}
        
        return best_match
    
    def _correlation_similarity(self, feature_vector, signs):
        """Clasificación basada en correlación de Pearson"""
        best_match = {"sign": None, "confidence": 0.0}
        
        for sign in signs:
            pattern = self.dataset.get_sign_pattern(sign)
            if pattern is not None and len(pattern) == len(feature_vector):
                try:
                    correlation, _ = pearsonr(feature_vector, pattern)
                    # Convertir correlación [-1,1] a [0,1]
                    confidence = (correlation + 1) / 2 if not np.isnan(correlation) else 0
                    
                    if confidence > best_match["confidence"]:
                        best_match = {"sign": sign, "confidence": confidence}
                except:
                    continue
        
        return best_match
    
    def _basic_pattern_match(self, feature_vector, signs):
        """Clasificación basada en patrones básicos simples"""
        best_match = {"sign": None, "confidence": 0.0}
        
        # Extraer características interpretables del vector
        interpreted_features = self._interpret_feature_vector(feature_vector)
        
        for sign in signs:
            sign_info = self.dataset.get_sign_info(sign)
            if sign_info and "pattern" in sign_info:
                confidence = self._match_basic_pattern(interpreted_features, sign_info["pattern"])
                
                if confidence > best_match["confidence"]:
                    best_match = {"sign": sign, "confidence": confidence}
        
        return best_match
    
    def _interpret_feature_vector(self, feature_vector):
        """Interpreta el vector de características a patrones simples"""
        # Los índices corresponden al orden en SignFeatureExtractor
        fingers_extension = feature_vector[10:15]  # Estados de flexión de dedos
        hand_openness = feature_vector[-1]  # Última característica es apertura
        
        # Determinar si cada dedo está extendido (umbral adaptativo)
        extension_threshold = np.mean(fingers_extension) if len(fingers_extension) > 0 else 1.0
        fingers_extended = [ext > extension_threshold for ext in fingers_extension]
        
        return {
            "fingers_extended": fingers_extended,
            "hand_openness": hand_openness,
            "extension_values": fingers_extension.tolist()
        }
    
    def _match_basic_pattern(self, interpreted_features, pattern):
        """Compara características interpretadas con patrón básico"""
        confidence = 0.0
        total_checks = 0
        
        # Comparar extensión de dedos
        if "fingers_extended" in pattern:
            expected = pattern["fingers_extended"]
            actual = interpreted_features["fingers_extended"]
            
            if len(expected) == len(actual):
                matches = sum(1 for e, a in zip(expected, actual) if e == a)
                finger_confidence = matches / len(expected)
                confidence += finger_confidence * 0.6
                total_checks += 0.6
        
        # Comparar apertura de mano
        if "hand_openness" in pattern:
            expected_openness = pattern["hand_openness"]
            actual_openness = interpreted_features["hand_openness"]
            
            # Calcular similitud en apertura (tolerancia del 30%)
            tolerance = 0.3
            diff = abs(expected_openness - actual_openness)
            openness_confidence = max(0, 1 - (diff / tolerance))
            confidence += openness_confidence * 0.4
            total_checks += 0.4
        
        return confidence / total_checks if total_checks > 0 else 0
    
    def _combine_metric_results(self, metric_results):
        """Combina resultados de diferentes métricas usando pesos"""
        sign_scores = {}
        
        # Acumular puntuaciones ponderadas
        for metric, result in metric_results.items():
            if result["sign"] and result["confidence"] > 0:
                sign = result["sign"]
                weight = self.metric_weights.get(metric, 0.25)
                
                if sign not in sign_scores:
                    sign_scores[sign] = {"total_score": 0, "metric_count": 0, "details": {}}
                
                sign_scores[sign]["total_score"] += result["confidence"] * weight
                sign_scores[sign]["metric_count"] += 1
                sign_scores[sign]["details"][metric] = result["confidence"]
        
        # Encontrar mejor coincidencia
        if not sign_scores:
            return self._empty_result()
        
        best_sign = max(sign_scores.items(), key=lambda x: x[1]["total_score"])
        sign_name = best_sign[0]
        score_info = best_sign[1]
        
        return {
            "sign": sign_name,
            "confidence": score_info["total_score"],
            "details": score_info["details"],
            "timestamp": time.time()
        }
    
    def _apply_temporal_smoothing(self, current_result):
        """Aplica suavizado temporal para estabilizar predicciones"""
        # Agregar al historial
        self.prediction_history.append(current_result)
        
        # Mantener tamaño del historial
        if len(self.prediction_history) > self.history_size:
            self.prediction_history.pop(0)
        
        # Si no hay suficiente historial, retornar resultado actual
        if len(self.prediction_history) < self.stable_frames:
            current_result["stability"] = "inestable"
            return current_result
        
        # Contar ocurrencias de cada seña en el historial reciente
        recent_predictions = self.prediction_history[-self.stable_frames:]
        sign_counts = {}
        
        for pred in recent_predictions:
            if pred["sign"] and pred["confidence"] > self.confidence_threshold:
                sign = pred["sign"]
                if sign not in sign_counts:
                    sign_counts[sign] = {"count": 0, "total_confidence": 0}
                sign_counts[sign]["count"] += 1
                sign_counts[sign]["total_confidence"] += pred["confidence"]
        
        # Verificar si hay consenso
        if sign_counts:
            most_frequent = max(sign_counts.items(), key=lambda x: x[1]["count"])
            sign_name = most_frequent[0]
            count_info = most_frequent[1]
            
            # Confirmar si la seña es estable
            if count_info["count"] >= self.stable_frames:
                avg_confidence = count_info["total_confidence"] / count_info["count"]
                return {
                    "sign": sign_name,
                    "confidence": avg_confidence,
                    "stability": "estable",
                    "consensus_count": count_info["count"],
                    "timestamp": time.time()
                }
        
        # No hay consenso suficiente
        current_result["stability"] = "inestable"
        return current_result
    
    def _empty_result(self):
        """Retorna resultado vacío"""
        return {
            "sign": None,
            "confidence": 0.0,
            "details": {},
            "stability": "sin_datos",
            "timestamp": time.time()
        }
    
    def add_training_sample(self, sign_name, hand_landmarks, description=""):
        """
        Añade una muestra de entrenamiento al dataset
        
        Args:
            sign_name (str): Nombre de la seña
            hand_landmarks: Landmarks de MediaPipe
            description (str): Descripción opcional
        """
        feature_vector = self.feature_extractor.extract_features(hand_landmarks)
        if feature_vector is not None:
            self.dataset.add_sign_pattern(sign_name, feature_vector, description)
            return True
        return False
    
    def get_classifier_stats(self):
        """Retorna estadísticas del clasificador"""
        dataset_stats = self.dataset.get_dataset_stats()
        
        return {
            "dataset_stats": dataset_stats,
            "confidence_threshold": self.confidence_threshold,
            "history_size": self.history_size,
            "stable_frames": self.stable_frames,
            "available_metrics": list(self.classification_metrics.keys()),
            "metric_weights": self.metric_weights
        }
    
    def reset_history(self):
        """Reinicia el historial de predicciones"""
        self.prediction_history = []
    
    def update_confidence_threshold(self, new_threshold):
        """Actualiza el umbral de confianza"""
        if 0 <= new_threshold <= 1:
            self.confidence_threshold = new_threshold
            return True
        return False
