# src/modules/phone.py
"""
Telefon bilgileri - Batarya, depolama, şarj, sensörler
"""

import psutil
import platform
import os
from datetime import datetime


class PhoneInfo:
    """Telefon donanım bilgileri"""
    
    def __init__(self):
        self.battery = None
        self.storage = None
    
    def get_battery_info(self) -> str:
        """Batarya bilgileri"""
        try:
            import psutil
            battery = psutil.sensors_battery()
            if battery:
                percent = battery.percent
                charging = "Şarj Oluyor" if battery.power_plugged else "Pil"
                
                # Kalan süre
                time_left = ""
                if not battery.power_plugged and battery.secsleft > 0 and battery.secsleft != -1:
                    hours = battery.secsleft // 3600
                    minutes = (battery.secsleft % 3600) // 60
                    time_left = f" ({hours} saat {minutes} dk kaldı)"
                elif battery.secsleft == -1:
                    time_left = " (Hesaplanamıyor)"
                
                # Şarj durumu emojisi
                emoji = "🔋" if percent > 20 else "⚠️"
                if percent > 80:
                    emoji = "⚡"
                
                return f"""{emoji} **Batarya Bilgileri**

Seviye: %{percent}
Durum: {charging}{time_left}"""
            else:
                return "❌ Batarya bilgisi alınamadı"
        except:
            return "❌ Batarya bilgisi alınamadı"
    
    def get_storage_info(self) -> str:
        """Depolama bilgileri"""
        try:
            disk = psutil.disk_usage('/')
            
            total = disk.total / (1024**3)
            used = disk.used / (1024**3)
            free = disk.free / (1024**3)
            percent = disk.percent
            
            # Renkli uyarı
            warning = "⚠️" if percent > 90 else "✅"
            
            return f"""💾 **Depolama Bilgileri**

{warning} Toplam: {total:.1f} GB
📊 Kullanılan: {used:.1f} GB (%{percent})
📦 Boş: {free:.1f} GB"""
        except:
            return "❌ Depolama bilgisi alınamadı"
    
    def get_ram_info(self) -> str:
        """RAM bilgileri"""
        try:
            memory = psutil.virtual_memory()
            
            total = memory.total / (1024**3)
            available = memory.available / (1024**3)
            used = memory.used / (1024**3)
            percent = memory.percent
            
            return f"""🧠 **RAM Bilgileri**

Toplam: {total:.1f} GB
Kullanılan: {used:.1f} GB (%{percent})
Boş: {available:.1f} GB"""
        except:
            return "❌ RAM bilgisi alınamadı"
    
    def get_cpu_info(self) -> str:
        """CPU bilgileri"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            freq_info = f"{cpu_freq.current:.0f} MHz" if cpu_freq else "Bilinmiyor"
            
            return f"""⚙️ **İşlemci Bilgileri**

Kullanım: %{cpu_percent}
Çekirdek: {cpu_count}
Frekans: {freq_info}"""
        except:
            return "❌ CPU bilgisi alınamadı"
    
    def get_system_info(self) -> str:
        """Sistem bilgileri"""
        import platform
        
        system = platform.system()
        release = platform.release()
        version = platform.version()
        machine = platform.machine()
        processor = platform.processer() or "Bilinmiyor"
        
        # Android mi kontrol et
        is_android = 'android' in system.lower() or 'linux' in system.lower()
        device_emoji = "📱" if is_android else "💻"
        
        return f"""{device_emoji} **Cihaz Bilgileri**

İşletim Sistemi: {system} {release}
İşlemci: {processor}
Mimari: {machine}
Versiyon: {version[:30]}..."""
    
    def get_all_info(self) -> str:
        """Tüm bilgileri getir"""
        return f"""
{self.get_battery_info()}

{self.get_storage_info()}

{self.get_ram_info()}

{self.get_cpu_info()}

{self.get_system_info()}
"""