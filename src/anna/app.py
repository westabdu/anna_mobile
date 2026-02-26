# ANNA_Mobil/src/anna/app.py
"""
A.N.N.A Mobil - BeeWare/Toga ile
- 🔐 Giriş sistemi
- 🎮 Tüm modüller entegre
- 📱 Android uyumlu
"""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
import threading
import time
from datetime import datetime
import hashlib

from anna.core.voice_engine import VoiceEngine
from anna.core.ai_engine import AIEngine
from anna.config.settings import Config

# Modüller
try:
    from anna.modules.calendar import CalendarManager
    CALENDAR_AVAILABLE = True
except:
    CALENDAR_AVAILABLE = False

try:
    from anna.modules.notes import NotesManager
    NOTES_AVAILABLE = True
except:
    NOTES_AVAILABLE = False

try:
    from anna.modules.gamification import Gamification
    GAME_AVAILABLE = True
except:
    GAME_AVAILABLE = False

try:
    from anna.modules.smart_home import SmartHome
    SMART_HOME_AVAILABLE = True
except:
    SMART_HOME_AVAILABLE = False

class LoginWindow(toga.Window):
    def __init__(self, on_success):
        super().__init__(title="A.N.N.A Giriş", size=(350, 450))
        self.on_success = on_success
        
        # GİRİŞ BİLGİLERİ (Kendi şifreni buraya yaz)
        self.USERNAME = "abdullah"
        self.PASSWORD_HASH = hashlib.sha256("ANNA2026".encode()).hexdigest()
        
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=20, alignment=CENTER))
        
        main_box.add(toga.Label("🔐", style=Pack(font_size=80, padding=10)))
        main_box.add(toga.Label("A.N.N.A Mobil", style=Pack(font_size=24, font_weight="bold", padding_bottom=20)))
        
        self.username_input = toga.TextInput(placeholder="Kullanıcı Adı", style=Pack(width=250, padding=5))
        main_box.add(self.username_input)
        
        self.password_input = toga.PasswordInput(placeholder="Şifre", style=Pack(width=250, padding=5))
        main_box.add(self.password_input)
        
        login_btn = toga.Button("GİRİŞ YAP", on_press=self.check_login, 
                               style=Pack(width=250, padding=10, background_color="#4facfe", color="white"))
        main_box.add(login_btn)
        
        self.error_label = toga.Label("", style=Pack(color="red", padding_top=10))
        main_box.add(self.error_label)
        
        self.content = main_box
    
    def check_login(self, widget):
        username = self.username_input.value.lower().strip()
        password = self.password_input.value
        
        if not username or not password:
            self.error_label.text = "❌ Kullanıcı adı ve şifre gerekli!"
            return
        
        if username == self.USERNAME and hashlib.sha256(password.encode()).hexdigest() == self.PASSWORD_HASH:
            self.close()
            self.on_success()
        else:
            self.error_label.text = "❌ Hatalı giriş!"
            self.password_input.value = ""

