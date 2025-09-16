import tkinter as tk
from tkinter import ttk, scrolledtext
import time
from hand_detector import HandDetector

class HandDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Detección de Manos - Interfaz Moderna")
        self.root.geometry("800x600")
        self.root.configure(bg='#1e1e1e')
        
        # Inicializar detector de manos
        self.hand_detector = HandDetector()
        self.hand_detector.set_callbacks(
            on_hand_detected=self.on_hand_detected,
            on_status_update=self.update_text,
            on_error=self.update_text,
            on_sign_detected=self.on_sign_detected
        )
        
        # Variables para traducción
        self.current_sign = "Sin seña detectada"
        self.sign_confidence = 0.0
        
        # Crear interfaz
        self.create_interface()
        
    def create_interface(self):
        """Crea la interfaz de usuario moderna"""
        # Estilo personalizado
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar colores oscuros
        style.configure('TFrame', background='#1e1e1e')
        style.configure('TLabel', background='#1e1e1e', foreground='#ffffff', font=('Arial', 12))
        style.configure('TButton', background='#404040', foreground='#ffffff', font=('Arial', 10, 'bold'))
        style.configure('TText', background='#2d2d2d', foreground='#ffffff', font=('Consolas', 10))
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="🤖 Traductor de Señas Peruano", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Frame de controles
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Fila 1 de controles
        controls_row1 = ttk.Frame(controls_frame)
        controls_row1.pack(fill=tk.X, pady=(0, 10))
        
        # Botón de inicio/parada
        self.start_button = ttk.Button(controls_row1, text="▶️ Iniciar Detección", 
                                      command=self.toggle_detection)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón traducción
        self.translation_button = ttk.Button(controls_row1, text="🇪🇸 Traducción: ON", 
                                            command=self.toggle_translation)
        self.translation_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Estado de la detección
        self.status_label = ttk.Label(controls_row1, text="Estado: Detenido", 
                                     foreground='#ff6b6b')
        self.status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Fila 2 de controles - Entrenamiento
        controls_row2 = ttk.Frame(controls_frame)
        controls_row2.pack(fill=tk.X)
        
        # Campo para nombre de seña
        ttk.Label(controls_row2, text="Entrenar seña:").pack(side=tk.LEFT)
        self.training_entry = ttk.Entry(controls_row2, width=15)
        self.training_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        # Botón de entrenamiento
        self.train_button = ttk.Button(controls_row2, text="🎯 Entrenar", 
                                      command=self.start_training)
        self.train_button.pack(side=tk.LEFT)
        
        # Frame para la seña detectada
        sign_frame = ttk.LabelFrame(main_frame, text="👋 Seña Detectada", padding="10")
        sign_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.sign_label = ttk.Label(sign_frame, text=self.current_sign, 
                                   font=('Arial', 18, 'bold'), foreground='#4ecdc4')
        self.sign_label.pack()
        
        self.confidence_label = ttk.Label(sign_frame, 
                                         text=f"Confianza: {self.sign_confidence:.0%}", 
                                         font=('Arial', 12))
        self.confidence_label.pack()
        
        # Frame para el cuadro de texto
        text_frame = ttk.LabelFrame(main_frame, text="📝 Registro de Actividad", 
                                   padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cuadro de texto con scroll
        self.text_area = scrolledtext.ScrolledText(text_frame, height=15, wrap=tk.WORD)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Texto inicial
        initial_text = """¡Bienvenido al Traductor de Señas Peruano!

Características disponibles:
• Detección y traducción de señas en tiempo real
• Entrenamiento de nuevas señas personalizadas
• Señas básicas incluidas: HOLA, GRACIAS, SI, NO, BIEN, etc.
• Sistema de confianza y estabilidad para mayor precisión

Instrucciones:
1. Presiona 'Iniciar Detección' para comenzar
2. Coloca tu mano frente a la cámara
3. Para entrenar: escribe el nombre de la seña y presiona 'Entrenar'
4. Mantén la seña estática por unos segundos para mejor reconocimiento

¡Disfruta traduciendo señas!"""
        
        self.text_area.insert(tk.END, initial_text)
        
        # Frame de información
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        info_text = "💡 Consejo: Asegúrate de tener buena iluminación y mantén las señas estáticas por 2-3 segundos"
        info_label = ttk.Label(info_frame, text=info_text, foreground='#4ecdc4')
        info_label.pack()
        
    def toggle_detection(self):
        """Alterna entre iniciar y parar la detección"""
        if not self.hand_detector.is_running():
            self.start_detection()
        else:
            self.stop_detection()
            
    def start_detection(self):
        """Inicia la detección de manos"""
        success = self.hand_detector.start_detection()
        
        if success:
            self.start_button.config(text="⏹️ Parar Detección")
            self.status_label.config(text="Estado: Detectando...", foreground='#4ecdc4')
        else:
            self.status_label.config(text="Estado: Error", foreground='#ff6b6b')
            
    def stop_detection(self):
        """Para la detección de manos"""
        self.hand_detector.stop_detection()
        
        self.start_button.config(text="▶️ Iniciar Detección")
        self.status_label.config(text="Estado: Detenido", foreground='#ff6b6b')
        
    def on_hand_detected(self, hand_count):
        """Callback cuando se detectan manos"""
        if hand_count > 0:
            self.update_text(f"👋 Detectadas {hand_count} mano(s) en la imagen")
        else:
            self.update_text(f"👋 No se detectan manos")
            # Limpiar seña cuando no hay manos
            self.update_sign_display("Sin seña detectada", 0.0)
    
    def on_sign_detected(self, sign_result):
        """Callback cuando se detecta una seña"""
        sign_name = sign_result.get('sign', 'Desconocida')
        confidence = sign_result.get('confidence', 0.0)
        stability = sign_result.get('stability', 'inestable')
        
        # Actualizar display de seña
        self.update_sign_display(sign_name, confidence)
        
        # Log detallado
        self.update_text(
            f"👋 Seña: {sign_name} | "
            f"Confianza: {confidence:.1%} | "
            f"Estabilidad: {stability}"
        )
    
    def update_sign_display(self, sign_name, confidence):
        """Actualiza la visualización de la seña detectada"""
        self.current_sign = sign_name
        self.sign_confidence = confidence
        
        # Usar after para actualizar desde otro hilo
        self.root.after(0, self._update_sign_labels)
    
    def _update_sign_labels(self):
        """Actualiza las etiquetas de seña (llamado desde hilo principal)"""
        self.sign_label.config(text=self.current_sign)
        
        # Color basado en confianza
        if self.sign_confidence > 0.8:
            color = '#4ecdc4'  # Verde azulado (alta confianza)
        elif self.sign_confidence > 0.6:
            color = '#ffeb3b'  # Amarillo (confianza media)
        elif self.sign_confidence > 0.3:
            color = '#ff9800'  # Naranja (baja confianza)
        else:
            color = '#757575'  # Gris (sin seña)
        
        self.sign_label.config(foreground=color)
        self.confidence_label.config(text=f"Confianza: {self.sign_confidence:.0%}")
    
    def toggle_translation(self):
        """Activa/desactiva la traducción"""
        if hasattr(self.hand_detector, 'toggle_translation'):
            enabled = self.hand_detector.toggle_translation()
            status_text = "ON" if enabled else "OFF"
            color = '#4ecdc4' if enabled else '#ff6b6b'
            
            self.translation_button.config(text=f"🇪🇸 Traducción: {status_text}")
            # Note: ttk buttons don't support foreground color changes easily
            
            if not enabled:
                self.update_sign_display("Traducción desactivada", 0.0)
    
    def start_training(self):
        """Inicia el entrenamiento de una nueva seña"""
        sign_name = self.training_entry.get().strip().upper()
        
        if not sign_name:
            self.update_text("⚠️ Error: Ingresa el nombre de la seña a entrenar")
            return
        
        if not self.hand_detector.is_running():
            self.update_text("⚠️ Error: Inicia la detección primero")
            return
        
        # Iniciar entrenamiento
        self.hand_detector.add_training_sample(sign_name, f"Seña entrenada por usuario")
        self.update_text(f"🎯 Preparado para entrenar '{sign_name}' - mantén la seña por 2 segundos")
        
        # Limpiar campo
        self.training_entry.delete(0, tk.END)
        
    def update_text(self, message):
        """Actualiza el área de texto con un nuevo mensaje"""
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        # Usar after para actualizar desde otro hilo
        self.root.after(0, lambda: self._append_text(formatted_message))
        
    def _append_text(self, message):
        """Anexa texto al área de texto (llamado desde el hilo principal)"""
        self.text_area.insert(tk.END, message)
        self.text_area.see(tk.END)
        
    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        if self.hand_detector.is_running():
            self.hand_detector.stop_detection()
        self.hand_detector.cleanup()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = HandDetectionApp(root)
    
    # Configurar cierre de ventana
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Centrar ventana
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (800 // 2)
    y = (root.winfo_screenheight() // 2) - (600 // 2)
    root.geometry(f"800x600+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()