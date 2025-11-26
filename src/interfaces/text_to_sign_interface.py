"""
Interfaz gráfica para traducir texto a señas animadas en 3D
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

from src.core.landmarks_3d_manager import Landmarks3DManager, SignTo3DTranslator
from src.visualizers.hand_3d_visualizer import Hand3DVisualizer
from src.visualizers.realistic_hand_visualizer import RealisticHand3DVisualizer


class TextToSignTranslator(tk.Tk):
    """Interfaz para traducir texto a señas animadas"""
    
    def __init__(self):
        super().__init__()
        
        self.title("Traductor Texto → Señas 3D")
        self.geometry("1000x700")
        self.configure(bg='#2c3e50')
        
        # Inicializar managers
        self.landmarks_manager = Landmarks3DManager()
        self.translator = SignTo3DTranslator(self.landmarks_manager)
        
        # Visualizador realista
        self.realistic_visualizer = RealisticHand3DVisualizer(figsize=(8, 6))
        
        # Estado
        self.is_animating = False
        self.animation_thread = None
        self.use_realistic = True  # Usar visualización realista por defecto
        
        self.create_ui()
        self.list_available_signs()
        
    def create_ui(self):
        """Crea la interfaz de usuario"""
        
        # Frame principal
        main_frame = tk.Frame(self, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # === PANEL IZQUIERDO: Controles ===
        left_panel = tk.Frame(main_frame, bg='#34495e', relief=tk.RAISED, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
        
        # Título
        title_label = tk.Label(
            left_panel,
            text="📝 Traductor Texto → Señas",
            font=('Arial', 16, 'bold'),
            bg='#34495e',
            fg='white'
        )
        title_label.pack(pady=10)
        
        # Área de texto de entrada
        input_frame = tk.LabelFrame(
            left_panel,
            text="Texto a traducir",
            font=('Arial', 12, 'bold'),
            bg='#34495e',
            fg='white'
        )
        input_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        self.text_input = scrolledtext.ScrolledText(
            input_frame,
            height=8,
            font=('Arial', 12),
            wrap=tk.WORD,
            bg='#ecf0f1',
            fg='#2c3e50'
        )
        self.text_input.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        self.text_input.insert(1.0, "Escribe aquí el texto a traducir...")
        
        # Botón traducir
        self.translate_btn = tk.Button(
            left_panel,
            text="🎬 Traducir y Animar",
            command=self.start_translation,
            font=('Arial', 14, 'bold'),
            bg='#27ae60',
            fg='white',
            activebackground='#229954',
            cursor='hand2',
            height=2
        )
        self.translate_btn.pack(padx=10, pady=10, fill=tk.X)
        
        # Botón detener
        self.stop_btn = tk.Button(
            left_panel,
            text="⏹ Detener",
            command=self.stop_animation,
            font=('Arial', 12, 'bold'),
            bg='#e74c3c',
            fg='white',
            activebackground='#c0392b',
            cursor='hand2',
            state=tk.DISABLED
        )
        self.stop_btn.pack(padx=10, pady=(0, 10), fill=tk.X)
        
        # Lista de señas disponibles
        signs_frame = tk.LabelFrame(
            left_panel,
            text="Señas disponibles",
            font=('Arial', 12, 'bold'),
            bg='#34495e',
            fg='white'
        )
        signs_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        self.signs_listbox = tk.Listbox(
            signs_frame,
            font=('Arial', 10),
            bg='#ecf0f1',
            fg='#2c3e50',
            selectmode=tk.SINGLE
        )
        self.signs_listbox.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        signs_scrollbar = tk.Scrollbar(signs_frame, command=self.signs_listbox.yview)
        signs_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.signs_listbox.config(yscrollcommand=signs_scrollbar.set)
        
        # Estado
        self.status_label = tk.Label(
            left_panel,
            text="Estado: Listo",
            font=('Arial', 10),
            bg='#34495e',
            fg='#ecf0f1',
            anchor=tk.W
        )
        self.status_label.pack(padx=10, pady=5, fill=tk.X)
        
        # === PANEL DERECHO: Visualización 3D ===
        right_panel = tk.Frame(main_frame, bg='#34495e', relief=tk.RAISED, bd=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Usar la figura del visualizador realista
        self.fig = self.realistic_visualizer.fig
        self.ax = self.realistic_visualizer.ax
        
        # Canvas para mostrar la figura
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_panel)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Información de animación
        self.info_label = tk.Label(
            right_panel,
            text="Esperando traducción...",
            font=('Arial', 12, 'bold'),
            bg='#34495e',
            fg='white'
        )
        self.info_label.pack(pady=5)
        
    def list_available_signs(self):
        """Lista las señas disponibles en el dataset"""
        signs = self.landmarks_manager.get_all_signs()
        
        self.signs_listbox.delete(0, tk.END)
        
        if not signs:
            self.signs_listbox.insert(tk.END, "No hay señas guardadas")
            self.signs_listbox.config(fg='red')
        else:
            for sign in sorted(signs):
                sign_type = self.landmarks_manager.get_sign_type(sign)
                display_text = f"{sign} ({sign_type})"
                self.signs_listbox.insert(tk.END, display_text)
        
        self.update_status(f"Señas cargadas: {len(signs)}")
    
    def update_status(self, message):
        """Actualiza el mensaje de estado"""
        self.status_label.config(text=f"Estado: {message}")
    
    def start_translation(self):
        """Inicia la traducción y animación"""
        if self.is_animating:
            return
        
        # Obtener texto
        text = self.text_input.get(1.0, tk.END).strip()
        
        if not text or text == "Escribe aquí el texto a traducir...":
            self.update_status("❌ Ingresa texto para traducir")
            return
        
        # Desactivar botón y activar stop
        self.translate_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.is_animating = True
        
        # Iniciar animación en thread separado
        self.animation_thread = threading.Thread(
            target=self._animate_text,
            args=(text,),
            daemon=True
        )
        self.animation_thread.start()
    
    def stop_animation(self):
        """Detiene la animación"""
        self.is_animating = False
        self.translate_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.update_status("⏹ Animación detenida")
    
    def _animate_text(self, text):
        """Anima el texto completo (ejecutado en thread)"""
        try:
            self.update_status(f"🎬 Traduciendo: {text}")
            
            # Obtener secuencia de animación
            sequence = self.translator.text_to_landmarks_sequence(text)
            
            if not sequence:
                self.update_status("❌ No se pudo generar animación")
                self.is_animating = False
                return
            
            # Animar cada seña
            for sign_data in sequence:
                if not self.is_animating:
                    break
                
                sign = sign_data['sign']
                sign_type = sign_data['type']
                frames = sign_data.get('frames')
                
                if frames is None:
                    # Seña desconocida
                    self.info_label.config(text=f"❓ Seña '{sign}' no encontrada")
                    self._draw_neutral_pose()
                    self.after(500, lambda: None)
                    continue
                
                # Actualizar info
                self.info_label.config(text=f"🎭 {sign} ({sign_type})")
                
                if sign_type == "static":
                    # Mostrar seña estática
                    self._draw_hand(frames[0])
                    self.after(800, lambda: None)  # Mantener 0.8s
                    
                elif sign_type == "dynamic":
                    # Animar frames dinámicos
                    for i, frame in enumerate(frames):
                        if not self.is_animating:
                            break
                        self._draw_hand(frame)
                        self.after(33, lambda: None)  # ~30 FPS
                
                # Pausa entre señas
                self.after(150, lambda: None)
            
            # Finalizar
            if self.is_animating:
                self.update_status("✅ Traducción completada")
                self.info_label.config(text="✅ Animación completada")
            
        except Exception as e:
            self.update_status(f"❌ Error: {e}")
            print(f"Error en animación: {e}")
        
        finally:
            self.is_animating = False
            self.translate_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
    
    def _draw_hand(self, landmarks_3d, hand_color='skin'):
        """
        Dibuja una mano REALISTA en el plot 3D
        
        Args:
            landmarks_3d: Lista de 21 puntos [x, y, z] o lista de 2 manos
            hand_color: Color base de la mano ('skin', 'blue', etc.)
        """
        # Usar el visualizador realista
        self.realistic_visualizer.draw_realistic_hand(landmarks_3d, hand_color, clear=True)
        
        # Actualizar el canvas embebido
        self.canvas.draw()
    
    def _draw_neutral_pose(self):
        """Dibuja pose neutra"""
        neutral = self.translator._get_neutral_pose()
        self._draw_hand(neutral)


def main():
    """Función principal"""
    app = TextToSignTranslator()
    app.mainloop()


if __name__ == "__main__":
    main()
