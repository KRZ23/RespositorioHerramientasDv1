import cv2
import mediapipe as mp
import threading
import time

class HandDetector:
    """
    Clase modular para detección de manos usando MediaPipe y OpenCV.
    Maneja toda la lógica de detección de forma independiente.
    """
    
    def __init__(self):
        """Inicializa el detector de manos"""
        # Configurar MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Variables de control
        self.is_detecting = False
        self.cap = None
        self.detection_thread = None
        self.window_created = False
        
        # Callbacks para comunicación con la interfaz
        self.on_hand_detected = None
        self.on_status_update = None
        self.on_error = None
        
    def set_callbacks(self, on_hand_detected=None, on_status_update=None, on_error=None):
        """
        Establece callbacks para comunicación con la interfaz
        
        Args:
            on_hand_detected: Función que se llama cuando se detectan manos (hand_count)
            on_status_update: Función que se llama para actualizar estado (message)
            on_error: Función que se llama en caso de error (error_message)
        """
        self.on_hand_detected = on_hand_detected
        self.on_status_update = on_status_update
        self.on_error = on_error
        
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
                
            # Inicializar cámara
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                error_msg = "❌ Error: No se pudo acceder a la cámara"
                if self.on_error:
                    self.on_error(error_msg)
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
            return False
            
    def stop_detection(self):
        """Para la detección de manos"""
        self.is_detecting = False
        
        # Esperar a que termine el hilo
        if self.detection_thread and self.detection_thread.is_alive():
            self.detection_thread.join(timeout=1.0)
        
        # Liberar recursos
        if self.cap:
            self.cap.release()
            
        cv2.destroyAllWindows()
        
        if self.on_status_update:
            self.on_status_update("⏹️ Detección detenida")
            
    def is_running(self):
        """Verifica si la detección está activa"""
        return self.is_detecting
        
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
                results = self.hands.process(imgRGB)
                
                # Contar manos detectadas
                current_hand_count = len(results.multi_hand_landmarks) if results.multi_hand_landmarks else 0
                
                # Notificar cambio en número de manos
                if current_hand_count != hand_count:
                    hand_count = current_hand_count
                    if self.on_hand_detected:
                        self.on_hand_detected(hand_count)
                
                # Dibujar landmarks si se detectan manos
                if results.multi_hand_landmarks:
                    for handLms in results.multi_hand_landmarks:
                        self.mp_draw.draw_landmarks(img, handLms, self.mp_hands.HAND_CONNECTIONS)
                
                # Mostrar ventana de video (solo crear una vez)
                if not self.window_created:
                    cv2.namedWindow("Detección de Manos", cv2.WINDOW_NORMAL)
                    self.window_created = True
                cv2.imshow("Detección de Manos", img)
                
                # Verificar si se presiona 'q' para salir
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except Exception as e:
            error_msg = f"❌ Error en detección: {str(e)}"
            if self.on_error:
                self.on_error(error_msg)
        finally:
            # Limpiar al salir
            if self.cap:
                self.cap.release()
            cv2.destroyAllWindows()
            self.is_detecting = False
            
    def cleanup(self):
        """Limpia todos los recursos"""
        self.stop_detection()
        if self.hands:
            self.hands.close()
