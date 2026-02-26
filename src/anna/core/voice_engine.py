# core/voice_engine.py - Android Uyumlu Versiyon
"""
A.N.N.A'nın ses motoru - Android için optimize edilmiş
"""

import threading
import queue
import time
import speech_recognition as sr
from loguru import logger

# Android'de pygame YERİNE:
try:
    from android.media import MediaPlayer
    ANDROID_MODE = True
except ImportError:
    ANDROID_MODE = False
    # Bilgisayarda pygame kullan
    import pygame
    pygame.mixer.init()

class VoiceEngine:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        
        # Ses kuyruğu
        self.sound_queue = queue.Queue()
        self.is_playing = False
        self.sound_thread = threading.Thread(target=self._sound_worker, daemon=True)
        self.sound_thread.start()
        
        # Mikrofonu başlat
        self._init_microphone()
        
        logger.success("✅ Ses motoru (Android uyumlu) hazır")
    
    def _init_microphone(self):
        try:
            mikrofonlar = sr.Microphone.list_microphone_names()
            if mikrofonlar:
                self.microphone = sr.Microphone(device_index=0)
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    print("✅ Mikrofon hazır")
            else:
                print("⚠️ Mikrofon bulunamadı")
        except Exception as e:
            print(f"❌ Mikrofon hatası: {e}")
    
    def _sound_worker(self):
        """Ses çalma thread'i"""
        while True:
            try:
                text = self.sound_queue.get(timeout=1)
                self.is_playing = True
                
                if ANDROID_MODE:
                    # Android'de gTTS kullan
                    self._play_android(text)
                else:
                    # Bilgisayarda pygame
                    self._play_pygame(text)
                
                self.is_playing = False
                self.sound_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Ses hatası: {e}")
                self.is_playing = False
    
    def _play_android(self, text):
        """Android'de ses çal"""
        from gtts import gTTS
        import tempfile
        import os
        
        try:
            # Geçici dosya oluştur
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                temp_file = fp.name
            
            # gTTS ile ses oluştur
            tts = gTTS(text=text, lang='tr', slow=False)
            tts.save(temp_file)
            
            # Android MediaPlayer ile çal
            player = MediaPlayer()
            player.setDataSource(temp_file)
            player.prepare()
            player.start()
            
            # Ses bitene kadar bekle
            while player.isPlaying():
                time.sleep(0.1)
            
            player.release()
            os.unlink(temp_file)
            
        except Exception as e:
            print(f"⚠️ Ses çalınamadı, metin: {text}")
    
    def _play_pygame(self, text):
        """Bilgisayarda pygame ile ses çal"""
        from gtts import gTTS
        import tempfile
        import os
        import pygame
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                temp_file = fp.name
            
            tts = gTTS(text=text, lang='tr', slow=False)
            tts.save(temp_file)
            
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            os.unlink(temp_file)
            
        except Exception as e:
            print(f"⚠️ Ses çalınamadı, metin: {text}")
    
    def konus(self, text: str):
        """Metni sese çevir ve kuyruğa ekle"""
        print(f"🤖 A.N.N.A: {text}")
        if text and text.strip():
            self.sound_queue.put(text)
    
    def dinle(self, timeout=5) -> str:
        """Mikrofondan dinle"""
        if self.microphone is None:
            return ""
        
        try:
            with self.microphone as source:
                print("\n🎤 Dinliyorum...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=5)
            
            text = self.recognizer.recognize_google(audio, language="tr-TR")
            print(f"📝 Anlaşılan: {text}")
            return text.lower()
            
        except sr.WaitTimeoutError:
            print("⏱️ Süre doldu")
        except sr.UnknownValueError:
            print("🤔 Anlaşılamadı")
        except Exception as e:
            logger.error(f"Ses hatası: {e}")
        
        return ""
    
    def is_busy(self) -> bool:
        return self.is_playing or not self.sound_queue.empty()