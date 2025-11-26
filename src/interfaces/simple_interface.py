#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interfaz Simplificada para Traductor de Señas LSP
==================================================
NUEVO ENFOQUE con Queue thread-safe y polling
- Un solo thread lee la cámara (hand_detector)
- Queue para pasar frames de forma segura
- UI hace polling de frames en lugar de callbacks
- TTS en thread separado sin bloqueos
"""

# Suprimir logs de TensorFlow/MediaPipe ANTES de cualquier import
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['GLOG_minloglevel'] = '2'

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import threading
import time
import queue
from src.core.hand_detector import HandDetector
from gtts import gTTS
import pygame
import tempfile

class SimpleTranslatorInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Traductor LSP - Modo Simple")
        self.root.geometry("800x600")
        self.root.configure(bg='#1a1a2e')
        
        # Queue thread-safe para frames (CLAVE DEL NUEVO ENFOQUE)
        self.frame_queue = queue.Queue(maxsize=2)  # Buffer pequeño para frames recientes
        
        # Queue para TTS
        self.tts_queue = queue.Queue()
        
        # Estado de la aplicación
        self.is_running = False
        self.spoken_mode = False
        self.last_spoken_time = 0
        self.speech_cooldown = 3.0  # segundos entre traducciones habladas
        
        # Inicializar pygame para audio
        pygame.mixer.init()
        
        # Inicializar detector de manos SIN ventana de OpenCV
        self.hand_detector = HandDetector(show_window=False)
        self.hand_detector.set_callbacks(
            on_sign_detected=self._on_sign_detected_callback,
            on_status_update=None,  # No necesitamos status updates aquí
            on_error=None
        )
        
        # Thread para TTS
        self.tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
        self.tts_thread.start()
        
        # Crear UI
        self._create_ui()
        
        # Iniciar polling de frames
        self._poll_frames()
        
    def _create_ui(self):
        """Crea la interfaz de usuario"""
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # === ÁREA DE CÁMARA ===
        camera_frame = tk.Frame(main_frame, bg='#16213e', relief=tk.RIDGE, bd=2)
        camera_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.camera_label = tk.Label(camera_frame, bg='#16213e', text="Cámara desactivada")
        self.camera_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # === PANEL DE CONTROLES ===
        controls_frame = tk.Frame(main_frame, bg='#1a1a2e')
        controls_frame.pack(fill=tk.X)
        
        # Frame para botones principales
        buttons_frame = tk.Frame(controls_frame, bg='#1a1a2e')
        buttons_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Botón INICIAR
        self.start_button = tk.Button(
            buttons_frame,
            text="▶ INICIAR",
            command=self._start_detection,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 12, 'bold'),
            width=12,
            height=2,
            relief=tk.RAISED,
            bd=3,
            cursor='hand2'
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # Botón DETENER
        self.stop_button = tk.Button(
            buttons_frame,
            text="■ DETENER",
            command=self._stop_detection,
            bg='#f44336',
            fg='white',
            font=('Arial', 12, 'bold'),
            width=12,
            height=2,
            relief=tk.RAISED,
            bd=3,
            cursor='hand2',
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Botón MODO VOZ
        self.voice_button = tk.Button(
            buttons_frame,
            text="🔊 VOZ: OFF",
            command=self._toggle_voice,
            bg='#2196F3',
            fg='white',
            font=('Arial', 12, 'bold'),
            width=12,
            height=2,
            relief=tk.RAISED,
            bd=3,
            cursor='hand2'
        )
        self.voice_button.pack(side=tk.LEFT, padx=5)
        
        # Botón SALIR
        exit_button = tk.Button(
            buttons_frame,
            text="✖ SALIR",
            command=self._exit_app,
            bg='#9E9E9E',
            fg='white',
            font=('Arial', 12, 'bold'),
            width=12,
            height=2,
            relief=tk.RAISED,
            bd=3,
            cursor='hand2'
        )
        exit_button.pack(side=tk.LEFT, padx=5)
        
        # === ÁREA DE ESTADO ===
        status_frame = tk.Frame(main_frame, bg='#16213e', relief=tk.RIDGE, bd=2)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = tk.Label(
            status_frame,
            text="Estado: Listo para iniciar",
            bg='#16213e',
            fg='#00d4ff',
            font=('Arial', 11),
            anchor=tk.W,
            padx=10,
            pady=5
        )
        self.status_label.pack(fill=tk.X)
        
        # Etiqueta de última seña detectada
        self.last_sign_label = tk.Label(
            status_frame,
            text="Última seña: ---",
            bg='#16213e',
            fg='#ffffff',
            font=('Arial', 11, 'bold'),
            anchor=tk.W,
            padx=10,
            pady=5
        )
        self.last_sign_label.pack(fill=tk.X)
        
    def _poll_frames(self):
        """
        Polling de frames desde la queue (CLAVE DEL NUEVO ENFOQUE)
        Se llama a sí mismo cada 30ms
        """
        try:
            # Intentar obtener frame sin bloquear
            frame = self.frame_queue.get_nowait()
            
            # Convertir frame a formato Tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (640, 480))
            img = Image.fromarray(frame_resized)
            imgtk = ImageTk.PhotoImage(image=img)
            
            # Actualizar UI
            self.camera_label.config(image=imgtk, text="")
            self.camera_label.image = imgtk
            
        except queue.Empty:
            # No hay frames disponibles, continuar
            pass
        except Exception as e:
            print(f"Error en polling de frames: {e}")
        
        # Continuar polling si está activo
        if self.is_running:
            self.root.after(30, self._poll_frames)
    
    def _frame_producer(self):
        """
        Thread que produce frames y los pone en la queue
        Este método captura frames del detector y los encola
        """
        while self.is_running:
            try:
                # Obtener frame del detector
                if self.hand_detector.cap is not None and self.hand_detector.cap.isOpened():
                    ret, frame = self.hand_detector.cap.read()
                    
                    if ret:
                        # Intentar poner frame en queue sin bloquear
                        try:
                            # Si la queue está llena, descartar el frame viejo
                            if self.frame_queue.full():
                                try:
                                    self.frame_queue.get_nowait()
                                except:
                                    pass
                            
                            self.frame_queue.put_nowait(frame)
                        except queue.Full:
                            pass  # Descartar frame si no se puede encolar
                
                time.sleep(0.03)  # ~30 FPS
                
            except Exception as e:
                print(f"Error en productor de frames: {e}")
                time.sleep(0.1)
    
    def _on_sign_detected_callback(self, sign_data):
        """
        Callback cuando se detecta una seña
        Se ejecuta en el thread de detección
        """
        if not sign_data or not isinstance(sign_data, dict):
            return
        
        sign = sign_data.get('sign', 'DESCONOCIDO')
        confidence = sign_data.get('confidence', 0)
        
        # Actualizar UI (thread-safe con after)
        self.root.after(0, self._update_sign_display, sign, confidence)
        
        # Encolar para TTS si modo voz está activo
        if self.spoken_mode:
            current_time = time.time()
            if current_time - self.last_spoken_time >= self.speech_cooldown:
                self.last_spoken_time = current_time
                self.tts_queue.put(sign)
    
    def _update_sign_display(self, sign, confidence):
        """Actualiza la visualización de la seña detectada (thread-safe)"""
        self.last_sign_label.config(
            text=f"Última seña: {sign} ({confidence*100:.1f}%)"
        )
    
    def _tts_worker(self):
        """Worker thread para TTS (NUEVO ENFOQUE - sin bloqueos)"""
        while True:
            try:
                # Esperar por texto para hablar (bloqueante pero en thread separado)
                text = self.tts_queue.get()
                
                if text is None:  # Señal de parada
                    break
                
                # Generar y reproducir audio
                try:
                    tts = gTTS(text=text, lang='es', slow=False)
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                        temp_file = fp.name
                        tts.save(temp_file)
                    
                    pygame.mixer.music.load(temp_file)
                    pygame.mixer.music.play()
                    
                    # Esperar a que termine (pero en thread separado, no bloquea UI)
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                    
                    # Cooldown para evitar saturación
                    time.sleep(0.2)
                    
                    # Limpiar archivo temporal
                    try:
                        os.unlink(temp_file)
                    except:
                        pass
                        
                except Exception as e:
                    print(f"Error en TTS: {e}")
                
            except Exception as e:
                print(f"Error en TTS worker: {e}")
    
    def _start_detection(self):
        """Inicia la detección"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Iniciar detección en hand_detector
        self.hand_detector.start_detection()
        
        # Iniciar thread productor de frames
        self.frame_producer_thread = threading.Thread(target=self._frame_producer, daemon=True)
        self.frame_producer_thread.start()
        
        # Iniciar polling de frames
        self._poll_frames()
        
        # Actualizar UI
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Estado: Detectando señas...")
        
    def _stop_detection(self):
        """Detiene la detección"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Detener detección en hand_detector
        self.hand_detector.stop_detection()
        
        # Limpiar queue de frames
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except:
                break
        
        # Actualizar UI
        self.camera_label.config(image="", text="Cámara desactivada")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="Estado: Detenido")
        self.last_sign_label.config(text="Última seña: ---")
        
    def _toggle_voice(self):
        """Activa/desactiva el modo voz"""
        self.spoken_mode = not self.spoken_mode
        
        if self.spoken_mode:
            self.voice_button.config(text="🔊 VOZ: ON", bg='#4CAF50')
            self.status_label.config(text="Estado: Modo voz ACTIVADO")
        else:
            self.voice_button.config(text="🔊 VOZ: OFF", bg='#2196F3')
            if self.is_running:
                self.status_label.config(text="Estado: Detectando señas...")
            else:
                self.status_label.config(text="Estado: Listo para iniciar")
    
    def _exit_app(self):
        """Cierra la aplicación"""
        if messagebox.askokcancel("Salir", "¿Deseas cerrar la aplicación?"):
            # Detener detección si está activa
            if self.is_running:
                self._stop_detection()
            
            # Detener thread de TTS
            self.tts_queue.put(None)
            
            # Cerrar ventana
            self.root.quit()
            self.root.destroy()

def main():
    root = tk.Tk()
    app = SimpleTranslatorInterface(root)
    root.protocol("WM_DELETE_WINDOW", app._exit_app)
    root.mainloop()

if __name__ == "__main__":
    main()
