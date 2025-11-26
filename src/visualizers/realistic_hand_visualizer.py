"""
Visualizador 3D REALISTA de manos con superficies y sombreado
Usa triángulos para crear manos sólidas en lugar de solo líneas
"""

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from src.core.landmarks_3d_manager import Landmarks3DManager, SignTo3DTranslator


class RealisticHand3DVisualizer:
    """Visualizador 3D REALISTA de manos con superficies"""
    
    def __init__(self, figsize=(12, 9)):
        self.fig = plt.figure(figsize=figsize)
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.setup_plot()
        
    def setup_plot(self):
        """Configura los ejes del plot 3D"""
        self.ax.set_xlabel('X', fontsize=12)
        self.ax.set_ylabel('Y', fontsize=12)
        self.ax.set_zlabel('Z', fontsize=12)
        self.ax.set_xlim([0, 1])
        self.ax.set_ylim([0, 1])
        self.ax.set_zlim([-0.3, 0.3])
        self.ax.invert_yaxis()
        self.ax.set_title('Mano Realista 3D', fontsize=16, fontweight='bold')
        
        # Color de fondo
        self.ax.set_facecolor('#1a1a1a')
        self.fig.patch.set_facecolor('#2c2c2c')
        
    def _create_finger_mesh(self, landmarks, finger_indices, color, alpha=0.7):
        """
        Crea una malla triangular para un dedo usando los landmarks
        
        Args:
            landmarks: Array de landmarks 3D
            finger_indices: Lista de índices del dedo [base, mid1, mid2, tip]
            color: Color del dedo
            alpha: Transparencia
        """
        if len(finger_indices) < 4:
            return []
        
        meshes = []
        
        # Radio base para crear el cilindro del dedo
        base_radius = 0.02
        tip_radius = 0.015
        segments = 8  # Número de segmentos alrededor del dedo
        
        for i in range(len(finger_indices) - 1):
            start_idx = finger_indices[i]
            end_idx = finger_indices[i + 1]
            
            start = landmarks[start_idx]
            end = landmarks[end_idx]
            
            # Radio interpolado
            t = i / (len(finger_indices) - 1)
            radius = base_radius * (1 - t) + tip_radius * t
            
            # Crear cilindro entre dos puntos
            direction = end - start
            length = np.linalg.norm(direction)
            
            if length < 0.001:
                continue
            
            direction = direction / length
            
            # Crear círculo perpendicular
            if abs(direction[2]) < 0.9:
                perp1 = np.cross(direction, [0, 0, 1])
            else:
                perp1 = np.cross(direction, [1, 0, 0])
            
            perp1 = perp1 / np.linalg.norm(perp1)
            perp2 = np.cross(direction, perp1)
            
            # Crear vértices del cilindro
            for seg in range(segments):
                angle1 = 2 * np.pi * seg / segments
                angle2 = 2 * np.pi * (seg + 1) / segments
                
                # Puntos en el círculo inicial
                p1 = start + radius * (np.cos(angle1) * perp1 + np.sin(angle1) * perp2)
                p2 = start + radius * (np.cos(angle2) * perp1 + np.sin(angle2) * perp2)
                
                # Puntos en el círculo final
                p3 = end + radius * (np.cos(angle1) * perp1 + np.sin(angle1) * perp2)
                p4 = end + radius * (np.cos(angle2) * perp1 + np.sin(angle2) * perp2)
                
                # Crear dos triángulos para el segmento
                tri1 = [p1, p2, p3]
                tri2 = [p2, p4, p3]
                
                meshes.append(tri1)
                meshes.append(tri2)
        
        return meshes
    
    def _create_palm_mesh(self, landmarks):
        """
        Crea una malla triangular para la palma de la mano
        
        Args:
            landmarks: Array de landmarks 3D
        """
        # Puntos clave de la palma: muñeca y bases de dedos
        wrist = landmarks[0]
        thumb_base = landmarks[1]
        index_base = landmarks[5]
        middle_base = landmarks[9]
        ring_base = landmarks[13]
        pinky_base = landmarks[17]
        
        # Crear triángulos para la palma
        palm_triangles = [
            # Centro de la palma
            [wrist, index_base, middle_base],
            [wrist, middle_base, ring_base],
            [wrist, ring_base, pinky_base],
            
            # Conexión con el pulgar
            [wrist, thumb_base, index_base],
            
            # Parte superior de la palma
            [index_base, middle_base, ring_base],
            [index_base, ring_base, pinky_base],
        ]
        
        return palm_triangles
    
    def draw_realistic_hand(self, landmarks_3d, hand_color='skin', clear=True):
        """
        Dibuja una mano REALISTA con superficies y sombreado
        
        Args:
            landmarks_3d: Lista de 21 puntos [x, y, z] o lista de 2 manos
            hand_color: 'skin', 'blue', 'red', o color hex
            clear: Si True, limpia el plot antes de dibujar
        """
        if clear:
            self.ax.clear()
            self.setup_plot()
        
        # Detectar si es una o dos manos
        if isinstance(landmarks_3d, list) and len(landmarks_3d) > 0:
            first_item = landmarks_3d[0]
            if isinstance(first_item, list) and len(first_item) == 3:
                # Una sola mano
                self._draw_single_realistic_hand(landmarks_3d, hand_color)
            elif len(landmarks_3d) == 2 and isinstance(first_item, list):
                # Dos manos
                self._draw_single_realistic_hand(landmarks_3d[0], 'skin')
                self._draw_single_realistic_hand(landmarks_3d[1], 'lightblue')
    
    def _draw_single_realistic_hand(self, landmarks_3d, hand_color):
        """Dibuja una sola mano con superficies realistas"""
        if not landmarks_3d or len(landmarks_3d) != 21:
            return
        
        landmarks_array = np.array(landmarks_3d)
        
        # Definir color de piel realista
        if hand_color == 'skin':
            base_color = '#FFDAB9'  # PeachPuff
            finger_colors = {
                'thumb': '#FFD7BA',
                'index': '#FFCBA4',
                'middle': '#FFCBA4',
                'ring': '#FFCBA4',
                'pinky': '#FFD7BA',
                'palm': '#FFDAB9'
            }
        elif hand_color == 'blue':
            base_color = '#ADD8E6'
            finger_colors = {
                'thumb': '#87CEEB',
                'index': '#87CEEB',
                'middle': '#87CEEB',
                'ring': '#87CEEB',
                'pinky': '#87CEEB',
                'palm': '#B0D8E6'
            }
        elif hand_color == 'lightblue':
            base_color = '#B0E0E6'
            finger_colors = {
                'thumb': '#87CEFA',
                'index': '#87CEFA',
                'middle': '#87CEFA',
                'ring': '#87CEFA',
                'pinky': '#87CEFA',
                'palm': '#B0E0E6'
            }
        else:
            base_color = hand_color
            finger_colors = {key: hand_color for key in ['thumb', 'index', 'middle', 'ring', 'pinky', 'palm']}
        
        # Definir dedos
        fingers = {
            'thumb': [0, 1, 2, 3, 4],
            'index': [0, 5, 6, 7, 8],
            'middle': [0, 9, 10, 11, 12],
            'ring': [0, 13, 14, 15, 16],
            'pinky': [0, 17, 18, 19, 20]
        }
        
        all_meshes = []
        
        # Crear mallas para cada dedo
        for finger_name, indices in fingers.items():
            color = finger_colors[finger_name]
            meshes = self._create_finger_mesh(landmarks_array, indices, color)
            
            if meshes:
                # Crear colección de polígonos para este dedo
                poly = Poly3DCollection(meshes, alpha=0.8, facecolor=color, 
                                       edgecolor='#8B7355', linewidths=0.5)
                poly.set_zsort('average')
                self.ax.add_collection3d(poly)
        
        # Crear malla para la palma
        palm_meshes = self._create_palm_mesh(landmarks_array)
        if palm_meshes:
            palm_poly = Poly3DCollection(palm_meshes, alpha=0.85, 
                                        facecolor=finger_colors['palm'],
                                        edgecolor='#8B7355', linewidths=0.5)
            palm_poly.set_zsort('average')
            self.ax.add_collection3d(palm_poly)
        
        # Agregar puntos clave sutiles para referencia
        self.ax.scatter(
            landmarks_array[0:1, 0],
            landmarks_array[0:1, 1],
            landmarks_array[0:1, 2],
            c='#8B4513', s=50, alpha=0.6, zorder=100
        )
    
    def show_sign(self, sign_name: str, landmarks_manager: Landmarks3DManager):
        """Muestra una seña guardada con visualización realista"""
        sign_data = landmarks_manager.get_sign_landmarks(sign_name)
        
        if not sign_data:
            print(f"Seña '{sign_name}' no encontrada")
            return
        
        frames = sign_data.get("frames", [])
        sign_type = sign_data.get("type", "static")
        num_hands = sign_data.get("num_hands", 1)
        
        self.ax.set_title(f'{sign_name} ({sign_type}) - {num_hands} mano(s)', 
                         fontsize=16, fontweight='bold')
        
        if sign_type == "static":
            if frames:
                self.draw_realistic_hand(frames[0])
                plt.draw()
                plt.pause(0.1)
        else:
            self.animate_frames(frames, sign_name)
    
    def animate_frames(self, frames, title="Animación"):
        """Anima una secuencia de frames con visualización realista"""
        if not frames:
            return
        
        plt.ion()
        
        for i, frame in enumerate(frames):
            self.draw_realistic_hand(frame)
            self.ax.set_title(f'{title} - Frame {i+1}/{len(frames)}', 
                            fontsize=16, fontweight='bold')
            plt.draw()
            plt.pause(0.033)
        
        plt.ioff()
    
    def animate_text(self, text: str, translator: SignTo3DTranslator):
        """Anima una secuencia de texto completa con visualización realista"""
        sequence = translator.get_complete_animation_sequence(text, smooth=True)
        
        if not sequence:
            print("No se pudo generar animación para el texto")
            return
        
        self.animate_frames(sequence, title=f"Traduciendo: {text}")
    
    def show(self):
        """Muestra el plot"""
        plt.show()
    
    def close(self):
        """Cierra el plot"""
        plt.close(self.fig)


