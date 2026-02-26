# ANNA_Mobil/src/anna/app.py
"""
A.N.N.A Mobil - BeeWare/Toga ile
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
from .modules.ar_system import ARSystem
from .config.settings import Config

class AnnaMobile(toga.App):
    def startup(self):
        """Ana pencereyi oluştur"""
        
        # Sistemleri başlat
        self.config = Config()
        self.voice = VoiceEngine()
        self.ai = AIEngine(self.config)
        self.ar = ARSystem()
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
        
        # ----- İÇERİK ALANI (Notebook ile sekmeler) -----
        self.notebook = toga.Tabbed(style=Pack(flex=1))
        
        # Ana Sayfa Sekmesi
        home_box = self._build_home_tab()
        self.notebook.add("Ana", home_box)
        
        # Konuşma Sekmesi
        voice_box = self._build_voice_tab()
        self.notebook.add("Konuş", voice_box)
        
        # AR Sekmesi
        ar_box = self._build_ar_tab()
        self.notebook.add("AR", ar_box)
        
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
    
    def _build_ar_tab(self):
        box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        # AR mod seçici
        self.ar_mode_select = toga.Selection(
            items=["Nesne Tanıma", "Yüz Tespiti", "El Tespiti", "QR Okuma", "OCR", "Renk Analizi"],
            on_select=self.change_ar_mode,
            style=Pack(padding_bottom=10)
        )
        box.add(self.ar_mode_select)
        
        # AR kontrol butonları
        btn_row = toga.Box(style=Pack(direction=ROW, padding=5))
        start_btn = toga.Button("▶️ Başlat", on_press=self.start_ar, style=Pack(flex=1, padding_right=5))
        stop_btn = toga.Button("⏹️ Durdur", on_press=self.stop_ar, style=Pack(flex=1))
        
        btn_row.add(start_btn)
        btn_row.add(stop_btn)
        box.add(btn_row)
        
        self.ar_status = toga.Label(
            "AR hazır",
            style=Pack(padding_top=10, color="#888888")
        )
        box.add(self.ar_status)
        
        return box
    
    def _build_profile_tab(self):
        box = toga.Box(style=Pack(direction=COLUMN, padding=10, alignment="center"))
        
        box.add(toga.Label("👤", style=Pack(font_size=60, padding=10)))
        box.add(toga.Label(self.user, style=Pack(font_size=20, font_weight="bold")))
        box.add(toga.Label("Premium Üye", style=Pack(color="#888888", padding_bottom=20)))
        
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
    
    def start_ar(self, widget):
        result = self.ar.start_camera()
        self.ar_status.text = f"🟢 {result}"
    
    def stop_ar(self, widget):
        result = self.ar.stop_camera()
        self.ar_status.text = f"🔴 {result}"
    
    def change_ar_mode(self, widget):
        mode_map = {
            "Nesne Tanıma": "objects",
            "Yüz Tespiti": "faces",
            "El Tespiti": "hands",
            "QR Okuma": "qr",
            "OCR": "ocr",
            "Renk Analizi": "color"
        }
        mode = mode_map[self.ar_mode_select.value]
        self.ar.set_mode(mode)
    
    def show_settings(self, widget):
        self.main_window.info_dialog("Ayarlar", "Ayarlar yakında...")
    
    def logout(self, widget):
        self.main_window.info_dialog("Çıkış", "Görüşmek üzere!")
        self.exit()

def main():
    return AnnaMobile("A.N.N.A Mobil", "com.annamobile")