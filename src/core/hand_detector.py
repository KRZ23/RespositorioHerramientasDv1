import cv2
try:
    import mediapipe as mp
    HAS_MEDIAPIPE = True
except Exception:
    mp = None
    HAS_MEDIAPIPE = False
import threading
import time
from src.core.sign_classifier import SignClassifier
from src.core.movement_analyzer import MovementAnalyzer
from src.utils.dynamic_signs_dataset import DYNAMIC_SIGNS_PATTERNS, is_dynamic_sign
from src.core.landmarks_3d_manager import Landmarks3DManager

class HandDetector:
    """
    Clase modular para detección de manos usando MediaPipe y OpenCV.
    Maneja toda la lógica de detección de forma independiente.
    """
    
    def __init__(self, show_window=True):
        self.show_window = show_window
        # Configurar MediaPipe (si está disponible)
        if HAS_MEDIAPIPE and mp is not None:
            try:
                self.mp_hands = mp.solutions.hands
                self.hands = self.mp_hands.Hands(
                    static_image_mode=False,
                    max_num_hands=2,
                    min_detection_confidence=0.7,
                    min_tracking_confidence=0.5
                )
                self.mp_draw = mp.solutions.drawing_utils
            except Exception:
                # Fallback a modo sin mediapipe
                self.mp_hands = None
                self.hands = None
                self.mp_draw = None
        else:
            self.mp_hands = None
            self.hands = None
            self.mp_draw = None
        
        # Variables de control
        self.is_detecting = False
        self.cap = None
        self.detection_thread = None
        self.window_created = False
        
        # Inicializar clasificador de señas (umbral reducido para mejor detección)
        self.sign_classifier = SignClassifier(confidence_threshold=0.35)
        self.translation_enabled = True
        
        # Inicializar analizador de movimiento para señas dinámicas
        self.movement_analyzer = MovementAnalyzer(buffer_size=15, fps=30)
        self.use_movement_detection = True  # Activar detección de movimiento
        
        # Inicializar gestor de landmarks 3D
        self.landmarks_3d_manager = Landmarks3DManager()
        
        # Callbacks para comunicación con la interfaz
        self.on_hand_detected = None
        self.on_status_update = None
        self.on_error = None
        self.on_sign_detected = None  # Nuevo callback para señas traducidas
        self.on_training_mode = False  # Modo de entrenamiento
        
    def set_callbacks(self, on_hand_detected=None, on_status_update=None, on_error=None, on_sign_detected=None):
        """
        Establece callbacks para comunicación con la interfaz
        
        Args:
            on_hand_detected: Función que se llama cuando se detectan manos (hand_count)
            on_status_update: Función que se llama para actualizar estado (message)
            on_error: Función que se llama en caso de error (error_message)
            on_sign_detected: Función que se llama cuando se detecta una seña (sign_result)
        """
        self.on_hand_detected = on_hand_detected
        self.on_status_update = on_status_update
        self.on_error = on_error
        self.on_sign_detected = on_sign_detected
        
    def start_detection(self):
        """
        Inicia la detección de manos
        
        Returns:
            bool: True si se inició correctamente, False en caso contrario
        """
        try:
            # Verificar si ya está detectando
            if self.is_detecting:
                if self.on_status_update:
                    self.on_status_update("⚠️ La detección ya está en curso")
                return False
            
            # 🔧 FIX: Asegurarse de liberar la cámara anterior si existe
            if self.cap is not None:
                try:
                    self.cap.release()
                    self.cap = None
                except:
                    pass
                
            # Inicializar cámara
            self.cap = cv2.VideoCapture(0)
            
            # 🔧 FIX: Dar un momento para que la cámara se inicialice
            import time
            time.sleep(0.5)
            
            if not self.cap.isOpened():
                error_msg = "❌ Error: No se pudo acceder a la cámara"
                if self.on_error:
                    self.on_error(error_msg)
                self.cap = None
                return False
                
            # Iniciar detección
            self.is_detecting = True
            self.window_created = False
            
            # Iniciar hilo de detección
            self.detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
            self.detection_thread.start()
            
            if self.on_status_update:
                self.on_status_update("✅ Detección iniciada correctamente")
            
            return True
            
        except Exception as e:
            error_msg = f"❌ Error al iniciar detección: {str(e)}"
            if self.on_error:
                self.on_error(error_msg)
            if self.cap:
                self.cap.release()
                self.cap = None
            return False
            
    def stop_detection(self):
        """Para la detección de manos"""
        if not self.is_detecting:
            return  # Ya está detenido
            
        self.is_detecting = False
        
        # 🔧 FIX: Esperar un poco más para que el hilo termine
        if self.detection_thread and self.detection_thread.is_alive():
            self.detection_thread.join(timeout=2.0)
        
        # 🔧 FIX: Cerrar ventanas de OpenCV primero
        try:
            cv2.destroyAllWindows()
            # Dar tiempo para que las ventanas se cierren
            import time
            time.sleep(0.3)
        except:
            pass
        
        # 🔧 FIX: Liberar recursos de cámara con retry
        if self.cap is not None:
            try:
                self.cap.release()
                import time
                time.sleep(0.2)  # Dar tiempo para que se libere
            except Exception as e:
                print(f"Error al liberar cámara: {e}")
            finally:
                self.cap = None  # Resetear a None para permitir reinicio
        
        # Resetear el hilo
        self.detection_thread = None
        self.window_created = False
        
        if self.on_status_update:
            self.on_status_update("⏹️ Detección detenida")
    
    def _classify_dynamic_sign(self, landmarks):
        """
        Clasifica señas dinámicas basándose en patrones de movimiento.
        NO usa TensorFlow ni ML, solo análisis de características.
        
        Args:
            landmarks: Landmarks de MediaPipe de la mano actual
            
        Returns:
            dict con sign, confidence, description si se detecta, None si no
        """
        # Agregar frame actual al buffer de movimiento
        self.movement_analyzer.add_frame(landmarks)
        
        # Obtener características de movimiento
        movement_features = self.movement_analyzer.get_movement_features()
        
        if not movement_features:
            return None
        
        # Verificar si hay suficiente movimiento
        avg_speed = movement_features.get('avg_speed', 0)
        if avg_speed < 0.02:  # Umbral de movimiento mínimo
            return None
        
        # Buscar coincidencias en patrones dinámicos
        best_match = None
        best_score = 0.0
        
        for sign_name, pattern in DYNAMIC_SIGNS_PATTERNS.items():
            score = self._match_movement_pattern(movement_features, pattern, landmarks)
            
            if score > best_score:
                best_score = score
                best_match = sign_name
        
        # Retornar resultado si supera umbral
        if best_score > 0.6:
            return {
                'sign': best_match,
                'confidence': best_score,
                'description': f"Seña dinámica: {best_match}",
                'type': 'dynamic'
            }
        
        return None
    
    def _match_movement_pattern(self, features, pattern, landmarks):
        """
        Compara características de movimiento con un patrón de seña dinámica.
        
        Args:
            features: Dict con características de movimiento
            pattern: Dict con patrón esperado de la seña
            landmarks: Landmarks actuales de la mano
            
        Returns:
            float: Puntuación de 0 a 1
        """
        score = 0.0
        weights = {
            'pattern': 0.20,
            'direction': 0.15,
            'frequency': 0.15,
            'speed': 0.15,
            'trajectory': 0.10,
            'hand_shape': 0.25
        }
        
        # 1. Comparar patrón de movimiento
        if features.get('movement_pattern') == pattern.get('movement_pattern'):
            score += weights['pattern']
        
        # 2. Comparar dirección
        direction_score = self._compare_direction(
            features.get('direction', 'ESTATICO'),
            pattern.get('direction', 'ESTATICO')
        )
        score += direction_score * weights['direction']
        
        # 3. Comparar frecuencia
        freq = features.get('frequency', 0)
        freq_range = pattern.get('frequency_range', (0, 100))
        if freq_range[0] <= freq <= freq_range[1]:
            score += weights['frequency']
        
        # 4. Comparar velocidad promedio
        speed = features.get('avg_speed', 0)
        speed_range = pattern.get('avg_speed_range', (0, 100))
        if speed_range[0] <= speed <= speed_range[1]:
            score += weights['speed']
        
        # 5. Comparar longitud de trayectoria
        trajectory = features.get('trajectory_length', 0)
        trajectory_range = pattern.get('trajectory_length_range', (0, 100))
        if trajectory_range[0] <= trajectory <= trajectory_range[1]:
            score += weights['trajectory']
        
        # 6. Comparar forma de mano (usando landmarks)
        if 'hand_shape' in pattern:
            hand_shape_score = self._match_hand_shape(landmarks, pattern['hand_shape'])
            score += hand_shape_score * weights['hand_shape']
        else:
            score += weights['hand_shape']  # Si no hay shape específico, dar puntos
        
        return score
    
    def _compare_direction(self, detected, expected):
        """Compara direcciones con tolerancia para direcciones compatibles"""
        if detected == expected:
            return 1.0
        
        # Direcciones compatibles (devuelve score parcial)
        compatible = {
            'ARRIBA': ['ARRIBA_IZQUIERDA', 'ARRIBA_DERECHA'],
            'ABAJO': ['ABAJO_IZQUIERDA', 'ABAJO_DERECHA'],
            'IZQUIERDA': ['ARRIBA_IZQUIERDA', 'ABAJO_IZQUIERDA'],
            'DERECHA': ['ARRIBA_DERECHA', 'ABAJO_DERECHA'],
            'IZQUIERDA_DERECHA': ['IZQUIERDA', 'DERECHA'],
            'ARRIBA_ABAJO': ['ARRIBA', 'ABAJO']
        }
        
        if expected in compatible and detected in compatible[expected]:
            return 0.7
        if detected in compatible and expected in compatible[detected]:
            return 0.7
        
        return 0.0
    
    def _match_hand_shape(self, landmarks, hand_shape_pattern):
        """
        Compara la forma de la mano actual con un patrón esperado.
        
        Args:
            landmarks: Landmarks de MediaPipe
            hand_shape_pattern: Dict con fingers_extended, hand_openness, etc.
            
        Returns:
            float: Puntuación de 0 a 1
        """
        try:
            # Convertir landmarks a lista de puntos
            points = [[lm.x, lm.y, lm.z] for lm in landmarks]
            
            score = 0.0
            
            # Comparar dedos extendidos
            if 'fingers_extended' in hand_shape_pattern:
                expected_fingers = hand_shape_pattern['fingers_extended']
                actual_fingers = self._get_fingers_extended(points)
                
                matches = sum(1 for e, a in zip(expected_fingers, actual_fingers) if e == a)
                score += (matches / 5.0) * 0.6  # 60% del peso en dedos
            
            # Comparar apertura de mano
            if 'hand_openness' in hand_shape_pattern:
                expected_openness = hand_shape_pattern['hand_openness']
                actual_openness = self._get_hand_openness(points)
                
                # Tolerancia de ±0.15
                diff = abs(expected_openness - actual_openness)
                if diff < 0.15:
                    score += 0.4  # 40% del peso en apertura
                elif diff < 0.3:
                    score += 0.2  # Parcial si está cerca
            
            return score if score > 0 else 0.5
            
        except Exception:
            return 0.5  # Score neutro en caso de error
    
    def _get_fingers_extended(self, points):
        """Calcula qué dedos están extendidos (heurística simple)"""
        try:
            fingers = []
            # Índices: WRIST=0, tips=[4,8,12,16,20], pips=[3,6,10,14,18]
            finger_indices = [(4,3), (8,6), (12,10), (16,14), (20,18)]
            
            for tip_idx, pip_idx in finger_indices:
                tip_y = points[tip_idx][1]
                pip_y = points[pip_idx][1]
                
                # En coordenadas de imagen, Y menor = más arriba
                is_extended = tip_y < pip_y
                fingers.append(is_extended)
            
            return fingers
        except:
            return [False] * 5
    
    def _get_hand_openness(self, points):
        """Calcula apertura de la mano (0=cerrada, 1=abierta)"""
        try:
            # Distancia promedio entre dedos adyacentes
            fingertips = [4, 8, 12, 16, 20]
            total_distance = 0
            
            for i in range(len(fingertips) - 1):
                p1 = points[fingertips[i]]
                p2 = points[fingertips[i+1]]
                dist = ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)**0.5
                total_distance += dist
            
            # Normalizar (valores típicos entre 0.2 y 0.8)
            openness = min(total_distance / 2.0, 1.0)
            return openness
        except:
            return 0.5
            
    def is_running(self):
        """Verifica si la detección está activa"""
        return self.is_detecting
    
    def toggle_translation(self):
        """Activa/desactiva la traducción de señas"""
        self.translation_enabled = not self.translation_enabled
        status = "activada" if self.translation_enabled else "desactivada"
        if self.on_status_update:
            self.on_status_update(f"Traducción {status}")
        return self.translation_enabled
    
    def is_translation_enabled(self):
        """Verifica si la traducción está activada"""
        return self.translation_enabled
    
    def add_training_sample(self, sign_name, description=""):
        """Añade muestra de entrenamiento de seña ESTÁTICA"""
        # Esta función será llamada desde la interfaz cuando se quiera entrenar
        # El entrenamiento se hará con el próximo frame detectado
        self.training_sign_name = sign_name
        self.training_description = description
        self.on_training_mode = True
        self.dynamic_training_mode = False  # Modo estático
        if self.on_status_update:
            self.on_status_update(f"Modo entrenamiento ESTÁTICO: {sign_name}")
    
    def start_dynamic_training(self, sign_name):
        """
        Inicia el entrenamiento de una seña DINÁMICA
        Captura el patrón de movimiento durante 2-3 segundos
        """
        import json
        
        self.training_sign_name = sign_name
        self.on_training_mode = True
        self.dynamic_training_mode = True  # Modo dinámico
        self.dynamic_training_buffer = []  # Buffer para guardar características de movimiento
        self.dynamic_training_landmarks_buffer = []  # Buffer para landmarks 3D
        self.dynamic_training_start_time = time.time()
        
        if self.on_status_update:
            self.on_status_update(f"Modo entrenamiento DINÁMICO: {sign_name} - Realiza el movimiento...")
    
    def _save_dynamic_pattern(self, sign_name, features_list):
        """
        Guarda el patrón de movimiento capturado en el dataset dinámico
        
        Args:
            sign_name: Nombre de la seña
            features_list: Lista de características de movimiento capturadas
        """
        import json
        import os
        
        try:
            # Calcular estadísticas promedio del movimiento
            if not features_list:
                return False
            
            # Promediar características
            avg_features = {
                'movement_pattern': features_list[-1].get('movement_pattern', 'LINEAR'),
                'direction': features_list[-1].get('direction', 'ESTATICO'),
                'frequency_range': (
                    min(f.get('frequency', 0) for f in features_list),
                    max(f.get('frequency', 0) for f in features_list)
                ),
                'avg_speed_range': (
                    min(f.get('avg_speed', 0) for f in features_list),
                    max(f.get('avg_speed', 0) for f in features_list)
                ),
                'trajectory_length_range': (
                    min(f.get('trajectory_length', 0) for f in features_list),
                    max(f.get('trajectory_length', 0) for f in features_list)
                )
            }
            
            # Cargar dataset existente
            dataset_file = 'src/utils/dynamic_signs_dataset.py'
            with open(dataset_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Agregar nueva seña al diccionario DYNAMIC_SIGNS_PATTERNS
            new_pattern = f"""
    '{sign_name}': {{
        'movement_pattern': '{avg_features['movement_pattern']}',
        'direction': '{avg_features['direction']}',
        'frequency_range': {avg_features['frequency_range']},
        'avg_speed_range': {avg_features['avg_speed_range']},
        'trajectory_length_range': {avg_features['trajectory_length_range']},
        'hand_shape': {{
            'fingers_extended': [True, True, True, True, True],
            'hand_openness': 0.6
        }}
    }},
"""
            
            # Insertar antes del cierre del diccionario
            insertion_point = content.rfind('}')
            if insertion_point > 0:
                # Encontrar el último patrón
                last_pattern = content.rfind("    },", 0, insertion_point)
                if last_pattern > 0:
                    content = content[:last_pattern + 6] + new_pattern + content[last_pattern + 6:]
                    
                    # Guardar archivo actualizado
                    with open(dataset_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error guardando patrón dinámico: {e}")
            return False
        
    def _detection_loop(self):
        """Bucle principal de detección (ejecutado en hilo separado)"""
        hand_count = 0
        
        try:
            while self.is_detecting:
                success, img = self.cap.read()
                if not success:
                    break
                    
                # Convierte BGR a RGB
                imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                # Usar MediaPipe si está disponible, si no, operar en modo limitado
                results = None
                if self.hands is not None:
                    try:
                        results = self.hands.process(imgRGB)
                    except Exception:
                        results = None

                # Contar manos detectadas (si MediaPipe no está presente siempre 0)
                current_hand_count = 0
                if results and getattr(results, 'multi_hand_landmarks', None):
                    current_hand_count = len(results.multi_hand_landmarks)
                
                # Notificar cambio en número de manos
                if current_hand_count != hand_count:
                    hand_count = current_hand_count
                    if self.on_hand_detected:
                        self.on_hand_detected(hand_count)
                
                # Procesar traducción de señas si está habilitada y MediaPipe devuelve landmarks
                if self.translation_enabled and results and getattr(results, 'multi_hand_landmarks', None):
                    # Detectar número de manos
                    all_hands = results.multi_hand_landmarks
                    num_hands = len(all_hands)
                    first_hand = all_hands[0]
                    
                    # Modo entrenamiento
                    if self.on_training_mode and hasattr(self, 'training_sign_name'):
                        
                        # Verificar si es entrenamiento dinámico
                        if getattr(self, 'dynamic_training_mode', False):
                            # ENTRENAMIENTO DINÁMICO - Capturar movimiento durante 4 segundos
                            self.movement_analyzer.add_frame(first_hand.landmark)
                            
                            # Inicializar buffers si no existen
                            if not hasattr(self, 'dynamic_training_buffer'):
                                self.dynamic_training_buffer = []
                            if not hasattr(self, 'dynamic_training_landmarks_buffer'):
                                self.dynamic_training_landmarks_buffer = []
                            
                            # Siempre guardar landmarks 3D (no depender de features)
                            self.dynamic_training_landmarks_buffer.append(first_hand.landmark)
                            
                            # Intentar extraer features (puede ser None en los primeros frames)
                            features = self.movement_analyzer.get_movement_features()
                            if features:
                                self.dynamic_training_buffer.append(features)
                            
                            # Mostrar progreso cada 0.5 segundos
                            elapsed = time.time() - getattr(self, 'dynamic_training_start_time', time.time())
                            if not hasattr(self, 'last_progress_update'):
                                self.last_progress_update = 0
                            if elapsed - self.last_progress_update >= 0.5:
                                self.last_progress_update = elapsed
                                frames_captured = len(self.dynamic_training_buffer)
                                if self.on_status_update:
                                    self.on_status_update(f"📊 Capturando... {frames_captured} frames - {elapsed:.1f}s / 4.0s")
                            
                            # Verificar si ya pasaron 4 segundos
                            if elapsed >= 4.0:
                                # Guardar patrón capturado
                                if len(self.dynamic_training_buffer) >= 5:
                                    success = self._save_dynamic_pattern(
                                        self.training_sign_name,
                                        self.dynamic_training_buffer
                                    )
                                    
                                    # Guardar también landmarks 3D
                                    try:
                                        self.landmarks_3d_manager.save_dynamic_sign(
                                            self.training_sign_name,
                                            self.dynamic_training_landmarks_buffer,
                                            "Seña dinámica entrenada por usuario"
                                        )
                                    except Exception as e:
                                        print(f"Error guardando landmarks 3D dinámicos: {e}")
                                    
                                    if success and self.on_status_update:
                                        self.on_status_update(f"✓ Seña dinámica '{self.training_sign_name}' guardada!")
                                    elif self.on_status_update:
                                        self.on_status_update(f"✗ Error guardando '{self.training_sign_name}'")
                                else:
                                    if self.on_status_update:
                                        captured = len(self.dynamic_training_buffer)
                                        self.on_status_update(f"✗ Solo se capturaron {captured} frames (mínimo 5). Mueve la mano más!")
                                
                                # Limpiar variables
                                self.on_training_mode = False
                                self.dynamic_training_mode = False
                                delattr(self, 'training_sign_name')
                                if hasattr(self, 'dynamic_training_buffer'):
                                    delattr(self, 'dynamic_training_buffer')
                                if hasattr(self, 'dynamic_training_landmarks_buffer'):
                                    delattr(self, 'dynamic_training_landmarks_buffer')
                                if hasattr(self, 'last_progress_update'):
                                    delattr(self, 'last_progress_update')
                        
                        else:
                            # ENTRENAMIENTO ESTÁTICO - Captura un solo frame
                            success = self.sign_classifier.add_training_sample(
                                self.training_sign_name, first_hand, 
                                getattr(self, 'training_description', '')
                            )
                            
                            # También guardar landmarks 3D para animación (1 o 2 manos)
                            try:
                                if num_hands > 1:
                                    # Seña con 2 manos
                                    self.landmarks_3d_manager.save_static_sign(
                                        self.training_sign_name,
                                        all_hands,
                                        getattr(self, 'training_description', '') + ' (2 manos)',
                                        num_hands=2
                                    )
                                    if self.on_status_update:
                                        self.on_status_update(f"✓ Seña estática con 2 manos '{self.training_sign_name}' guardada!")
                                else:
                                    # Seña con 1 mano
                                    self.landmarks_3d_manager.save_static_sign(
                                        self.training_sign_name,
                                        first_hand.landmark,
                                        getattr(self, 'training_description', ''),
                                        num_hands=1
                                    )
                                    if success and self.on_status_update:
                                        self.on_status_update(f"✓ Seña estática '{self.training_sign_name}' guardada!")
                            except Exception as e:
                                print(f"Error guardando landmarks 3D: {e}")
                            
                            self.on_training_mode = False
                            delattr(self, 'training_sign_name')
                    
                    # Clasificación normal
                    else:
                        sign_detected = False
                        
                        # 1️⃣ Intentar primero clasificación DINÁMICA si está activada
                        if self.use_movement_detection:
                            try:
                                dynamic_result = self._classify_dynamic_sign(first_hand.landmark)
                                
                                # Verificar que sea dict válido antes de usar
                                if (dynamic_result is not None and 
                                    isinstance(dynamic_result, dict) and 
                                    dynamic_result.get('confidence', 0) > 0.65):
                                    
                                    # Seña dinámica detectada con alta confianza
                                    if self.on_sign_detected:
                                        self.on_sign_detected(dynamic_result)
                                    sign_detected = True
                            except Exception as e:
                                # Si hay error en detección dinámica, continuar con estática
                                pass
                        
                        # 2️⃣ Si no se detectó seña dinámica, intentar clasificación ESTÁTICA
                        if not sign_detected:
                            try:
                                sign_result = self.sign_classifier.classify_hand_landmarks(first_hand)
                                
                                # Notificar si se detectó una seña con suficiente confianza
                                if (sign_result and sign_result['sign'] and 
                                    sign_result['confidence'] > 0.5 and 
                                    sign_result.get('stability') == 'estable'):
                                    
                                    if self.on_sign_detected:
                                        self.on_sign_detected(sign_result)
                            except Exception as e:
                                # Ignorar errores en clasificación estática
                                pass
                
                # Dibujar landmarks si se detectan manos (solo si mediapipe está presente)
                if results and getattr(results, 'multi_hand_landmarks', None) and self.mp_draw is not None and self.mp_hands is not None:
                    for handLms in results.multi_hand_landmarks:
                        try:
                            self.mp_draw.draw_landmarks(img, handLms, self.mp_hands.HAND_CONNECTIONS)
                        except Exception:
                            # ignorar fallos en dibujo
                            pass
                
                # Mostrar ventana de video SOLO si show_window=True
                if self.show_window:
                    if not self.window_created:
                        cv2.namedWindow("Detección de Manos", cv2.WINDOW_NORMAL)
                        self.window_created = True
                    cv2.imshow("Detección de Manos", img)
                    
                    # Verificar si se presiona 'q' para salir
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                else:
                    # Si no hay ventana, solo esperar un poco para no saturar CPU
                    time.sleep(0.001)
                    
        except Exception as e:
            error_msg = f"❌ Error en detección: {str(e)}"
            if self.on_error:
                self.on_error(error_msg)
        finally:
            # 🔧 FIX: Marcar como no detectando primero
            self.is_detecting = False
            
            # 🔧 FIX: NO liberar la cámara aquí, dejar que stop_detection lo haga
            # para evitar conflictos de liberación doble
            
            # Cerrar solo las ventanas de OpenCV
            try:
                cv2.destroyAllWindows()
            except:
                pass
            
    def cleanup(self):
        """Limpia todos los recursos"""
        self.stop_detection()
        
        # 🔧 FIX: Asegurar que la cámara se libere completamente
        if self.cap is not None:
            try:
                self.cap.release()
                self.cap = None
            except Exception:
                pass
        
        # Cerrar mediapipe
        if getattr(self, 'hands', None):
            try:
                self.hands.close()
            except Exception:
                pass
        
        # Cerrar todas las ventanas de OpenCV
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass
