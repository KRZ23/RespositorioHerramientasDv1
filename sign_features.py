import numpy as np
import math

class SignFeatureExtractor:
    """
    Extrae características relevantes de los landmarks de la mano para clasificación de señas.
    """
    
    def __init__(self):
        """Inicializa el extractor de características"""
        # Índices de landmarks importantes de MediaPipe
        self.WRIST = 0
        self.THUMB_TIP = 4
        self.INDEX_TIP = 8
        self.MIDDLE_TIP = 12
        self.RING_TIP = 16
        self.PINKY_TIP = 20
        
        # Índices de articulaciones intermedias
        self.THUMB_IP = 3
        self.INDEX_PIP = 6
        self.MIDDLE_PIP = 10
        self.RING_PIP = 14
        self.PINKY_PIP = 18
        
    def extract_features(self, hand_landmarks):
        """
        Extrae un vector de características de los landmarks de la mano
        
        Args:
            hand_landmarks: Landmarks de MediaPipe para una mano
            
        Returns:
            np.array: Vector de características normalizado
        """
        if not hand_landmarks:
            return None
            
        # Convertir landmarks a array numpy
        points = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark])
        
        # Normalizar respecto a la muñeca
        wrist = points[self.WRIST]
        normalized_points = points - wrist
        
        # Calcular características
        features = []
        
        # 1. Distancias desde la muñeca a cada punta de dedo
        fingertips = [self.THUMB_TIP, self.INDEX_TIP, self.MIDDLE_TIP, self.RING_TIP, self.PINKY_TIP]
        for tip in fingertips:
            distance = np.linalg.norm(normalized_points[tip])
            features.append(distance)
        
        # 2. Ángulos entre dedos (usando solo coordenadas x, y)
        angles = self._calculate_finger_angles(normalized_points)
        features.extend(angles)
        
        # 3. Estados de flexión de dedos (comparar punta vs articulación intermedia)
        finger_states = self._calculate_finger_states(normalized_points)
        features.extend(finger_states)
        
        # 4. Orientación general de la mano
        orientation = self._calculate_hand_orientation(normalized_points)
        features.extend(orientation)
        
        # 5. Apertura de la mano (distancia promedio entre dedos)
        hand_openness = self._calculate_hand_openness(normalized_points)
        features.append(hand_openness)
        
        return np.array(features)
    
    def _calculate_finger_angles(self, points):
        """Calcula ángulos entre dedos adyacentes"""
        fingertips = [self.THUMB_TIP, self.INDEX_TIP, self.MIDDLE_TIP, self.RING_TIP, self.PINKY_TIP]
        angles = []
        
        for i in range(len(fingertips) - 1):
            # Vector desde muñeca a cada dedo
            v1 = points[fingertips[i]][:2]  # Solo x, y
            v2 = points[fingertips[i + 1]][:2]
            
            # Calcular ángulo
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
            angle = math.acos(np.clip(cos_angle, -1.0, 1.0))
            angles.append(angle)
            
        return angles
    
    def _calculate_finger_states(self, points):
        """Determina si cada dedo está extendido o doblado"""
        finger_pairs = [
            (self.THUMB_TIP, self.THUMB_IP),
            (self.INDEX_TIP, self.INDEX_PIP),
            (self.MIDDLE_TIP, self.MIDDLE_PIP),
            (self.RING_TIP, self.RING_PIP),
            (self.PINKY_TIP, self.PINKY_PIP)
        ]
        
        states = []
        for tip_idx, pip_idx in finger_pairs:
            # Distancia de la punta vs articulación intermedia desde la muñeca
            tip_dist = np.linalg.norm(points[tip_idx])
            pip_dist = np.linalg.norm(points[pip_idx])
            
            # Si la punta está más lejos que la articulación, el dedo está extendido
            extension_ratio = tip_dist / (pip_dist + 1e-8)
            states.append(extension_ratio)
            
        return states
    
    def _calculate_hand_orientation(self, points):
        """Calcula la orientación general de la mano"""
        # Vector desde muñeca hasta dedo medio
        middle_vector = points[self.MIDDLE_TIP][:2]
        
        # Ángulo respecto al eje horizontal
        angle = math.atan2(middle_vector[1], middle_vector[0])
        
        # Normalizar a [0, 2π]
        if angle < 0:
            angle += 2 * math.pi
            
        # Convertir a componentes sin y cos para continuidad
        return [math.sin(angle), math.cos(angle)]
    
    def _calculate_hand_openness(self, points):
        """Calcula qué tan abierta está la mano"""
        fingertips = [self.INDEX_TIP, self.MIDDLE_TIP, self.RING_TIP, self.PINKY_TIP]
        
        # Calcular distancias promedio entre dedos adyacentes
        total_distance = 0
        count = 0
        
        for i in range(len(fingertips) - 1):
            dist = np.linalg.norm(points[fingertips[i]][:2] - points[fingertips[i + 1]][:2])
            total_distance += dist
            count += 1
            
        return total_distance / count if count > 0 else 0

    def get_feature_names(self):
        """Retorna los nombres de las características extraídas"""
        names = []
        
        # Distancias de dedos
        fingers = ["Pulgar", "Índice", "Medio", "Anular", "Meñique"]
        for finger in fingers:
            names.append(f"Dist_{finger}")
        
        # Ángulos entre dedos
        for i in range(4):
            names.append(f"Angulo_{fingers[i]}_{fingers[i+1]}")
        
        # Estados de flexión
        for finger in fingers:
            names.append(f"Flexion_{finger}")
        
        # Orientación
        names.extend(["Orient_Sin", "Orient_Cos"])
        
        # Apertura
        names.append("Apertura_Mano")
        
        return names
