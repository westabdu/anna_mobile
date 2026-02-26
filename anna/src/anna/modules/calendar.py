# modules/calendar.py
"""
Takvim ve hatırlatıcı modülü
"""
import json
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger

class CalendarManager:
    """Etkinlik ve hatırlatıcı yönetimi"""
    
    def __init__(self):
        self.data_dir = Path("data/calendar")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.events_file = self.data_dir / "events.json"
        self.reminders_file = self.data_dir / "reminders.json"
        self.events = self._load_events()
        self.reminders = self._load_reminders()
        self._start_reminder_thread()
        logger.info("📅 Takvim modülü hazır")
    
    def _load_events(self):
        """Etkinlikleri yükle"""
        if self.events_file.exists():
            try:
                with open(self.events_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_events(self):
        """Etkinlikleri kaydet"""
        with open(self.events_file, 'w', encoding='utf-8') as f:
            json.dump(self.events, f, indent=2, ensure_ascii=False)
    
    def _load_reminders(self):
        """Hatırlatıcıları yükle"""
        if self.reminders_file.exists():
            try:
                with open(self.reminders_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_reminders(self):
        """Hatırlatıcıları kaydet"""
        with open(self.reminders_file, 'w', encoding='utf-8') as f:
            json.dump(self.reminders, f, indent=2, ensure_ascii=False)
    
    def _start_reminder_thread(self):
        """Hatırlatıcı kontrol thread'ini başlat"""
        def check_reminders():
            while True:
                now = datetime.now()
                for reminder in self.reminders:
                    if not reminder.get("notified", False):
                        reminder_time = datetime.fromisoformat(reminder["time"])
                        if now >= reminder_time:
                            # Hatırlatma zamanı geldi
                            self._trigger_reminder(reminder)
                            reminder["notified"] = True
                            self._save_reminders()
                time.sleep(10)
        
        threading.Thread(target=check_reminders, daemon=True).start()
    
    def _trigger_reminder(self, reminder):
        """Hatırlatıcıyı tetikle"""
        # Bu fonksiyon main.py'den set edilecek
        if hasattr(self, 'callback'):
            self.callback(f"⏰ Hatırlatma: {reminder['title']}")
    
    def set_callback(self, callback):
        """Bildirim callback'ini ayarla"""
        self.callback = callback
    
    def add_event(self, title, date_str, time_str, description=""):
        """Etkinlik ekle"""
        try:
            event_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            event = {
                "id": len(self.events) + 1,
                "title": title,
                "datetime": event_time.isoformat(),
                "date": date_str,
                "time": time_str,
                "description": description,
                "created": datetime.now().isoformat()
            }
            self.events.append(event)
            self._save_events()
            return f"✅ Etkinlik eklendi: {title} ({date_str} {time_str})"
        except Exception as e:
            return f"❌ Etkinlik eklenemedi: {str(e)}"
    
    def add_reminder(self, title, minutes):
        """Hatırlatıcı ekle (dakika cinsinden)"""
        try:
            reminder_time = datetime.now() + timedelta(minutes=minutes)
            reminder = {
                "id": len(self.reminders) + 1,
                "title": title,
                "time": reminder_time.isoformat(),
                "minutes": minutes,
                "notified": False,
                "created": datetime.now().isoformat()
            }
            self.reminders.append(reminder)
            self._save_reminders()
            return f"✅ {minutes} dakika sonra hatırlatıcı kuruldu: {title}"
        except Exception as e:
            return f"❌ Hatırlatıcı eklenemedi: {str(e)}"
    
    def get_today_events(self):
        """Bugünkü etkinlikleri göster"""
        today = datetime.now().date()
        today_events = []
        
        for event in self.events:
            event_date = datetime.fromisoformat(event["datetime"]).date()
            if event_date == today:
                today_events.append(event)
        
        if not today_events:
            return "📅 Bugün hiç etkinliğin yok"
        
        result = "📅 **BUGÜNKÜ ETKİNLİKLER**\n"
        for event in today_events:
            result += f"• {event['time']} - {event['title']}\n"
        return result
    
    def get_week_events(self):
        """Haftalık etkinlikleri göster"""
        today = datetime.now().date()
        week_events = []
        
        for event in self.events:
            event_date = datetime.fromisoformat(event["datetime"]).date()
            if 0 <= (event_date - today).days <= 7:
                week_events.append(event)
        
        if not week_events:
            return "📅 Bu hafta hiç etkinliğin yok"
        
        result = "📅 **HAFTALIK ETKİNLİKLER**\n"
        for event in sorted(week_events, key=lambda x: x["datetime"]):
            event_date = datetime.fromisoformat(event["datetime"])
            result += f"• {event_date.strftime('%d %B')} - {event['title']}\n"
        return result
    
    def list_reminders(self):
        """Aktif hatırlatıcıları listele"""
        active = [r for r in self.reminders if not r.get("notified", False)]
        
        if not active:
            return "⏰ Aktif hatırlatıcı yok"
        
        result = "⏰ **AKTİF HATIRLATICILAR**\n"
        for reminder in active:
            reminder_time = datetime.fromisoformat(reminder["time"])
            remaining = reminder_time - datetime.now()
            minutes = int(remaining.total_seconds() / 60)
            result += f"• {reminder['title']} - {minutes} dakika sonra\n"
        return result