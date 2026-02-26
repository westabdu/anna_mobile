# modules/network.py
"""
Ağ izleme ve analiz modülü
"""
import os

import psutil
import socket
import subprocess
import speedtest
import requests
from datetime import datetime
from loguru import logger

class NetworkMonitor:
    """Ağ bağlantılarını ve hızını izle"""
    
    def __init__(self):
        self.hostname = socket.gethostname()
        self.local_ip = self._get_local_ip()
        self.public_ip = None
        logger.info("🌐 Ağ izleme modülü hazır")
    
    def _get_local_ip(self):
        """Yerel IP adresini al"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def _get_public_ip(self):
        """Genel IP adresini al"""
        try:
            response = requests.get('https://api.ipify.org', timeout=5)
            self.public_ip = response.text
            return self.public_ip
        except:
            return "Bağlantı yok"
    
    def get_network_info(self):
        """Ağ bilgilerini göster"""
        self._get_public_ip()
        
        return f"""
🌐 **AĞ BİLGİLERİ**

🖥️ Hostname: {self.hostname}
🏠 Yerel IP: {self.local_ip}
🌍 Genel IP: {self.public_ip or 'Bağlanıyor...'}

📡 Aktif Bağlantılar: {len(psutil.net_connections())}
"""
    
    def get_network_speed(self):
        """İnternet hızını test et"""
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            
            # İndirme hızı
            download_speed = st.download() / 1_000_000  # Mbps
            # Yükleme hızı
            upload_speed = st.upload() / 1_000_000  # Mbps
            # Ping
            ping = st.results.ping
            
            return f"""
🚀 **İNTERNET HIZI**

📥 İndirme: {download_speed:.2f} Mbps
📤 Yükleme: {upload_speed:.2f} Mbps
📶 Ping: {ping:.0f} ms
"""
        except Exception as e:
            return f"❌ Hız testi başarısız: {str(e)}"
    
    def get_network_io(self):
        """Ağ trafiğini göster"""
        counters = psutil.net_io_counters()
        
        bytes_sent = counters.bytes_sent / (1024**3)  # GB
        bytes_recv = counters.bytes_recv / (1024**3)  # GB
        packets_sent = counters.packets_sent
        packets_recv = counters.packets_recv
        
        return f"""
📊 **AĞ TRAFİĞİ**

📤 Gönderilen: {bytes_sent:.2f} GB ({packets_sent:,} paket)
📥 Alınan: {bytes_recv:.2f} GB ({packets_recv:,} paket)
"""
    
    def get_active_connections(self):
        """Aktif bağlantıları göster"""
        connections = psutil.net_connections()
        
        if not connections:
            return "🔌 Aktif bağlantı yok"
        
        # Portlara göre grupla
        ports = {}
        for conn in connections:
            if conn.raddr and conn.raddr.port:
                port = conn.raddr.port
                ports[port] = ports.get(port, 0) + 1
        
        result = "🔌 **AKTİF BAĞLANTILAR**\n"
        for port, count in sorted(ports.items())[:10]:
            result += f"• Port {port}: {count} bağlantı\n"
        
        return result
    
    def ping(self, host="8.8.8.8"):
        """Belirtilen hosta ping at"""
        try:
            param = '-n' if os.name == 'nt' else '-c'
            command = ['ping', param, '1', host]
            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.returncode == 0:
                return f"✅ {host} erişilebilir"
            else:
                return f"❌ {host} erişilemez"
        except:
            return f"❌ Ping başarısız"
    
    def scan_network(self):
        """Yerel ağı tara (basit)"""
        base_ip = '.'.join(self.local_ip.split('.')[:-1])
        active_hosts = []
        
        for i in range(1, 5):  # Sadece ilk 5 IP'yi dene
            ip = f"{base_ip}.{i}"
            response = self.ping(ip)
            if "✅" in response:
                active_hosts.append(ip)
        
        if active_hosts:
            return f"🔍 Ağda bulunan cihazlar:\n" + "\n".join(f"• {ip}" for ip in active_hosts)
        else:
            return "🔍 Ağda başka cihaz bulunamadı"
    
    def get_wifi_info(self):
        """WiFi bilgilerini göster (Windows)"""
        if os.name != 'nt':
            return "📡 WiFi bilgisi sadece Windows'ta gösterilebilir"
        
        try:
            result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], 
                                   capture_output=True, text=True)
            
            if "SSID" in result.stdout:
                lines = result.stdout.split('\n')
                ssid = ""
                signal = ""
                
                for line in lines:
                    if "SSID" in line and "BSSID" not in line:
                        ssid = line.split(':')[1].strip()
                    if "Signal" in line:
                        signal = line.split(':')[1].strip()
                
                return f"📡 Bağlı WiFi: {ssid} ({signal})"
            else:
                return "📡 WiFi bağlantısı yok"
        except:
            return "📡 WiFi bilgisi alınamadı"