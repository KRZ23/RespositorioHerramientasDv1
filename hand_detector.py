import cv2
try:
    import mediapipe as mp
    HAS_MEDIAPIPE = True
except Exception:
    mp = None
    HAS_MEDIAPIPE = False
import threading
import time
from sign_classifier import SignClassifier

class HandDetector:
    """
    Clase modular para detección de manos usando MediaPipe y OpenCV.
    Maneja toda la lógica de detección de forma independiente.
    """
    
    def __init__(self, show_window=True):
        """
        Inicializa el detector de manos
        
        Args:
            show_window (bool): Si True, muestra ventana de OpenCV. Si False, solo procesa en background.
        """
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
        
        # Inicializar clasificador de señas
        self.sign_classifier = SignClassifier(confidence_threshold=0.6)
        self.translation_enabled = True
        
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
        """Añade muestra de entrenamiento del frame actual"""
        # Esta función será llamada desde la interfaz cuando se quiera entrenar
        # El entrenamiento se hará con el próximo frame detectado
        self.training_sign_name = sign_name
        self.training_description = description
        self.on_training_mode = True
        if self.on_status_update:
            self.on_status_update(f"Modo entrenamiento: {sign_name}")
        
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
                    # Tomar la primera mano detectada para clasificación
                    first_hand = results.multi_hand_landmarks[0]
                    
                    # Modo entrenamiento
                    if self.on_training_mode and hasattr(self, 'training_sign_name'):
                        success = self.sign_classifier.add_training_sample(
                            self.training_sign_name, first_hand, 
                            getattr(self, 'training_description', '')
                        )
                        if success and self.on_status_update:
                            self.on_status_update(f"Muestra de {self.training_sign_name} guardada ✓")
                        self.on_training_mode = False
                        delattr(self, 'training_sign_name')
                    
                    # Clasificación normal
                    else:
                        sign_result = self.sign_classifier.classify_hand_landmarks(first_hand)
                        
                        # Notificar si se detectó una seña con suficiente confianza
                        if (sign_result and sign_result['sign'] and 
                            sign_result['confidence'] > 0.5 and 
                            sign_result.get('stability') == 'estable'):
                            
                            if self.on_sign_detected:
                                self.on_sign_detected(sign_result)
                
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
