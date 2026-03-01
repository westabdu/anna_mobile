# src/modules/mobile_voice_enhanced.py - ANDROID UYUMLU
"""
A.N.N.A Mobile Gelişmiş Ses Motoru
- 🎙️ Wake word (Jarvis, Bilgisayar, Alexa)
- 🗣️ Doğal ses sentezi (Edge-TTS + gTTS yedek)
- 👂 Ses tanıma (Google Speech)
- 📊 Ses seviyesi göstergesi
- 🔇 Sessiz mod
- 💬 Konuşma geçmişi
"""

import os
import sys
import asyncio
import tempfile
import threading
import queue
import time
import json
from datetime import datetime
from pathlib import Path

# Android tespiti
IS_ANDROID = 'android' in sys.platform or 'ANDROID_ARGUMENT' in os.environ

# Ses tanıma
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except:
    SR_AVAILABLE = False

# Ses sentezi
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except:
    GTTS_AVAILABLE = False

try:
    import edge_tts
    EDGE_AVAILABLE = True
except:
    EDGE_AVAILABLE = False

# Wake word (Android'de çalışır)
try:
    import pvporcupine
    PORCUPINE_AVAILABLE = True
except:
    PORCUPINE_AVAILABLE = False

# Ses çalma
try:
    import pygame
    PYGAME_AVAILABLE = True
except:
    PYGAME_AVAILABLE = False

# Ses kayıt (Android'de sınırlı)
try:
    import sounddevice as sd
    import soundfile as sf
    import numpy as np
    SOUNDDEVICE_AVAILABLE = True
except:
    SOUNDDEVICE_AVAILABLE = False


