import tkinter as tk
from tkinter import ttk, scrolledtext
import time
import threading
import tempfile
import os
from gtts import gTTS
from pygame import mixer
from hand_detector import HandDetector

class HandDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🤟 Traductor de Señas Peruano - v2.1")
        self.root.geometry("1100x700")
        self.root.configure(bg='#0f0f23')  # Azul oscuro moderno
        self.root.minsize(900, 600)
        
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
        
        # 🆕 Array para almacenar traducciones
        self.translation_history = []
        self.max_history = 100  # Máximo de traducciones en historial
        
        # 🆕 Control de duplicados (cooldown)
        self.last_sign_detected = None
        self.last_sign_time = 0
        self.sign_cooldown = 2.0  # Segundos de espera antes de detectar la misma seña otra vez
        
        # 🆕 Inicializar motor de Text-to-Speech (gTTS + pygame)
        try:
            # Inicializar pygame mixer para reproducción de audio
            mixer.init()
            self.tts_available = True
            self.tts_temp_files = []  # Lista para limpiar archivos temporales
            print("✅ TTS inicializado correctamente (gTTS + pygame)")
        except Exception as e:
            self.tts_available = False
            print(f"⚠️ TTS no disponible: {e}")
        
        # Variables de estadísticas
        self.detection_count = 0
        self.successful_translations = 0
        self.session_start_time = time.time()
        
        # Paleta de colores moderna
        self.colors = {
            'primary': '#6366f1',     # Índigo vibrante
            'secondary': '#8b5cf6',   # Violeta
            'success': '#10b981',     # Verde esmeralda
            'warning': '#f59e0b',     # Ámbar
            'error': '#ef4444',       # Rojo
            'text_primary': '#f8fafc', # Blanco suave
            'text_secondary': '#cbd5e1', # Gris claro
            'background': '#0f0f23',   # Azul oscuro
            'surface': '#1e1b4b',     # Azul medio
            'accent': '#06b6d4'       # Cian
        }
        
        # Crear interfaz
        self.create_interface()
        
    def create_interface(self):
        """Crea la interfaz de usuario moderna"""
        # Estilo personalizado
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar estilos modernos
        style.configure('TFrame', background=self.colors['background'])
        style.configure('TLabel', 
                    background=self.colors['background'], 
                    foreground=self.colors['text_primary'], 
                    font=('Inter', 11))
        style.configure('Title.TLabel', 
                    background=self.colors['background'], 
                    foreground=self.colors['primary'], 
                    font=('Inter', 20, 'bold'))
        style.configure('Subtitle.TLabel', 
                    background=self.colors['background'], 
                    foreground=self.colors['text_secondary'], 
                    font=('Inter', 10))
        style.configure('TButton', 
                    background=self.colors['primary'], 
                    foreground=self.colors['text_primary'], 
                    font=('Inter', 10, 'bold'),
                    focuscolor='none')
        style.configure('Success.TButton', 
                    background=self.colors['success'])
        style.configure('Warning.TButton', 
                    background=self.colors['warning'])
        style.configure('TEntry', 
                    background=self.colors['surface'], 
                    foreground=self.colors['text_primary'],
                    borderwidth=0,
                    font=('Inter', 10))
        style.configure('TLabelFrame', 
                    background=self.colors['background'],
                    foreground=self.colors['text_secondary'],
                    borderwidth=1)
        style.configure('TLabelFrame.Label', 
                    background=self.colors['background'],
                    foreground=self.colors['accent'],
                    font=('Inter', 10, 'bold'))
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="25")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header con título y subtítulo
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 25))
        
        # Título principal
        title_label = ttk.Label(header_frame, text="� Traductor de Señas Peruano", 
                            style='Title.TLabel')
        title_label.pack()
        
        # Subtítulo
        subtitle_label = ttk.Label(header_frame, 
                                text="Inteligencia Artificial para Lenguaje de Señas • Versión 2.0", 
                                style='Subtitle.TLabel')
        subtitle_label.pack(pady=(5, 0))
        
        # Panel de estadísticas (arriba)
        stats_frame = ttk.LabelFrame(main_frame, text="📊 Estadísticas de Sesión", padding="15")
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        # Estadísticas en columnas
        self.detections_label = ttk.Label(stats_grid, text="🎯 Detecciones: 0")
        self.detections_label.grid(row=0, column=0, padx=(0, 20), sticky='w')
        
        self.translations_label = ttk.Label(stats_grid, text="✅ Traducciones: 0")
        self.translations_label.grid(row=0, column=1, padx=(0, 20), sticky='w')
        
        self.accuracy_label = ttk.Label(stats_grid, text="🎯 Precisión: 0%")
        self.accuracy_label.grid(row=0, column=2, padx=(0, 20), sticky='w')
        
        self.session_time_label = ttk.Label(stats_grid, text="⏱️ Tiempo: 00:00")
        self.session_time_label.grid(row=0, column=3, sticky='w')
        
        # Actualizar estadísticas cada segundo
        self.update_stats()
        
        # Frame de controles
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Fila 1 de controles
        controls_row1 = ttk.Frame(controls_frame)
        controls_row1.pack(fill=tk.X, pady=(0, 15))
        
        # Botón de inicio/parada
        self.start_button = ttk.Button(controls_row1, text="🚀 Iniciar Detección", 
                                    command=self.toggle_detection,
                                    style='Success.TButton')
        self.start_button.pack(side=tk.LEFT, padx=(0, 15))
        
        # Botón traducción
        self.translation_button = ttk.Button(controls_row1, text="� Traducción: ACTIVA", 
                                            command=self.toggle_translation)
        self.translation_button.pack(side=tk.LEFT, padx=(0, 15))
        
        # Botón de ayuda
        self.help_button = ttk.Button(controls_row1, text="❓ Ayuda", 
                                    command=self.show_help)
        self.help_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Estado de la detección con indicador visual
        status_frame = ttk.Frame(controls_row1)
        status_frame.pack(side=tk.LEFT, padx=(15, 0))
        
        ttk.Label(status_frame, text="Estado:").pack(side=tk.LEFT)
        self.status_indicator = ttk.Label(status_frame, text="🔴", font=('Arial', 14))
        self.status_indicator.pack(side=tk.LEFT, padx=(5, 3))
        
        self.status_label = ttk.Label(status_frame, text="Detenido")
        self.status_label.pack(side=tk.LEFT)
        
        # Fila 2 de controles - Entrenamiento
        training_frame = ttk.LabelFrame(controls_frame, text="🎓 Entrenamiento Personalizado", padding="10")
        training_frame.pack(fill=tk.X, pady=(10, 0))
        
        training_controls = ttk.Frame(training_frame)
        training_controls.pack(fill=tk.X)
        
        # Campo para nombre de seña con placeholder
        ttk.Label(training_controls, text="Nombre de la seña:").pack(side=tk.LEFT)
        self.training_entry = ttk.Entry(training_controls, width=20, font=('Inter', 10))
        self.training_entry.pack(side=tk.LEFT, padx=(10, 15))
        self.training_entry.insert(0, "Ej: HOLA_PERSONALIZADO")
        self.training_entry.bind('<FocusIn>', self.on_entry_focus_in)
        self.training_entry.bind('<FocusOut>', self.on_entry_focus_out)
        
        # Botón de entrenamiento
        self.train_button = ttk.Button(training_controls, text="🧠 Entrenar Nueva Seña", 
                                    command=self.start_training,
                                    style='Warning.TButton')
        self.train_button.pack(side=tk.LEFT, padx=(0, 15))
        
        # 🆕 Control de cooldown
        ttk.Label(training_controls, text="Cooldown (seg):").pack(side=tk.LEFT)
        self.cooldown_var = tk.DoubleVar(value=2.0)
        self.cooldown_spinbox = ttk.Spinbox(training_controls, 
                                          from_=0.5, 
                                          to=10.0, 
                                          increment=0.5,
                                          textvariable=self.cooldown_var,
                                          width=5,
                                          command=self.update_cooldown)
        self.cooldown_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        self.cooldown_spinbox.bind('<Return>', lambda e: self.update_cooldown())
        
        # Frame para la seña detectada - Más visual
        sign_frame = ttk.LabelFrame(main_frame, text="🤲 Reconocimiento en Tiempo Real", padding="20")
        sign_frame.pack(fill=tk.X, pady=(15, 15))
        
        # Container para la seña
        sign_container = ttk.Frame(sign_frame)
        sign_container.pack(fill=tk.X)
        
        # Seña detectada con emoji grande
        self.sign_emoji = ttk.Label(sign_container, text="🤔", font=('Arial', 32))
        self.sign_emoji.pack()
        
        self.sign_label = ttk.Label(sign_container, text=self.current_sign, 
                                font=('Inter', 22, 'bold'))
        self.sign_label.pack(pady=(5, 0))
        
        # Barra de confianza visual
        confidence_frame = ttk.Frame(sign_container)
        confidence_frame.pack(fill=tk.X, pady=(10, 5))
        
        ttk.Label(confidence_frame, text="Confianza:").pack(side=tk.LEFT)
        self.confidence_bar = tk.Canvas(confidence_frame, height=20, width=200, 
                                    bg=self.colors['surface'], highlightthickness=0)
        self.confidence_bar.pack(side=tk.LEFT, padx=(10, 10))
        
        self.confidence_label = ttk.Label(confidence_frame, 
                                        text=f"{self.sign_confidence:.0%}")
        self.confidence_label.pack(side=tk.LEFT)
        
        # 🆕 Frame para historial de traducciones
        history_frame = ttk.LabelFrame(main_frame, text="📜 Historial de Traducciones", 
                                    padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 10))
        
        # Contenedor para la lista y botones
        history_container = ttk.Frame(history_frame)
        history_container.pack(fill=tk.BOTH, expand=True)
        
        # Lista del historial con scrollbar
        history_list_frame = ttk.Frame(history_container)
        history_list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.history_listbox = tk.Listbox(history_list_frame, 
                                        height=8,
                                        font=('Inter', 10),
                                        bg=self.colors['surface'],
                                        fg=self.colors['text_primary'],
                                        selectbackground=self.colors['primary'],
                                        selectforeground=self.colors['text_primary'],
                                        borderwidth=0,
                                        highlightthickness=0)
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(history_list_frame, orient="vertical", 
                                command=self.history_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_listbox.config(yscrollcommand=scrollbar.set)
        
        # Panel de botones para el historial
        history_buttons_frame = ttk.Frame(history_container)
        history_buttons_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # Botón para reproducir en voz
        self.speak_button = ttk.Button(history_buttons_frame, 
                                    text="🔊 Reproducir\nSelección",
                                    command=self.speak_selected,
                                    style='Success.TButton',
                                    width=15)
        self.speak_button.pack(pady=(0, 10))
        
        # Botón para reproducir todo
        self.speak_all_button = ttk.Button(history_buttons_frame, 
                                        text="🔊 Reproducir\nTodo",
                                        command=self.speak_all,
                                        width=15)
        self.speak_all_button.pack(pady=(0, 10))
        
        # Botón para limpiar historial
        self.clear_button = ttk.Button(history_buttons_frame, 
                                    text="🗑️ Limpiar\nHistorial",
                                    command=self.clear_history,
                                    style='Warning.TButton',
                                    width=15)
        self.clear_button.pack(pady=(0, 10))
        
        # Botón para exportar
        self.export_button = ttk.Button(history_buttons_frame, 
                                    text="💾 Exportar",
                                    command=self.export_history,
                                    width=15)
        self.export_button.pack()
        
        # Frame para el cuadro de texto
        text_frame = ttk.LabelFrame(main_frame, text="📝 Registro de Actividad", 
                                padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cuadro de texto con scroll
        self.text_area = scrolledtext.ScrolledText(text_frame, height=15, wrap=tk.WORD)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        
        # Texto inicial con mejor formato
        initial_text = """🌟 ¡Bienvenido al Traductor de Señas Peruano v2.1! 🌟

🚀 CARACTERÍSTICAS NUEVAS:
• 🎯 Detección mejorada con IA avanzada
• 📊 Estadísticas en tiempo real 
• 🎨 Interfaz moderna y amigable
• 🧠 Entrenamiento personalizado de señas
• 📈 Indicadores visuales de confianza
• 📜 Historial de traducciones (sin duplicados)
• 🔊 Text-to-Speech con Google (lectura en voz alta)
• 💾 Exportación de traducciones
• ⏱️ Control de cooldown ajustable

� SEÑAS INCLUIDAS:
HOLA • GRACIAS • SÍ • NO • BIEN • MAL • AMOR • PAZ • AGUA • COMIDA

📚 INSTRUCCIONES RÁPIDAS:
1. 🚀 Presiona 'Iniciar Detección'
2. 🤲 Coloca tu mano frente a la cámara
3. ⏱️ Ajusta el cooldown si hay muchos duplicados (por defecto 2 seg)
4. 🎓 Para entrenar nuevas señas: escribe el nombre y presiona 'Entrenar'
5. 📜 Revisa tu historial de traducciones
6. 🔊 Reproduce las traducciones en voz alta

💡 CONSEJOS:
• Asegúrate de tener buena iluminación
• Usa fondos simples para mejor detección
• Mantén las manos en el centro del campo visual
• El cooldown evita duplicados (ajústalo según necesites)

¡Comienza tu experiencia de traducción! 🎉"""
        
        self.text_area.insert(tk.END, initial_text)
        
        # Frame de información
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        info_text = "💡 Estado: Listo para comenzar • Asegúrate de tener buena iluminación para mejor detección"
        self.info_label = ttk.Label(info_frame, text=info_text)
        self.info_label.pack()
        
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
            self.start_button.config(text="⏹️ Detener", style='Warning.TButton')
            self.status_indicator.config(text="🟢")
            self.status_label.config(text="Detectando...")
            self.info_label.config(text="🎯 Detección activa • Coloca tu mano frente a la cámara")
        else:
            self.status_indicator.config(text="🔴")
            self.status_label.config(text="Error de cámara")
            self.info_label.config(text="❌ Error: No se pudo acceder a la cámara")
            
    def stop_detection(self):
        """Para la detección de manos"""
        self.hand_detector.stop_detection()
        
        self.start_button.config(text="🚀 Iniciar Detección", style='Success.TButton')
        self.status_indicator.config(text="🔴")
        self.status_label.config(text="Detenido")
        self.info_label.config(text="💡 Presiona 'Iniciar Detección' para comenzar")
        
    def on_hand_detected(self, hand_count):
        """Callback cuando se detectan manos"""
        if hand_count > 0:
            self.detection_count += 1
            self.update_text(f"👋 Detectadas {hand_count} mano(s) en la imagen")
        else:
            self.update_text("👋 No se detectan manos")
            # Limpiar seña cuando no hay manos
            self.update_sign_display("Sin seña detectada", 0.0)
    
    def on_sign_detected(self, sign_result):
        """Callback cuando se detecta una seña"""
        sign_name = sign_result.get('sign', 'Desconocida')
        confidence = sign_result.get('confidence', 0.0)
        stability = sign_result.get('stability', 'inestable')
        
        # Contar traducciones exitosas
        if confidence > 0.5 and sign_name != "Desconocida":
            self.successful_translations += 1
            # 🆕 Agregar al historial si la confianza es suficiente
            self.add_to_history(sign_name, confidence)
        
        # Actualizar display de seña
        self.update_sign_display(sign_name, confidence)
        
        # Log detallado
        self.update_text(
            f"🤟 Seña: {sign_name} | "
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
        
        # Emoji y color basado en confianza
        if self.sign_confidence > 0.8:
            color = self.colors['success']
            emoji = "🎯"  # Alta confianza
        elif self.sign_confidence > 0.6:
            color = self.colors['warning'] 
            emoji = "🤔"  # Confianza media
        elif self.sign_confidence > 0.3:
            color = self.colors['text_secondary']
            emoji = "🤷"  # Baja confianza
        else:
            color = self.colors['text_secondary']
            emoji = "🤔"  # Sin seña
            
        # Actualizar emoji y color
        self.sign_emoji.config(text=emoji)
        self.sign_label.config(foreground=color)
        self.confidence_label.config(text=f"{self.sign_confidence:.0%}")
        
        # Actualizar barra de confianza visual
        self.update_confidence_bar()
    
    def toggle_translation(self):
        """Activa/desactiva la traducción"""
        if hasattr(self.hand_detector, 'toggle_translation'):
            enabled = self.hand_detector.toggle_translation()
            status_text = "ACTIVA" if enabled else "INACTIVA"
            
            self.translation_button.config(text=f"� Traducción: {status_text}")
            
            if not enabled:
                self.update_sign_display("Traducción desactivada", 0.0)
    
    def update_cooldown(self):
        """Actualiza el tiempo de cooldown desde el spinbox"""
        try:
            new_cooldown = self.cooldown_var.get()
            self.sign_cooldown = new_cooldown
            self.update_text(f"⏱️ Cooldown actualizado a {new_cooldown:.1f} segundos")
        except:
            pass
    
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
        self.hand_detector.add_training_sample(sign_name, "Seña entrenada por usuario")
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
        
    def update_stats(self):
        """Actualiza las estadísticas en tiempo real"""
        try:
            # Calcular tiempo de sesión
            session_time = int(time.time() - self.session_start_time)
            minutes = session_time // 60
            seconds = session_time % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            
            # Calcular precisión
            accuracy = (self.successful_translations / max(1, self.detection_count)) * 100
            
            # Actualizar labels
            self.detections_label.config(text=f"🎯 Detecciones: {self.detection_count}")
            self.translations_label.config(text=f"✅ Traducciones: {self.successful_translations}")
            self.accuracy_label.config(text=f"📈 Precisión: {accuracy:.1f}%")
            self.session_time_label.config(text=f"⏱️ Tiempo: {time_str}")
            
        except Exception as e:
            pass  # Silenciar errores de actualización
        
        # Programar siguiente actualización
        self.root.after(1000, self.update_stats)
    
    def update_confidence_bar(self):
        """Actualiza la barra visual de confianza"""
        try:
            self.confidence_bar.delete("all")
            
            # Fondo de la barra
            self.confidence_bar.create_rectangle(0, 0, 200, 20, 
                                            fill=self.colors['surface'], outline="")
            
            # Barra de progreso
            width = int(200 * self.sign_confidence)
            if width > 0:
                # Color basado en confianza
                if self.sign_confidence > 0.8:
                    color = self.colors['success']
                elif self.sign_confidence > 0.6:
                    color = self.colors['warning']
                else:
                    color = self.colors['error']
                
                
                self.confidence_bar.create_rectangle(0, 0, width, 20, 
                                                fill=color, outline="")
        except Exception as e:
            pass  # Silenciar errores gráficos
    
    def on_entry_focus_in(self, event):
        """Limpia el placeholder cuando se enfoca el campo"""
        if self.training_entry.get() == "Ej: HOLA_PERSONALIZADO":
            self.training_entry.delete(0, tk.END)
    
    def on_entry_focus_out(self, event):
        """Restaura el placeholder si el campo está vacío"""
        if not self.training_entry.get():
            self.training_entry.insert(0, "Ej: HOLA_PERSONALIZADO")
    
    def show_help(self):
        """Muestra ventana de ayuda"""
        help_window = tk.Toplevel(self.root)
        help_window.title("🆘 Ayuda - Traductor de Señas")
        help_window.geometry("600x500")
        help_window.configure(bg=self.colors['background'])
        help_window.transient(self.root)
        help_window.grab_set()
        
        # Centrar ventana
        help_window.update_idletasks()
        x = (help_window.winfo_screenwidth() // 2) - (600 // 2)
        y = (help_window.winfo_screenheight() // 2) - (500 // 2)
        help_window.geometry(f"600x500+{x}+{y}")
        
        # Contenido de ayuda
        help_frame = ttk.Frame(help_window, padding="20")
        help_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(help_frame, text="🆘 Guía de Uso", 
                font=('Inter', 16, 'bold')).pack(pady=(0, 20))
        
        help_text = scrolledtext.ScrolledText(help_frame, height=20, wrap=tk.WORD)
        help_text.pack(fill=tk.BOTH, expand=True)
        
        help_content = """📖 GUÍA COMPLETA DEL TRADUCTOR DE SEÑAS PERUANO

🚀 INICIO RÁPIDO:
1. Presiona 'Iniciar Detección' para activar la cámara
2. Coloca tu mano frente a la cámara web
3. Realiza las señas despacio y manténlas por 2-3 segundos
4. Observa el resultado en tiempo real

🤲 SEÑAS DISPONIBLES:
• HOLA - Mano abierta con movimiento de saludo
• GRACIAS - Mano hacia el pecho, dedos juntos  
• SÍ - Puño cerrado con movimiento de asentimiento
• NO - Índice extendido con movimiento lateral
• BIEN - Pulgar hacia arriba
• MAL - Pulgar hacia abajo
• AMOR - Índice y meñique extendidos (I Love You)
• PAZ - Índice y medio extendidos (V de victoria)
• AGUA - Mano formando copa
• COMIDA - Dedos juntos hacia la boca

🧠 ENTRENAR NUEVAS SEÑAS:
1. Escribe el nombre de la nueva seña en el campo de entrenamiento
2. Presiona 'Entrenar Nueva Seña'
3. Realiza la seña frente a la cámara
4. Mantén la posición por 3-5 segundos
5. La seña se guardará automáticamente

📊 ENTENDIENDO LAS ESTADÍSTICAS:
• Detecciones: Número total de veces que se detectó una mano
• Traducciones: Señas reconocidas exitosamente
• Precisión: Porcentaje de detecciones que resultaron en traducciones
• Tiempo: Duración de la sesión actual

🎯 CONSEJOS PARA MEJOR DETECCIÓN:
• Usa iluminación uniforme y brillante
• Evita fondos complejos o con mucho contraste
• Mantén las manos en el centro del campo visual
• Realiza movimientos lentos y deliberados
• Asegúrate de que toda la mano sea visible

⚙️ CONFIGURACIÓN:
• Traducción: Activa/desactiva el reconocimiento automático
• El indicador de estado muestra el estado actual del sistema
• La barra de confianza indica qué tan seguro está el sistema

❗ SOLUCIÓN DE PROBLEMAS:
• Si no se detectan manos: Revisa la iluminación y posición
• Si la precisión es baja: Practica las señas más lentamente
• Si hay errores de cámara: Verifica que no esté siendo usada por otra app

¡Disfruta aprendiendo lenguaje de señas! 🌟"""
        
        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)
        
        # Botón cerrar
        ttk.Button(help_frame, text="✅ Cerrar", 
                command=help_window.destroy).pack(pady=(10, 0))
    
    def add_to_history(self, sign_name, confidence):
        """Agrega una traducción al historial con control de duplicados"""
        if sign_name == "Sin seña detectada" or sign_name == "Desconocida":
            return
        
        current_time = time.time()
        
        # 🆕 Verificar cooldown: evitar duplicados de la misma seña
        if (self.last_sign_detected == sign_name and 
            (current_time - self.last_sign_time) < self.sign_cooldown):
            # Aún está en cooldown, no agregar
            return
        
        # Actualizar control de cooldown
        self.last_sign_detected = sign_name
        self.last_sign_time = current_time
        
        timestamp = time.strftime("%H:%M:%S")
        
        # Crear entrada del historial
        history_entry = {
            'timestamp': timestamp,
            'sign': sign_name,
            'confidence': confidence,
            'datetime': current_time
        }
        
        # Agregar al array
        self.translation_history.append(history_entry)
        
        # Limitar tamaño del historial
        if len(self.translation_history) > self.max_history:
            self.translation_history.pop(0)
        
        # Actualizar la lista visual
        self.update_history_display()
        
        # Feedback visual/auditivo opcional
        self.update_text(f"➕ Agregado al historial: {sign_name}")
    
    def update_history_display(self):
        """Actualiza la lista visual del historial"""
        def _update():
            self.history_listbox.delete(0, tk.END)
            
            for entry in self.translation_history:
                display_text = f"[{entry['timestamp']}] {entry['sign']} ({entry['confidence']:.0%})"
                self.history_listbox.insert(tk.END, display_text)
            
            # Auto-scroll al final
            self.history_listbox.see(tk.END)
        
        # Ejecutar en hilo principal
        self.root.after(0, _update)
    
    def speak_selected(self):
        """Reproduce en voz la traducción seleccionada"""
        if not self.tts_available:
            self.update_text("⚠️ Text-to-Speech no disponible en este sistema")
            return
        
        selection = self.history_listbox.curselection()
        if not selection:
            self.update_text("⚠️ Selecciona una traducción para reproducir")
            return
        
        index = selection[0]
        if 0 <= index < len(self.translation_history):
            entry = self.translation_history[index]
            self.speak_text(entry['sign'])
            self.update_text(f"🔊 Reproduciendo: {entry['sign']}")
    
    def speak_all(self):
        """Reproduce todas las traducciones del historial"""
        if not self.tts_available:
            self.update_text("⚠️ Text-to-Speech no disponible en este sistema")
            return
        
        if not self.translation_history:
            self.update_text("⚠️ No hay traducciones en el historial")
            return
        
        # Crear frase con todas las señas
        signs = [entry['sign'] for entry in self.translation_history]
        full_text = " ".join(signs)
        
        self.speak_text(full_text)
        self.update_text(f"🔊 Reproduciendo todo el historial ({len(signs)} señas)")
    
    def speak_text(self, text):
        """Reproduce texto usando TTS (gTTS + pygame) en un hilo separado"""
        def _speak():
            temp_file = None
            try:
                # Crear archivo temporal para el audio
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                    temp_file = fp.name
                
                # Generar audio con gTTS (Google Text-to-Speech)
                tts = gTTS(text=text, lang='es', slow=False)
                tts.save(temp_file)
                
                # Reproducir con pygame
                mixer.music.load(temp_file)
                mixer.music.play()
                
                # Esperar a que termine la reproducción
                while mixer.music.get_busy():
                    time.sleep(0.1)
                
                # Limpiar archivo temporal
                if temp_file and os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                        
            except Exception as e:
                self.update_text(f"❌ Error al reproducir: {e}")
                if temp_file and os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
        
        # Ejecutar en hilo separado para no bloquear la UI
        tts_thread = threading.Thread(target=_speak, daemon=True)
        tts_thread.start()
    
    def clear_history(self):
        """Limpia el historial de traducciones"""
        self.translation_history.clear()
        self.history_listbox.delete(0, tk.END)
        self.update_text("🗑️ Historial de traducciones limpiado")
    
    def export_history(self):
        """Exporta el historial a un archivo de texto"""
        if not self.translation_history:
            self.update_text("⚠️ No hay traducciones para exportar")
            return
        
        try:
            filename = f"traducciones_{time.strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 50 + "\n")
                f.write("HISTORIAL DE TRADUCCIONES - LENGUAJE DE SEÑAS PERUANO\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Sesión: {time.strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Total de traducciones: {len(self.translation_history)}\n\n")
                f.write("-" * 50 + "\n\n")
                
                for i, entry in enumerate(self.translation_history, 1):
                    f.write(f"{i}. [{entry['timestamp']}] {entry['sign']} "
                           f"(Confianza: {entry['confidence']:.1%})\n")
                
                f.write("\n" + "-" * 50 + "\n")
                f.write("Texto completo:\n")
                signs = [entry['sign'] for entry in self.translation_history]
                f.write(" ".join(signs) + "\n")
            
            self.update_text(f"💾 Historial exportado a: {filename}")
            
        except Exception as e:
            self.update_text(f"❌ Error al exportar: {e}")

    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        if self.hand_detector.is_running():
            self.hand_detector.stop_detection()
        self.hand_detector.cleanup()
        
        # Detener música si está reproduciéndose
        try:
            if self.tts_available:
                mixer.music.stop()
        except:
            pass
        
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