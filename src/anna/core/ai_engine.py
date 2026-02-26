# core/ai_engine.py
"""
A.N.N.A'nın yapay zeka motoru - Local Ollama ile çalışan versiyon
- Sohbet için qwen2.5:7b
- Kod yazma için deepseek-coder:6.7b
- Tamamen local, API gerekmez
"""

import re
import requests
import json
import subprocess
from datetime import datetime
from loguru import logger
from config.settings import Config
from core.personality import Personality
from core.memory import Memory
from core.voice_engine import VoiceEngine

from modules.face_recognition import FaceRecognition
from modules.weather import WeatherAPI
from modules.news import NewsAPI
from modules.computer_control import ComputerControl
from modules.web_search import WebSearch
from modules.whatsapp_enhanced import WhatsAppEnhanced

class AIEngine:
    """A.N.N.A'nın beyni - Hafıza, kişilik ve modül entegrasyonu (Local Ollama)"""
    
    def __init__(self, config: Config):
        self.config = config
        self.personality = Personality()
        self.memory = Memory(config.DATA_DIR / "jarvis.db")
        self.voice = VoiceEngine()
        
        # ---------- OLLAMA MODELLERİ ----------
        # Sohbet modeli (genel amaçlı)
        self.chat_model = "qwen2.5:7b"
        # Kod yazma modeli (programlama için)
        self.code_model = "deepseek-coder:6.7b"
        
        # Ollama sunucu adresi (varsayılan)
        self.ollama_url = "http://localhost:11434/api/generate"
        
        # Ollama'nın çalıştığını kontrol et
        self._check_ollama()
        
        # Modülleri başlat
        self.face = FaceRecognition()
        self.weather = WeatherAPI()
        self.news = NewsAPI()
        self.whatsapp = WhatsAppEnhanced()
        self.computer = ComputerControl()
        self.web = WebSearch()
        
        # Kullanıcı adını hatırla
        self.user_name = self.memory.get_profile("user_name") or "Efendim"
        self.personality.user_name = self.user_name
        
        logger.success(f"✅ AI Engine (Local) başlatıldı - Kullanıcı: {self.user_name}")
        logger.info(f"📌 Sohbet modeli: {self.chat_model}")
        logger.info(f"📌 Kod modeli: {self.code_model}")
    
    def _check_ollama(self):
        """Ollama'nın çalışıp çalışmadığını kontrol et"""
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                
                if self.chat_model not in model_names:
                    logger.warning(f"⚠️ {self.chat_model} bulunamadı. Lütfen 'ollama pull {self.chat_model}' ile indirin.")
                if self.code_model not in model_names:
                    logger.warning(f"⚠️ {self.code_model} bulunamadı. Lütfen 'ollama pull {self.code_model}' ile indirin.")
                
                logger.success("✅ Ollama sunucusu çalışıyor")
            else:
                logger.error("❌ Ollama sunucusu çalışmıyor! Lütfen 'ollama serve' komutunu çalıştırın.")
        except requests.exceptions.ConnectionError:
            logger.error("❌ Ollama sunucusuna bağlanılamadı! Lütfen 'ollama serve' komutunu çalıştırın.")
            logger.info("💡 İpucu: Yeni bir terminal açıp 'ollama serve' yazın")
    
    def _ollama_istek(self, model: str, prompt: str, sistem: str = None) -> str:
        """
        Ollama'ya istek gönder
        model: kullanılacak model adı
        prompt: kullanıcı mesajı
        sistem: sistem prompt'u (opsiyonel)
        """
        try:
            # İstek verisini hazırla
            data = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                }
            }
            
            # Sistem prompt'u varsa ekle
            if sistem:
                data["system"] = sistem
            
            # POST isteği gönder
            response = requests.post(self.ollama_url, json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                logger.error(f"Ollama hatası: {response.status_code}")
                return f"❌ Ollama hatası: {response.status_code}"
                
        except requests.exceptions.Timeout:
            logger.error("Ollama zaman aşımı")
            return "❌ İstek zaman aştı. Model çok yavaş olabilir."
        except Exception as e:
            logger.error(f"Ollama bağlantı hatası: {e}")
            return f"❌ Bağlantı hatası: {e}"
    
    def cevapla(self, mesaj: str) -> str:
        """Ana cevaplama fonksiyonu - tüm modüller entegre"""
        
        # ---------- YÜZ TANIMA ----------
        if "yüz kaydet" in mesaj.lower():
            isim = mesaj.lower().replace("yüz kaydet", "").strip()
            if self.face.register_face(isim or "kullanıcı"):
                return "Yüzünüz kaydedildi efendim. Artık sizi tanıyorum."
        
        if "ben kimim" in mesaj.lower() or "yüz tanı" in mesaj.lower():
            user = self.face.recognize()
            if user:
                return f"Hoş geldiniz {user}!"
            return "Yüzünüzü tanıyamadım. Lütfen önce yüz kaydedin."
        
        # ---------- HAVA DURUMU ----------
        if "hava" in mesaj.lower():
            sehir = re.sub(r'(hava|nasıl|durumu|kaç derece|sıcaklık)', '', mesaj.lower()).strip()
            if sehir:
                return self.weather.get_weather(sehir)
            return "Hangi şehrin hava durumunu öğrenmek istersiniz?"
        
        if "tahmin" in mesaj.lower() or "yarın hava" in mesaj.lower():
            sehir = mesaj.lower().replace("tahmin", "").replace("yarın hava", "").strip()
            if sehir:
                return self.weather.get_forecast(sehir)
        
        # ---------- HABERLER ----------
        if "haber" in mesaj.lower() or "manşet" in mesaj.lower():
            if "teknoloji" in mesaj.lower():
                return self.news.get_headlines(category="technology")
            elif "spor" in mesaj.lower():
                return self.news.get_headlines(category="sports")
            elif "ekonomi" in mesaj.lower():
                return self.news.get_headlines(category="business")
            else:
                return self.news.get_headlines()
        
        if "ara" in mesaj.lower() and "haber" in mesaj.lower():
            konu = mesaj.lower().replace("ara", "").replace("haber", "").strip()
            if konu:
                return self.news.search_news(konu)
        
        # ---------- İNTERNET ARAMA ----------
        if "ara" in mesaj.lower() or "internette ara" in mesaj.lower() or "sorgula" in mesaj.lower():
            sorgu = re.sub(r'(ara|internette ara|sorgula|google\'da ara|youtube\'da ara)', '', mesaj.lower()).strip()
            if sorgu:
                return self.web.search(sorgu)
            return "Ne aramamı istersiniz?"
        
        if "youtube" in mesaj.lower() and "ara" in mesaj.lower():
            video = mesaj.lower().replace("youtube", "").replace("ara", "").strip()
            if video:
                import pywhatkit as kit
                kit.playonyt(video)
                return f"YouTube'da {video} aranıyor..."
        
        # ---------- KOD YAZMA KOMUTU ----------
        if "kod yaz" in mesaj.lower() or "program yaz" in mesaj.lower() or "uygulama yap" in mesaj.lower():
            return self._kod_yaz(mesaj)
        
        # ---------- WHATSAPP (Gelişmiş) ----------
        if "whatsapp" in mesaj.lower() and "mesaj" in mesaj.lower():
            pattern = r'(.+?) (?:mesaj|yaz) (?:gönder|at)'
            match = re.search(pattern, mesaj.lower())
            
            if match:
                kisi = match.group(1).strip()
                # Mesaj içeriğini sor
                self.voice.konus(f"{kisi} için ne mesajı göndereyim?")
                
                # Kullanıcıdan mesaj al
                msg = self.voice.dinle(timeout=10)
                
                if msg:
                    # WhatsApp Web'i aç ve mesaj gönder
                    self.whatsapp.open_web_whatsapp()
                    result = self.whatsapp.search_and_send(kisi, msg)
                    return f"{kisi}'e mesaj gönderiliyor: {msg[:30]}..."
            
            return "Kime mesaj göndermemi istersiniz?"
        
        # ---------- WHATSAPP WEB ----------
        if "whatsapp web" in mesaj.lower() or "whatsapp'ı aç" in mesaj.lower():
            self.whatsapp.open_web_whatsapp()
            return "WhatsApp Web açılıyor..."
        
        # ---------- BİLGİSAYAR KONTROLÜ ----------
        if "aç" in mesaj.lower() and ("program" in mesaj.lower() or "uygulama" in mesaj.lower()):
            program = mesaj.lower().replace("aç", "").replace("programı", "").replace("uygulamayı", "").strip()
            if program:
                return self.computer.open_application(program)
        
        if "kapat" in mesaj.lower() and ("program" in mesaj.lower() or "uygulama" in mesaj.lower()):
            program = mesaj.lower().replace("kapat", "").replace("programı", "").replace("uygulamayı", "").strip()
            if program:
                return self.computer.close_application(program)
        
        if "ekran görüntüsü" in mesaj.lower() or "screenshot" in mesaj.lower():
            return self.computer.take_screenshot()
        
        if "sistem" in mesaj.lower() and "durum" in mesaj.lower():
            return self.computer.get_system_info()
        
        if "ses" in mesaj.lower() and ("ayarla" in mesaj.lower() or "değiştir" in mesaj.lower()):
            level = re.findall(r'\d+', mesaj)
            if level:
                return self.computer.set_volume(int(level[0]))
        
        # ---------- DİĞER ----------
        if "ip adresim" in mesaj.lower():
            ip = requests.get('https://api64.ipify.org').text
            return f"IP adresiniz: {ip}"
        
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
                response = f"Hoş geldin {name}! Seni tanıdığıma memnun oldum."
                self.memory.add_conversation(mesaj, response, self.personality.mood)
                return response
        
        # Adını sor
        if "adım ne" in mesaj.lower() or "ben kimim" in mesaj.lower():
            response = f"Adın {self.user_name}, bunu nasıl unutursun?"
            self.memory.add_conversation(mesaj, response, self.personality.mood)
            return response
        
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
        
        # İstatistikler
        if "istatistik" in mesaj.lower() or "kaç konuşma" in mesaj.lower():
            stats = self.memory.get_stats()
            return f"Toplam {stats['total_conversations']} konuşma yaptık. Son 7 günde {stats['last_7_days']} kez konuştuk."
        
        # ---------- KİŞİLİK VE NORMAL CEVAP ----------
        
        # Önce kişilik tepkisini kontrol et
        personality_response = self.personality.react_to_command(mesaj)
        if personality_response:
            self.memory.add_conversation(mesaj, personality_response, self.personality.mood)
            return personality_response
        
        # Espri kontrolü
        if "şaka yap" in mesaj.lower():
            response = self.personality.tell_joke()
            self.memory.add_conversation(mesaj, response, self.personality.mood)
            return response
        
        # ---------- NORMAL SOHBET (Local Ollama) ----------
        return self._get_ai_response(mesaj)
    
    def _kod_yaz(self, mesaj: str) -> str:
        """Kod yazma modelini kullan (deepseek-coder)"""
        try:
            # Mesajı temizle
            prompt = mesaj.lower().replace("kod yaz", "").replace("program yaz", "").replace("uygulama yap", "").strip()
            
            # Kod yazma için özel sistem prompt'u
            sistem = """
            Sen bir yazılım geliştiricisin. Kullanıcının istediği programı yaz.
            Sadece kod yaz, açıklama ekleme. Kodun çalışabilir ve hatasız olmasına dikkat et.
            """
            
            response = self._ollama_istek(self.code_model, prompt or "Merhaba Dünya yazdıran Python kodu yaz", sistem)
            
            # Kod bloklarını düzgün göster
            if "```" not in response:
                response = f"```python\n{response}\n```"
            
            return response
        except Exception as e:
            logger.error(f"Kod yazma hatası: {e}")
            return f"❌ Kod yazılamadı: {e}"
    
    def _get_ai_response(self, mesaj: str) -> str:
        """Local Ollama'dan cevap al (qwen2.5)"""
        try:
            # Kişilik ruh haline göre sistem prompt'u
            mood_prompts = {
                "professional": "Profesyonel ve yardımsever bir asistansın. Kısa ve öz cevaplar ver.",
                "playful": "Esprili ve samimi bir asistansın. Biraz şakacı olabilirsin.",
                "sarcastic": "Hafif alaycı ama saygılı bir asistansın. Espirili cevaplar ver."
            }
            
            sistem = mood_prompts.get(self.personality.mood, 
                                      "Yardımsever bir asistansın. Türkçe cevap ver.")
            
            response = self._ollama_istek(self.chat_model, mesaj, sistem)
            
            self.memory.add_conversation(mesaj, response, self.personality.mood)
            return response
            
        except Exception as e:
            logger.error(f"AI hatası: {e}")
            return f"❌ Bir hata oluştu: {e}"
    
    def set_mood(self, mood: str) -> str:
        """Ruh halini değiştir"""
        return self.personality.set_mood(mood)
    
    def check_models(self):
        """İndirilmiş modelleri listele"""
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                return models
        except:
            return []