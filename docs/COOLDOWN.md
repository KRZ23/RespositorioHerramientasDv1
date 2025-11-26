# 🔄 Sistema de Cooldown - Prevención de Duplicados

## 📋 Problema Identificado

Cuando el detector está activo continuamente, puede registrar la misma seña múltiples veces (100+ registros de una sola seña), lo que satura el historial y hace difícil revisar las traducciones reales.

## ✅ Solución Implementada

### 🎯 Sistema de Cooldown

Se implementó un sistema de "tiempo de espera" (cooldown) que evita que la misma seña se registre múltiples veces consecutivamente.

### ⚙️ Cómo Funciona

1. **Tiempo de Espera**: Después de detectar una seña, el sistema espera un tiempo configurable (por defecto 2 segundos) antes de volver a registrar la misma seña.

2. **Control Inteligente**: 
   - Si detectas "HOLA" → Se registra inmediatamente
   - Si sigues mostrando "HOLA" → No se registra de nuevo hasta que pasen 2 segundos
   - Si cambias a "GRACIAS" → Se registra inmediatamente (es una seña diferente)

3. **Ajustable**: Puedes modificar el tiempo de cooldown desde la interfaz según tus necesidades.

## 🎨 Interfaz

### Nuevo Control en la UI

```
┌─────────────────────────────────────────┐
│ 🎓 Entrenamiento Personalizado          │
│                                         │
│ Nombre: [________] [Entrenar]          │
│ Cooldown (seg): [2.0] ⬆️⬇️              │
└─────────────────────────────────────────┘
```

### Valores Recomendados

| Situación | Cooldown | Descripción |
|-----------|----------|-------------|
| Señas rápidas | 0.5-1.0 seg | Para cambios rápidos de señas |
| **Normal (recomendado)** | **2.0 seg** | **Balance perfecto** |
| Señas lentas | 3.0-5.0 seg | Para práctica o demostración |
| Sin límite | 10.0 seg | Para control manual total |

## 💻 Implementación Técnica

### Variables de Control

```python
self.last_sign_detected = None      # Última seña detectada
self.last_sign_time = 0              # Timestamp de última detección
self.sign_cooldown = 2.0             # Tiempo de espera (segundos)
```

### Lógica de Filtrado

```python
def add_to_history(self, sign_name, confidence):
    current_time = time.time()
    
    # Verificar cooldown
    if (self.last_sign_detected == sign_name and 
        (current_time - self.last_sign_time) < self.sign_cooldown):
        return  # Aún en cooldown, no agregar
    
    # Actualizar control
    self.last_sign_detected = sign_name
    self.last_sign_time = current_time
    
    # Agregar al historial
    self.translation_history.append(...)
```

## 📊 Resultados

### Antes del Cooldown
```
[12:00:01] HOLA (85%)
[12:00:01] HOLA (87%)
[12:00:01] HOLA (86%)
[12:00:02] HOLA (88%)
[12:00:02] HOLA (85%)
... (95 registros más)
```

### Después del Cooldown (2 segundos)
```
[12:00:01] HOLA (85%)
[12:00:03] GRACIAS (92%)
[12:00:05] BIEN (88%)
[12:00:08] AMOR (90%)
```

## 🎯 Beneficios

1. **✅ Historial limpio**: Solo muestra cambios reales de señas
2. **✅ Fácil revisión**: Puedes ver la secuencia real de comunicación
3. **✅ Exportación útil**: Los archivos exportados son legibles
4. **✅ Menos ruido**: Estadísticas más precisas
5. **✅ Personalizable**: Ajusta según tu velocidad de comunicación

## 🔧 Cómo Ajustar el Cooldown

### Desde la Interfaz

1. Encuentra el campo "Cooldown (seg):" en la sección de Entrenamiento
2. Usa las flechas ⬆️⬇️ para ajustar en incrementos de 0.5 segundos
3. O escribe directamente el valor y presiona Enter
4. El cambio se aplica inmediatamente

### Feedback Visual

Cuando cambias el cooldown, verás un mensaje en el log:
```
[12:34:56] ⏱️ Cooldown actualizado a 3.0 segundos
```

## 💡 Casos de Uso

### Práctica Individual
- **Cooldown**: 2-3 segundos
- **Razón**: Tiempo para cambiar de seña cómodamente

### Demostración/Enseñanza
- **Cooldown**: 3-5 segundos
- **Razón**: Tiempo para explicar cada seña

### Comunicación Rápida
- **Cooldown**: 1-2 segundos
- **Razón**: Fluidez en la conversación

### Testing/Desarrollo
- **Cooldown**: 0.5-1 segundo
- **Razón**: Probar rápidamente múltiples señas

## 📝 Notas Adicionales

- El cooldown NO afecta la detección visual en tiempo real
- Solo controla cuándo se agrega una entrada al historial
- Cada seña diferente se registra inmediatamente sin esperar
- El contador se resetea automáticamente al cambiar de seña

## 🆕 Versión

- **Agregado en**: v2.1
- **Fecha**: 20 de Octubre 2025
- **Estado**: ✅ Estable y probado

---

**¡Disfruta de un historial más limpio y organizado!** 🎉
