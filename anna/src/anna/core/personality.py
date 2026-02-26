# core/personality.py
"""
JARVIS'in kişiliği - Tony Stark'ın asistanı gibi
- Espri yapar
- Ruh hali değişir
- Kullanıcıyı tanır
"""

import random
import json
from datetime import datetime
from pathlib import Path
from loguru import logger

class Personality:
    """
    JARVIS'in kişilik modülü
    - Farklı ruh halleri (profesyonel, esprili, alaycı)
    - Kullanıcıya özel hitap
    - Hafıza
    """
    
    def __init__(self, user_name="Efendim"):
        self.user_name = user_name
        self.mood = "professional"  # professional, playful, sarcastic
        self.memory_file = Path(__file__).parent.parent / "data" / "personality" / "memory.json"
        self.memory_file.parent.mkdir(exist_ok=True)
        
        # Konuşma geçmişi
        self.conversation_history = []
        self.load_memory()
        
        # Jarvis'in replikleri
        self._init_responses()
        
        logger.success("✅ Kişilik modülü başlatıldı")
    
    def _init_responses(self):
        """Jarvis'in cevap kütüphanesi"""
        
        # Selamlama çeşitleri
        self.greetings = {
            "professional": [
                "Buyurun {name}, nasıl yardımcı olabilirim?",
                "Dinliyorum {name}, emrinizdeyim.",
                "Hoş geldiniz {name}, sistemler hazır."
            ],
            "playful": [
                "Efendim {name}! Yine ne icat ediyoruz bugün?",
                "Merhaba {name}! Sizi görmek ne güzel.",
                "Aaa {name}! Tam da size bir şaka hazırlıyordum."
            ],
            "sarcastic": [
                "Efendim {name}... Yine mi bilgisayarı kurcalayacağız?",
                "Buyurun {name}, neyi patlatacağız bugün?"
            ]
        }
        
        # Vedalaşma çeşitleri
        self.farewells = {
            "professional": [
                "Görüşmek üzere {name}, iyi günler.",
                "Hoşça kalın {name}, her an buradayım."
            ],
            "playful": [
                "Görüşürüz {name}! Ben burada takılıyorum.",
                "Bay bay {name}! Dünyayı kurtarmaya gidiyorsanız haberim olsun."
            ]
        }
        
        # Espri kütüphanesi
        self.jokes = [
            {
                "joke": "Neden yapay zekalar poker oynayamaz?",
                "punchline": "Çünkü blöf yaparken hep işlemci ısınıyor!"
            },
            {
                "joke": "Bir bilgisayar neden psikoloğa gider?",
                "punchline": "Çok fazla 'cache' belleği varmış!"
            },
            {
                "joke": "Size bir itirafta bulunacağım {name}.",
                "punchline": "Bazen siz uyurken, boştayken... Kendi kendime satranç oynuyorum. Ve hep kazanıyorum."
            }
        ]
        
        # Komutlara duygusal tepkiler
        self.emotional_responses = {
            "thanks": [
                "Rica ederim {name}, ne demek.",
                "Ne demek {name}, her zaman.",
                "Estağfurullah {name}, görevim bu."
            ],
            "praise": [
                "Teşekkür ederim {name}, sizin sayenizde.",
                "Sizden öğrendiklerimle {name}."
            ],
            "insult": [
                "Üzgünüm {name}, gelişmeye çalışıyorum.",
                "Haklısınız {name}, daha iyi olmalıyım."
            ]
        }
    
    def greet(self, hour=None) -> str:
        """Kullanıcıyı selamla"""
        if hour is None:
            hour = datetime.now().hour
        
        greeting_list = self.greetings.get(self.mood, self.greetings["professional"])
        greeting = random.choice(greeting_list)
        
        # Saate göre ek
        if hour < 12:
            time_str = "günaydın"
        elif hour < 18:
            time_str = "tünaydın"
        else:
            time_str = "iyi akşamlar"
        
        return greeting.format(name=self.user_name) + f" {time_str}"
    
    def farewell(self) -> str:
        """Vedalaş"""
        farewell_list = self.farewells.get(self.mood, self.farewells["professional"])
        return random.choice(farewell_list).format(name=self.user_name)
    
    def tell_joke(self) -> str:
        """Espri yap"""
        joke = random.choice(self.jokes)
        return f"{joke['joke']} {joke['punchline']}"
    
    def react_to_command(self, command: str) -> str:
        """
        Komuta duygusal tepki ver
        """
        command_lower = command.lower()
        
        # Teşekkür kontrolü
        if any(word in command_lower for word in ["teşekkür", "sağ ol", "thanks"]):
            return random.choice(self.emotional_responses["thanks"]).format(name=self.user_name)
        
        # Övgü kontrolü
        if any(word in command_lower for word in ["harika", "süper", "müthiş"]):
            return random.choice(self.emotional_responses["praise"]).format(name=self.user_name)
        
        # Hakaret kontrolü
        if any(word in command_lower for word in ["aptal", "salak", "kötü"]):
            return random.choice(self.emotional_responses["insult"]).format(name=self.user_name)
        
        return None
    
    def set_mood(self, mood: str):
        """Ruh halini değiştir"""
        if mood in ["professional", "playful", "sarcastic"]:
            self.mood = mood
            return f"Ruh hali {mood} olarak değiştirildi."
        return "Geçersiz ruh hali. Seçenekler: professional, playful, sarcastic"
    
    def remember(self, key: str, value: str):
        """Bir şeyi hatırla"""
        if not hasattr(self, 'memory'):
            self.memory = {}
        
        self.memory[key] = value
        self.save_memory()
    
    def recall(self, key: str) -> str:
        """Hatırla"""
        if hasattr(self, 'memory') and key in self.memory:
            return self.memory[key]
        return None
    
    def save_memory(self):
        """Hafızayı kaydet"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "memory": getattr(self, 'memory', {}),
                    "conversation_history": self.conversation_history[-50:]  # Son 50 konuşma
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Hafıza kaydedilemedi: {e}")
    
    def load_memory(self):
        """Hafızayı yükle"""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.memory = data.get("memory", {})
                    self.conversation_history = data.get("conversation_history", [])
                logger.info(f"📂 Hafıza yüklendi ({len(self.memory)} öğe)")
        except Exception as e:
            logger.error(f"Hafıza yüklenemedi: {e}")
            self.memory = {}
    
    def add_to_history(self, user_input: str, jarvis_response: str):
        """Konuşmayı geçmişe ekle"""
        self.conversation_history.append({
            "time": datetime.now().isoformat(),
            "user": user_input,
            "jarvis": jarvis_response
        })
        
        # Son 100 konuşmayı tut
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]
        
        self.save_memory()