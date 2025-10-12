import numpy as np
import tensorflow as tf
import os
import json

# 1. Cargar datos desde tu estructura de carpetas
# (Iterar sobre ml_pipeline/data/{etiqueta}/*.json)

# 2. Preprocesar los datos
# (Convertir a arrays de numpy, crear etiquetas numéricas)

# 3. Dividir en conjuntos de entrenamiento y validación
# (X_train, y_train, X_val, y_val)

# 4. Definir el modelo LSTM simple
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(T, D)), # T=48, D=225
    tf.keras.layers.LSTM(64),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(num_clases, activation='softmax')
])

# 5. Compilar y entrenar el modelo
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=50)

# 6. Guardar y exportar a ONNX
model.save('mi_modelo_lsp')
# os.system('python -m tf2onnx.convert --saved-model mi_modelo_lsp --output ../public/lsp_model.onnx')