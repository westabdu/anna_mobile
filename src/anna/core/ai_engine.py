# core/ai_engine.py - Android için optimize edilmiş
"""
A.N.N.A'nın yapay zeka motoru - Android için offline mod
"""

import re
import requests
from datetime import datetime
from loguru import logger
from anna.config.settings import Config
from anna.core.personality import Personality
from anna.core.memory import Memory
from anna.core.voice_engine import VoiceEngine

# Android'de çalışmayan modülleri devre dışı bırak
try:
    from anna.modules.weather import WeatherAPI
    WEATHER_AVAILABLE = True
except ImportError:
    WEATHER_AVAILABLE = False

try:
    from anna.modules.news import NewsAPI
    NEWS_AVAILABLE = True
except ImportError:
    NEWS_AVAILABLE = False

try:
    from anna.modules.web_search import WebSearch
    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False

try:
    from anna.modules.calendar import CalendarManager
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False

try:
    from anna.modules.notes import NotesManager
    NOTES_AVAILABLE = True
except ImportError:
    NOTES_AVAILABLE = False

try:
    from anna.modules.gamification import Gamification
    GAME_AVAILABLE = True
except ImportError:
    GAME_AVAILABLE = False

class AIEngine:
    def __init__(self, config: Config):
        self.config = config
        self.personality = Personality()
        self.memory = Memory(config.DATA_DIR / "jarvis.db")
        self.voice = VoiceEngine()
        
        # İnternet kontrolü
        self.is_online = self._check_internet()
        
        # Modülleri başlat (varsa)
        self.weather = WeatherAPI() if WEATHER_AVAILABLE else None
        self.news = NewsAPI() if NEWS_AVAILABLE else None
        self.web = WebSearch() if WEB_AVAILABLE else None
        self.calendar = CalendarManager() if CALENDAR_AVAILABLE else None
        self.notes = NotesManager() if NOTES_AVAILABLE else None
        self.game = Gamification() if GAME_AVAILABLE else None
        
        # Kullanıcı adı
        self.user_name = self.memory.get_profile("user_name") or "Efendim"
        self.personality.user_name = self.user_name
        
        logger.success("✅ AI Engine (Android) başlatıldı")
        if not self.is_online:
            logger.info("📴 Offline mod aktif")
    
    def _check_internet(self):
        try:
            requests.get("https://www.google.com", timeout=3)
            return True
        except:
            return False
    
    def cevapla(self, mesaj: str) -> str:
        mesaj = mesaj.lower()
        
        # ----- YARDIM KOMUTLARI -----
        if "yardım" in mesaj or "ne yapabilirsin" in mesaj:
            return self._yardim()
        
        # ----- HAVA DURUMU -----
        if "hava" in mesaj and self.weather and self.is_online:
            return self.weather.get_weather("İstanbul")
        
        # ----- TARİH/SAAT -----
        if "tarih" in mesaj or "saat" in mesaj:
            return datetime.now().strftime("%d %B %Y, %H:%M")
        
        # ----- NOTLAR -----
        if "not al" in mesaj and self.notes:
            note = mesaj.replace("not al", "").strip()
            if note:
                self.notes.add_note("Hızlı Not", note)
                return f"✅ Not alındı: {note[:30]}..."
        
        if "notlarım" in mesaj and self.notes:
            notes = self.notes.list_notes()
            return notes
        
        # ----- HATIRLATICI -----
        if "hatırlat" in mesaj and "dakika" in mesaj and self.calendar:
            import re
            dk = re.findall(r'\d+', mesaj)
            if dk:
                note = mesaj.replace("hatırlat", "").replace(dk[0], "").replace("dakika", "").strip()
                return self.calendar.add_reminder(note, int(dk[0]))
        
        # ----- BASİT SOHBET -----
        if "merhaba" in mesaj or "selam" in mesaj:
            return f"Merhaba {self.user_name}, nasılsın?"
        if "nasılsın" in mesaj:
            return "İyiyim, seni dinliyorum!"
        if "teşekkür" in mesaj:
            return "Rica ederim 😊"
        if "görüşürüz" in mesaj:
            return "Görüşmek üzere!"
        if "naber" in mesaj:
            return "İyilik senden naber?"
        
        # ----- ESPRİLER -----
        if "şaka yap" in mesaj:
            return self.personality.tell_joke()
        
        # ----- OYUNLAŞTIRMA -----
        if "istatistik" in mesaj and self.game:
            return self.game.get_stats()
        
        if "başarımlar" in mesaj and self.game:
            return self.game.get_achievements()
        
        # ----- EASTER EGG'LER -----
        if self.game:
            egg = self.game.check_easter_egg(mesaj)
            if egg:
                return egg
        
        # ----- VARSAYILAN CEVAP -----
        if self.is_online:
            return f"'{mesaj}' dedin. Bunu not aldım."
        else:
            return "Anladım. Devam etmek için internet gerekebilir."
    
    def _yardim(self):
        return """🤖 **A.N.N.A Komutları**
        
🌤️ hava durumu
📅 tarih/saat
📝 not al [not]
📋 notlarım
⏰ hatırlat [şey] [dakika]
😂 şaka yap
📊 istatistik
🏆 başarımlar
"""

    def set_mood(self, mood: str):
        return self.personality.set_mood(mood)