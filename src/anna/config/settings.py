# config/settings.py
"""
A.N.N.A yapılandırma dosyası - Android için optimize edilmiş
- Telefonda çalışacak ayarlar
- Hafif ve hızlı
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = DATA_DIR / "logs"
    MEMORY_DIR = DATA_DIR / "memory"
    
    # ---------- ANDROİD İÇİN BASİT API KEY'LER ----------
    # İnternet varsa çalışır, yoksa offline moda geçer
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
    SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")
    PICOVOICE_ACCESS_KEY = os.getenv("PICOVOICE_ACCESS_KEY", "")
    
    # ---------- ANDROİD MODU ----------
    IS_ANDROID = True  # Telefonda olduğumuzu belirt
    
    # ---------- OFFLINE MOD ----------
    OFFLINE_MODE = False  # İnternet yoksa True olur
    
    # ---------- SES MOTORU ----------
    # Android'de gTTS kullanılır (pygame yok)
    DEFAULT_VOICE = "tr"  # Türkçe
    
    # ---------- HAFIZA AYARLARI ----------
    MAX_CONVERSATIONS = 100  # Telefonda fazla yer kaplamasın
    
    @classmethod
    def create_dirs(cls):
        """Gerekli klasörleri oluştur"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)
        cls.MEMORY_DIR.mkdir(exist_ok=True)
        
        # Ses dosyaları için klasör (Android'de geçici)
        (cls.DATA_DIR / "temp").mkdir(exist_ok=True)
        
        return cls
    
    @classmethod
    def check_internet(cls):
        """İnternet bağlantısını kontrol et (opsiyonel)"""
        try:
            import requests
            requests.get("https://www.google.com", timeout=2)
            cls.OFFLINE_MODE = False
            return True
        except:
            cls.OFFLINE_MODE = True
            return False