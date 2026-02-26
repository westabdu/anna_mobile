# core/voice_engine.py - gTTS ile (Google TTS) + ECHO Korumalı
"""
A.N.N.A'nın ses motoru - gTTS ile (Türkçe destekli)
- Enerji eşiği yüksek (daha az hassas)
- Zaman filtresi (kendi sesini duymaz)
- Kelime filtresi (kısa komutları engeller)
"""

from gtts import gTTS
import tempfile
import pygame
import os
import threading
import queue
import time
import speech_recognition as sr
from loguru import logger

class VoiceEngine:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        
        # gTTS ayarları
        self.language = 'tr'  # Türkçe
        self.slow = False  # Normal hız
        
        # SES TANIMA AYARLARI (Echo koruma)
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 4000  # Normalde 300-500, yüksek = az hassas
        self.recognizer.pause_threshold = 1.5  # Sessizlik süresi (uzun = geç keser)
        self.recognizer.phrase_threshold = 0.5
        self.recognizer.non_speaking_duration = 0.8
        
        # Son konuşma zamanı (echo engelleme için)
        self.last_spoke_time = 0
        self.last_spoken_text = ""
        
        # SES ÇALMA İÇİN THREAD ve QUEUE
        self.sound_queue = queue.Queue()
        self.is_playing = False
        self.sound_thread = threading.Thread(target=self._sound_worker, daemon=True)
        self.sound_thread.start()
        
        # Mikrofon kalibrasyonu
        self._init_microphone()
        
        # Pygame mixer'ı başlat
        pygame.mixer.init()
        
        logger.success("✅ Ses motoru (gTTS) hazır")
        print("🔊 A.N.N.A hazır - Google TTS ile Türkçe konuşacak")
        print("🛡️ Echo koruma: Aktif (enerji:4000, zaman:2s, kelime filtre)")
    
    def _init_microphone(self):
        """Mikrofonu başlat"""
        try:
            mikrofonlar = sr.Microphone.list_microphone_names()
            print(f"🎤 Bulunan mikrofonlar: {mikrofonlar}")
            
            if mikrofonlar:
                self.microphone = sr.Microphone(device_index=0)
                with self.microphone as source:
                    print("🎤 Mikrofon kalibre ediliyor...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    print("✅ Mikrofon kalibre edildi")
            else:
                print("❌ Mikrofon bulunamadı")
        except Exception as e:
            print(f"❌ Mikrofon hatası: {e}")
    
    def _sound_worker(self):
        """Sesleri sırayla çalan worker thread"""
        while True:
            try:
                text = self.sound_queue.get(timeout=1)
                self.is_playing = True
                
                # Son konuşma zamanını kaydet (dinleme filtresi için)
                self.last_spoke_time = time.time()
                self.last_spoken_text = text
                
                # Boş metin kontrolü
                if not text or text.isspace():
                    print("⚠️ Boş metin, ses çalınmadı")
                    self.is_playing = False
                    self.sound_queue.task_done()
                    continue
                
                temp_file = None
                try:
                    # Geçici dosya oluştur
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                        temp_file = fp.name
                    
                    print(f"🔊 Ses oluşturuluyor: {text[:30]}...")
                    
                    # gTTS ile ses oluştur
                    tts = gTTS(text=text, lang=self.language, slow=self.slow)
                    tts.save(temp_file)
                    
                    # Ses çal
                    pygame.mixer.music.load(temp_file)
                    pygame.mixer.music.play()
                    
                    # Ses bitene kadar bekle
                    while pygame.mixer.music.get_busy():
                        pygame.time.wait(100)
                    
                except Exception as e:
                    logger.error(f"Ses oluşturma hatası: {e}")
                    print(f"🤖 {text}")  # Ses yoksa yazı olarak göster
                
                finally:
                    if temp_file and os.path.exists(temp_file):
                        try:
                            os.unlink(temp_file)
                        except:
                            pass
                
                self.is_playing = False
                self.sound_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Ses çalma hatası: {e}")
                self.is_playing = False
    
    def konus(self, text: str):
        """Metni sese çevir ve kuyruğa ekle"""
        print(f"🤖 A.N.N.A: {text}")
        
        # Metni temizle
        text = text.strip()
        if not text:
            return
        
        self.sound_queue.put(text)
    
    def konus_ve_bekle(self, text: str, timeout=30):
        """Metni sese çevir ve bitene kadar bekle"""
        self.konus(text)
        
        # Sesin bitmesini bekle
        start_time = time.time()
        while self.is_busy() and (time.time() - start_time) < timeout:
            time.sleep(0.1)
    
    def is_busy(self) -> bool:
        return self.is_playing or not self.sound_queue.empty()
    
    def _is_anna_speaking(self, text):
        """ANNA'nın kendi sesini tanı"""
        # ANNA'nın sık kullandığı kalıplar
        anna_phrases = [
            "merhaba",
            "dinliyorum",
            "anlıyorum",
            "yardımcı olabilirim",
            "buyur",
            "efendim",
            "anladım",
            "tamam",
            "size nasıl yardımcı olabilirim",
            "memnuniyet duyarım"
        ]
        
        # Çok kısa cümleleri filtrele (1-2 kelime)
        words = text.split()
        if len(words) <= 2:
            return True
        
        # Belli kalıpları filtrele
        text_lower = text.lower()
        for phrase in anna_phrases:
            if phrase in text_lower and len(phrase.split()) <= 2:
                return True
        
        return False
    
    def dinle(self, timeout=5) -> str:
        """Mikrofondan ses al ve metne çevir - ECHO Korumalı"""
        if self.microphone is None:
            return ""
        
        # ----- ZAMAN FİLTRESİ -----
        # ANNA konuşuyorsa bekle (2 saniye)
        time_since_last_spoke = time.time() - self.last_spoke_time
        if time_since_last_spoke < 2.0:
            print(f"🔇 ANNA konuşuyor, {2.0 - time_since_last_spoke:.1f} saniye bekleniyor...")
            time.sleep(2.0 - time_since_last_spoke)
        
        try:
            with self.microphone as source:
                print("\n🎤 Dinliyorum...")
                
                # ----- ENERJİ FİLTRESİ -----
                # Yüksek enerji eşiği (sadece yüksek sesleri al)
                self.recognizer.energy_threshold = 4000
                
                # Dinle
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=5)
            
            # Ses tanıma
            text = self.recognizer.recognize_google(audio, language="tr-TR")
            print(f"📝 Anlaşılan: {text}")
            
            # ----- KELİME FİLTRESİ -----
            # ANNA'nın kendi sesini filtrele
            if self._is_anna_speaking(text):
                print("🔇 Kendi sesimi duydum, yok sayıyorum")
                return ""
            
            # Son 2 saniye içinde aynı metni söylediyse engelle
            if text.lower() == self.last_spoken_text.lower():
                print("🔇 Aynı metni tekrar duydum, yok sayıyorum")
                return ""
            
            return text.lower()
            
        except sr.WaitTimeoutError:
            print("\r⏱️ Süre doldu")
        except sr.UnknownValueError:
            print("\r🤔 Anlaşılamadı")
        except Exception as e:
            logger.error(f"Ses hatası: {e}")
        
        return ""
    
    def dinle_manuel(self, timeout=5) -> str:
        """Manuel dinleme (butonla tetiklenen) - Filtresiz"""
        if self.microphone is None:
            return ""
        
        try:
            with self.microphone as source:
                print("\n🎤 [MANUEL] Dinliyorum...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            text = self.recognizer.recognize_google(audio, language="tr-TR")
            print(f"📝 Anlaşılan: {text}")
            return text.lower()
            
        except sr.WaitTimeoutError:
            print("\r⏱️ Süre doldu")
        except sr.UnknownValueError:
            print("\r🤔 Anlaşılamadı")
        except:
            pass
        
        return ""