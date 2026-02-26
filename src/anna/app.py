# ANNA_Mobil/src/anna/app.py
"""
A.N.N.A Mobil - BeeWare/Toga ile
- Sesli komut
- Sohbet asistanı
- QR kod okuma
- Günlük bildirimler
"""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import threading
import time
from datetime import datetime

# Mevcut modülleri import et
from .core.voice_engine import VoiceEngine
from .core.ai_engine import AIEngine
from .config.settings import Config

class AnnaMobile(toga.App):
    def startup(self):
        """Ana pencereyi oluştur"""
        
        # Sistemleri başlat
        self.config = Config()
        self.voice = VoiceEngine()
        self.ai = AIEngine(self.config)
        self.user = "Efendim"
        
        # Ana kutu
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        # ----- ÜST BAR -----
        header_box = toga.Box(style=Pack(direction=ROW, padding=5))
        
        icon_label = toga.Label("🤖", style=Pack(font_size=24, padding_right=5))
        title_label = toga.Label("A.N.N.A", style=Pack(font_size=20, font_weight="bold"))
        
        header_box.add(icon_label)
        header_box.add(title_label)
        header_box.add(toga.Box(style=Pack(flex=1)))  # Boşluk
        
        # ----- İÇERİK ALANI -----
        self.notebook = toga.Tabbed(style=Pack(flex=1))
        
        # Ana Sayfa Sekmesi
        home_box = self._build_home_tab()
        self.notebook.add("Ana", home_box)
        
        # Konuşma Sekmesi
        voice_box = self._build_voice_tab()
        self.notebook.add("Konuş", voice_box)
        
        # QR/Tarama Sekmesi
        scan_box = self._build_scan_tab()
        self.notebook.add("Tarama", scan_box)
        
        # Profil Sekmesi
        profile_box = self._build_profile_tab()
        self.notebook.add("Profil", profile_box)
        
        # Ana kutuya ekle
        main_box.add(header_box)
        main_box.add(self.notebook)
        
        self.main_window = toga.MainWindow(title="A.N.N.A Mobil")
        self.main_window.content = main_box
        self.main_window.show()
    
    def _build_home_tab(self):
        box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        # Hoşgeldin mesajı
        welcome = toga.Label(
            f"Merhaba, {self.user} 👋",
            style=Pack(font_size=22, font_weight="bold", padding_bottom=10)
        )
        box.add(welcome)
        
        # Hava durumu
        weather_box = toga.Box(style=Pack(direction=ROW, padding=10, background_color="#2a2a2a"))
        weather_box.add(toga.Label("☀️", style=Pack(font_size=40, padding_right=10)))
        weather_box.add(toga.Label("İstanbul\n18°C", style=Pack(font_size=16)))
        
        box.add(weather_box)
        
        # Hatırlatıcı
        reminder_box = toga.Box(style=Pack(direction=ROW, padding=10, background_color="#1a1a2a"))
        reminder_box.add(toga.Label("📅", style=Pack(font_size=30, padding_right=10)))
        reminder_box.add(toga.Label("Süt almayı unutma!", style=Pack(font_size=14)))
        
        box.add(reminder_box)
        
        return box
    
    def _build_voice_tab(self):
        box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        self.chat_display = toga.MultilineTextInput(
            readonly=True,
            style=Pack(flex=1, padding_bottom=10)
        )
        box.add(self.chat_display)
        
        input_row = toga.Box(style=Pack(direction=ROW, padding=5))
        
        self.message_input = toga.TextInput(style=Pack(flex=1, padding_right=5))
        send_btn = toga.Button(
            "Gönder",
            on_press=self.send_message,
            style=Pack(padding=5)
        )
        mic_btn = toga.Button(
            "🎤",
            on_press=self.start_listening,
            style=Pack(padding=5)
        )
        
        input_row.add(self.message_input)
        input_row.add(send_btn)
        input_row.add(mic_btn)
        
        box.add(input_row)
        return box
    
    def _build_scan_tab(self):
        """QR Kod Tarama Sekmesi"""
        box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        # Başlık
        title = toga.Label(
            "📱 QR KOD TARAMA",
            style=Pack(font_size=18, font_weight="bold", padding_bottom=10)
        )
        box.add(title)
        
        # Kamera görüntüsü simülasyonu
        camera_frame = toga.Box(
            style=Pack(
                padding=20,
                background_color="#2a2a2a",
                height=200,
                alignment="center"
            )
        )
        camera_frame.add(toga.Label(
            "📷 Kamera görüntüsü burada olacak",
            style=Pack(color="#888888", text_align="center")
        ))
        box.add(camera_frame)
        
        # Kontrol butonları
        btn_row = toga.Box(style=Pack(direction=ROW, padding=10))
        
        scan_btn = toga.Button(
            "🔍 Tara",
            on_press=self.start_scan,
            style=Pack(flex=1, padding_right=5)
        )
        
        btn_row.add(scan_btn)
        box.add(btn_row)
        
        # Sonuç alanı
        self.scan_result = toga.Label(
            "QR kod bekleniyor...",
            style=Pack(padding_top=10, color="#888888")
        )
        box.add(self.scan_result)
        
        return box
    
    def _build_profile_tab(self):
        box = toga.Box(style=Pack(direction=COLUMN, padding=10, alignment="center"))
        
        box.add(toga.Label("👤", style=Pack(font_size=60, padding=10)))
        box.add(toga.Label(self.user, style=Pack(font_size=20, font_weight="bold")))
        box.add(toga.Label("Premium Üye", style=Pack(color="#888888", padding_bottom=20)))
        
        # İstatistikler
        stats_box = toga.Box(style=Pack(direction=ROW, padding=10))
        stats_box.add(toga.Label("📊 127 konuşma", style=Pack(flex=1)))
        box.add(stats_box)
        
        # Ayarlar butonu
        settings_btn = toga.Button(
            "⚙️ Ayarlar",
            on_press=self.show_settings,
            style=Pack(padding=5, width=200)
        )
        box.add(settings_btn)
        
        # Çıkış butonu
        logout_btn = toga.Button(
            "🚪 Çıkış",
            on_press=self.logout,
            style=Pack(padding=5, width=200)
        )
        box.add(logout_btn)
        
        return box
    
    # ========== FONKSİYONLAR ==========
    
    def send_message(self, widget):
        msg = self.message_input.value
        if msg:
            self.chat_display.value += f"Sen: {msg}\n"
            response = self.ai.cevapla(msg)
            self.chat_display.value += f"A.N.N.A: {response}\n\n"
            self.message_input.value = ""
            self.voice.konus(response)
    
    def start_listening(self, widget):
        threading.Thread(target=self._listen_thread, daemon=True).start()
    
    def _listen_thread(self):
        text = self.voice.dinle(timeout=5)
        if text:
            self.message_input.value = text
            self.send_message(None)
    
    def start_scan(self, widget):
        """QR tarama başlat"""
        self.scan_result.text = "🔍 Taranıyor..."
        # Gerçek tarama için pyzbar kullanılacak
        threading.Thread(target=self._scan_thread, daemon=True).start()
    
    def _scan_thread(self):
        time.sleep(2)  # Simülasyon
        self.scan_result.text = "✅ QR kod bulundu: https://github.com/westabdu/anna_mobile"
    
    def show_settings(self, widget):
        self.main_window.info_dialog("Ayarlar", "Ayarlar yakında...")
    
    def logout(self, widget):
        self.main_window.info_dialog("Çıkış", "Görüşmek üzere!")
        self.exit()

def main():
    return AnnaMobile("A.N.N.A Mobil", "com.annamobile")