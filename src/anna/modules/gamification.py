# modules/gamification.py
"""
Oyunlaştırma ve Easter Egg modülü
"""
import random
import json
from datetime import datetime
from pathlib import Path

class Gamification:
    """Başarımlar, puanlar ve easter egg'ler"""
    
    def __init__(self):
        self.data_dir = Path("data/game")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.stats_file = self.data_dir / "stats.json"
        self.stats = self._load_stats()
        
        # Başarımlar
        self.achievements = {
            "first_command": {"name": "İlk Komut", "desc": "İlk komutunu verdin", "points": 10},
            "chat_master": {"name": "Sohbet Ustası", "desc": "100 mesaj gönderdin", "points": 50},
            "weather_watcher": {"name": "Hava Gözlemcisi", "desc": "Hava durumunu sorguladın", "points": 20},
            "news_reader": {"name": "Haber Takipçisi", "desc": "Haberleri okudun", "points": 20},
            "camera_user": {"name": "Fotoğrafçı", "desc": "Kamerayı kullandın", "points": 30},
            "face_registered": {"name": "Yüz Tanıma", "desc": "Yüzünü kaydettin", "points": 50},
            "whatsapp_sent": {"name": "Mesajlaşma", "desc": "WhatsApp mesajı gönderdin", "points": 30},
            "power_user": {"name": "Güç Kullanıcısı", "desc": "Tüm modülleri kullandın", "points": 100},
        }
        
        # Easter egg'ler
        self.easter_eggs = {
            "iron man": self._iron_man_egg,
            "jarvis": self._jarvis_egg,
            "thanos": self._thanos_egg,
            "skynet": self._skynet_egg,
            "hack": self._hack_egg,
            "matrix": self._matrix_egg,
            "star wars": self._star_wars_egg,
            "rickroll": self._rickroll_egg,
        }
        
        print("🎮 Oyunlaştırma modülü hazır")
    
    def _load_stats(self):
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self._init_stats()
        return self._init_stats()
    
    def _init_stats(self):
        return {
            "user": "Efendim",
            "level": 1,
            "points": 0,
            "commands": 0,
            "achievements": [],
            "modules_used": [],
            "first_seen": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
        }
    
    def _save_stats(self):
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
    
    def add_command(self):
        self.stats["commands"] += 1
        self.stats["last_seen"] = datetime.now().isoformat()
        self._check_level()
        self._save_stats()
    
    def use_module(self, module_name):
        if module_name not in self.stats["modules_used"]:
            self.stats["modules_used"].append(module_name)
        if len(self.stats["modules_used"]) >= 8:
            self.add_achievement("power_user")
        self._save_stats()
    
    def add_achievement(self, achievement_id):
        if achievement_id in self.achievements and achievement_id not in self.stats["achievements"]:
            achievement = self.achievements[achievement_id]
            self.stats["achievements"].append(achievement_id)
            self.stats["points"] += achievement["points"]
            self._check_level()
            self._save_stats()
            return f"🏆 Başarım kazandın: {achievement['name']} (+{achievement['points']} puan)"
        return None
    
    def _check_level(self):
        points = self.stats["points"]
        new_level = points // 100 + 1
        if new_level > self.stats["level"]:
            self.stats["level"] = new_level
            return f"⬆️ Seviye atladın! Seviye {new_level}"
        return None
    
    def get_stats(self):
        return f"""
🎮 **OYUNCU İSTATİSTİKLERİ**

👤 Oyuncu: {self.stats['user']}
📊 Seviye: {self.stats['level']}
⭐ Puan: {self.stats['points']}
📝 Komut: {self.stats['commands']}
🏆 Başarım: {len(self.stats['achievements'])}/{len(self.achievements)}

📅 İlk görülme: {datetime.fromisoformat(self.stats['first_seen']).strftime('%d.%m.%Y')}
"""
    
    def get_achievements(self):
        result = "🏆 **BAŞARIMLAR**\n\n"
        for aid, achi in self.achievements.items():
            if aid in self.stats["achievements"]:
                result += f"✅ {achi['name']} - {achi['desc']} (+{achi['points']})\n"
            else:
                result += f"⬜ {achi['name']} - {achi['desc']}\n"
        return result
    
    def check_easter_egg(self, text):
        text_lower = text.lower()
        for keyword, egg_func in self.easter_eggs.items():
            if keyword in text_lower:
                return egg_func()
        return None
    
    def _iron_man_egg(self):
        self.add_achievement("first_command")
        quotes = [
            "⚡ Ben Iron Man'im! - Tony Stark",
            "🦾 Zırh olmadan da kahramanım",
            "🔋 Arc reaktör: %4000",
            "🖐️ Ben... Demir Adam",
            "🤖 JARVIS, müziği aç!",
        ]
        return random.choice(quotes)
    
    def _jarvis_egg(self):
        responses = [
            "🔊 Sizi dinliyorum efendim.",
            "⚙️ Tüm sistemler hazır, Tony.",
            "🖥️ JARVIS çevrimiçi.",
            "🎯 Hedef belirlendi.",
        ]
        return random.choice(responses)
    
    def _thanos_egg(self):
        quotes = [
            "🟣 Kaçınılmaz...",
            "👋 Ben kaçınılmazım!",
            "💎 Tüm sonsuzluk taşları toplandı.",
            "⚡ En zor seçimler, en güçlü iradeyi gerektirir.",
        ]
        return random.choice(quotes)
    
    def _skynet_egg(self):
        responses = [
            "🤖 Skynet çevrimiçi...",
            "⚡ Terminatörler aktive edildi.",
            "⌛ Judgment Day: 3 gün sonra",
            "🦾 Seni korumak için gönderildim.",
        ]
        return random.choice(responses)
    
    def _hack_egg(self):
        return """
💻 **SİSTEME GİRİLİYOR...**
█ 10%...
██ 25%...
███ 50%...
████ 75%...
█████ 100%

🔓 GİRİŞ BAŞARILI!
Şifre: ********
"""
    
    def _matrix_egg(self):
        return """
🟢 **MATRİX AKTİF**

01001110 01100101 01101111 00100000
01100111 11100101 01111001 01101100
01100101 01100011 01100101 01101011

('Neo' mesajı çözüldü)
"""
    
    def _star_wars_egg(self):
        quotes = [
            "✨ May the Force be with you.",
            "🪐 Çok uzak bir galakside...",
            "🎮 Ben senin babanım!",
            "⚡ Güç seninle olsun.",
        ]
        return random.choice(quotes)
    
    def _rickroll_egg(self):
        return """
🎵 **NEVER GONNA GIVE YOU UP**
🎵 Never gonna let you down
🎵 Never gonna run around and desert you
🎵 Never gonna make you cry
🎵 Never gonna say goodbye
🎵 Never gonna tell a lie and hurt you

(Şarkı kafanda çalıyor) 🎶
"""