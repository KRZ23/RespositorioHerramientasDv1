import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands() # Inicializa el detector de manos
mp_draw = mp.solutions.drawing_utils # Utilidades para dibujar

cap = cv2.VideoCapture(0) # Captura de video desde la cámara 0

while True:
    success, img = cap.read()
    if not success:
        break

    # Convierte BGR a RGB
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB) # Procesa la imagen con MediaPipe

    if results.multi_hand_landmarks: # Si se detectan manos
        for handLms in results.multi_hand_landmarks:
            # Dibuja los puntos de referencia en la imagen original
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Hand Detection", img) # Muestra la imagen con las detecciones
    if cv2.waitKey(1) & 0xFF == ord('q'): # Presiona 'q' para salir
        break

cap.release()
cv2.destroyAllWindows()