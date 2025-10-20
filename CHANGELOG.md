# 📋 Registro de Cambios - Traductor de Señas Peruano

## 🆕 Versión 2.1 - 20 de Octubre 2025

### ✨ Nuevas Características

#### 📜 Historial de Traducciones
- **Array de almacenamiento**: Todas las traducciones detectadas se guardan automáticamente
- **Límite de 100 traducciones**: Sistema de gestión automática del historial
- **Vista visual**: Lista interactiva con timestamp y nivel de confianza
- **Selección múltiple**: Navegación fácil por el historial

#### 🔊 Text-to-Speech (Lectura en Voz Alta)
- **Motor TTS integrado**: Utiliza pyttsx3 para síntesis de voz offline
- **Reproducción individual**: Reproduce cualquier traducción seleccionada
- **Reproducción completa**: Escucha todo el historial en secuencia
- **Configuración automática**: Intenta usar voz en español si está disponible
- **Ejecución en hilo separado**: No bloquea la interfaz de usuario

#### 💾 Exportación de Datos
- **Exportar a archivo TXT**: Guarda todo el historial con timestamp
- **Formato organizado**: Incluye estadísticas y texto completo
- **Nombre único**: Usa fecha y hora para evitar sobrescribir

#### 🎨 Mejoras de Interfaz
- **Panel de historial expandido**: Visualización clara de traducciones
- **Botones intuitivos**: Reproducir, limpiar y exportar
- **Geometría optimizada**: Ventana ampliada a 1100x700 para mejor UX
- **Colores modernos**: Esquema de colores mejorado

### 🔧 Funcionalidades

#### Gestión de Historial
```python
# Agregar traducción al historial (automático cuando confianza > 0.5)
self.add_to_history(sign_name, confidence)

# Limpiar historial
self.clear_history()

# Exportar historial
self.export_history()  # Crea archivo traducciones_YYYYMMDD_HHMMSS.txt
```

#### Text-to-Speech
```python
# Reproducir traducción seleccionada
self.speak_selected()

# Reproducir todo el historial
self.speak_all()

# Reproducir texto personalizado
self.speak_text("Hola mundo")
```

### 📊 Estructura de Datos del Historial

Cada entrada en el array `translation_history` contiene:
```python
{
    'timestamp': '12:34:56',          # Hora de detección
    'sign': 'HOLA',                   # Nombre de la seña
    'confidence': 0.85,                # Nivel de confianza (0-1)
    'datetime': 1729425896.12         # Unix timestamp
}
```

### 🎯 Umbral de Confianza

- Solo se agregan al historial señas con **confianza > 0.5**
- Esto asegura calidad en las traducciones almacenadas
- Reduce ruido de detecciones falsas

### 🔊 Configuración de TTS

El motor TTS se configura automáticamente con:
- **Velocidad**: 150 palabras por minuto
- **Volumen**: 90%
- **Voz**: Español (si está disponible en el sistema)
- **Modo**: Offline (no requiere internet)

### 📦 Nuevas Dependencias

```bash
pip install pyttsx3
```

### 🐛 Correcciones

- Resuelto conflicto con numpy y OpenCV
- Reinstalada scipy correctamente
- Limpiada instalación duplicada de opencv-contrib-python

### 🎓 Uso

1. **Ver historial**: El panel inferior izquierdo muestra todas las traducciones
2. **Seleccionar traducción**: Haz clic en cualquier entrada del historial
3. **Reproducir**: Presiona "🔊 Reproducir Selección" para escuchar
4. **Reproducir todo**: Presiona "🔊 Reproducir Todo" para escuchar el historial completo
5. **Limpiar**: Usa "🗑️ Limpiar Historial" para resetear
6. **Exportar**: Guarda el historial con "💾 Exportar"

---

## 📌 Versión 2.0 (Anterior)

### Características Base
- ✅ Detección de manos con MediaPipe
- ✅ 10 señas peruanas pre-configuradas
- ✅ Entrenamiento personalizado
- ✅ Estadísticas en tiempo real
- ✅ Interfaz moderna con Tkinter
- ✅ Indicadores visuales de confianza
- ✅ Multi-métrico de clasificación

---

## 🚀 Próximas Funcionalidades (Roadmap)

- [ ] Modelo LSTM pre-entrenado para LSP
- [ ] Dataset expandido (50+ señas)
- [ ] Reconocimiento de secuencias de señas
- [ ] Traducción bidirecccional (texto → señas)
- [ ] Soporte para grabación de video
- [ ] Analytics avanzados
- [ ] API REST para integración

---

**Desarrollado con ❤️ para la comunidad sorda peruana**
