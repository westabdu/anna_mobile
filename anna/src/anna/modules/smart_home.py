# modules/smart_home.py
"""
Akıllı ev kontrolü - ESP32 ile entegrasyon
"""
import threading
import time
import random
from loguru import logger

class SmartHome:
    """ESP32 ile akıllı ev cihazlarını kontrol et"""
    
    def __init__(self):
        self.devices = {
            "salon": {
                "light": False,
                "light_brightness": 100,
                "curtain": False,
                "temperature": 22,
                "humidity": 45
            },
            "yatak odası": {
                "light": False,
                "light_brightness": 60,
                "curtain": False,
                "temperature": 21,
                "humidity": 50
            },
            "mutfak": {
                "light": False,
                "light_brightness": 100,
                "curtain": False,
                "temperature": 23,
                "humidity": 55
            },
            "banyo": {
                "light": False,
                "light_brightness": 80,
                "fan": False,
                "temperature": 24,
                "humidity": 70
            }
        }
        
        # ESP32 bağlantısı (simülasyon)
        self.esp_connected = False
        self._connect_esp()
        logger.info("🏠 Akıllı ev modülü hazır")
    
    def _connect_esp(self):
        """ESP32'ye bağlan (gerçek uygulamada MQTT kullan)"""
        try:
            # import paho.mqtt.client as mqtt
            # self.client = mqtt.Client()
            # self.client.connect("192.168.1.100", 1883)
            self.esp_connected = True
            logger.success("✅ ESP32 bağlantısı kuruldu")
        except:
            self.esp_connected = False
            logger.warning("⚠️ ESP32 bağlantısı yok, simülasyon modu")
    
    def control_light(self, room, state=None):
        """Işığı kontrol et"""
        if room not in self.devices:
            return f"❌ {room} bulunamadı"
        
        if state is None:
            # Mevcut durumu değiştir
            self.devices[room]["light"] = not self.devices[room]["light"]
        else:
            self.devices[room]["light"] = state
        
        status = "açıldı" if self.devices[room]["light"] else "kapandı"
        
        # ESP32'ye komut gönder
        if self.esp_connected:
            # self.client.publish(f"home/{room}/light", "ON" if state else "OFF")
            pass
        
        return f"💡 {room} ışığı {status}"
    
    def set_light_brightness(self, room, brightness):
        """Işık parlaklığını ayarla (0-100)"""
        if room not in self.devices:
            return f"❌ {room} bulunamadı"
        
        brightness = max(0, min(100, brightness))
        self.devices[room]["light_brightness"] = brightness
        
        if self.esp_connected:
            # self.client.publish(f"home/{room}/brightness", str(brightness))
            pass
        
        return f"💡 {room} ışık parlaklığı %{brightness} olarak ayarlandı"
    
    def control_curtain(self, room, state):
        """Pencereyi aç/kapa"""
        if room not in self.devices or "curtain" not in self.devices[room]:
            return f"❌ {room} için perde kontrolü yok"
        
        self.devices[room]["curtain"] = state
        status = "açıldı" if state else "kapandı"
        
        return f"🪟 {room} perdesi {status}"
    
    def get_room_status(self, room):
        """Oda durumunu göster"""
        if room not in self.devices:
            return f"❌ {room} bulunamadı"
        
        d = self.devices[room]
        light_status = "🟢 Açık" if d["light"] else "⚫ Kapalı"
        
        result = f"🏠 **{room.upper()}**\n"
        result += f"💡 Işık: {light_status}\n"
        result += f"☀️ Parlaklık: %{d['light_brightness']}\n"
        
        if "curtain" in d:
            curtain_status = "🟢 Açık" if d["curtain"] else "⚫ Kapalı"
            result += f"🪟 Perde: {curtain_status}\n"
        
        if "fan" in d:
            fan_status = "🟢 Açık" if d["fan"] else "⚫ Kapalı"
            result += f"🌀 Fan: {fan_status}\n"
        
        result += f"🌡️ Sıcaklık: {d['temperature']}°C\n"
        result += f"💧 Nem: %{d['humidity']}"
        
        return result
    
    def get_all_status(self):
        """Tüm ev durumunu göster"""
        result = "🏠 **EV DURUMU**\n\n"
        for room in self.devices:
            d = self.devices[room]
            light_emoji = "🟢" if d["light"] else "⚫"
            result += f"{light_emoji} {room}: {d['temperature']}°C\n"
        return result
    
    def set_temperature(self, room, temp):
        """Sıcaklık ayarla (klima/termosat)"""
        if room not in self.devices:
            return f"❌ {room} bulunamadı"
        
        self.devices[room]["temperature"] = temp
        return f"🌡️ {room} sıcaklığı {temp}°C olarak ayarlandı"
    
    def scan_devices(self):
        """Yeni cihazları tara"""
        # ESP32'den yeni cihazları bul
        new_devices = ["ofis", "çocuk odası", "misafir odası"]
        for device in new_devices:
            if device not in self.devices:
                self.devices[device] = {
                    "light": False,
                    "light_brightness": 80,
                    "temperature": 22,
                    "humidity": 50
                }
        return f"🔍 {len(new_devices)} yeni cihaz bulundu"