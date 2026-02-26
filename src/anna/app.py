# ANNA_Mobil/src/anna/app.py
"""
A.N.N.A Mobil - BeeWare/Toga ile
- Gelişmiş GUI
- 🔐 Şifre korumalı giriş
- Sesli komut
- Sohbet asistanı
- QR kod okuma
- Günlük bildirimler
"""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
import threading
import time
from datetime import datetime
import hashlib

from .core.voice_engine import VoiceEngine
from .core.ai_engine import AIEngine
from .config.settings import Config

class LoginWindow(toga.Window):
    """Giriş Penceresi"""
    
    def __init__(self, on_success):
        super().__init__(title="A.N.N.A Giriş", size=(350, 450))
        self.on_success = on_success
        
        # GİRİŞ BİLGİLERİ (Burayı değiştir!)
        self.USERNAME = "abdullah"
        self.PASSWORD_HASH = hashlib.sha256("ANNA2026".encode()).hexdigest()
        
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=20, alignment=CENTER))
        
        # Logo
        logo = toga.Label("🔐", style=Pack(font_size=80, padding=10))
        main_box.add(logo)
        
        # Başlık
        title = toga.Label(
            "A.N.N.A Mobil",
            style=Pack(font_size=24, font_weight="bold", padding_bottom=20)
        )
        main_box.add(title)
        
        # Kullanıcı adı
        self.username_input = toga.TextInput(
            placeholder="Kullanıcı Adı",
            style=Pack(width=250, padding=5, font_size=14)
        )
        main_box.add(self.username_input)
        
        # Şifre
        self.password_input = toga.PasswordInput(
            placeholder="Şifre",
            style=Pack(width=250, padding=5, font_size=14)
        )
        main_box.add(self.password_input)
        
        # Giriş butonu
        login_btn = toga.Button(
            "GİRİŞ YAP",
            on_press=self.check_login,
            style=Pack(
                width=250,
                padding=10,
                background_color="#4facfe",
                color="white",
                font_weight="bold"
            )
        )
        main_box.add(login_btn)
        
        # Hata mesajı
        self.error_label = toga.Label(
            "",
            style=Pack(color="red", padding_top=10, font_size=12)
        )
        main_box.add(self.error_label)
        
        # Versiyon
        version = toga.Label(
            "v1.0.0",
            style=Pack(color="#888888", padding_top=20, font_size=10)
        )
        main_box.add(version)
        
        self.content = main_box
    
    def check_login(self, widget):
        """Giriş bilgilerini kontrol et"""
        username = self.username_input.value.lower().strip()
        password = self.password_input.value
        
        if not username or not password:
            self.error_label.text = "❌ Kullanıcı adı ve şifre gerekli!"
            return
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if username == self.USERNAME and password_hash == self.PASSWORD_HASH:
            self.close()
            self.on_success()
        else:
            self.error_label.text = "❌ Hatalı kullanıcı adı veya şifre!"
            self.password_input.value = ""

