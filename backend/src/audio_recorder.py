import threading
import wave
import tempfile
import os
from pathlib import Path
from typing import Callable, Optional

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False


class AudioRecorder:
    def __init__(self):
        self.is_recording = False
        self.frames = []
        self.audio = None
        self.stream = None
        self.record_thread = None
        
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_size = 1024
        self.format = pyaudio.paInt16 if PYAUDIO_AVAILABLE else None
        
        self.temp_dir = Path(tempfile.gettempdir()) / "rubber_duck"
        self.temp_dir.mkdir(exist_ok=True)
    
    def start_recording(self, on_error: Optional[Callable] = None):
        if not PYAUDIO_AVAILABLE:
            if on_error:
                on_error("PyAudio nie jest zainstalowane")
            return False
        
        if self.is_recording:
            return False
        
        try:
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            self.is_recording = True
            self.frames = []
            
            self.record_thread = threading.Thread(target=self._record_loop)
            self.record_thread.daemon = True
            self.record_thread.start()
            
            return True
            
        except Exception as e:
            if on_error:
                on_error(str(e))
            self._cleanup()
            return False
    
    def _record_loop(self):
        while self.is_recording:
            try:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                self.frames.append(data)
            except Exception:
                break
    
    def stop_recording(self) -> Optional[str]:
        if not self.is_recording:
            return None
        
        self.is_recording = False
        
        if self.record_thread:
            self.record_thread.join(timeout=1.0)
        
        audio_path = None
        
        if self.frames:
            audio_path = str(self.temp_dir / "recording.wav")
            try:
                with wave.open(audio_path, 'wb') as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(self.audio.get_sample_size(self.format))
                    wf.setframerate(self.sample_rate)
                    wf.writeframes(b''.join(self.frames))
            except Exception as e:
                print(f"Error saving audio: {e}")
                audio_path = None
        
        self._cleanup()
        return audio_path
    
    def _cleanup(self):
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
            self.stream = None
        
        if self.audio:
            try:
                self.audio.terminate()
            except:
                pass
            self.audio = None
        
        self.frames = []
    
    def is_available(self) -> bool:
        if not PYAUDIO_AVAILABLE:
            return False
        
        try:
            audio = pyaudio.PyAudio()
            device_count = audio.get_device_count()
            audio.terminate()
            return device_count > 0
        except:
            return False
