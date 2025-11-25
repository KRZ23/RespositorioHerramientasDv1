"""
Visualizador 3D de señas usando Matplotlib
Permite visualizar y animar los landmarks 3D de las manos
"""

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from landmarks_3d_manager import Landmarks3DManager, SignTo3DTranslator
import time


class Hand3DVisualizer:
    """Visualizador 3D de mano usando Matplotlib"""
    
    # Conexiones entre landmarks de MediaPipe (índices)
    HAND_CONNECTIONS = [
        # Pulgar
        (0, 1), (1, 2), (2, 3), (3, 4),
        # Índice
        (0, 5), (5, 6), (6, 7), (7, 8),
        # Medio
        (0, 9), (9, 10), (10, 11), (11, 12),
        # Anular
        (0, 13), (13, 14), (14, 15), (15, 16),
        # Meñique
        (0, 17), (17, 18), (18, 19), (19, 20),
        # Palma
        (5, 9), (9, 13), (13, 17)
    ]
    
    def __init__(self, figsize=(10, 8)):
        """
        Inicializa el visualizador 3D
        
        Args:
            figsize: Tamaño de la figura (ancho, alto)
        """
        self.fig = plt.figure(figsize=figsize)
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.setup_plot()
        
    def setup_plot(self):
        """Configura los ejes del plot 3D"""
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.ax.set_xlim([0, 1])
        self.ax.set_ylim([0, 1])
        self.ax.set_zlim([-0.3, 0.3])
        
        # Invertir eje Y para que coincida con la cámara
        self.ax.invert_yaxis()
        
        # Título
        self.ax.set_title('Visualización 3D de Seña', fontsize=14, fontweight='bold')
        
    def draw_hand(self, landmarks_3d, clear=True):
        """
        Dibuja una mano en 3D con colores por dedo
        
        Args:
            landmarks_3d: Lista de 21 puntos [x, y, z] o lista de 2 manos
            clear: Si True, limpia el plot antes de dibujar
        """
        if clear:
            self.ax.clear()
            self.setup_plot()
        
        # Detectar si es una o dos manos
        if isinstance(landmarks_3d, list) and len(landmarks_3d) > 0:
            first_item = landmarks_3d[0]
            # Si el primer elemento es una lista de 3 coordenadas, es una mano
            if isinstance(first_item, list) and len(first_item) == 3:
                # Una sola mano
                self._draw_single_hand(landmarks_3d)
            # Si tiene 2 elementos y cada uno es una lista de 21 landmarks
            elif len(landmarks_3d) == 2 and isinstance(first_item, list):
                # Dos manos
                self._draw_single_hand(landmarks_3d[0])
                self._draw_single_hand(landmarks_3d[1])
    
    def _draw_single_hand(self, landmarks_3d):
        """Dibuja una sola mano con colores por dedo"""
        if not landmarks_3d or len(landmarks_3d) != 21:
            return
        
        landmarks_array = np.array(landmarks_3d)
        
        # Colores por dedo
        finger_colors = {
            'thumb': '#e74c3c',      # Pulgar - Rojo
            'index': '#f39c12',      # Índice - Naranja
            'middle': '#2ecc71',     # Medio - Verde
            'ring': '#3498db',       # Anular - Azul
            'pinky': '#9b59b6',      # Meñique - Púrpura
            'palm': '#95a5a6'        # Palma - Gris
        }
        
        # Conexiones agrupadas por dedo
        finger_connections = {
            'thumb': [(0, 1), (1, 2), (2, 3), (3, 4)],
            'index': [(0, 5), (5, 6), (6, 7), (7, 8)],
            'middle': [(0, 9), (9, 10), (10, 11), (11, 12)],
            'ring': [(0, 13), (13, 14), (14, 15), (15, 16)],
            'pinky': [(0, 17), (17, 18), (18, 19), (19, 20)],
            'palm': [(5, 9), (9, 13), (13, 17)]
        }
        
        # Dibujar conexiones con colores
        for finger, connections in finger_connections.items():
            color = finger_colors[finger]
            for start_idx, end_idx in connections:
                start_point = landmarks_array[start_idx]
                end_point = landmarks_array[end_idx]
                
                self.ax.plot(
                    [start_point[0], end_point[0]],
                    [start_point[1], end_point[1]],
                    [start_point[2], end_point[2]],
                    color=color,
                    linewidth=4,
                    alpha=0.9
                )
        
        # Dibujar articulaciones
        # Muñeca
        self.ax.scatter(
            [landmarks_array[0, 0]],
            [landmarks_array[0, 1]],
            [landmarks_array[0, 2]],
            c='#2c3e50',
            s=200,
            alpha=1.0,
            edgecolors='white',
            linewidths=2
        )
        
        # Bases de dedos
        base_indices = [1, 5, 9, 13, 17]
        for idx in base_indices:
            self.ax.scatter(
                [landmarks_array[idx, 0]],
                [landmarks_array[idx, 1]],
                [landmarks_array[idx, 2]],
                c='#34495e',
                s=100,
                alpha=0.9,
                edgecolors='white',
                linewidths=1
            )
        
        # Articulaciones medias
        joint_indices = [2, 3, 6, 7, 10, 11, 14, 15, 18, 19]
        for idx in joint_indices:
            self.ax.scatter(
                [landmarks_array[idx, 0]],
                [landmarks_array[idx, 1]],
                [landmarks_array[idx, 2]],
                c='#7f8c8d',
                s=60,
                alpha=0.8
            )
        
        # Puntas de dedos (coloreadas)
        tip_indices = [4, 8, 12, 16, 20]
        tip_colors = ['#e74c3c', '#f39c12', '#2ecc71', '#3498db', '#9b59b6']
        for idx, tip_color in zip(tip_indices, tip_colors):
            self.ax.scatter(
                [landmarks_array[idx, 0]],
                [landmarks_array[idx, 1]],
                [landmarks_array[idx, 2]],
                c=tip_color,
                s=120,
                alpha=1.0,
                edgecolors='white',
                linewidths=2
            )
        
    def show_sign(self, sign_name: str, landmarks_manager: Landmarks3DManager):
        """
        Muestra una seña guardada
        
        Args:
            sign_name: Nombre de la seña
            landmarks_manager: Manager de landmarks 3D
        """
        sign_data = landmarks_manager.get_sign_landmarks(sign_name)
        
        if not sign_data:
            print(f"Seña '{sign_name}' no encontrada")
            return
        
        frames = sign_data.get("frames", [])
        sign_type = sign_data.get("type", "static")
        
        self.ax.set_title(f'{sign_name} ({sign_type})', fontsize=14, fontweight='bold')
        
        if sign_type == "static":
            # Mostrar frame único
            if frames:
                self.draw_hand(frames[0])
                plt.draw()
                plt.pause(0.1)
        else:
            # Animar frames dinámicos
            self.animate_frames(frames, sign_name)
    
    def animate_frames(self, frames, title="Animación"):
        """
        Anima una secuencia de frames
        
        Args:
            frames: Lista de frames con landmarks 3D
            title: Título de la animación
        """
        if not frames:
            return
        
        plt.ion()  # Modo interactivo
        
        for i, frame in enumerate(frames):
            self.draw_hand(frame)
            self.ax.set_title(f'{title} - Frame {i+1}/{len(frames)}', 
                            fontsize=14, fontweight='bold')
            plt.draw()
            plt.pause(0.033)  # ~30 FPS
        
        plt.ioff()
    
    def animate_text(self, text: str, translator: SignTo3DTranslator):
        """
        Anima una secuencia de texto completa
        
        Args:
            text: Texto a animar (ej: "HOLA COMO ESTAS")
            translator: Traductor de texto a landmarks
        """
        sequence = translator.get_complete_animation_sequence(text, smooth=True)
        
        if not sequence:
            print("No se pudo generar animación para el texto")
            return
        
        self.animate_frames(sequence, title=f"Traduciendo: {text}")
    
    def show(self):
        """Muestra el plot (bloqueante)"""
        plt.show()
    
    def close(self):
        """Cierra el plot"""
        plt.close(self.fig)