class VoiceEngineEnhanced:
    """
    Gelişmiş ses motoru - A.N.N.A'ya gerçek sesli asistan deneyimi
    """
    
    def __init__(self):
        # Android'de farklı depolama
        if IS_ANDROID:
            self.data_dir = Path("/storage/emulated/0/ANNA/voice")
        else:
            self.data_dir = Path("data/voice")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Temel bileşenler
        self.recognizer = sr.Recognizer() if SR_AVAILABLE else None
        self.microphone = None
        self._init_microphone()
        
        # Wake word
        self.porcupine = None
        self.wake_active = False
        self.wake_callback = None
        self.wake_keywords = ["jarvis", "computer", "alexa", "bilgisayar"]
        self._init_wake_word()
        
        # PYGAME MİXER'ı BAŞLAT (Android'de farklı ayarlar)
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.quit()
                if IS_ANDROID:
                    # Android için daha düşük kalite
                    pygame.mixer.init(frequency=16000, size=-16, channels=1, buffer=256)
                else:
                    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                print("✅ Pygame mixer hazır")
            except Exception as e:
                print(f"⚠️ Pygame mixer hatası: {e}")
        
        # Ses kuyruğu
        self.sound_queue = queue.Queue()
        self.is_playing = False
        self.sound_thread = threading.Thread(target=self._sound_worker, daemon=True)
        self.sound_thread.start()
        
        # Ses ayarları
        self.volume = 0.8
        self.speed = 1.0
        self.muted = False
        self.language = 'tr'
        
        # Ses profilleri
        self.voices = {
            'tr-TR-EmelNeural': '👩 Emel (Doğal)',
            'tr-TR-AhmetNeural': '👨 Ahmet (Profesyonel)',
            'tr-TR-DenizNeural': '🧑 Deniz (Samimi)',
            'tr-TR-AtillaNeural': '👨 Atilla (Enerjik)'
        }
        self.current_voice = 'tr-TR-DenizNeural'
        
        # Konuşma geçmişi
        self.history = []
        self.history_file = self.data_dir / "voice_history.json"
        self._load_history()
        
        # İstatistikler
        self.stats = {
            'words_spoken': 0,
            'sentences_spoken': 0,
            'listening_sessions': 0,
            'wake_word_triggers': 0
        }
        
        print("\n" + "="*50)
        print("🎤 A.N.N.A GELİŞMİŞ SES MOTORU")
        print("="*50)
        print(f"🎙️ Ses Tanıma: {'✅' if SR_AVAILABLE else '❌'}")
        print(f"🔊 Edge-TTS: {'✅' if EDGE_AVAILABLE else '❌'}")
        print(f"🎵 Pygame: {'✅' if PYGAME_AVAILABLE else '❌'}")
        print(f"🎚️ Wake Word: {'✅' if PORCUPINE_AVAILABLE else '❌'}")
        print(f"📱 Android: {'✅' if IS_ANDROID else '❌'}")
        print("="*50)
    
    def _init_microphone(self):
        """Mikrofonu başlat (Android'de farklı)"""
        if not SR_AVAILABLE:
            return
        
        try:
            if IS_ANDROID:
                # Android'de mikrofon indeksi farklı olabilir
                self.microphone = sr.Microphone(device_index=None)
            else:
                self.microphone = sr.Microphone()
            
            with self.microphone as source:
                print("🎤 Mikrofon kalibre ediliyor...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self.recognizer.energy_threshold = 3000
                self.recognizer.dynamic_energy_threshold = True
                print("✅ Mikrofon hazır")
        except Exception as e:
            print(f"❌ Mikrofon hatası: {e}")
    
    def _init_wake_word(self):
        """Wake word sistemini başlat (Android'de PICOVOICE_ACCESS_KEY gerekli)"""
        if not PORCUPINE_AVAILABLE:
            return
        
        # PICOVOICE_ACCESS_KEY environment variable'dan alınır
        access_key = os.getenv("PICOVOICE_ACCESS_KEY")
        if not access_key:
            print("⚠️ PICOVOICE_ACCESS_KEY yok, wake word çalışmaz")
            return
        
        try:
            self.porcupine = pvporcupine.create(
                access_key=access_key,
                keywords=self.wake_keywords,
                sensitivities=[0.5] * len(self.wake_keywords)
            )
            print(f"✅ Wake word hazır: {', '.join(self.wake_keywords)}")
        except Exception as e:
            print(f"❌ Wake word hatası: {e}")
    
    def _sound_worker(self):
        """Ses çalma worker'ı"""
        while True:
            try:
                text, voice, speed = self.sound_queue.get(timeout=1)
                self.is_playing = True
                
                if not self.muted:
                    # Her konuşma için yeni event loop
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self._speak_async(text, voice, speed))
                    loop.close()
                else:
                    print(f"🔇 [SESSİZ] A.N.N.A: {text}")
                
                self.is_playing = False
                self.sound_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Ses worker hatası: {e}")
                self.is_playing = False
    
    async def _speak_async(self, text: str, voice: str = None, speed: float = 1.0):
        """Asenkron konuşma"""
        voice = voice or self.current_voice
        temp_file = None
        
        try:
            # Kelime sayısını hesapla
            words = len(text.split())
            self.stats['words_spoken'] += words
            self.stats['sentences_spoken'] += 1
            
            # Konuşma geçmişine ekle
            self._add_to_history(text, voice)
            
            # Önce Edge-TTS dene
            if EDGE_AVAILABLE:
                try:
                    # Hız ayarı
                    rate = f"{int(speed * 100)}+%"
                    
                    communicate = edge_tts.Communicate(text, voice, rate=rate)
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                        temp_file = fp.name
                    
                    await communicate.save(temp_file)
                    
                    if PYGAME_AVAILABLE and os.path.exists(temp_file):
                        pygame.mixer.music.load(temp_file)
                        pygame.mixer.music.set_volume(self.volume)
                        pygame.mixer.music.play()
                        
                        # Ses bitene kadar bekle
                        while pygame.mixer.music.get_busy():
                            await asyncio.sleep(0.1)
                        
                        # Dosyayı sil
                        try:
                            os.unlink(temp_file)
                        except:
                            pass
                        return
                except Exception as e:
                    print(f"⚠️ Edge-TTS hatası: {e}")
            
            # Edge yoksa veya hata verdiyse gTTS dene
            if GTTS_AVAILABLE:
                try:
                    tts = gTTS(text=text, lang=self.language, slow=(speed < 0.8))
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                        temp_file = fp.name
                    tts.save(temp_file)
                    
                    if PYGAME_AVAILABLE and os.path.exists(temp_file):
                        pygame.mixer.music.load(temp_file)
                        pygame.mixer.music.set_volume(self.volume)
                        pygame.mixer.music.play()
                        
                        while pygame.mixer.music.get_busy():
                            await asyncio.sleep(0.1)
                        
                        try:
                            os.unlink(temp_file)
                        except:
                            pass
                        return
                except Exception as e:
                    print(f"⚠️ gTTS hatası: {e}")
            
            # Hiçbiri çalışmazsa yazdır
            print(f"🗣️ A.N.N.A: {text}")
            
        except Exception as e:
            print(f"❌ Ses sentezi hatası: {e}")
            print(f"🗣️ A.N.N.A: {text}")
        
        finally:
            # Temizlik
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except:
                    pass
    
    def speak(self, text: str, wait: bool = False):
        """Konuş"""
        if not text:
            return
        
        print(f"🗣️ A.N.N.A: {text}")
        self.sound_queue.put((text, self.current_voice, self.speed))
        
        if wait:
            while self.is_busy():
                time.sleep(0.1)
    
    def speak_with_voice(self, text: str, voice: str, wait: bool = False):
        """Belirli bir sesle konuş"""
        if voice in self.voices:
            self.sound_queue.put((text, voice, self.speed))
    
    def listen(self, timeout: int = 5, phrase_limit: int = 10) -> str:
        """Dinle ve metne çevir"""
        if not SR_AVAILABLE or not self.microphone:
            return ""
        
        self.stats['listening_sessions'] += 1
        
        try:
            with self.microphone as source:
                print("🎤 Dinliyorum...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout,
                    phrase_time_limit=phrase_limit
                )
            
            text = self.recognizer.recognize_google(audio, language="tr-TR")
            print(f"📝 Anlaşılan: {text}")
            return text.lower()
            
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            print(f"❌ Dinleme hatası: {e}")
            return ""
    
    def listen_with_indicator(self, timeout: int = 5):
        """Ses seviyesi göstergeli dinleme"""
        if not SOUNDDEVICE_AVAILABLE:
            return self.listen(timeout)
        
        print("🎤 Dinliyor... (ses seviyesi gösteriliyor)")
        result = [""]  # Thread'ler arası iletişim için
        
        def audio_callback(indata, frames, time_info, status):
            volume_norm = np.linalg.norm(indata) * 10
            bars = int(volume_norm)
            print(f"\r{'█' * min(bars, 50)}", end='', flush=True)
        
        def listen_thread():
            result[0] = self.listen(timeout)
        
        thread = threading.Thread(target=listen_thread)
        thread.start()
        
        with sd.InputStream(callback=audio_callback, channels=1):
            thread.join(timeout=timeout+1)
        
        print()  # Yeni satır
        return result[0]
    
    def start_wake_word(self, callback):
        """Wake word dinlemeyi başlat"""
        if not self.porcupine:
            return False
        
        self.wake_callback = callback
        self.wake_active = True
        threading.Thread(target=self._wake_loop, daemon=True).start()
        print("🔊 Wake word dinleniyor... ('Jarvis' deyin)")
        return True
    
    def _wake_loop(self):
        """Wake word döngüsü"""
        if not self.porcupine or not SOUNDDEVICE_AVAILABLE:
            return
        
        frame_length = self.porcupine.frame_length
        
        try:
            with sd.InputStream(
                samplerate=self.porcupine.sample_rate,
                channels=1,
                dtype='int16',
                blocksize=frame_length
            ) as stream:
                
                while self.wake_active:
                    try:
                        frame, overflowed = stream.read(frame_length)
                        
                        if len(frame) == frame_length:
                            pcm = frame.flatten().astype(np.int16).tobytes()
                            result = self.porcupine.process(pcm)
                            
                            if result >= 0:
                                word = self.wake_keywords[result]
                                print(f"\n🔊 '{word}' algılandı!")
                                self.stats['wake_word_triggers'] += 1
                                
                                if self.wake_callback:
                                    self.wake_callback(word)
                                
                                time.sleep(1.5)
                        
                        time.sleep(0.01)
                    except Exception as e:
                        print(f"⚠️ Wake word döngü hatası: {e}")
                        time.sleep(0.1)
                    
        except Exception as e:
            print(f"❌ Wake word ses akışı hatası: {e}")
    
    def stop_wake_word(self):
        """Wake word dinlemeyi durdur"""
        self.wake_active = False
        print("⏹️ Wake word durduruldu")
    
    def set_volume(self, volume: float):
        """Ses seviyesini ayarla (0.0 - 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        print(f"🔊 Ses seviyesi: %{int(self.volume * 100)}")
    
    def set_speed(self, speed: float):
        """Konuşma hızını ayarla (0.5 - 2.0)"""
        self.speed = max(0.5, min(2.0, speed))
        print(f"⚡ Konuşma hızı: {self.speed}x")
    
    def set_voice(self, voice: str):
        """Sesi değiştir"""
        if voice in self.voices:
            self.current_voice = voice
            print(f"🎙️ Ses değiştirildi: {self.voices[voice]}")
            return True
        return False
    
    def toggle_mute(self):
        """Sessiz modu aç/kapa"""
        self.muted = not self.muted
        status = "açıldı" if self.muted else "kapatıldı"
        print(f"🔇 Sessiz mod {status}")
        return self.muted
    
    def get_voices(self) -> dict:
        """Kullanılabilir sesleri listele"""
        return self.voices
    
    def is_busy(self) -> bool:
        """Konuşuyor mu?"""
        return self.is_playing or not self.sound_queue.empty()
    
    def _add_to_history(self, text: str, voice: str):
        """Konuşma geçmişine ekle"""
        self.history.append({
            'text': text,
            'voice': voice,
            'timestamp': datetime.now().isoformat(),
            'words': len(text.split())
        })
        
        # Son 100 konuşmayı tut
        if len(self.history) > 100:
            self.history = self.history[-100:]
        
        self._save_history()
    
    def _save_history(self):
        """Geçmişi kaydet"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'history': self.history,
                    'stats': self.stats
                }, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def _load_history(self):
        """Geçmişi yükle"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = data.get('history', [])
                    self.stats = data.get('stats', self.stats)
        except:
            pass
    
    def get_stats(self) -> str:
        """İstatistikleri göster"""
        return f"""