class AnnaMobile(toga.App):
    def startup(self):
        """Ana pencereyi oluştur"""
        
        # Sistemleri başlat
        self.config = Config()
        self.voice = VoiceEngine()
        self.ai = AIEngine(self.config)
        self.user = "Efendim"
        
        # Ana pencereyi oluştur
        self.main_window = toga.MainWindow(title="A.N.N.A Mobil")
        
        # Giriş penceresini göster
        self.show_login()
    
    def show_login(self):
        """Giriş penceresini göster"""
        login_window = LoginWindow(self.show_main_app)
        login_window.show()
    
    def show_main_app(self):
        """Ana uygulamayı göster"""
        
        # Ana kutu
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        # ----- ÜST BAR (Gelişmiş) -----
        header_box = toga.Box(style=Pack(direction=ROW, padding=10))
        
        # Logo ve başlık
        icon_label = toga.Label("🤖", style=Pack(font_size=28, padding_right=5))
        title_label = toga.Label("A.N.N.A", style=Pack(font_size=22, font_weight="bold"))
        
        header_box.add(icon_label)
        header_box.add(title_label)
        header_box.add(toga.Box(style=Pack(flex=1)))
        
        # Saat
        self.time_label = toga.Label(
            datetime.now().strftime("%H:%M"),
            style=Pack(color="#888888", font_size=14, padding_right=10)
        )
        header_box.add(self.time_label)
        
        # Pil simülasyonu
        battery_label = toga.Label("🔋 85%", style=Pack(color="#43e97b", font_size=12))
        header_box.add(battery_label)
        
        main_box.add(header_box)
        
        # ----- HOŞGELDİN KARTI -----
        welcome_box = toga.Box(
            style=Pack(
                direction=ROW,
                padding=15,
                background_color="#2a2a3a",
                margin_bottom=10
            )
        )
        welcome_box.add(toga.Label(
            f"👋 Hoş geldin, {self.user}",
            style=Pack(font_size=16, font_weight="bold")
        ))
        main_box.add(welcome_box)
        
        # ----- İÇERİK ALANI (Sekmeler) -----
        self.notebook = toga.Tabbed(style=Pack(flex=1))
        
        # Ana Sayfa Sekmesi
        home_box = self._build_home_tab()
        self.notebook.add("🏠 Ana", home_box)
        
        # Konuşma Sekmesi
        voice_box = self._build_voice_tab()
        self.notebook.add("💬 Sohbet", voice_box)
        
        # QR/Tarama Sekmesi
        scan_box = self._build_scan_tab()
        self.notebook.add("📷 Tarama", scan_box)
        
        # Profil Sekmesi
        profile_box = self._build_profile_tab()
        self.notebook.add("👤 Profil", profile_box)
        
        main_box.add(self.notebook)
        
        # Saat güncelleme thread'i
        self._update_time()
        
        self.main_window.content = main_box
        self.main_window.show()
    
    def _update_time(self):
        """Saati güncelle"""
        def update():
            while True:
                self.time_label.text = datetime.now().strftime("%H:%M")
                time.sleep(60)
        threading.Thread(target=update, daemon=True).start()
    
    def _build_home_tab(self):
        box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        # Hava durumu kartı
        weather_box = toga.Box(
            style=Pack(
                direction=ROW,
                padding=15,
                background_color="#2a2a3a",
                margin_bottom=10
            )
        )
        weather_box.add(toga.Label("☀️", style=Pack(font_size=40, padding_right=15)))
        
        weather_info = toga.Box(style=Pack(direction=COLUMN))
        weather_info.add(toga.Label("İstanbul", style=Pack(font_size=16)))
        weather_info.add(toga.Label("18°C / 64°F", style=Pack(color="#888888")))
        
        weather_box.add(weather_info)
        weather_box.add(toga.Box(style=Pack(flex=1)))
        weather_box.add(toga.Label("Hissedilen 16°C", style=Pack(color="#888888", font_size=12)))
        
        box.add(weather_box)
        
        # Hatırlatıcı kartı
        reminder_box = toga.Box(
            style=Pack(
                direction=ROW,
                padding=15,
                background_color="#1a1a2a",
                margin_bottom=10
            )
        )
        reminder_box.add(toga.Label("📅", style=Pack(font_size=30, padding_right=15)))
        
        reminder_info = toga.Box(style=Pack(direction=COLUMN))
        reminder_info.add(toga.Label("Bugün", style=Pack(font_size=14, color="#ff9a9e")))
        reminder_info.add(toga.Label("Süt almayı unutma!", style=Pack(font_size=16)))
        
        reminder_box.add(reminder_info)
        box.add(reminder_box)
        
        # Hızlı işlemler
        quick_label = toga.Label("Hızlı İşlemler", style=Pack(font_size=16, padding_bottom=10))
        box.add(quick_label)
        
        quick_grid = toga.Box(style=Pack(direction=ROW, padding=5))
        
        # Mikrofon butonu
        mic_btn = toga.Button(
            "🎤",
            on_press=self.start_listening,
            style=Pack(flex=1, padding=10, margin_right=5)
        )
        quick_grid.add(mic_btn)
        
        # QR butonu
        qr_btn = toga.Button(
            "📷",
            on_press=self.go_to_scan_tab,
            style=Pack(flex=1, padding=10, margin_left=5)
        )
        quick_grid.add(qr_btn)
        
        box.add(quick_grid)
        
        return box
    
    def _build_voice_tab(self):
        box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        # Sohbet geçmişi
        self.chat_display = toga.MultilineTextInput(
            readonly=True,
            style=Pack(flex=1, padding_bottom=10)
        )
        box.add(self.chat_display)
        
        # Giriş alanı
        input_box = toga.Box(style=Pack(direction=ROW, padding=5))
        
        self.message_input = toga.TextInput(
            placeholder="Mesaj yaz...",
            style=Pack(flex=1, padding_right=5)
        )
        
        send_btn = toga.Button(
            "Gönder",
            on_press=self.send_message,
            style=Pack(padding=5, background_color="#4facfe", color="white")
        )
        
        mic_btn = toga.Button(
            "🎤",
            on_press=self.start_listening,
            style=Pack(padding=5, background_color="#a88bff", color="white")
        )
        
        input_box.add(self.message_input)
        input_box.add(send_btn)
        input_box.add(mic_btn)
        
        box.add(input_box)
        
        return box
    
    def _build_scan_tab(self):
        """QR Kod Tarama Sekmesi"""
        box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        # Kamera çerçevesi
        camera_frame = toga.Box(
            style=Pack(
                padding=20,
                background_color="#2a2a3a",
                height=250,
                alignment=CENTER
            )
        )
        camera_frame.add(toga.Label(
            "📷 Kamera görüntüsü",
            style=Pack(color="#888888", text_align="center", font_size=14)
        ))
        box.add(camera_frame)
        
        # Butonlar
        btn_box = toga.Box(style=Pack(direction=ROW, padding=10))
        
        scan_btn = toga.Button(
            "🔍 Tara",
            on_press=self.start_scan,
            style=Pack(flex=1, padding=10, background_color="#43e97b", color="white")
        )
        btn_box.add(scan_btn)
        
        box.add(btn_box)
        
        # Sonuç kartı
        result_box = toga.Box(
            style=Pack(
                padding=15,
                background_color="#1a1a2a",
                margin_top=10
            )
        )
        
        self.scan_result = toga.Label(
            "QR kod bekleniyor...",
            style=Pack(color="#888888")
        )
        result_box.add(self.scan_result)
        
        box.add(result_box)
        
        return box
    
    def _build_profile_tab(self):
        box = toga.Box(style=Pack(direction=COLUMN, padding=20, alignment=CENTER))
        
        # Avatar
        avatar = toga.Label(
            "👤",
            style=Pack(font_size=80, padding=10, background_color="#2a2a3a", width=120, height=120)
        )
        box.add(avatar)
        
        # Kullanıcı bilgileri
        box.add(toga.Label(
            self.user,
            style=Pack(font_size=22, font_weight="bold", padding_top=10)
        ))
        box.add(toga.Label(
            "Premium Üye",
            style=Pack(color="#888888", padding_bottom=20)
        ))
        
        # İstatistikler
        stats_box = toga.Box(style=Pack(direction=ROW, padding=10))
        stats_box.add(toga.Label("📊 127 konuşma", style=Pack(flex=1)))
        stats_box.add(toga.Label("⭐ 45 puan", style=Pack(flex=1)))
        box.add(stats_box)
        
        # Ayarlar butonu
        settings_btn = toga.Button(
            "⚙️ Ayarlar",
            on_press=self.show_settings,
            style=Pack(width=250, padding=10, margin_top=20)
        )
        box.add(settings_btn)
        
        # Çıkış butonu
        logout_btn = toga.Button(
            "🚪 Çıkış Yap",
            on_press=self.logout,
            style=Pack(width=250, padding=10, background_color="#ff4d4d", color="white")
        )
        box.add(logout_btn)
        
        return box
    
    # ========== FONKSİYONLAR ==========
    
    def go_to_scan_tab(self, widget):
        """Tarama sekmesine git"""
        self.notebook.current_tab = self.notebook.tabs[2]
    
    def send_message(self, widget):
        msg = self.message_input.value
        if msg:
            self.chat_display.value += f"👤 Sen: {msg}\n"
            response = self.ai.cevapla(msg)
            self.chat_display.value += f"🤖 A.N.N.A: {response}\n\n"
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
        threading.Thread(target=self._scan_thread, daemon=True).start()
    
    def _scan_thread(self):
        time.sleep(2)
        self.scan_result.text = "✅ https://github.com/westabdu/anna_mobile"
    
    def show_settings(self, widget):
        self.main_window.info_dialog("Ayarlar", "Ayarlar yakında...")
    
    def logout(self, widget):
        self.main_window.info_dialog("Çıkış", "Görüşmek üzere!")
        self.main_window.close()
        self.show_login()

def main():
    return AnnaMobile("A.N.N.A Mobil", "com.annamobile")