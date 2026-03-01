# src/modules/reminders.py - ANDROID UYUMLU
"""
Hatırlatıcılar - Yerel bildirimler
"""

import json
import time
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
import threading

# Android tespiti
IS_ANDROID = 'android' in sys.platform or 'ANDROID_ARGUMENT' in os.environ

# Bildirimler
if IS_ANDROID:
    try:
        from android import notification
        ANDROID_NOTIFICATION_AVAILABLE = True
    except:
        ANDROID_NOTIFICATION_AVAILABLE = False

try:
    from plyer import notification
    PLYER_AVAILABLE = True
except:
    PLYER_AVAILABLE = False


class ReminderManager:
    """Hatırlatıcı yönetimi"""
    
    def __init__(self):
        # Android'de depolama yolu farklı
        if IS_ANDROID:
            try:
                from android.storage import primary_external_storage_path
                base_path = Path(primary_external_storage_path()) / "ANNA" / "data"
                self.data_dir = base_path / "reminders"
            except:
                self.data_dir = Path("/storage/emulated/0/ANNA/data/reminders")
        else:
            self.data_dir = Path("data/reminders")
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.reminders_file = self.data_dir / "reminders.json"
        self.reminders = self._load_reminders()
        
        # Hatırlatıcı kontrol thread'i
        self.checking = True
        self.thread = threading.Thread(target=self._check_loop, daemon=True)
        self.thread.start()
    
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
        try:
            with open(self.reminders_file, 'w', encoding='utf-8') as f:
                json.dump(self.reminders, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def _check_loop(self):
        """Hatırlatıcı kontrol döngüsü"""
        while self.checking:
            now = datetime.now()
            
            for reminder in self.reminders:
                if not reminder.get('notified', False):
                    try:
                        reminder_time = datetime.fromisoformat(reminder['time'])
                        
                        if now >= reminder_time:
                            self._show_notification(reminder)
                            reminder['notified'] = True
                            self._save_reminders()
                    except:
                        pass
            
            time.sleep(10)
    
    def _show_notification(self, reminder):
        """Bildirim göster"""
        
        # Android bildirimi
        if IS_ANDROID and ANDROID_NOTIFICATION_AVAILABLE:
            try:
                notification.notify(
                    title=reminder['title'],
                    message=reminder['message'],
                    id=reminder['id']
                )
            except:
                pass
        
        # Plyer bildirimi
        elif PLYER_AVAILABLE:
            try:
                notification.notify(
                    title=f"⏰ {reminder['title']}",
                    message=reminder['message'],
                    timeout=5
                )
            except:
                pass
        
        # Konsol bildirimi (her zaman)
        print(f"\n⏰ HATIRLATICI: {reminder['title']} - {reminder['message']}")
    
    def add_reminder(self, title: str, message: str, minutes: int) -> str:
        """Hatırlatıcı ekle"""
        reminder_time = datetime.now() + timedelta(minutes=minutes)
        
        reminder = {
            'id': len(self.reminders) + 1,
            'title': title,
            'message': message,
            'time': reminder_time.isoformat(),
            'minutes': minutes,
            'notified': False,
            'created': datetime.now().isoformat()
        }
        
        self.reminders.append(reminder)
        self._save_reminders()
        
        return f"⏰ {minutes} dakika sonra hatırlatıcı kuruldu: {title}"
    
    def list_reminders(self) -> str:
        """Hatırlatıcıları listele"""
        active = [r for r in self.reminders if not r.get('notified', False)]
        
        if not active:
            return "📭 Aktif hatırlatıcı yok"
        
        result = "⏰ **AKTİF HATIRLATICILAR**\n\n"
        for r in active:
            try:
                reminder_time = datetime.fromisoformat(r['time'])
                remaining = reminder_time - datetime.now()
                minutes = int(remaining.total_seconds() / 60)
                if minutes > 0:
                    result += f"• {r['title']}: {minutes} dakika sonra\n"
                else:
                    result += f"• {r['title']}: şimdi\n"
            except:
                result += f"• {r['title']}\n"
        
        return result
    
    def delete_reminder(self, reminder_id: int) -> str:
        """Hatırlatıcı sil"""
        for i, r in enumerate(self.reminders):
            if r['id'] == reminder_id:
                title = r['title']
                self.reminders.pop(i)
                self._save_reminders()
                return f"✅ Hatırlatıcı silindi: {title}"
        
        return "❌ Hatırlatıcı bulunamadı"
    
    def clear_all(self):
        """Tüm hatırlatıcıları temizle"""
        self.reminders = []
        self._save_reminders()
        print("🧹 Tüm hatırlatıcılar temizlendi")