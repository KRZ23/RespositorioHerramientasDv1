"""
Dataset de Señas Dinámicas LSP (Lengua de Señas Peruana)
=========================================================
Patrones de movimiento para señas que requieren detección temporal.
SIN usar TensorFlow ni modelos de ML - solo análisis de movimiento.
"""

# Patrones de señas dinámicas comunes en LSP
DYNAMIC_SIGNS_PATTERNS = {
    'HOLA': {
        'movement_pattern': 'WAVE',  # Movimiento ondulante
        'direction': 'IZQUIERDA_DERECHA',
        'frequency_range': (1.5, 4.0),  # Hz (oscilaciones por segundo)
        'avg_speed_range': (0.05, 0.3),  # Velocidad promedio normalizada
        'trajectory_length_range': (0.3, 1.5),  # Longitud de trayectoria
        'hand_shape': {
            'fingers_extended': [True, True, True, True, True],  # Todos los dedos
            'hand_openness': 0.7  # Mano abierta
        }
    },
    
    'ADIOS': {
        'movement_pattern': 'WAVE',
        'direction': 'ARRIBA_ABAJO',  # Movimiento vertical
        'frequency_range': (1.5, 4.0),
        'avg_speed_range': (0.05, 0.3),
        'trajectory_length_range': (0.3, 1.5),
        'hand_shape': {
            'fingers_extended': [True, True, True, True, True],
            'hand_openness': 0.7
        }
    },
    
    'SI': {
        'movement_pattern': 'OSCILLATE',  # Oscilación
        'direction': 'ARRIBA_ABAJO',
        'frequency_range': (2.0, 5.0),  # Movimiento más rápido
        'avg_speed_range': (0.08, 0.4),
        'trajectory_length_range': (0.2, 0.8),
        'hand_shape': {
            'fingers_extended': [False, True, False, False, False],  # Solo índice
            'hand_openness': 0.3
        }
    },
    
    'NO': {
        'movement_pattern': 'OSCILLATE',
        'direction': 'IZQUIERDA_DERECHA',
        'frequency_range': (2.0, 5.0),
        'avg_speed_range': (0.08, 0.4),
        'trajectory_length_range': (0.2, 0.8),
        'hand_shape': {
            'fingers_extended': [False, True, False, False, False],
            'hand_openness': 0.3
        }
    },
    
    'AYUDA': {
        'movement_pattern': 'SHAKE',  # Sacudida
        'direction': 'ESTATICO',  # Sin dirección específica
        'frequency_range': (3.0, 6.0),  # Rápido
        'avg_speed_range': (0.1, 0.5),
        'trajectory_length_range': (0.4, 1.2),
        'hand_shape': {
            'fingers_extended': [True, True, True, True, True],
            'hand_openness': 0.6
        }
    },
    
    'VENIR': {
        'movement_pattern': 'APPROACH',  # Acercamiento
        'direction': 'ADELANTE',  # Hacia la cámara (Z positivo)
        'frequency_range': (0.5, 2.0),  # Más lento
        'avg_speed_range': (0.03, 0.2),
        'trajectory_length_range': (0.2, 0.8),
        'hand_shape': {
            'fingers_extended': [False, True, True, False, False],  # Índice y medio
            'hand_openness': 0.4
        }
    },
    
    'IR': {
        'movement_pattern': 'RETREAT',  # Alejamiento
        'direction': 'ATRAS',  # Alejándose de la cámara (Z negativo)
        'frequency_range': (0.5, 2.0),
        'avg_speed_range': (0.03, 0.2),
        'trajectory_length_range': (0.2, 0.8),
        'hand_shape': {
            'fingers_extended': [False, True, True, False, False],
            'hand_openness': 0.4
        }
    },
    
    'ESPERAR': {
        'movement_pattern': 'CIRCLE',  # Movimiento circular
        'direction': 'CIRCULAR',
        'frequency_range': (0.8, 2.5),
        'avg_speed_range': (0.04, 0.25),
        'trajectory_length_range': (0.5, 1.5),
        'hand_shape': {
            'fingers_extended': [True, True, True, True, True],
            'hand_openness': 0.5
        }
    },
    
    'RAPIDO': {
        'movement_pattern': 'LINEAR',  # Movimiento lineal rápido
        'direction': 'DERECHA',
        'frequency_range': (0.5, 2.0),
        'avg_speed_range': (0.15, 0.6),  # MUY rápido
        'trajectory_length_range': (0.4, 1.5),
        'hand_shape': {
            'fingers_extended': [False, True, False, False, False],
            'hand_openness': 0.3
        }
    },
    'CUADRADO': {
        'movement_pattern': 'CIRCULAR',
        'direction': '[-8.08565669e-01  5.88397956e-01 -3.05562296e-06]',
        'frequency_range': (0, 0),
        'avg_speed_range': (0.17889006340436972, 0.5674311592429292),
        'trajectory_length_range': (0.18839858987553976, 1.2887999703996034),
        'hand_shape': {
            'fingers_extended': [True, True, True, True, True],
            'hand_openness': 0.6
        }
    },
    'MI NOMBRE ES': {
        'movement_pattern': 'CIRCULAR',
        'direction': '[8.77206998e-01 4.80109085e-01 2.90962655e-07]',
        'frequency_range': (0, 0),
        'avg_speed_range': (0.0856204557359962, 0.5927923203147581),
        'trajectory_length_range': (0.026002672768698075, 0.9516324643609801),
        'hand_shape': {
            'fingers_extended': [True, True, True, True, True],
            'hand_openness': 0.6
        }
    },
    'MI NOMBRE ES': {
        'movement_pattern': 'LINEAL',
        'direction': '[-9.83101856e-01 -1.83054222e-01  1.19670916e-07]',
        'frequency_range': (0, 0),
        'avg_speed_range': (0.15414657350786323, 2.3377711974723296),
        'trajectory_length_range': (0.08869857566022249, 0.9906229966018254),
        'hand_shape': {
            'fingers_extended': [True, True, True, True, True],
            'hand_openness': 0.6
        }
    },
    'CRIS': {
        'movement_pattern': 'CIRCULAR',
        'direction': '[-3.23600842e-01  9.46190413e-01  3.84989666e-07]',
        'frequency_range': (0, 0),
        'avg_speed_range': (0.059371290925506234, 0.3795029429260622),
        'trajectory_length_range': (0.1552439366596982, 0.4683124980215589),
        'hand_shape': {
            'fingers_extended': [True, True, True, True, True],
            'hand_openness': 0.6
        }
    },




    
    'LENTO': {
        'movement_pattern': 'LINEAR',
        'direction': 'DERECHA',
        'frequency_range': (0.3, 1.5),
        'avg_speed_range': (0.02, 0.1),  # MUY lento
        'trajectory_length_range': (0.3, 1.2),
        'hand_shape': {
            'fingers_extended': [True, True, True, True, True],
            'hand_openness': 0.6
        }
    }
}

def is_dynamic_sign(sign_name):
    """
    Verifica si una seña es dinámica (requiere análisis de movimiento)
    
    Args:
        sign_name: Nombre de la seña
        
    Returns:
        bool: True si la seña es dinámica
    """
    return sign_name.upper() in DYNAMIC_SIGNS_PATTERNS

def get_sign_pattern(sign_name):
    """
    Obtiene el patrón de movimiento de una seña dinámica
    
    Args:
        sign_name: Nombre de la seña
        
    Returns:
        dict: Patrón de movimiento o None si no existe
    """
    return DYNAMIC_SIGNS_PATTERNS.get(sign_name.upper())

def get_all_dynamic_signs():
    """
    Obtiene lista de todas las señas dinámicas disponibles
    
    Returns:
        list: Lista de nombres de señas dinámicas
    """
    return list(DYNAMIC_SIGNS_PATTERNS.keys())
