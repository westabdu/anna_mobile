# src/modules/phone.py - ANDROID UYUMLU
"""
Telefon bilgileri - Batarya, depolama, şarj, sensörler
"""

import sys
import os
import platform
from datetime import datetime

# Android tespiti
IS_ANDROID = 'android' in sys.platform or 'ANDROID_ARGUMENT' in os.environ

# Android için özel modüller
if IS_ANDROID:
    try:
        from android import battery, storage
        ANDROID_API_AVAILABLE = True
    except:
        ANDROID_API_AVAILABLE = False

# Bilgisayar için psutil
try:
    import psutil
    PSUTIL_AVAILABLE = True
except:
    PSUTIL_AVAILABLE = False


class PhoneInfo:
    """Telefon donanım bilgileri"""
    
    def __init__(self):
        self.battery = None
        self.storage = None
        
        if IS_ANDROID:
            print("📱 Android modunda çalışıyor")
    
    def get_battery_info(self) -> str:
        """Batarya bilgileri"""
        
        # Android için
        if IS_ANDROID and ANDROID_API_AVAILABLE:
            try:
                percent = battery.get_level()
                charging = battery.is_charging()
                
                emoji = "🔋" if percent > 20 else "⚠️"
                if percent > 80:
                    emoji = "⚡"
                
                status = "Şarj Oluyor" if charging else "Pil"
                
                return f"""{emoji} **Batarya Bilgileri**

Seviye: %{percent}
Durum: {status}"""
            except:
                pass
        
        # Bilgisayar için (psutil)
        elif PSUTIL_AVAILABLE:
            try:
                battery = psutil.sensors_battery()
                if battery:
                    percent = battery.percent
                    charging = "Şarj Oluyor" if battery.power_plugged else "Pil"
                    
                    time_left = ""
                    if not battery.power_plugged and battery.secsleft > 0 and battery.secsleft != -1:
                        hours = battery.secsleft // 3600
                        minutes = (battery.secsleft % 3600) // 60
                        time_left = f" ({hours} saat {minutes} dk kaldı)"
                    
                    emoji = "🔋" if percent > 20 else "⚠️"
                    if percent > 80:
                        emoji = "⚡"
                    
                    return f"""{emoji} **Batarya Bilgileri**

Seviye: %{percent}
Durum: {charging}{time_left}"""
            except:
                pass
        
        return "❌ Batarya bilgisi alınamadı"
    
    def get_storage_info(self) -> str:
        """Depolama bilgileri"""
        
        # Android için
        if IS_ANDROID:
            try:
                # Android depolama bilgileri
                from android import storage
                stat = storage.get_storage_stats()
                
                total = stat['total'] / (1024**3)
                used = stat['used'] / (1024**3)
                free = stat['free'] / (1024**3)
                percent = (used / total) * 100 if total > 0 else 0
                
                warning = "⚠️" if percent > 90 else "✅"
                
                return f"""💾 **Depolama Bilgileri**

{warning} Toplam: {total:.1f} GB
📊 Kullanılan: {used:.1f} GB (%{percent:.1f})
📦 Boş: {free:.1f} GB"""
            except:
                pass
        
        # Bilgisayar için (psutil)
        elif PSUTIL_AVAILABLE:
            try:
                disk = psutil.disk_usage('/')
                
                total = disk.total / (1024**3)
                used = disk.used / (1024**3)
                free = disk.free / (1024**3)
                percent = disk.percent
                
                warning = "⚠️" if percent > 90 else "✅"
                
                return f"""💾 **Depolama Bilgileri**

{warning} Toplam: {total:.1f} GB
📊 Kullanılan: {used:.1f} GB (%{percent})
📦 Boş: {free:.1f} GB"""
            except:
                pass
        
        return "❌ Depolama bilgisi alınamadı"
    
    def get_ram_info(self) -> str:
        """RAM bilgileri"""
        
        # Android için
        if IS_ANDROID:
            try:
                from android import memory
                mem = memory.get_memory_info()
                
                total = mem['total'] / (1024**3)
                available = mem['available'] / (1024**3)
                used = total - available
                percent = (used / total) * 100
                
                return f"""🧠 **RAM Bilgileri**

Toplam: {total:.1f} GB
Kullanılan: {used:.1f} GB (%{percent:.1f})
Boş: {available:.1f} GB"""
            except:
                pass
        
        # Bilgisayar için (psutil)
        elif PSUTIL_AVAILABLE:
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
                pass
        
        return "❌ RAM bilgisi alınamadı"
    
    def get_cpu_info(self) -> str:
        """CPU bilgileri"""
        
        # Android için
        if IS_ANDROID:
            try:
                from android import cpu
                cpu_count = cpu.get_count()
                cpu_percent = cpu.get_usage()
                
                return f"""⚙️ **İşlemci Bilgileri**

Kullanım: %{cpu_percent}
Çekirdek: {cpu_count}"""
            except:
                pass
        
        # Bilgisayar için (psutil)
        elif PSUTIL_AVAILABLE:
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
                pass
        
        return "❌ CPU bilgisi alınamadı"
    
    def get_system_info(self) -> str:
        """Sistem bilgileri"""
        
        system = platform.system()
        release = platform.release()
        machine = platform.machine()
        
        device_emoji = "📱" if IS_ANDROID else "💻"
        os_name = "Android" if IS_ANDROID else system
        
        return f"""{device_emoji} **Cihaz Bilgileri**

İşletim Sistemi: {os_name} {release}
Mimari: {machine}"""
    
    def get_all_info(self) -> str:
        """Tüm bilgileri getir"""
        return f"""
{self.get_battery_info()}

{self.get_storage_info()}

{self.get_ram_info()}

{self.get_cpu_info()}

{self.get_system_info()}
"""