class AnnaMobile(toga.App):
    def startup(self):
        self.config = Config()
        self.voice = VoiceEngine()
        self.ai = AIEngine(self.config)
        self.user = "Efendim"
        
        # Modülleri başlat
        self.calendar = CalendarManager() if CALENDAR_AVAILABLE else None
        self.notes = NotesManager() if NOTES_AVAILABLE else None
        self.game = Gamification() if GAME_AVAILABLE else None
        self.smart_home = SmartHome() if SMART_HOME_AVAILABLE else None
        
        self.main_window = toga.MainWindow(title="A.N.N.A Mobil")
        self.show_login()
    
    def show_login(self):
        LoginWindow(self.show_main_app).show()
    
    def show_main_app(self):
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        # Üst Bar
        header = toga.Box(style=Pack(direction=ROW, padding=10))
        header.add(toga.Label("🤖", style=Pack(font_size=24)))
        header.add(toga.Label("A.N.N.A", style=Pack(font_size=20, font_weight="bold", padding_left=5)))
        header.add(toga.Box(style=Pack(flex=1)))
        header.add(toga.Label(datetime.now().strftime("%H:%M"), style=Pack(color="#888888")))
        main_box.add(header)
        
        # Sekmeler
        self.notebook = toga.Tabbed(style=Pack(flex=1))
        self.notebook.add("🏠 Ana", self._build_home_tab())
        self.notebook.add("💬 Sohbet", self._build_voice_tab())
        self.notebook.add("📋 Notlar", self._build_notes_tab())
        self.notebook.add("👤 Profil", self._build_profile_tab())
        
        main_box.add(self.notebook)
        self.main_window.content = main_box
        self.main_window.show()
    
    def _build_home_tab(self):
        box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        # Hava durumu
        weather = toga.Box(style=Pack(direction=ROW, padding=10, background_color="#2a2a3a"))
        weather.add(toga.Label("☀️", style=Pack(font_size=40, padding_right=10)))
        weather.add(toga.Label("İstanbul\n18°C", style=Pack(font_size=16)))
        box.add(weather)
        
        # Hatırlatıcı (Calendar varsa)
        if self.calendar:
            reminder = toga.Box(style=Pack(direction=ROW, padding=10, background_color="#1a1a2a", margin_top=10))
            reminder.add(toga.Label("📅", style=Pack(font_size=30, padding_right=10)))
            reminder.add(toga.Label("Bugün 3 etkinlik", style=Pack(font_size=14)))
            box.add(reminder)
        
        # Hızlı butonlar
        grid = toga.Box(style=Pack(direction=ROW, padding=10))
        grid.add(toga.Button("🎤", on_press=self.start_listening, style=Pack(flex=1, padding=10, margin_right=5)))
        grid.add(toga.Button("📷", on_press=lambda x: self._go_to_tab(2), style=Pack(flex=1, padding=10, margin_left=5)))
        box.add(grid)
        
        return box
    
    def _build_voice_tab(self):
        box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        self.chat_display = toga.MultilineTextInput(readonly=True, style=Pack(flex=1, padding_bottom=10))
        box.add(self.chat_display)
        
        input_row = toga.Box(style=Pack(direction=ROW, padding=5))
        self.message_input = toga.TextInput(style=Pack(flex=1, padding_right=5))
        input_row.add(self.message_input)
        input_row.add(toga.Button("Gönder", on_press=self.send_message, style=Pack(padding=5, background_color="#4facfe", color="white")))
        input_row.add(toga.Button("🎤", on_press=self.start_listening, style=Pack(padding=5, background_color="#a88bff", color="white")))
        
        box.add(input_row)
        return box
    
    def _build_notes_tab(self):
        box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        if not self.notes:
            box.add(toga.Label("📝 Notlar modülü yok", style=Pack(padding=20, color="#888888")))
            return box
        
        self.note_input = toga.TextInput(placeholder="Notunuz...", style=Pack(padding=5))
        box.add(self.note_input)
        
        btn_row = toga.Box(style=Pack(direction=ROW, padding=5))
        btn_row.add(toga.Button("💾 Kaydet", on_press=self.save_note, style=Pack(flex=1, padding=5, margin_right=5)))
        btn_row.add(toga.Button("📋 Listele", on_press=self.show_notes, style=Pack(flex=1, padding=5, margin_left=5)))
        box.add(btn_row)
        
        self.notes_display = toga.MultilineTextInput(readonly=True, style=Pack(flex=1, padding_top=10))
        box.add(self.notes_display)
        
        return box
    
    def _build_profile_tab(self):
        box = toga.Box(style=Pack(direction=COLUMN, padding=20, alignment=CENTER))
        
        box.add(toga.Label("👤", style=Pack(font_size=80, padding=10)))
        box.add(toga.Label(self.user, style=Pack(font_size=20, font_weight="bold")))
        
        if self.game:
            stats = self.game.get_stats()
            box.add(toga.Label(stats, style=Pack(padding=20, color="#888888", font_size=12)))
        
        box.add(toga.Button("🚪 Çıkış", on_press=self.logout, 
                           style=Pack(width=200, padding=10, margin_top=20, background_color="#ff4d4d", color="white")))
        
        return box
    
    # ========== FONKSİYONLAR ==========
    
    def _go_to_tab(self, index):
        self.notebook.current_tab = self.notebook.tabs[index]
    
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
    
    def save_note(self, widget):
        if self.notes and self.note_input.value:
            self.notes.add_note("Hızlı Not", self.note_input.value)
            self.note_input.value = ""
            self.show_notes(None)
    
    def show_notes(self, widget):
        if self.notes:
            self.notes_display.value = self.notes.list_notes()
    
    def logout(self, widget):
        self.main_window.close()
        self.show_login()

def main():
    return AnnaMobile("A.N.N.A Mobil", "com.annamobile")