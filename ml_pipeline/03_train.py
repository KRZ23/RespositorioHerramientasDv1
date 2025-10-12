# ml_pipeline/03_train.py

import os
import json
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input
from tensorflow.keras.utils import to_categorical

# --- PARÁMETROS DE CONFIGURACIÓN ---
DATA_PATH = "ml_pipeline/data/raw"
MODEL_SAVE_PATH = "mi_modelo_lsp"
ONNX_EXPORT_PATH = "public/lsp_model.onnx"
SEQUENCE_LENGTH = 48  # T
VECTOR_DIMENSION = 225 # D
LABELS = ["HOLA", "ADIOS", "GRACIAS", "PORFAVOR", "PERU"]

# --- 1. CARGA Y PROCESAMIENTO DE DATOS ---
sequences, sequence_labels = [], []
for label_index, label in enumerate(LABELS):
    label_path = os.path.join(DATA_PATH, label)
    if not os.path.isdir(label_path):
        print(f"Advertencia: No se encontró el directorio para la etiqueta '{label}'. Saltando.")
        continue
    
    for filename in os.listdir(label_path):
        if filename.endswith(".json"):
            filepath = os.path.join(label_path, filename)
            with open(filepath, 'r') as f:
                data = json.load(f)
                # Asegurarse que los datos tengan la forma correcta (T, D)
                if np.array(data['frames']).shape == (SEQUENCE_LENGTH, VECTOR_DIMENSION):
                    sequences.append(data['frames'])
                    sequence_labels.append(label_index)

if not sequences:
    raise ValueError("No se encontraron datos válidos. Asegúrate de recolectar muestras primero.")

X = np.array(sequences)
y = np.array(sequence_labels)

# Convertir etiquetas a one-hot encoding
y_categorical = to_categorical(y, num_classes=len(LABELS))

# Dividir en conjuntos de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y_categorical, test_size=0.2, random_state=42, stratify=y)

print(f"Datos cargados: {len(X)} muestras.")
print(f"Forma de datos de entrenamiento (X_train): {X_train.shape}")
print(f"Forma de etiquetas de entrenamiento (y_train): {y_train.shape}")


# --- 2. DEFINICIÓN DEL MODELO ---
model = Sequential([
    Input(shape=(SEQUENCE_LENGTH, VECTOR_DIMENSION)),
    LSTM(64, return_sequences=True, activation='relu'),
    LSTM(128, return_sequences=False, activation='relu'),
    Dense(64, activation='relu'),
    Dense(32, activation='relu'),
    Dense(len(LABELS), activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.summary()

# --- 3. ENTRENAMIENTO DEL MODELO ---
print("\n--- Iniciando Entrenamiento ---")
model.fit(X_train, y_train, epochs=100, validation_data=(X_test, y_test))


# --- 4. GUARDADO Y EXPORTACIÓN A ONNX ---
print("\n--- Guardando y Exportando Modelo a ONNX ---")
model.save(MODEL_SAVE_PATH)

# La exportación a ONNX requiere tf2onnx. Asegúrate de instalarlo: pip install tf2onnx
# El comando se ejecuta en la terminal.
onnx_command = f"python -m tf2onnx.convert --saved-model {MODEL_SAVE_PATH} --output {ONNX_EXPORT_PATH}"
print(f"Ejecuta este comando en tu terminal para convertir el modelo a ONNX:\n{onnx_command}")

# Intenta ejecutar el comando automáticamente
try:
    os.system(onnx_command)
    print("Modelo exportado a ONNX exitosamente.")
except Exception as e:
    print(f"Error al exportar a ONNX automáticamente: {e}")