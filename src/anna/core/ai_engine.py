# core/ai_engine.py
"""
A.N.N.A'nın yapay zeka motoru - Android için optimize edilmiş
- İnternet yoksa bile çalışır (offline)
- Telefon için hafif mod
"""

import re
import requests
import json
from datetime import datetime
from loguru import logger
from config.settings import Config
from core.personality import Personality
from core.memory import Memory
from core.voice_engine import VoiceEngine

# Android'de çalışmayan modülleri geçici olarak devre dışı bırak
try:
    from modules.weather import WeatherAPI
    WEATHER_AVAILABLE = True
except ImportError:
    WEATHER_AVAILABLE = False
    print("⚠️ Weather modülü yok")

try:
    from modules.news import NewsAPI
    NEWS_AVAILABLE = True
except ImportError:
    NEWS_AVAILABLE = False
    print("⚠️ News modülü yok")

try:
    from modules.web_search import WebSearch
    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False
    print("⚠️ WebSearch modülü yok")

try:
    from modules.computer_control import ComputerControl
    COMPUTER_AVAILABLE = True
except ImportError:
    COMPUTER_AVAILABLE = False
    print("⚠️ ComputerControl modülü yok")

try:
    from modules.whatsapp_enhanced import WhatsAppEnhanced
    WHATSAPP_AVAILABLE = True
except ImportError:
    WHATSAPP_AVAILABLE = False
    print("⚠️ WhatsApp modülü yok")

# Yüz tanıma (Android'de çalışmaz)
try:
    from modules.face_recognition import FaceRecognition
    FACE_AVAILABLE = True
except ImportError:
    FACE_AVAILABLE = False
    print("⚠️ FaceRecognition modülü yok (Android'de çalışmaz)")