def demo():
    """Demo del visualizador realista"""
    print("=" * 60)
    print("🙌 VISUALIZADOR 3D REALISTA DE MANOS")
    print("=" * 60)
    print()
    print("✨ Características:")
    print("   • Manos con superficies sólidas (no líneas)")
    print("   • Color de piel realista")
    print("   • Sombreado y profundidad")
    print("   • Soporte para 1 o 2 manos")
    print()
    
    manager = Landmarks3DManager()
    signs = manager.get_all_signs()
    
    if not signs:
        print("⚠️  No hay señas para visualizar")
        return
    
    print(f"✓ {len(signs)} seña(s) disponible(s)\n")
    
    print("Opciones:")
    print("1. Ver una seña específica")
    print("2. Animar texto")
    print()
    
    choice = input("Opción (1-2): ").strip()
    
    visualizer = RealisticHand3DVisualizer()
    
    if choice == "1":
        print("\nSeñas disponibles:")
        for i, sign in enumerate(sorted(signs), 1):
            print(f"  {i}. {sign}")
        
        sign_name = input("\nNombre de la seña: ").strip().upper()
        visualizer.show_sign(sign_name, manager)
        visualizer.show()
        
    elif choice == "2":
        text = input("\nTexto a traducir: ").strip()
        translator = SignTo3DTranslator(manager)
        visualizer.animate_text(text, translator)
        visualizer.show()
    
    visualizer.close()


if __name__ == "__main__":
    demo()
