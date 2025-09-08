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
            on_error=self.update_text
        )
        
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
        title_label = ttk.Label(main_frame, text="🤖 Detección de Manos Inteligente", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Frame de controles
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Botón de inicio/parada
        self.start_button = ttk.Button(controls_frame, text="▶️ Iniciar Detección", 
                                      command=self.toggle_detection)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Estado de la detección
        self.status_label = ttk.Label(controls_frame, text="Estado: Detenido", 
                                     foreground='#ff6b6b')
        self.status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Frame para el cuadro de texto
        text_frame = ttk.LabelFrame(main_frame, text="📝 Área de Texto (Para fines futuros)", 
                                   padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cuadro de texto con scroll
        self.text_area = scrolledtext.ScrolledText(text_frame, height=15, wrap=tk.WORD)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Texto inicial
        initial_text = """¡Bienvenido a la aplicación de detección de manos!

Esta área de texto está disponible para:
• Mostrar información de detección en tiempo real
• Registrar comandos de voz
• Mostrar estadísticas de uso
• Cualquier otra funcionalidad futura

Presiona 'Iniciar Detección' para comenzar a detectar manos."""
        
        self.text_area.insert(tk.END, initial_text)
        
        # Frame de información
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        info_text = "💡 Consejo: Asegúrate de tener buena iluminación para una mejor detección"
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
            self.update_text("👋 No se detectan manos")
        
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