class AIEngine:
    """A.N.N.A'nın beyni - Android için optimize edilmiş"""
    
    def __init__(self, config: Config):
        self.config = config
        self.personality = Personality()
        self.memory = Memory(config.DATA_DIR / "jarvis.db")
        self.voice = VoiceEngine()
        
        # ---------- ANDROİD İÇİN OFFLINE MOD ----------
        # Telefonda Ollama yok, basit yanıtlar verecek
        self.is_online = self._check_internet()
        
        # ---------- MODÜLLERİ BAŞLAT (Android'de çalışanlar) ----------
        self.weather = WeatherAPI() if WEATHER_AVAILABLE else None
        self.news = NewsAPI() if NEWS_AVAILABLE else None
        self.web = WebSearch() if WEB_AVAILABLE else None
        self.computer = ComputerControl() if COMPUTER_AVAILABLE else None
        self.whatsapp = WhatsAppEnhanced() if WHATSAPP_AVAILABLE else None
        self.face = FaceRecognition() if FACE_AVAILABLE else None
        
        # Kullanıcı adını hatırla
        self.user_name = self.memory.get_profile("user_name") or "Efendim"
        self.personality.user_name = self.user_name
        
        logger.success(f"✅ AI Engine (Android) başlatıldı - Kullanıcı: {self.user_name}")
        if not self.is_online:
            logger.info("📴 İnternet yok, offline modda çalışıyor")
    
    def _check_internet(self):
        """İnternet bağlantısını kontrol et"""
        try:
            requests.get("https://www.google.com", timeout=3)
            return True
        except:
            return False
    
    def cevapla(self, mesaj: str) -> str:
        """Ana cevaplama fonksiyonu - Android için"""
        
        # ---------- OFFLINE CEVAPLAR ----------
        if not self.is_online:
            return self._offline_response(mesaj)
        
        # ---------- YÜZ TANIMA (Android'de çalışmaz) ----------
        if "yüz kaydet" in mesaj.lower() or "yüz tanı" in mesaj.lower():
            return "Yüz tanıma özelliği Android sürümünde devre dışıdır. Bilgisayarda kullanabilirsiniz."
        
        # ---------- HAVA DURUMU ----------
        if "hava" in mesaj.lower() and self.weather:
            sehir = re.sub(r'(hava|nasıl|durumu|kaç derece|sıcaklık)', '', mesaj.lower()).strip()
            if sehir:
                return self.weather.get_weather(sehir)
            return "Hangi şehrin hava durumunu öğrenmek istersiniz?"
        
        # ---------- HABERLER ----------
        if "haber" in mesaj.lower() and self.news:
            if "teknoloji" in mesaj.lower():
                return self.news.get_headlines(category="technology")
            elif "spor" in mesaj.lower():
                return self.news.get_headlines(category="sports")
            else:
                return self.news.get_headlines()
        
        # ---------- İNTERNET ARAMA ----------
        if "ara" in mesaj.lower() and self.web:
            sorgu = re.sub(r'(ara|internette ara|sorgula)', '', mesaj.lower()).strip()
            if sorgu:
                return self.web.search(sorgu)
            return "Ne aramamı istersiniz?"
        
        # ---------- WHATSAPP (Basit) ----------
        if "whatsapp" in mesaj.lower() and self.whatsapp:
            return "WhatsApp özelliği şu anda Android'de çalışmıyor. Yakında eklenecek."
        
        # ---------- TARİH VE SAAT ----------
        if "tarih" in mesaj.lower() or "saat" in mesaj.lower():
            now = datetime.now()
            return now.strftime("Saat %H:%M, %d %B %Y")
        
        # ---------- ÖZEL KOMUTLAR ----------
        
        # İsmini öğren
        if "benim adım" in mesaj.lower():
            name = mesaj.lower().replace("benim adım", "").strip()
            if name:
                self.memory.set_profile("user_name", name)
                self.user_name = name
                self.personality.user_name = name
                return f"Hoş geldin {name}! Seni tanıdığıma memnun oldum."
        
        # Adını sor
        if "adım ne" in mesaj.lower() or "ben kimim" in mesaj.lower():
            return f"Adın {self.user_name}, bunu nasıl unutursun?"
        
        # Dün ne konuştuk?
        if "dün ne konuştuk" in mesaj.lower() or "geçmiş" in mesaj.lower():
            recent = self.memory.get_recent_conversations(3)
            if recent:
                response = "Son konuştuklarımız:\n"
                for conv in recent:
                    response += f"• Sen: {conv['user'][:50]}...\n"
                return response
            return "Daha önce konuşmadık gibi?"
        
        # Not al
        if "not al" in mesaj.lower():
            note_content = mesaj.lower().replace("not al", "").strip()
            if note_content:
                note_id = self.memory.add_note("Hızlı Not", note_content)
                return f"Not alındı (ID: {note_id})"
        
        # Notları göster
        if "notlarım" in mesaj.lower():
            notes = self.memory.get_notes()
            if notes:
                response = "Notların:\n"
                for note in notes[:5]:
                    response += f"• {note['content'][:50]}...\n"
                return response
            return "Hiç not almamışsın."
        
        # ---------- KİŞİLİK VE ESPRİLER ----------
        personality_response = self.personality.react_to_command(mesaj)
        if personality_response:
            return personality_response
        
        if "şaka yap" in mesaj.lower():
            return self.personality.tell_joke()
        
        # ---------- DİĞER SOHBET ----------
        if self.is_online:
            return self._online_response(mesaj)
        else:
            return self._offline_response(mesaj)
    
    def _offline_response(self, mesaj: str) -> str:
        """İnternet yokken basit cevaplar"""
        mesaj = mesaj.lower()
        
        if "merhaba" in mesaj or "selam" in mesaj:
            return f"Merhaba {self.user_name}, nasılsın?"
        
        if "nasılsın" in mesaj:
            return "İyiyim, seni dinliyorum!"
        
        if "ne yapıyorsun" in mesaj:
            return "Sana yardım etmeye çalışıyorum. Bir şey sormak ister misin?"
        
        if "teşekkür" in mesaj:
            return "Rica ederim, her zaman!"
        
        if "görüşürüz" in mesaj or "hoşçakal" in mesaj:
            return "Görüşmek üzere, iyi günler!"
        
        # Varsayılan cevap
        return "Anladım. Devam etmek için internet bağlantısı gerekebilir. Oflline moddayım."
    
    def _online_response(self, mesaj: str) -> str:
        """İnternet varken basit cevaplar (Ollama'sız)"""
        # Burada basit bir sohbet motoru olabilir
        # Şimdilik basit cevaplar verelim
        return f"'{mesaj}' dedin. Bunu not aldım. Yakında daha akıllı olacağım!"
    
    def set_mood(self, mood: str) -> str:
        """Ruh halini değiştir"""
        return self.personality.set_mood(mood)