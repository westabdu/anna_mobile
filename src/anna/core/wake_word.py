# core/wake_word.py
"""
Wake Word Sistemi - "Jarvis" deyince uyanır
Porcupine motoru ile offline çalışır
"""

import struct
import threading
import time
from pathlib import Path
from loguru import logger
import pyaudio
import pvporcupine

from config.settings import Config

class WakeWordSystem:
    """
    Porcupine ile wake word algılama
    - "Jarvis" kelimesini dinler
    - Algılayınca callback fonksiyonu çağrılır
    - Düşük gecikme, yüksek doğruluk
    """
    
    def __init__(self, config: Config, callback=None, sensitivity=0.5):
        """
        Args:
            config: Config objesi (access_key için)
            callback: Wake word algılandığında çağrılacak fonksiyon
            sensitivity: 0-1 arası hassasiyet (0.5 ideal)
        """
        self.config = config
        self.callback = callback
        self.sensitivity = sensitivity
        self.is_listening = False
        self.listener_thread = None
        self.porcupine = None
        self.audio_stream = None
        self.pa = None
        
        # Access key'i config'den al
        self.access_key = config.PICOVOICE_ACCESS_KEY
        if not self.access_key:
            logger.error("❌ PICOVOICE_ACCESS_KEY bulunamadı! .env dosyasını kontrol et.")
        
        # Özel keyword dosyası (opsiyonel - "hey jarvis" için)
        self.custom_keyword_path = Path(__file__).parent.parent / "hey_jarvis.ppn"
        
        logger.info("🔊 Wake word sistemi başlatılıyor...")
        self._init_porcupine()
    
    def _init_porcupine(self):
        """Porcupine motorunu başlat"""
        if not self.access_key:
            logger.error("Access key yok, wake word çalışmaz!")
            self.porcupine = None
            return
        
        try:
            # Eğer özel keyword dosyası varsa onu kullan
            if self.custom_keyword_path.exists():
                logger.info(f"📁 Özel keyword bulundu: {self.custom_keyword_path}")
                self.porcupine = pvporcupine.create(
                    access_key=self.access_key,
                    keywords=["jarvis"],
                    keyword_paths=[str(self.custom_keyword_path)],
                    sensitivities=[self.sensitivity]
                )
                logger.success("✅ 'Jarvis' ve 'Hey Jarvis' aktif!")
            else:
                # Sadece built-in "jarvis" kelimesi
                self.porcupine = pvporcupine.create(
                    access_key=self.access_key,
                    keywords=["jarvis"],
                    sensitivities=[self.sensitivity]
                )
                logger.success("✅ 'Jarvis' aktif!")
            
            logger.info(f"🎚️ Hassasiyet: {self.sensitivity}")
            
        except Exception as e:
            logger.error(f"❌ Porcupine başlatılamadı: {e}")
            logger.warning("⚠️ Wake word olmadan devam edilecek")
            self.porcupine = None
    
    def start(self):
        """Wake word dinlemeyi başlat"""
        if self.porcupine is None:
            logger.error("Porcupine başlatılamadı!")
            return False
        
        if self.is_listening:
            logger.warning("Wake word zaten dinleniyor")
            return True
        
        try:
            # PyAudio'yı başlat
            self.pa = pyaudio.PyAudio()
            
            # Ses akışını başlat
            self.audio_stream = self.pa.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length
            )
            
            self.is_listening = True
            self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listener_thread.start()
            
            logger.success("👂 Wake word dinleniyor... 'Jarvis' deyin")
            return True
            
        except Exception as e:
            logger.error(f"Ses akışı başlatılamadı: {e}")
            return False
    
    def _listen_loop(self):
        """Ana dinleme döngüsü"""
        while self.is_listening:
            try:
                # Mikrofondan ses oku
                pcm = self.audio_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
                
                # Wake word kontrolü
                result = self.porcupine.process(pcm)
                
                if result >= 0:
                    logger.success("🔊 'Jarvis' algılandı!")
                    
                    # Callback'i çağır (eğer varsa)
                    if self.callback:
                        threading.Thread(target=self.callback, args=("jarvis",), daemon=True).start()
                    
                    # Biraz bekle (çok sık algılamayı önlemek için)
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Dinleme hatası: {e}")
                time.sleep(0.1)
    
    def stop(self):
        """Wake word dinlemeyi durdur"""
        self.is_listening = False
        
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
        
        if self.pa:
            self.pa.terminate()
        
        if self.porcupine:
            self.porcupine.delete()
        
        logger.info("⏹️ Wake word durduruldu")
    
    def set_callback(self, callback):
        """Callback fonksiyonunu değiştir"""
        self.callback = callback
        logger.debug("Callback güncellendi")