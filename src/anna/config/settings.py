# config/settings.py
"""
A.N.N.A yapılandırma dosyası
- Local AI (Ollama) için API key gerekmez
- Sadece harici servisler için API key'ler
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
    
    # ---------- API KEY'LER (HALA GEREKLİ) ----------
    # Hava durumu için (OpenWeatherMap)
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
    
    # Haberler için (NewsAPI)
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    
    # Web arama için (SerpAPI - opsiyonel)
    SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
    
    # Wake word için (Picovoice)
    PICOVOICE_ACCESS_KEY = os.getenv("PICOVOICE_ACCESS_KEY")
    
    # ---------- KALDIRILAN API KEY'LER ----------
    # GEMINI_API_KEY - Artık kullanılmıyor (Local Ollama'ya geçtik)
    # GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # SİLİNDİ
    
    # ---------- OLLAMA AYARLARI ----------
    OLLAMA_URL = "http://localhost:11434"
    CHAT_MODEL = "qwen2.5:7b"
    CODE_MODEL = "deepseek-coder:6.7b"
    
    # ---------- SES MOTORU ----------
    DEFAULT_VOICE = "serena"  # serena, vivian, sohee, anna, aiden, ryan
    USE_GPU = True  # GPU varsa True
    
    @classmethod
    def create_dirs(cls):
        """Gerekli klasörleri oluştur"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)
        cls.MEMORY_DIR.mkdir(exist_ok=True)
        
        # Ses modeli için klasör
        (cls.DATA_DIR / "voices").mkdir(exist_ok=True)
        
        return cls