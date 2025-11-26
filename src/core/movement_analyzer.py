"""
Analizador de Movimiento para Señas Dinámicas
Detecta patrones de movimiento sin usar Deep Learning
"""

import numpy as np
from collections import deque
import time

class MovementAnalyzer:
    """
    Analiza movimientos de señas usando análisis temporal de landmarks
    """
    
    def __init__(self, buffer_size=15, fps=30):
        """
        Inicializa el analizador de movimiento
        
        Args:
            buffer_size: Número de frames a mantener en el buffer (15 frames = 0.5s a 30fps)
            fps: Frames por segundo esperados
        """
        self.buffer_size = buffer_size
        self.fps = fps
        self.dt = 1.0 / fps  # Delta time entre frames
        
        # Buffer circular para almacenar landmarks históricos
        self.landmarks_buffer = deque(maxlen=buffer_size)
        self.timestamps_buffer = deque(maxlen=buffer_size)
        
        # Caché para velocidades y aceleraciones
        self.velocities = None
        self.accelerations = None
        
    def add_frame(self, landmarks):
        """
        Agrega un nuevo frame de landmarks al buffer
        
        Args:
            landmarks: Lista de 21 landmarks de MediaPipe
        """
        # Convertir landmarks a array numpy (21 puntos x 3 coordenadas)
        landmarks_array = np.array([[lm.x, lm.y, lm.z] for lm in landmarks])
        
        self.landmarks_buffer.append(landmarks_array)
        self.timestamps_buffer.append(time.time())
        
        # Calcular velocidades y aceleraciones si hay suficientes frames
        if len(self.landmarks_buffer) >= 3:
            self._calculate_kinematics()
    
    def _calculate_kinematics(self):
        """Calcula velocidades y aceleraciones de los landmarks"""
        if len(self.landmarks_buffer) < 2:
            return
        
        # Calcular velocidades (diferencia entre frames consecutivos)
        velocities = []
        for i in range(1, len(self.landmarks_buffer)):
            dt = self.timestamps_buffer[i] - self.timestamps_buffer[i-1]
            if dt > 0:
                velocity = (self.landmarks_buffer[i] - self.landmarks_buffer[i-1]) / dt
                velocities.append(velocity)
        
        if velocities:
            self.velocities = np.array(velocities)
        
        # Calcular aceleraciones (cambio de velocidad)
        if len(velocities) >= 2:
            accelerations = []
            for i in range(1, len(velocities)):
                dt = self.timestamps_buffer[i+1] - self.timestamps_buffer[i]
                if dt > 0:
                    accel = (velocities[i] - velocities[i-1]) / dt
                    accelerations.append(accel)
            
            if accelerations:
                self.accelerations = np.array(accelerations)
    
    def get_movement_features(self):
        """
        Extrae características de movimiento del buffer actual
        
        Returns:
            dict: Diccionario con características de movimiento
        """
        if len(self.landmarks_buffer) < 3:
            return None
        
        features = {}
        
        # 1. VELOCIDAD MEDIA de cada landmark
        if self.velocities is not None:
            avg_velocities = np.mean(self.velocities, axis=0)
            features['avg_velocity'] = np.linalg.norm(avg_velocities, axis=1)  # Magnitud por landmark
            features['avg_speed'] = np.mean(features['avg_velocity'])  # Velocidad media global
        
        # 2. DIRECCIÓN DOMINANTE del movimiento
        if self.velocities is not None:
            # Dirección de la muñeca (landmark 0)
            wrist_velocities = self.velocities[:, 0, :]
            avg_direction = np.mean(wrist_velocities, axis=0)
            features['direction'] = avg_direction / (np.linalg.norm(avg_direction) + 1e-6)
            
            # Clasificar dirección (arriba/abajo/izquierda/derecha)
            features['direction_class'] = self._classify_direction(features['direction'])
        
        # 3. TRAYECTORIA de la muñeca
        wrist_positions = np.array([lm[0] for lm in self.landmarks_buffer])
        features['trajectory_length'] = self._calculate_trajectory_length(wrist_positions)
        features['trajectory_smoothness'] = self._calculate_smoothness(wrist_positions)
        
        # 4. ÁREA CUBIERTA por el movimiento
        features['movement_area'] = self._calculate_movement_area(wrist_positions)
        
        # 5. PATRÓN DE MOVIMIENTO (circular, lineal, etc.)
        features['movement_pattern'] = self._detect_movement_pattern(wrist_positions)
        
        # 6. ACELERACIÓN (para detectar movimientos bruscos vs suaves)
        if self.accelerations is not None:
            avg_accel = np.mean(np.abs(self.accelerations))
            features['avg_acceleration'] = avg_accel
            features['is_abrupt'] = avg_accel > 10.0  # Umbral ajustable
        
        # 7. FRECUENCIA de movimiento (para detectar repeticiones)
        features['movement_frequency'] = self._calculate_frequency()
        
        return features
    
    def _classify_direction(self, direction_vector):
        """Clasifica la dirección del movimiento en 8 direcciones cardinales"""
        x, y, z = direction_vector
        
        # Ignorar Z por ahora (profundidad)
        angle = np.arctan2(y, x) * 180 / np.pi
        
        if -22.5 <= angle < 22.5:
            return 'DERECHA'
        elif 22.5 <= angle < 67.5:
            return 'ARRIBA_DERECHA'
        elif 67.5 <= angle < 112.5:
            return 'ARRIBA'
        elif 112.5 <= angle < 157.5:
            return 'ARRIBA_IZQUIERDA'
        elif angle >= 157.5 or angle < -157.5:
            return 'IZQUIERDA'
        elif -157.5 <= angle < -112.5:
            return 'ABAJO_IZQUIERDA'
        elif -112.5 <= angle < -67.5:
            return 'ABAJO'
        else:  # -67.5 <= angle < -22.5
            return 'ABAJO_DERECHA'
    
    def _calculate_trajectory_length(self, positions):
        """Calcula la longitud total de la trayectoria"""
        if len(positions) < 2:
            return 0.0
        
        distances = np.linalg.norm(np.diff(positions, axis=0), axis=1)
        return np.sum(distances)
    
    def _calculate_smoothness(self, positions):
        """
        Calcula la suavidad de la trayectoria
        Retorna valor entre 0 (muy irregular) y 1 (muy suave)
        """
        if len(positions) < 3:
            return 1.0
        
        # Calcular cambios de dirección
        directions = np.diff(positions, axis=0)
        direction_changes = np.diff(directions, axis=0)
        
        # Suavidad inversa a la magnitud de cambios de dirección
        avg_change = np.mean(np.linalg.norm(direction_changes, axis=1))
        smoothness = 1.0 / (1.0 + avg_change * 10)  # Normalizar
        
        return smoothness
    
    def _calculate_movement_area(self, positions):
        """Calcula el área rectangular cubierta por el movimiento"""
        if len(positions) < 2:
            return 0.0
        
        min_coords = np.min(positions, axis=0)
        max_coords = np.max(positions, axis=0)
        
        # Área 2D (ignorar Z)
        width = max_coords[0] - min_coords[0]
        height = max_coords[1] - min_coords[1]
        
        return width * height
    
    def _detect_movement_pattern(self, positions):
        """
        Detecta el patrón de movimiento
        Returns: 'CIRCULAR', 'LINEAL', 'ZIGZAG', 'ESTATICO'
        """
        if len(positions) < 5:
            return 'ESTATICO'
        
        # 1. Verificar si es estático
        movement_range = np.max(positions, axis=0) - np.min(positions, axis=0)
        if np.all(movement_range < 0.05):  # Umbral de movimiento mínimo
            return 'ESTATICO'
        
        # 2. Detectar movimiento circular
        # Calcular centro de masa
        center = np.mean(positions, axis=0)
        
        # Calcular distancias al centro
        distances_to_center = np.linalg.norm(positions - center, axis=1)
        
        # Si las distancias son similares, es circular
        distance_variance = np.var(distances_to_center)
        if distance_variance < 0.01:
            return 'CIRCULAR'
        
        # 3. Detectar movimiento lineal
        # Ajustar una línea recta y calcular R²
        if len(positions) >= 5:
            x = positions[:, 0]
            y = positions[:, 1]
            
            # Regresión lineal simple
            A = np.vstack([x, np.ones(len(x))]).T
            m, c = np.linalg.lstsq(A, y, rcond=None)[0]
            
            # Calcular R² (coeficiente de determinación)
            y_pred = m * x + c
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - (ss_res / (ss_tot + 1e-6))
            
            if r_squared > 0.8:
                return 'LINEAL'
        
        # 4. Si no es ninguno de los anteriores, es zigzag
        return 'ZIGZAG'
    
    def _calculate_frequency(self):
        """
        Calcula la frecuencia dominante del movimiento
        Útil para detectar movimientos repetitivos (ej: saludar con la mano)
        """
        if len(self.landmarks_buffer) < 10:
            return 0.0
        
        # Analizar oscilaciones en la posición de la muñeca
        wrist_positions = np.array([lm[0] for lm in self.landmarks_buffer])
        
        # Usar la coordenada Y (vertical) para detectar oscilaciones
        y_positions = wrist_positions[:, 1]
        
        # Contar cruces por el valor medio
        mean_y = np.mean(y_positions)
        crossings = 0
        
        for i in range(1, len(y_positions)):
            if (y_positions[i-1] < mean_y <= y_positions[i]) or \
               (y_positions[i-1] >= mean_y > y_positions[i]):
                crossings += 1
        
        # Frecuencia = cruces / (2 * tiempo_total)
        if len(self.timestamps_buffer) >= 2:
            time_span = self.timestamps_buffer[-1] - self.timestamps_buffer[0]
            if time_span > 0:
                frequency = crossings / (2 * time_span)
                return frequency
        
        return 0.0
    
    def is_moving(self, threshold=0.01):
        """
        Determina si hay movimiento significativo
        
        Args:
            threshold: Umbral de velocidad para considerar movimiento
            
        Returns:
            bool: True si hay movimiento
        """
        features = self.get_movement_features()
        if features is None:
            return False
        
        return features.get('avg_speed', 0) > threshold
    
    def clear(self):
        """Limpia el buffer de landmarks"""
        self.landmarks_buffer.clear()
        self.timestamps_buffer.clear()
        self.velocities = None
        self.accelerations = None
    
    def get_movement_signature(self):
        """
        Genera una 'firma' única del movimiento para comparación
        
        Returns:
            numpy array: Vector de características normalizado
        """
        features = self.get_movement_features()
        if features is None:
            return None
        
        # Crear vector de características normalizado
        signature = np.array([
            features.get('avg_speed', 0),
            features.get('trajectory_length', 0),
            features.get('trajectory_smoothness', 0),
            features.get('movement_area', 0),
            features.get('avg_acceleration', 0),
            features.get('movement_frequency', 0),
            # Dirección codificada
            1.0 if features.get('direction_class') == 'ARRIBA' else 0.0,
            1.0 if features.get('direction_class') == 'ABAJO' else 0.0,
            1.0 if features.get('direction_class') == 'IZQUIERDA' else 0.0,
            1.0 if features.get('direction_class') == 'DERECHA' else 0.0,
            # Patrón de movimiento codificado
            1.0 if features.get('movement_pattern') == 'CIRCULAR' else 0.0,
            1.0 if features.get('movement_pattern') == 'LINEAL' else 0.0,
            1.0 if features.get('movement_pattern') == 'ZIGZAG' else 0.0,
        ])
        
        # Normalizar (evitar división por cero)
        norm = np.linalg.norm(signature)
        if norm > 0:
            signature = signature / norm
        
        return signature