📊 **SES İSTATİSTİKLERİ**

🗣️ Konuşulan kelime: {self.stats['words_spoken']}
💬 Konuşulan cümle: {self.stats['sentences_spoken']}
👂 Dinleme oturumu: {self.stats['listening_sessions']}
🔊 Wake word tetikleme: {self.stats['wake_word_triggers']}

🎙️ Aktif ses: {self.voices[self.current_voice]}
🔊 Ses seviyesi: %{int(self.volume * 100)}
⚡ Konuşma hızı: {self.speed}x
🔇 Sessiz mod: {'Açık' if self.muted else 'Kapalı'}
"""
    
    def get_history(self, limit: int = 5) -> str:
        """Son konuşmaları göster"""
        if not self.history:
            return "📭 Konuşma geçmişi yok"
        
        result = "📜 **SON KONUŞMALAR**\n\n"
        for h in self.history[-limit:]:
            time_str = datetime.fromisoformat(h['timestamp']).strftime('%H:%M')
            result += f"🕐 {time_str} - {h['text'][:50]}...\n"
        
        return result
    
    def clear_history(self):
        """Geçmişi temizle"""
        self.history = []
        self._save_history()
        print("🧹 Konuşma geçmişi temizlendi")
    
    def test_microphone(self):
        """Mikrofon testi"""
        print("🎤 Mikrofon testi başlıyor... 3 saniye konuşun")
        text = self.listen(timeout=3)
        if text:
            print(f"✅ Mikrofon çalışıyor! Duyulan: {text}")
            self.speak(f"Duyduğum: {text}")
            return True
        else:
            print("❌ Mikrofon çalışmıyor veya ses algılanamadı")
            return False
    
    def test_speaker(self):
        """Hoparlör testi"""
        print("🔊 Hoparlör testi...")
        self.speak("Merhaba! Ben A.N.N.A. Ses testi yapıyorum. Eğer beni duyuyorsanız, ses sisteminiz çalışıyor demektir.")
        return True