#!/usr/bin/env python3
"""
Configuración de iconos y símbolos para la interfaz del traductor de señas.
Incluye fallbacks para sistemas sin soporte completo de emojis.
"""

import tkinter as tk
import sys
import platform

def test_emoji_support():
    """Prueba si el sistema soporta emojis correctamente"""
    try:
        # Crear una ventana temporal para probar renderizado
        test_root = tk.Tk()
        test_root.withdraw()  # Ocultar ventana
        
        test_label = tk.Label(test_root, text="🤟", font=('Arial', 16))
        test_label.update_idletasks()
        
        # En sistemas sin soporte, los emojis pueden renderizarse como cuadrados
        test_root.destroy()
        return True
    except:
        return False

class IconConfig:
    """Configuración de iconos con fallbacks para sistemas sin emojis"""
    
    def __init__(self):
        self.has_emoji_support = test_emoji_support()
        
        # Configurar iconos basado en soporte del sistema
        if self.has_emoji_support:
            self.icons = self._get_emoji_icons()
        else:
            self.icons = self._get_ascii_icons()
    
    def _get_emoji_icons(self):
        """Iconos con emojis completos"""
        return {
            # Estados
            'running': '🟢',
            'stopped': '🔴',
            'warning': '🟡',
            'error': '❌',
            
            # Acciones
            'play': '🚀',
            'stop': '⏹️',
            'pause': '⏸️',
            'help': '❓',
            'settings': '⚙️',
            
            # Detección
            'hand': '🤲',
            'sign_detected': '🤟',
            'high_confidence': '🎯',
            'medium_confidence': '🤔',
            'low_confidence': '🤷',
            'no_detection': '👀',
            
            # Estadísticas
            'detections': '🎯',
            'translations': '✅',
            'accuracy': '📈',
            'time': '⏱️',
            
            # Entrenamiento
            'training': '🧠',
            'learning': '🎓',
            
            # Interface
            'title': '🤟',
            'info': '💡',
            'success': '✨',
            'globe': '🌐',
            'stats': '📊'
        }
    
    def _get_ascii_icons(self):
        """Iconos ASCII/Unicode de respaldo"""
        return {
            # Estados
            'running': '●',    # Punto verde (será coloreado)
            'stopped': '●',    # Punto rojo (será coloreado)
            'warning': '⚠',
            'error': '✗',
            
            # Acciones
            'play': '▶',
            'stop': '■',
            'pause': '⏸',
            'help': '?',
            'settings': '⚙',
            
            # Detección
            'hand': '✋',
            'sign_detected': '☞',
            'high_confidence': '●',
            'medium_confidence': '◐',
            'low_confidence': '○',
            'no_detection': '○',
            
            # Estadísticas
            'detections': '●',
            'translations': '✓',
            'accuracy': '↗',
            'time': '⏲',
            
            # Entrenamiento
            'training': '◎',
            'learning': '▲',
            
            # Interface
            'title': '♠',
            'info': 'ⓘ',
            'success': '★',
            'globe': '◉',
            'stats': '■'
        }
    
    def get_icon(self, key):
        """Obtiene un icono por su clave"""
        return self.icons.get(key, '•')
    
    def get_status_icon(self, status):
        """Obtiene icono de estado específico"""
        status_map = {
            'running': self.get_icon('running'),
            'stopped': self.get_icon('stopped'),
            'error': self.get_icon('error'),
            'warning': self.get_icon('warning')
        }
        return status_map.get(status, self.get_icon('stopped'))
    
    def get_confidence_icon(self, confidence):
        """Obtiene icono basado en nivel de confianza"""
        if confidence > 0.8:
            return self.get_icon('high_confidence')
        elif confidence > 0.6:
            return self.get_icon('medium_confidence') 
        elif confidence > 0.3:
            return self.get_icon('low_confidence')
        else:
            return self.get_icon('no_detection')

# Instancia global
icon_config = IconConfig()

# Función de conveniencia
def get_icon(key):
    """Función de conveniencia para obtener iconos"""
    return icon_config.get_icon(key)

def get_status_icon(status):
    """Función de conveniencia para iconos de estado"""
    return icon_config.get_status_icon(status)

def get_confidence_icon(confidence):
    """Función de conveniencia para iconos de confianza"""
    return icon_config.get_confidence_icon(confidence)

if __name__ == "__main__":
    # Prueba de iconos
    print("🧪 Probando soporte de iconos...")
    print(f"Sistema: {platform.system()} {platform.release()}")
    print(f"Soporte de emojis: {'Sí' if icon_config.has_emoji_support else 'No'}")
    print()
    
    print("Iconos de prueba:")
    test_keys = ['title', 'play', 'stop', 'hand', 'high_confidence', 'stats']
    for key in test_keys:
        print(f"  {key}: {get_icon(key)}")
    
    print()
    print("Iconos de confianza:")
    for conf in [0.9, 0.7, 0.4, 0.1]:
        print(f"  Confianza {conf:.0%}: {get_confidence_icon(conf)}")