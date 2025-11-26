"""
Módulo Core: Detección, clasificación y gestión de landmarks 3D
Contiene las clases principales para el procesamiento de señas
"""

from .hand_detector import HandDetector
from .sign_classifier import SignClassifier
from .landmarks_3d_manager import Landmarks3DManager, SignTo3DTranslator
from .movement_analyzer import MovementAnalyzer
from .sign_features import SignFeatureExtractor

__all__ = [
    'HandDetector',
    'SignClassifier',
    'Landmarks3DManager',
    'SignTo3DTranslator',
    'MovementAnalyzer',
    'SignFeatureExtractor'
]
