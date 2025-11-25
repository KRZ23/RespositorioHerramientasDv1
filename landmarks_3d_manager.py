"""
Sistema de gestión de landmarks 3D para animación de señas
Guarda las posiciones 3D completas de los 21 puntos de la mano
"""

import json
import os
import numpy as np
from typing import List, Dict, Optional


class Landmarks3DManager:
    """Gestiona el guardado y carga de landmarks 3D para animación"""
    
    def __init__(self, dataset_file="landmarks_3d_dataset.json"):
        self.dataset_file = dataset_file
        self.dataset = self._load_dataset()
    
    def _load_dataset(self) -> Dict:
        """Carga el dataset de landmarks 3D"""
        if os.path.exists(self.dataset_file):
            try:
                with open(self.dataset_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error cargando dataset 3D: {e}")
                return {}
        return {}
    
    def _save_dataset(self) -> bool:
        """Guarda el dataset de landmarks 3D"""
        try:
            with open(self.dataset_file, 'w', encoding='utf-8') as f:
                json.dump(self.dataset, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error guardando dataset 3D: {e}")
            return False
    
    def extract_landmarks_3d(self, hand_landmarks) -> List[List[float]]:
        """
        Extrae las coordenadas 3D (x, y, z) de los 21 landmarks de MediaPipe
        
        Args:
            hand_landmarks: Objeto de landmarks de MediaPipe
            
        Returns:
            Lista de 21 puntos [x, y, z]
        """
        landmarks_3d = []
        for landmark in hand_landmarks:
            landmarks_3d.append([
                float(landmark.x),
                float(landmark.y),
                float(landmark.z)
            ])
        return landmarks_3d
    
    def save_static_sign(self, sign_name: str, hand_landmarks, description: str = "", num_hands: int = 1) -> bool:
        """
        Guarda una seña estática con sus landmarks 3D (1 o 2 manos)
        
        Args:
            sign_name: Nombre de la seña
            hand_landmarks: Landmarks de MediaPipe (puede ser una lista de 1 o 2 manos)
            description: Descripción opcional
            num_hands: Número de manos en la seña
            
        Returns:
            True si se guardó correctamente
        """
        try:
            # Detectar si es una o dos manos
            if isinstance(hand_landmarks, list) and len(hand_landmarks) > 1 and hasattr(hand_landmarks[0], 'landmark'):
                # Múltiples manos detectadas
                landmarks_3d = []
                for hand in hand_landmarks[:2]:  # Máximo 2 manos
                    landmarks_3d.append(self.extract_landmarks_3d(hand.landmark))
            else:
                # Una sola mano
                landmarks_3d = self.extract_landmarks_3d(hand_landmarks)
            
            if sign_name not in self.dataset:
                self.dataset[sign_name] = {
                    "type": "static",
                    "description": description,
                    "frames": [],
                    "count": 0,
                    "num_hands": num_hands
                }
            
            # Agregar frame (para señas estáticas, solo hay 1 frame)
            self.dataset[sign_name]["frames"].append(landmarks_3d)
            self.dataset[sign_name]["count"] += 1
            self.dataset[sign_name]["description"] = description
            self.dataset[sign_name]["num_hands"] = num_hands
            
            return self._save_dataset()
            
        except Exception as e:
            print(f"Error guardando seña estática 3D: {e}")
            return False
    
    def save_dynamic_sign(self, sign_name: str, landmarks_sequence: List, description: str = "", num_hands: int = 1) -> bool:
        """
        Guarda una seña dinámica con múltiples frames de landmarks 3D (1 o 2 manos)
        
        Args:
            sign_name: Nombre de la seña
            landmarks_sequence: Lista de landmarks de cada frame (puede contener 1 o 2 manos por frame)
            description: Descripción opcional
            num_hands: Número de manos en la seña
            
        Returns:
            True si se guardó correctamente
        """
        try:
            # Convertir secuencia de landmarks a formato 3D
            frames_3d = []
            for hand_landmarks in landmarks_sequence:
                # Detectar si es una o dos manos por frame
                if isinstance(hand_landmarks, list) and len(hand_landmarks) > 1 and hasattr(hand_landmarks[0], 'landmark'):
                    # Múltiples manos en este frame
                    frame_data = []
                    for hand in hand_landmarks[:2]:  # Máximo 2 manos
                        frame_data.append(self.extract_landmarks_3d(hand.landmark))
                    frames_3d.append(frame_data)
                else:
                    # Una sola mano
                    landmarks_3d = self.extract_landmarks_3d(hand_landmarks)
                    frames_3d.append(landmarks_3d)
            
            # Guardar en dataset
            self.dataset[sign_name] = {
                "type": "dynamic",
                "description": description,
                "frames": frames_3d,
                "frame_count": len(frames_3d),
                "fps": 30,  # Asumiendo 30 FPS
                "num_hands": num_hands
            }
            
            return self._save_dataset()
            
        except Exception as e:
            print(f"Error guardando seña dinámica 3D: {e}")
            return False
    
    def get_sign_landmarks(self, sign_name: str) -> Optional[Dict]:
        """
        Obtiene los landmarks 3D de una seña
        
        Args:
            sign_name: Nombre de la seña
            
        Returns:
            Dict con los datos de la seña o None si no existe
        """
        return self.dataset.get(sign_name)
    
    def get_all_signs(self) -> List[str]:
        """Retorna lista de todas las señas guardadas"""
        return list(self.dataset.keys())
    
    def delete_sign(self, sign_name: str) -> bool:
        """Elimina una seña del dataset"""
        if sign_name in self.dataset:
            del self.dataset[sign_name]
            return self._save_dataset()
        return False
    
    def get_sign_type(self, sign_name: str) -> Optional[str]:
        """Retorna el tipo de seña (static o dynamic)"""
        if sign_name in self.dataset:
            return self.dataset[sign_name].get("type")
        return None
    
    def interpolate_frames(self, frames: List[List[List[float]]], target_fps: int = 60) -> List[List[List[float]]]:
        """
        Interpola frames para animación suave
        
        Args:
            frames: Lista de frames originales
            target_fps: FPS objetivo para interpolación
            
        Returns:
            Lista de frames interpolados
        """
        if len(frames) <= 1:
            return frames
        
        interpolated = []
        original_fps = 30  # FPS original
        ratio = target_fps / original_fps
        
        for i in range(len(frames) - 1):
            frame_a = np.array(frames[i])
            frame_b = np.array(frames[i + 1])
            
            # Interpolar entre frame_a y frame_b
            steps = int(ratio)
            for step in range(steps):
                alpha = step / steps
                interpolated_frame = (1 - alpha) * frame_a + alpha * frame_b
                interpolated.append(interpolated_frame.tolist())
        
        # Agregar último frame
        interpolated.append(frames[-1])
        
        return interpolated


class SignTo3DTranslator:
    """Traduce texto a secuencia de landmarks 3D para animación"""
    
    def __init__(self, landmarks_manager: Landmarks3DManager):
        self.landmarks_manager = landmarks_manager
    
    def text_to_landmarks_sequence(self, text: str) -> List[Dict]:
        """
        Convierte texto en secuencia de landmarks 3D para animar
        
        Args:
            text: Texto a traducir (ej: "HOLA COMO ESTAS")
            
        Returns:
            Lista de dicts con información de cada seña:
            [
                {
                    "sign": "HOLA",
                    "type": "dynamic",
                    "frames": [...],
                    "duration": 1.5
                },
                ...
            ]
        """
        words = text.upper().split()
        sequence = []
        
        for word in words:
            sign_data = self.landmarks_manager.get_sign_landmarks(word)
            
            if sign_data:
                sign_type = sign_data.get("type", "static")
                frames = sign_data.get("frames", [])
                
                # Calcular duración
                if sign_type == "dynamic":
                    frame_count = sign_data.get("frame_count", len(frames))
                    fps = sign_data.get("fps", 30)
                    duration = frame_count / fps
                else:
                    # Señas estáticas se mantienen por 0.8 segundos
                    duration = 0.8
                
                sequence.append({
                    "sign": word,
                    "type": sign_type,
                    "frames": frames,
                    "duration": duration
                })
            else:
                # Si no se encuentra la seña, agregar placeholder
                sequence.append({
                    "sign": word,
                    "type": "unknown",
                    "frames": None,
                    "duration": 0.5
                })
        
        return sequence
    
    def get_complete_animation_sequence(self, text: str, smooth: bool = True) -> List[List[List[float]]]:
        """
        Genera secuencia completa de frames para animar el texto
        
        Args:
            text: Texto a traducir
            smooth: Si True, interpola frames para transiciones suaves
            
        Returns:
            Lista de frames con landmarks 3D listos para animar
        """
        sequence = self.text_to_landmarks_sequence(text)
        all_frames = []
        
        for sign_data in sequence:
            frames = sign_data.get("frames")
            
            if frames is None:
                # Seña desconocida - agregar pose neutra
                neutral_pose = self._get_neutral_pose()
                all_frames.append(neutral_pose)
                continue
            
            sign_type = sign_data.get("type")
            
            if sign_type == "static":
                # Para señas estáticas, mantener el frame por varios frames
                static_frame = frames[0] if frames else self._get_neutral_pose()
                duration = sign_data.get("duration", 0.8)
                frame_count = int(duration * 30)  # 30 FPS
                
                for _ in range(frame_count):
                    all_frames.append(static_frame)
            
            elif sign_type == "dynamic":
                # Para señas dinámicas, agregar todos los frames
                if smooth and len(frames) > 1:
                    # Interpolar para suavidad
                    interpolated = self.landmarks_manager.interpolate_frames(frames, target_fps=60)
                    all_frames.extend(interpolated)
                else:
                    all_frames.extend(frames)
            
            # Agregar pequeña pausa entre señas (5 frames)
            if all_frames:
                pause_frame = all_frames[-1]
                for _ in range(5):
                    all_frames.append(pause_frame)
        
        return all_frames
    
    def _get_neutral_pose(self) -> List[List[float]]:
        """Retorna pose neutra de la mano (mano abierta)"""
        # Pose neutra básica - mano abierta centrada
        return [
            [0.5, 0.5, 0.0],  # 0: Muñeca
            [0.45, 0.45, 0.0],  # 1: Pulgar base
            [0.4, 0.4, 0.0],  # 2: Pulgar medio
            [0.35, 0.35, 0.0],  # 3: Pulgar punta
            [0.3, 0.3, 0.0],  # 4: Pulgar tip
            [0.5, 0.3, 0.0],  # 5: Índice base
            [0.5, 0.2, 0.0],  # 6: Índice medio
            [0.5, 0.1, 0.0],  # 7: Índice punta
            [0.5, 0.05, 0.0],  # 8: Índice tip
            [0.55, 0.3, 0.0],  # 9: Medio base
            [0.55, 0.18, 0.0],  # 10: Medio medio
            [0.55, 0.08, 0.0],  # 11: Medio punta
            [0.55, 0.03, 0.0],  # 12: Medio tip
            [0.6, 0.32, 0.0],  # 13: Anular base
            [0.6, 0.22, 0.0],  # 14: Anular medio
            [0.6, 0.13, 0.0],  # 15: Anular punta
            [0.6, 0.08, 0.0],  # 16: Anular tip
            [0.65, 0.35, 0.0],  # 17: Meñique base
            [0.65, 0.27, 0.0],  # 18: Meñique medio
            [0.65, 0.20, 0.0],  # 19: Meñique punta
            [0.65, 0.15, 0.0],  # 20: Meñique tip
        ]
