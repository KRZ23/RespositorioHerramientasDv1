"""
Módulo para detección de manos usando OpenCV y MediaPipe.
Utiliza la API de MediaPipe Hands y OpenCV para detección en tiempo real.
"""

import os
# Configuración para reducir mensajes
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Solo errores críticos de TF
os.environ['MEDIAPIPE_DISABLE_GPU'] = '1'  # Deshabilitar mensajes de GPU

import numpy as np
import cv2
import mediapipe as mp
import sys
import signal
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurar MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

def signal_handler(signum, frame):
    """Manejador de señales para cierre controlado."""
    logger.info("Señal de terminación recibida. Cerrando aplicación...")
    sys.exit(0)

def init_camera(camera_index=0):
    """Inicializa y verifica el acceso a la cámara."""
    try:
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            raise RuntimeError(f"No se pudo acceder a la cámara {camera_index}")
        
        # Configurar resolución para mejor rendimiento
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)  # Limitar FPS para mejor rendimiento
        
        actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        logger.info(f"Cámara inicializada: {actual_width}x{actual_height}")
        return cap
    except Exception as e:
        logger.error(f"Error al inicializar la cámara: {e}")
        raise

import os
# Configuración para reducir mensajes
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Solo errores críticos de TF
os.environ['MEDIAPIPE_DISABLE_GPU'] = '1'  # Deshabilitar mensajes de GPU

import numpy as np  # Requerido para el procesamiento de imágenes
import cv2
import mediapipe as mp
import sys
import time
import tempfile
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles  # Para estilos de dibujo mejorados

# Verificar si ya hay una instancia ejecutándose
LOCK_FILE = Path(tempfile.gettempdir()) / "hand_detection.lock"
if LOCK_FILE.exists():
    print("Ya hay una instancia del programa ejecutándose.")
    print("Si esto es un error, elimine el archivo:", LOCK_FILE)
    sys.exit(1)

# Crear archivo de bloqueo
LOCK_FILE.write_text("")

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def process_frame(frame, hands):
    """Procesa un frame y detecta las manos."""
    if frame is None:
        return None
    
    # Optimizar el frame para procesamiento
    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_rgb.flags.writeable = False
    results = hands.process(frame_rgb)
    frame_rgb.flags.writeable = True

    # Dibujar las detecciones
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())
    
    return frame

def main():
    """Función principal del programa."""
    # Registrar manejador de señales para cierre controlado
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    cap = None
    try:
        logger.info("Iniciando aplicación de detección de manos...")
        cap = init_camera()

        # Configurar detector de manos
        with mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
            model_complexity=1
        ) as hands:
            logger.info("Detector de manos inicializado. Presione 'ESC' para salir.")
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    logger.error("Error al leer el frame de la cámara.")
                    break

                # Procesar el frame
                processed_frame = process_frame(frame, hands)
                if processed_frame is None:
                    continue

                # Mostrar resultado
                cv2.imshow('Detección de manos', processed_frame)
                
                # Verificar si se presiona ESC
                if cv2.waitKey(1) & 0xFF == 27:
                    logger.info("Tecla ESC presionada. Cerrando aplicación...")
                    break

    except Exception as e:
        logger.error(f"Error en la aplicación: {e}")
    
    finally:
        if cap is not None:
            cap.release()
        cv2.destroyAllWindows()
        logger.info("Aplicación cerrada correctamente.")

if __name__ == '__main__':
    main()

try:
    # Inicializar la cámara
    print("Inicializando cámara...")
    cap = init_camera()
    
    print("Presione ESC para salir...")
    
    # Configurar el detector de manos
    # Configurar el detector de manos con parámetros optimizados
    hands = mp_hands.Hands(
        static_image_mode=False,  # Optimizado para video stream
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5,
        model_complexity=1  # Equilibrio entre precisión y velocidad
    )

    print("Presione 'ESC' para salir...")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Error al leer el frame de la cámara.")
            break

        # Optimizar el frame para procesamiento
        frame = cv2.flip(frame, 1)  # Espejo horizontal
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb.flags.writeable = False  # Mejora el rendimiento
        results = hands.process(frame_rgb)
        frame_rgb.flags.writeable = True

        # Dibujar las detecciones
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())

            cv2.imshow('Detección de manos', frame)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC para salir
                break

finally:
    # Asegurar que los recursos se liberen incluso si hay errores
    if 'cap' in locals():
        cap.release()
    cv2.destroyAllWindows()
    
    # Eliminar el archivo de bloqueo
    try:
        LOCK_FILE.unlink()
    except:
        pass
    
    print("Programa finalizado. Todos los recursos han sido liberados.")