def demo_visualizer():
    """Demo del visualizador 3D"""
    # Inicializar managers
    landmarks_manager = Landmarks3DManager()
    visualizer = Hand3DVisualizer()
    
    print("=== Visualizador 3D de Señas ===\n")
    
    # Listar señas disponibles
    signs = landmarks_manager.get_all_signs()
    
    if not signs:
        print("No hay señas guardadas en el dataset 3D")
        print("Primero entrena algunas señas usando la interfaz principal")
        return
    
    print(f"Señas disponibles ({len(signs)}):")
    for i, sign in enumerate(signs, 1):
        sign_type = landmarks_manager.get_sign_type(sign)
        print(f"  {i}. {sign} ({sign_type})")
    
    print("\n¿Qué quieres hacer?")
    print("1. Ver una seña específica")
    print("2. Animar texto completo")
    print("3. Ver todas las señas")
    
    choice = input("\nOpción (1-3): ").strip()
    
    if choice == "1":
        # Ver seña específica
        sign_name = input("\nNombre de la seña: ").strip().upper()
        visualizer.show_sign(sign_name, landmarks_manager)
        visualizer.show()
        
    elif choice == "2":
        # Animar texto
        text = input("\nTexto a traducir: ").strip()
        translator = SignTo3DTranslator(landmarks_manager)
        visualizer.animate_text(text, translator)
        visualizer.show()
        
    elif choice == "3":
        # Ver todas las señas
        plt.ion()
        for sign in signs:
            print(f"\nMostrando: {sign}")
            visualizer.show_sign(sign, landmarks_manager)
            input("Presiona Enter para continuar...")
        plt.ioff()
        visualizer.show()
    
    else:
        print("Opción inválida")
    
    visualizer.close()


if __name__ == "__main__":
    demo_visualizer()
