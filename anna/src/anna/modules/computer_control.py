# modules/computer_control.py
import os
import subprocess
import pyautogui
import psutil
import platform
from datetime import datetime
from loguru import logger

class ComputerControl:
    """Bilgisayar kontrolü - uygulamalar, dosyalar, sistem"""
    
    def __init__(self):
        pyautogui.FAILSAFE = True
        self.system = platform.system()
        logger.info("💻 Bilgisayar kontrolü hazır")
    
    def open_application(self, app_name: str) -> str:
        """Uygulama aç - Gelişmiş versiyon"""
        apps = {
            # Windows uygulamaları
            "notepad": "notepad.exe",
            "hesap makinesi": "calc.exe",
            "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "firefox": "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
            "edge": "msedge.exe",
            "vscode": "code",
            "spotify": "spotify",
            "cmd": "cmd.exe",
            "powershell": "powershell.exe",
            "task manager": "taskmgr.exe",
            "explorer": "explorer.exe",
            "word": "WINWORD.EXE",
            "excel": "EXCEL.EXE",
            "ppt": "POWERPNT.EXE",
            "paint": "mspaint.exe",
            "notepad++": "notepad++.exe",
        }
        
        try:
            app_key = app_name.lower().strip()
            
            # Tam eşleşme kontrolü
            if app_key in apps:
                os.startfile(apps[app_key])
                return f"✅ {app_name} açılıyor..."
            
            # Kısmi eşleşme kontrolü
            for key, path in apps.items():
                if key in app_key or app_key in key:
                    os.startfile(path)
                    return f"✅ {app_name} açılıyor ({key})..."
            
            # Windows search ile dene
            pyautogui.hotkey('win')
            pyautogui.write(app_name)
            pyautogui.sleep(0.5)
            pyautogui.press('enter')
            return f"🔍 {app_name} aranıyor..."
                
        except Exception as e:
            logger.error(f"Uygulama açma hatası: {e}")
            return f"❌ {app_name} açılamadı: {str(e)}"
    
    def close_application(self, app_name: str) -> str:
        """Uygulama kapat - Gelişmiş versiyon"""
        try:
            closed_count = 0
            app_name_lower = app_name.lower()
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if app_name_lower in proc_name:
                        proc.terminate()
                        closed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if closed_count > 0:
                return f"✅ {closed_count} {app_name} uygulaması kapatılıyor..."
            else:
                return f"⚠️ {app_name} bulunamadı."
            
        except Exception as e:
            logger.error(f"Uygulama kapatma hatası: {e}")
            return f"❌ Kapatılamadı: {str(e)}"
    
    def take_screenshot(self, filename: str = None) -> str:
        """Ekran görüntüsü al - Gelişmiş versiyon"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            # Screenshots klasörünü kontrol et
            screenshots_dir = "data/screenshots"
            os.makedirs(screenshots_dir, exist_ok=True)
            
            filepath = os.path.join(screenshots_dir, filename)
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            
            logger.info(f"📸 Ekran görüntüsü kaydedildi: {filename}")
            return f"✅ Ekran görüntüsü kaydedildi: {filename}"
            
        except Exception as e:
            logger.error(f"Screenshot hatası: {e}")
            return f"❌ Ekran görüntüsü alınamadı: {str(e)}"
    
    def get_system_info(self) -> str:
        """Detaylı sistem bilgileri"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            cpu_info = f"CPU: %{cpu_percent} kullanım ({cpu_count} çekirdek)"
            if cpu_freq:
                cpu_info += f", {cpu_freq.current:.0f}MHz"
            
            # RAM
            ram = psutil.virtual_memory()
            ram_used_gb = ram.used / (1024**3)
            ram_total_gb = ram.total / (1024**3)
            ram_percent = ram.percent
            ram_info = f"RAM: {ram_used_gb:.1f}/{ram_total_gb:.1f} GB (%{ram_percent})"
            
            # Disk
            disk = psutil.disk_usage('/')
            disk_used_gb = disk.used / (1024**3)
            disk_total_gb = disk.total / (1024**3)
            disk_percent = disk.percent
            disk_info = f"Disk: {disk_used_gb:.1f}/{disk_total_gb:.1f} GB (%{disk_percent})"
            
            # İşletim sistemi
            os_info = f"OS: {platform.system()} {platform.release()}"
            
            # Boot zamanı
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            uptime_hours = uptime.total_seconds() / 3600
            uptime_info = f"Uptime: {uptime_hours:.1f} saat"
            
            return f"{cpu_info}\n{ram_info}\n{disk_info}\n{os_info}\n{uptime_info}"
            
        except Exception as e:
            logger.error(f"Sistem bilgisi hatası: {e}")
            return f"❌ Sistem bilgisi alınamadı: {str(e)}"
    
    def set_volume(self, level: int) -> str:
        """Ses seviyesini ayarla (0-100)"""
        try:
            level = max(0, min(100, level))
            
            if self.system == "Windows":
                try:
                    from ctypes import cast, POINTER
                    from comtypes import CLSCTX_ALL
                    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                    
                    devices = AudioUtilities.GetSpeakers()
                    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    volume = cast(interface, POINTER(IAudioEndpointVolume))
                    volume.SetMasterVolumeLevelScalar(level / 100, None)
                except:
                    # Alternatif Windows metodu
                    import win32api
                    import win32con
                    print(win32api.GetUserName())  # Kullanıcı adını yazdırır
                    win32api.SendMessage(0xFFFF, win32con.WM_APPCOMMAND, 0, 0xA0000 | level)
            
            elif self.system == "Darwin":  # macOS
                os.system(f"osascript -e 'set volume output volume {level}'")
            
            else:  # Linux
                os.system(f"amixer set Master {level}%")
            
            return f"✅ Ses seviyesi %{level} olarak ayarlandı."
            
        except Exception as e:
            logger.error(f"Ses ayarlama hatası: {e}")
            return f"❌ Ses ayarlanamadı: {str(e)}"
    
    def lock_screen(self) -> str:
        """Ekranı kilitle"""
        try:
            if self.system == "Windows":
                import ctypes
                ctypes.windll.user32.LockWorkStation()
            elif self.system == "Darwin":
                os.system("pmset displaysleepnow")
            else:
                os.system("gnome-screensaver-command -l")
            return "✅ Ekran kilitlendi."
        except Exception as e:
            return f"❌ Ekran kilitlenemedi: {str(e)}"
    
    def sleep_computer(self) -> str:
        """Bilgisayarı uyku moduna al"""
        try:
            if self.system == "Windows":
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            else:
                os.system("systemctl suspend")
            return "✅ Bilgisayar uyku moduna alınıyor..."
        except Exception as e:
            return f"❌ Uyku modu hatası: {str(e)}"
    
    def get_process_list(self) -> list:
        """Çalışan prosesleri listele"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu': proc.info['cpu_percent'],
                    'memory': proc.info['memory_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return sorted(processes, key=lambda x: x['cpu'], reverse=True)[:20]