"""
Sistema de Caché de Audio con IA para Traductor de Señas
Genera y almacena voces de señas para reproducción sin entrecortes
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional
import hashlib

# Opciones de TTS con IA
TTS_ENGINES = {
    'gtts': 'gTTS (Google Text-to-Speech) - Gratis',
    'pyttsx3': 'pyttsx3 (Offline, voces del sistema)',
    'elevenlabs': 'ElevenLabs (Alta calidad, requiere API key)',
    'edge-tts': 'Edge TTS (Microsoft, gratis)',
    'coqui': 'Coqui TTS (Local, open source)',
}


class AudioCache:
    """Gestor de caché de audio para señas"""
    
    def __init__(self, cache_dir: str = "audio_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.metadata_file = self.cache_dir / "metadata.json"
        self.metadata = self._load_metadata()
        
    def _load_metadata(self) -> Dict:
        """Carga metadatos del caché"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_metadata(self):
        """Guarda metadatos"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
    
    def get_audio_path(self, text: str, voice_id: str = "default") -> Path:
        """Obtiene la ruta del archivo de audio para un texto"""
        # Crear hash único del texto + voz
        text_hash = hashlib.md5(f"{text}_{voice_id}".encode()).hexdigest()
        return self.cache_dir / f"{text_hash}.mp3"
    
    def is_cached(self, text: str, voice_id: str = "default") -> bool:
        """Verifica si el audio ya está en caché"""
        audio_path = self.get_audio_path(text, voice_id)
        return audio_path.exists()
    
    def add_to_cache(self, text: str, audio_path: Path, voice_id: str = "default"):
        """Registra un audio en el caché"""
        text_hash = hashlib.md5(f"{text}_{voice_id}".encode()).hexdigest()
        self.metadata[text_hash] = {
            'text': text,
            'voice_id': voice_id,
            'file': audio_path.name
        }
        self._save_metadata()


class SmartTTS:
    """Sistema TTS inteligente con múltiples engines"""
    
    def __init__(self, engine: str = "edge-tts", cache_dir: str = "audio_cache"):
        self.engine = engine
        self.cache = AudioCache(cache_dir)
        self._init_engine()
    
    def _init_engine(self):
        """Inicializa el motor TTS seleccionado"""
        if self.engine == "gtts":
            from gtts import gTTS
            self.tts_class = gTTS
            
        elif self.engine == "pyttsx3":
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            # Configurar voz en español
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if 'spanish' in voice.name.lower() or 'es' in voice.languages:
                    self.tts_engine.setProperty('voice', voice.id)
                    break
            self.tts_engine.setProperty('rate', 150)  # Velocidad
            
        elif self.engine == "edge-tts":
            # Edge TTS se importa dinámicamente cuando se usa
            pass
            
        elif self.engine == "elevenlabs":
            # ElevenLabs se importa cuando se usa
            pass
            
        elif self.engine == "coqui":
            # Coqui TTS se importa cuando se usa
            pass
    
    def generate_audio_gtts(self, text: str, output_path: Path):
        """Genera audio con gTTS"""
        from gtts import gTTS
        tts = gTTS(text=text, lang='es', slow=False)
        tts.save(str(output_path))
    
    def generate_audio_pyttsx3(self, text: str, output_path: Path):
        """Genera audio con pyttsx3"""
        self.tts_engine.save_to_file(text, str(output_path))
        self.tts_engine.runAndWait()
    
    async def generate_audio_edge(self, text: str, output_path: Path, voice: str = "es-ES-AlvaroNeural"):
        """Genera audio con Edge TTS (async)"""
        import edge_tts
        
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(output_path))
    
    def generate_audio_elevenlabs(self, text: str, output_path: Path, api_key: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM"):
        """Genera audio con ElevenLabs (requiere API key)"""
        from elevenlabs import generate, save, set_api_key
        
        set_api_key(api_key)
        audio = generate(
            text=text,
            voice=voice_id,
            model="eleven_multilingual_v2"
        )
        save(audio, str(output_path))
    
    def generate_audio_coqui(self, text: str, output_path: Path):
        """Genera audio con Coqui TTS (local, open source)"""
        from TTS.api import TTS
        
        # Inicializar modelo (solo primera vez)
        if not hasattr(self, 'coqui_model'):
            self.coqui_model = TTS(model_name="tts_models/es/css10/vits", progress_bar=False)
        
        self.coqui_model.tts_to_file(text=text, file_path=str(output_path))
    
    def speak(self, text: str, voice_id: str = "default", force_regenerate: bool = False) -> Path:
        """
        Genera o recupera audio del caché y devuelve la ruta
        
        Args:
            text: Texto a convertir en voz
            voice_id: ID de la voz (para diferenciar en caché)
            force_regenerate: Forzar regeneración aunque esté en caché
        
        Returns:
            Path al archivo de audio
        """
        audio_path = self.cache.get_audio_path(text, voice_id)
        
        # Si ya está en caché y no se fuerza regenerar
        if not force_regenerate and self.cache.is_cached(text, voice_id):
            print(f"✅ Audio en caché: {text}")
            return audio_path
        
        # Generar nuevo audio
        print(f"🎙️ Generando audio: {text}")
        
        try:
            if self.engine == "gtts":
                self.generate_audio_gtts(text, audio_path)
                
            elif self.engine == "pyttsx3":
                self.generate_audio_pyttsx3(text, audio_path)
                
            elif self.engine == "edge-tts":
                import asyncio
                asyncio.run(self.generate_audio_edge(text, audio_path))
                
            elif self.engine == "elevenlabs":
                # Requiere API key
                api_key = os.getenv("ELEVENLABS_API_KEY")
                if not api_key:
                    raise ValueError("ELEVENLABS_API_KEY no configurada")
                self.generate_audio_elevenlabs(text, audio_path, api_key)
                
            elif self.engine == "coqui":
                self.generate_audio_coqui(text, audio_path)
            
            # Registrar en caché
            self.cache.add_to_cache(text, audio_path, voice_id)
            print(f"✅ Audio generado y guardado en caché")
            
        except Exception as e:
            print(f"❌ Error generando audio: {e}")
            # Fallback a gTTS si falla
            if self.engine != "gtts":
                print("🔄 Intentando con gTTS como fallback...")
                self.generate_audio_gtts(text, audio_path)
        
        return audio_path
    
    def play_audio(self, audio_path: Path):
        """Reproduce un archivo de audio"""
        import pygame
        
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        try:
            pygame.mixer.music.load(str(audio_path))
            pygame.mixer.music.play()
            
            # Esperar a que termine
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
        except Exception as e:
            print(f"❌ Error reproduciendo audio: {e}")
    
    def speak_and_play(self, text: str, voice_id: str = "default"):
        """Genera (si es necesario) y reproduce audio"""
        audio_path = self.speak(text, voice_id)
        self.play_audio(audio_path)


def pregenerate_all_signs(dataset_path: str = "data/signs_dataset.json", engine: str = "edge-tts"):
    """
    Pre-genera audio para todas las señas del dataset
    Útil para ejecutar una vez y tener todo listo
    """
    print("\n" + "="*70)
    print("🎙️ PRE-GENERACIÓN DE AUDIO PARA TODAS LAS SEÑAS")
    print("="*70 + "\n")
    
    # Cargar dataset
    with open(dataset_path, 'r', encoding='utf-8') as f:
        signs = json.load(f)
    
    tts = SmartTTS(engine=engine)
    
    total = len(signs)
    for i, (sign_name, sign_data) in enumerate(signs.items(), 1):
        print(f"[{i}/{total}] Procesando: {sign_name}")
        tts.speak(sign_name)
    
    print(f"\n✅ ¡Completado! {total} audios generados")
    print(f"📁 Almacenados en: audio_cache/")


# Ejemplo de uso
if __name__ == "__main__":
    # Opción 1: Uso básico
    tts = SmartTTS(engine="edge-tts")  # o "gtts", "pyttsx3", "elevenlabs", "coqui"
    
    # Primera vez: genera y guarda
    tts.speak_and_play("HOLA")
    
    # Segunda vez: usa caché (instantáneo)
    tts.speak_and_play("HOLA")
    
    # Opción 2: Pre-generar todo el dataset
    # pregenerate_all_signs(engine="edge-tts")
