# main.py - A.N.N.A Mobile Ultimate (AR + Gelişmiş OCR)
"""
A.N.N.A Mobile Ultimate - Android için optimize edilmiş asistan
- 🔐 Gelişmiş giriş sistemi (şifre + biyometrik)
- 🤖 Yapay zeka (Gemini, Groq)
- 🌤️ Hava durumu
- 📱 Telefon bilgileri
- 👤 Rehber yönetimi
- 📸 Gelişmiş OCR + AR
- ⏰ Hatırlatıcılar
- 📰 Haberler
- 🎤 Sesli komut + wake word
- 🕶️ Artırılmış Gerçeklik (AR)
- 🎨 3 farklı mavi tema
"""

import flet as ft
import threading
import time
import random
from datetime import datetime
import os
from pathlib import Path

# ============================================
# MOBİL MODÜLLER
# ============================================
from src.auth.login import MobileAuth
from src.mobile_voice_enhanced import VoiceEngineEnhanced
from src.utils.theme import MobileTheme

# API modülleri
from src.api.gemini import GeminiAI
from src.api.groq import GroqAI
from src.api.weather import WeatherAPI
from src.api.news import NewsAPI

# Mobil özel modüller
from src.models.phone import PhoneInfo
from src.models.reminders import ReminderManager
from src.models.contacts import ContactsManager
from src.models.ocr import OCRManager
from src.models.ar_vision import ARVision  # YENİ AR MODÜLÜ

# ============================================
# TEMA AYARLARI
# ============================================
colors = MobileTheme.current

# ============================================
# GİRİŞ EKRANI (Aynı)
# ============================================
class LoginScreen(ft.Container):
    def __init__(self, page, on_success):
        super().__init__()
        self.page = page
        self.on_success = on_success
        self.auth = MobileAuth()
        
        self.expand = True
        self.bgcolor = colors["bg_primary"]
        self.alignment = ft.alignment.center
        self.padding = 20
        
        # Ana kart
        login_card = ft.Container(
            width=350,
            padding=30,
            bgcolor=colors["glass"],
            border_radius=30,
            border=ft.border.all(1, colors["primary"] + "40"),
            shadow=ft.BoxShadow(
                spread_radius=5,
                blur_radius=15,
                color=colors["primary"] + "30",
            ),
            animate=ft.animation.Animation(300),
        )
        
        # Logo
        logo = ft.Container(
            content=ft.Stack([
                ft.Container(
                    width=80,
                    height=80,
                    border_radius=40,
                    gradient=ft.RadialGradient(
                        colors=[colors["accent"] + "80", "transparent"],
                    ),
                ),
                ft.Container(
                    content=ft.Icon(ft.icons.AUTO_AWESOME, color=colors["accent_light"], size=50),
                    width=80,
                    height=80,
                    alignment=ft.alignment.center,
                ),
            ]),
            margin=ft.margin.only(bottom=10),
        )
        
        # Başlık
        title = ft.Text(
            "A.N.N.A",
            size=36,
            weight=ft.FontWeight.BOLD,
            color=colors["text"],
            text_align=ft.TextAlign.CENTER,
        )
        
        subtitle = ft.Text(
            "Mobil Asistan",
            size=14,
            color=colors["text_muted"],
            italic=True,
        )
        
        # Giriş metodu seçici
        self.method_dropdown = ft.Dropdown(
            width=280,
            options=[
                ft.dropdown.Option("password", "🔑 Şifre"),
                ft.dropdown.Option("pin", "🔢 PIN Kodu"),
                ft.dropdown.Option("pattern", "🎨 Desen Kilidi"),
                ft.dropdown.Option("biometric", "👆 Parmak İzi"),
            ],
            value="password",
            border_color=colors["primary"] + "80",
            bgcolor=colors["bg_secondary"],
            text_style=ft.TextStyle(color=colors["text"]),
        )
        
        # Şifre/PIN alanı
        self.password_field = ft.TextField(
            hint_text="Şifrenizi girin",
            password=True,
            can_reveal_password=True,
            border_color=colors["primary"] + "80",
            focused_border_color=colors["accent"],
            text_style=ft.TextStyle(color=colors["text"]),
            bgcolor=colors["bg_secondary"],
            border_radius=30,
            content_padding=15,
            width=280,
            cursor_color=colors["accent"],
            visible=True,
        )
        
        # Desen alanı
        self.pattern_field = ft.TextField(
            hint_text="Deseni girin (örn: 123456789)",
            border_color=colors["primary"] + "80",
            focused_border_color=colors["accent"],
            text_style=ft.TextStyle(color=colors["text"]),
            bgcolor=colors["bg_secondary"],
            border_radius=30,
            content_padding=15,
            width=280,
            cursor_color=colors["accent"],
            visible=False,
        )
        
        # Giriş butonu
        login_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.LOGIN, color=colors["text"], size=18),
                ft.Text("GİRİŞ YAP", color=colors["text"], weight=ft.FontWeight.BOLD, size=14),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
            width=280,
            padding=12,
            gradient=ft.LinearGradient(colors=[colors["primary"], colors["primary_light"]]),
            border_radius=30,
            animate=ft.animation.Animation(200),
            on_click=self.check_login,
        )
        
        # Biyometrik butonu
        self.bio_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.FINGERPRINT, color=colors["text"], size=18),
                ft.Text("Parmak İzi ile Giriş", color=colors["text"], weight=ft.FontWeight.BOLD, size=14),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
            width=280,
            padding=12,
            bgcolor="transparent",
            border=ft.border.all(1, colors["accent"] + "80"),
            border_radius=30,
            animate=ft.animation.Animation(200),
            on_click=self.check_biometric,
        )
        
        # Durum mesajı
        self.status_text = ft.Text("", color=colors["error"], size=12)
        
        # Loading
        self.loading = ft.ProgressRing(width=30, height=30, color=colors["accent"], visible=False)
        
        # Metod değiştirme
        def on_method_change(e):
            method = self.method_dropdown.value
            self.password_field.visible = (method in ["password", "pin"])
            self.pattern_field.visible = (method == "pattern")
            self.bio_btn.visible = (method == "biometric")
            self.update()
        
        self.method_dropdown.on_change = on_method_change
        
        # Layout
        login_card.content = ft.Column([
            logo,
            title,
            subtitle,
            ft.Container(height=20),
            self.method_dropdown,
            ft.Container(height=10),
            self.password_field,
            self.pattern_field,
            ft.Container(height=5),
            login_btn,
            ft.Container(height=5),
            self.bio_btn,
            ft.Container(height=15),
            self.status_text,
            ft.Container(height=5),
            self.loading,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0)
        
        self.content = ft.Container(content=login_card, alignment=ft.alignment.center)
    
    def check_login(self, e):
        method = self.method_dropdown.value
        
        if method == "password":
            if not self.password_field.value:
                self.status_text.value = "❌ Şifre girin!"
                self.status_text.update()
                return
            success, message = self.auth.check_password(self.password_field.value)
        
        elif method == "pin":
            if not self.password_field.value:
                self.status_text.value = "❌ PIN girin!"
                self.status_text.update()
                return
            success, message = self.auth.check_pin(self.password_field.value)
        
        elif method == "pattern":
            if not self.pattern_field.value:
                self.status_text.value = "❌ Desen girin!"
                self.status_text.update()
                return
            success, message = self.auth.check_pattern(self.pattern_field.value)
        
        elif method == "biometric":
            self.check_biometric(e)
            return
        
        else:
            success, message = False, "❌ Geçersiz metod"
        
        self.status_text.value = message
        self.status_text.color = colors["success"] if success else colors["error"]
        self.status_text.update()
        
        if success:
            self.loading.visible = True
            self.update()
            threading.Thread(target=lambda: (time.sleep(1), self.page.clean(), self.on_success()), daemon=True).start()
    
    def check_biometric(self, e):
        self.status_text.value = "🖐️ Parmak izi okutuluyor..."
        self.status_text.color = colors["info"]
        self.status_text.update()
        self.loading.visible = True
        self.update()
        
        def check():
            time.sleep(2)
            if self.auth.check_biometric():
                self.status_text.value = "✅ Giriş başarılı"
                self.status_text.update()
                time.sleep(0.5)
                self.page.clean()
                self.on_success()
            else:
                self.status_text.value = "❌ Parmak izi okunamadı"
                self.status_text.color = colors["error"]
                self.loading.visible = False
                self.update()
        
        threading.Thread(target=check, daemon=True).start()


# ============================================
# ANA UYGULAMA
# ============================================
def main(page: ft.Page):
    # Sayfa ayarları
    page.title = "A.N.N.A Mobile"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = colors["bg_primary"]
    page.padding = 0
    page.window_width = 400
    page.window_height = 800
    
    # ============================================
    # DURUM DEĞİŞKENLERİ
    # ============================================
    is_listening = False
    wake_active = False
    wave_active = False
    current_tab = 0
    current_theme = "dark"
    
    # ============================================
    # GİRİŞ EKRANINI GÖSTER
    # ============================================
    def show_login():
        page.clean()
        page.add(LoginScreen(page, lambda: show_main_app(is_listening, wake_active, wave_active, current_tab, current_theme)))
        page.update()
    
    # ============================================
    # ANA UYGULAMAYI BAŞLAT
    # ============================================
    def show_main_app(is_listening_param, wake_active_param, wave_active_param, current_tab_param, current_theme_param):
        # Parametreleri nonlocal olarak al
        nonlocal is_listening, wake_active, wave_active, current_tab, current_theme
        is_listening = is_listening_param
        wake_active = wake_active_param
        wave_active = wave_active_param
        current_tab = current_tab_param
        current_theme = current_theme_param
        
        # Core modülleri başlat
        voice = VoiceEngineEnhanced()
        voice.set_volume(0.8)
        voice.set_speed(1.2)
        voice.set_voice('tr-TR-EmelNeural')
        
        phone = PhoneInfo()
        reminders = ReminderManager()
        contacts = ContactsManager()
        ocr = OCRManager()
        weather_api = WeatherAPI()
        news_api = NewsAPI()
        ar_vision = ARVision()  # YENİ AR MODÜLÜ
        
        # AI seçimi
        groq = GroqAI()
        gemini = GeminiAI()
        
        if groq.available:
            ai = groq
            ai_name = "Groq AI (Çok Hızlı!)"
        elif gemini.available:
            ai = gemini
            ai_name = "Gemini AI"
        else:
            ai = None
            ai_name = "Yerel Mod (Sınırlı)"
        
        # UI bileşenleri
        chat_list = ft.ListView(spacing=10, auto_scroll=True, expand=True)
        
        # ============================================
        # FONKSİYONLAR
        # ============================================
        def add_message(sender: str, text: str, is_user: bool = True):
            color = colors["secondary"] if is_user else colors["primary"]
            icon = "👤" if is_user else "🤖"
            
            msg = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Text(icon, size=18),
                        width=36, height=36,
                        alignment=ft.alignment.center,
                        bgcolor=colors["glass"],
                        border_radius=18,
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(sender, size=11, color=color, weight=ft.FontWeight.BOLD),
                            ft.Text(text, color=colors["text"], size=12, selectable=True),
                        ]),
                        bgcolor=colors["glass"],
                        border_radius=15,
                        padding=10,
                        expand=True,
                    ),
                ], alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START),
                margin=ft.margin.only(bottom=5),
            )
            
            chat_list.controls.append(msg)
            page.update()
        
        # Ses dalgası animasyonu
        wave_bars = []
        for i in range(20):
            wave_bars.append(
                ft.Container(
                    width=3,
                    height=random.randint(10, 30),
                    bgcolor=colors["accent"],
                    border_radius=2,
                    animate=ft.animation.Animation(200),
                )
            )
        
        wave_container = ft.Row(wave_bars, alignment=ft.MainAxisAlignment.CENTER, spacing=3, visible=False)
        
        def animate_wave():
            nonlocal wave_active
            wave_active = True
            wave_container.visible = True
            page.update()
            
            def wave_loop():
                while wave_active:
                    for bar in wave_bars:
                        bar.height = random.randint(15, 40)
                        bar.bgcolor = random.choice([colors["accent"], colors["primary"], colors["secondary"]])
                    page.update()
                    time.sleep(0.1)
            
            threading.Thread(target=wave_loop, daemon=True).start()
        
        def stop_wave():
            nonlocal wave_active
            wave_active = False
            wave_container.visible = False
            page.update()
        
        # Wake word callback
        def on_wake_word(word):
            add_message("ANNA", f"🔊 '{word}' algılandı, dinliyorum...", is_user=False)
            voice.speak("Buyurun, dinliyorum.")
            animate_wave()
            
            def listen_thread():
                komut = voice.listen(timeout=5)
                stop_wave()
                if komut:
                    add_message("Sen", komut, is_user=True)
                    process_command(komut)
            
            threading.Thread(target=listen_thread, daemon=True).start()
        
        # Wake word toggle
        def toggle_wake(e):
            nonlocal wake_active
            if not wake_active:
                if voice.start_wake_word(on_wake_word):
                    wake_active = True
                    wake_btn.content.controls[0].name = ft.icons.MIC
                    wake_btn.content.controls[1].value = "Wake Açık"
                    wake_btn.border = ft.border.all(2, colors["success"])
                    add_message("ANNA", "Wake word aktif: 'Jarvis' deyin", is_user=False)
            else:
                voice.stop_wake_word()
                wake_active = False
                wake_btn.content.controls[0].name = ft.icons.MIC_OFF
                wake_btn.content.controls[1].value = "Wake Kapalı"
                wake_btn.border = ft.border.all(1, colors["error"] + "80")
                add_message("ANNA", "Wake word pasif", is_user=False)
            
            page.update()
        
        # Sesli komut butonu
        def start_listening(e):
            nonlocal is_listening
            if is_listening:
                return
            
            is_listening = True
            listen_btn.content.controls[0].name = ft.icons.MIC
            listen_btn.content.controls[1].value = "Dinliyor..."
            listen_btn.bgcolor = colors["primary"] + "40"
            animate_wave()
            page.update()
            
            def listen_thread():
                komut = voice.listen(timeout=5)
                stop_wave()
                
                def update_ui():
                    nonlocal is_listening
                    is_listening = False
                    listen_btn.content.controls[0].name = ft.icons.MIC_NONE
                    listen_btn.content.controls[1].value = "Sesli Komut"
                    listen_btn.bgcolor = "transparent"
                    page.update()
                    
                    if komut:
                        add_message("Sen", komut, is_user=True)
                        process_command(komut)
                
                page.run_thread(update_ui)
            
            threading.Thread(target=listen_thread, daemon=True).start()
        
        # Komut işleme
        def process_command(text: str):
            text_lower = text.lower()
            
            # AR komutları
            if "ar başlat" in text_lower or "kamera aç" in text_lower:
                result = ar_vision.start_camera()
                add_message("ANNA", result, is_user=False)
                voice.speak(result)
                change_tab(5)  # AR sekmesine geç
            
            elif "ar durdur" in text_lower or "kamera kapat" in text_lower:
                result = ar_vision.stop_camera()
                add_message("ANNA", result, is_user=False)
                voice.speak(result)
            
            elif "fotoğraf çek" in text_lower:
                result = ar_vision.take_photo()
                if isinstance(result, dict):
                    if result.get('scan', {}).get('text'):
                        add_message("ANNA", f"📝 Okunan: {result['scan']['text'][:100]}", is_user=False)
                    elif result.get('scan', {}).get('qr_codes'):
                        qr_text = result['scan']['qr_codes'][0]['data']
                        add_message("ANNA", f"📱 QR: {qr_text}", is_user=False)
                    else:
                        add_message("ANNA", "📸 Fotoğraf çekildi", is_user=False)
            
            # Hava durumu
            elif "hava" in text_lower:
                result = weather_api.get_weather()
                add_message("ANNA", result, is_user=False)
                voice.speak(result)
            
            # Haberler
            elif "haber" in text_lower:
                categories = {
                    'teknoloji': 'technology',
                    'spor': 'sports',
                    'ekonomi': 'business',
                    'sağlık': 'health',
                    'bilim': 'science',
                    'eğlence': 'entertainment'
                }
                
                kategori_bulundu = False
                for tr_kelime, en_kategori in categories.items():
                    if tr_kelime in text_lower:
                        result = news_api.get_headlines(category=en_kategori)
                        add_message("ANNA", result, is_user=False)
                        voice.speak(f"{tr_kelime} haberleri getiriliyor...")
                        kategori_bulundu = True
                        break
                
                if not kategori_bulundu:
                    result = news_api.get_headlines()
                    add_message("ANNA", result, is_user=False)
                    voice.speak("Güncel haberler getiriliyor...")
            
            # Telefon bilgileri
            elif "batarya" in text_lower:
                result = phone.get_battery_info()
                add_message("ANNA", result, is_user=False)
                voice.speak("Batarya bilgileri getiriliyor...")
            
            elif "depolama" in text_lower:
                result = phone.get_storage_info()
                add_message("ANNA", result, is_user=False)
                voice.speak("Depolama bilgileri getiriliyor...")
            
            # Rehber
            elif "rehber" in text_lower:
                result = contacts.format_contact_list()
                add_message("ANNA", result, is_user=False)
                voice.speak("Rehber listeleniyor...")
            
            # OCR (gelişmiş)
            elif "fotoğraf oku" in text_lower or "resim oku" in text_lower:
                add_message("ANNA", "📸 Kameradan fotoğraf çekiliyor...", is_user=False)
                voice.speak("Kameradan fotoğraf çekiyorum, lütfen bekleyin.")
                
                def ocr_thread():
                    result = ocr.camera_scan()
                    if result.get('success'):
                        add_message("ANNA", f"📝 {result['text'][:200]}", is_user=False)
                    else:
                        add_message("ANNA", "❌ Yazı okunamadı", is_user=False)
                
                threading.Thread(target=ocr_thread, daemon=True).start()
            
            # Hatırlatıcı
            elif "hatırlat" in text_lower:
                import re
                minutes = 5
                match = re.search(r'(\d+)\s*dakika', text_lower)
                if match:
                    minutes = int(match.group(1))
                
                message = text.replace("hatırlat", "").strip()
                if message:
                    result = reminders.add_reminder("Hatırlatıcı", message, minutes)
                    add_message("ANNA", result, is_user=False)
                    voice.speak(result)
            
            # Yardım
            elif "yardım" in text_lower:
                help_text = """🤖 **A.N.N.A Komutları**

🕶️ AR: 'kamera aç', 'fotoğraf çek'
🌤️ Hava durumu
📰 Haberler
📱 Telefon bilgisi
👤 Rehber
📸 OCR: 'fotoğraf oku'
⏰ Hatırlatıcı
💬 Sohbet"""
                add_message("ANNA", help_text, is_user=False)
                voice.speak("Size nasıl yardımcı olabilirim?")
            
            # AI sohbet
            else:
                if ai:
                    try:
                        response = ai.ask(text)
                        add_message("ANNA", response, is_user=False)
                        voice.speak(response)
                    except Exception as e:
                        error_msg = f"❌ AI hatası: {e}"
                        add_message("ANNA", error_msg, is_user=False)
                        voice.speak("Üzgünüm, şu anda cevap veremiyorum.")
                else:
                    response = "Merhaba! API anahtarlarınızı kontrol edin veya 'yardım' yazın."
                    add_message("ANNA", response, is_user=False)
                    voice.speak(response)
        
        # Mesaj gönderme
        def send_message(e):
            if not message_input.value:
                return
            
            msg = message_input.value
            message_input.value = ""
            page.update()
            
            add_message("Sen", msg, is_user=True)
            process_command(msg)
        
        # Tema değiştirici
        def change_theme(e):
            nonlocal current_theme
            if current_theme == "dark":
                current_theme = "ocean"
                MobileTheme.set_theme("ocean")
            elif current_theme == "ocean":
                current_theme = "ice"
                MobileTheme.set_theme("ice")
            else:
                current_theme = "dark"
                MobileTheme.set_theme("dark")
            
            globals()["colors"] = MobileTheme.current
            page.bgcolor = colors["bg_primary"]
            page.clean()
            show_main_app(is_listening, wake_active, wave_active, current_tab, current_theme)
        
        def change_theme_direct(theme):
            nonlocal current_theme
            current_theme = theme
            MobileTheme.set_theme(theme)
            globals()["colors"] = MobileTheme.current
            page.bgcolor = colors["bg_primary"]
            page.clean()
            show_main_app(is_listening, wake_active, wave_active, current_tab, current_theme)
        
        # Sekme değiştirici (AR SEKMESİ EKLENDİ)
        def change_tab(index):
            nonlocal current_tab
            current_tab = index
            
            if index == 0:
                content_area.content = build_chat_tab()
            elif index == 1:
                content_area.content = build_phone_tab()
            elif index == 2:
                content_area.content = build_weather_tab()
            elif index == 3:
                content_area.content = build_contacts_tab()
            elif index == 4:
                content_area.content = build_settings_tab()
            elif index == 5:  # YENİ AR SEKMESİ
                content_area.content = build_ar_tab()
            
            page.update()
        
        # ============================================
        # TAB İÇERİKLERİ
        # ============================================
        
        def build_chat_tab():
            return ft.Column([
                ft.Container(content=chat_list, expand=True),
            ], expand=True)
        
        def build_phone_tab():
            return ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Text("📱 TELEFON BİLGİLERİ", size=16, weight=ft.FontWeight.BOLD, color=colors["text"]),
                        ft.Divider(height=1, color=colors["primary"] + "40"),
                        ft.Container(height=10),
                        
                        ft.Container(
                            content=ft.Column([
                                ft.Row([ft.Icon(ft.icons.BATTERY_FULL, color=colors["success"]), ft.Text("Batarya", color=colors["text"], size=14)]),
                                ft.Text(phone.get_battery_info().replace("**", ""), color=colors["text_secondary"], size=12),
                            ]),
                            bgcolor=colors["glass"],
                            border_radius=15,
                            padding=15,
                            margin=ft.margin.only(bottom=10),
                            on_click=lambda _: show_detail_dialog("Batarya", phone.get_battery_info()),
                        ),
                        
                        ft.Container(
                            content=ft.Column([
                                ft.Row([ft.Icon(ft.icons.STORAGE, color=colors["primary"]), ft.Text("Depolama", color=colors["text"], size=14)]),
                                ft.Text(phone.get_storage_info().replace("**", ""), color=colors["text_secondary"], size=12),
                            ]),
                            bgcolor=colors["glass"],
                            border_radius=15,
                            padding=15,
                            margin=ft.margin.only(bottom=10),
                            on_click=lambda _: show_detail_dialog("Depolama", phone.get_storage_info()),
                        ),
                        
                        ft.Container(
                            content=ft.Column([
                                ft.Row([ft.Icon(ft.icons.MEMORY, color=colors["accent"]), ft.Text("RAM", color=colors["text"], size=14)]),
                                ft.Text(phone.get_ram_info().replace("**", ""), color=colors["text_secondary"], size=12),
                            ]),
                            bgcolor=colors["glass"],
                            border_radius=15,
                            padding=15,
                            margin=ft.margin.only(bottom=10),
                            on_click=lambda _: show_detail_dialog("RAM", phone.get_ram_info()),
                        ),
                        
                        ft.Container(
                            content=ft.Column([
                                ft.Row([ft.Icon(ft.icons.SPEED, color=colors["warning"]), ft.Text("İşlemci", color=colors["text"], size=14)]),
                                ft.Text(phone.get_cpu_info().replace("**", ""), color=colors["text_secondary"], size=12),
                            ]),
                            bgcolor=colors["glass"],
                            border_radius=15,
                            padding=15,
                            on_click=lambda _: show_detail_dialog("İşlemci", phone.get_cpu_info()),
                        ),
                    ]),
                    padding=10,
                )
            ], scroll=ft.ScrollMode.AUTO)
        
        def build_weather_tab():
            city_input = ft.TextField(
                hint_text="Şehir adı",
                border_color=colors["primary"] + "80",
                focused_border_color=colors["accent"],
                text_style=ft.TextStyle(color=colors["text"]),
                bgcolor=colors["bg_secondary"],
                border_radius=30,
                content_padding=15,
                expand=True,
            )
            
            weather_result = ft.Container(
                content=ft.Text("Hava durumu bilgisi burada görünecek", color=colors["text_muted"]),
                bgcolor=colors["glass"],
                border_radius=15,
                padding=15,
            )
            
            def get_weather(e):
                if city_input.value:
                    result = weather_api.get_weather(city_input.value)
                    weather_result.content = ft.Text(result, color=colors["text"])
                    page.update()
            
            return ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Text("🌤️ HAVA DURUMU", size=16, weight=ft.FontWeight.BOLD, color=colors["text"]),
                        ft.Divider(height=1, color=colors["primary"] + "40"),
                        ft.Container(height=10),
                        
                        ft.Row([
                            city_input,
                            ft.IconButton(
                                icon=ft.icons.SEARCH,
                                icon_color=colors["primary"],
                                on_click=get_weather,
                            ),
                        ]),
                        
                        ft.Container(height=10),
                        weather_result,
                    ]),
                    padding=10,
                )
            ], scroll=ft.ScrollMode.AUTO)
        
        def build_contacts_tab():
            search_input = ft.TextField(
                hint_text="Kişi ara...",
                border_color=colors["primary"] + "80",
                focused_border_color=colors["accent"],
                text_style=ft.TextStyle(color=colors["text"]),
                bgcolor=colors["bg_secondary"],
                border_radius=30,
                content_padding=15,
                expand=True,
            )
            
            contacts_list = ft.ListView(spacing=5, expand=True)
            
            def refresh_contacts():
                contacts_list.controls.clear()
                for c in contacts.get_all_contacts()[:10]:
                    fav = "⭐ " if c.get('favorite') else ""
                    contacts_list.controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Container(
                                    content=ft.Text(fav + c['name'][0].upper(), size=16, color=colors["text"]),
                                    width=40, height=40,
                                    alignment=ft.alignment.center,
                                    bgcolor=colors["primary"] + "40",
                                    border_radius=20,
                                ),
                                ft.Column([
                                    ft.Text(fav + c['name'], size=14, weight=ft.FontWeight.BOLD, color=colors["text"]),
                                    ft.Text(c['phone'], size=11, color=colors["text_muted"]),
                                ], spacing=2, expand=True),
                                ft.IconButton(
                                    icon=ft.icons.CALL,
                                    icon_color=colors["success"],
                                    on_click=lambda _, cid=c['id']: show_contact_dialog(cid),
                                ),
                            ]),
                            bgcolor=colors["glass"],
                            border_radius=10,
                            padding=10,
                            margin=ft.margin.only(bottom=5),
                        )
                    )
                page.update()
            
            def search_contacts(e):
                if search_input.value:
                    results = contacts.search_contacts(search_input.value)
                    contacts_list.controls.clear()
                    for c in results:
                        fav = "⭐ " if c.get('favorite') else ""
                        contacts_list.controls.append(
                            ft.Container(
                                content=ft.Row([
                                    ft.Container(
                                        content=ft.Text(fav + c['name'][0].upper(), size=16),
                                        width=40, height=40,
                                        alignment=ft.alignment.center,
                                        bgcolor=colors["primary"] + "40",
                                        border_radius=20,
                                    ),
                                    ft.Column([
                                        ft.Text(fav + c['name'], size=14, weight=ft.FontWeight.BOLD),
                                        ft.Text(c['phone'], size=11, color=colors["text_muted"]),
                                    ], spacing=2, expand=True),
                                ]),
                                bgcolor=colors["glass"],
                                border_radius=10,
                                padding=10,
                                margin=ft.margin.only(bottom=5),
                            )
                        )
                    page.update()
            
            refresh_contacts()
            
            return ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Text("👤 REHBER", size=16, weight=ft.FontWeight.BOLD, color=colors["text"]),
                        ft.Divider(height=1, color=colors["primary"] + "40"),
                        ft.Container(height=10),
                        
                        ft.Row([
                            search_input,
                            ft.IconButton(icon=ft.icons.SEARCH, icon_color=colors["primary"], on_click=search_contacts),
                        ]),
                        
                        ft.Container(height=10),
                        
                        ft.Row([
                            ft.Container(
                                content=ft.Text("📋 Tümü", color=colors["text"]),
                                bgcolor=colors["glass"], border_radius=15, padding=5,
                                on_click=lambda _: refresh_contacts(),
                            ),
                            ft.Container(width=5),
                            ft.Container(
                                content=ft.Text("⭐ Favoriler", color=colors["text"]),
                                bgcolor=colors["glass"], border_radius=15, padding=5,
                                on_click=lambda _: show_favorites(),
                            ),
                        ]),
                        
                        ft.Container(height=10),
                        contacts_list,
                    ]),
                    padding=10, expand=True,
                )
            ], expand=True)
        
        def build_settings_tab():
            return ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Text("⚙️ AYARLAR", size=16, weight=ft.FontWeight.BOLD, color=colors["text"]),
                        ft.Divider(height=1, color=colors["primary"] + "40"),
                        ft.Container(height=10),
                        
                        ft.Container(
                            content=ft.Column([
                                ft.Row([ft.Icon(ft.icons.COLOR_LENS, color=colors["accent"]), ft.Text("Tema", color=colors["text"], size=14)]),
                                ft.Row([
                                    ft.Container(content=ft.Text("🌙 Koyu", color=colors["text"], size=12), bgcolor=colors["glass"], border_radius=10, padding=5, on_click=lambda _: change_theme_direct("dark")),
                                    ft.Container(width=5),
                                    ft.Container(content=ft.Text("🌊 Okyanus", color=colors["text"], size=12), bgcolor=colors["glass"], border_radius=10, padding=5, on_click=lambda _: change_theme_direct("ocean")),
                                    ft.Container(width=5),
                                    ft.Container(content=ft.Text("❄️ Buz", color=colors["text"], size=12), bgcolor=colors["glass"], border_radius=10, padding=5, on_click=lambda _: change_theme_direct("ice")),
                                ]),
                            ]),
                            bgcolor=colors["glass"], border_radius=15, padding=15, margin=ft.margin.only(bottom=10),
                        ),
                        
                        ft.Container(
                            content=ft.Column([
                                ft.Row([ft.Icon(ft.icons.INFO, color=colors["primary"]), ft.Text("AI Modeli", color=colors["text"], size=14)]),
                                ft.Text(f"Kullanılan: {ai_name}", color=colors["text_secondary"], size=12),
                            ]),
                            bgcolor=colors["glass"], border_radius=15, padding=15, margin=ft.margin.only(bottom=10),
                        ),
                        
                        ft.Container(
                            content=ft.Column([
                                ft.Row([ft.Icon(ft.icons.NOTIFICATIONS, color=colors["warning"]), ft.Text("Hatırlatıcılar", color=colors["text"], size=14)]),
                                ft.Text(reminders.list_reminders().replace("**", ""), color=colors["text_secondary"], size=12),
                            ]),
                            bgcolor=colors["glass"], border_radius=15, padding=15, margin=ft.margin.only(bottom=10),
                        ),
                        
                        ft.Container(
                            content=ft.Column([
                                ft.Row([ft.Icon(ft.icons.DOCUMENT_SCANNER, color=colors["success"]), ft.Text("OCR", color=colors["text"], size=14)]),
                                ft.Text("Gelişmiş OCR ile fotoğraftan yazı oku", color=colors["text_secondary"], size=12),
                            ]),
                            bgcolor=colors["glass"], border_radius=15, padding=15,
                        ),
                    ]),
                    padding=10,
                )
            ], scroll=ft.ScrollMode.AUTO)
        
        # ============================================
        # YENİ AR TAB'I
        # ============================================
        
        def build_ar_tab():
            """AR ve Gelişmiş OCR tab'ı"""
            
            # Kamera görüntüsü placeholder
            camera_view = ft.Container(
                content=ft.Text("📷 Kamera görüntüsü burada olacak\n(AR aktif değil)", 
                               color=colors["text_muted"], size=12, text_align=ft.TextAlign.CENTER),
                bgcolor=colors["bg_secondary"],
                border_radius=15,
                height=250,
                alignment=ft.alignment.center,
            )
            
            # Sonuç alanı
            result_text = ft.Container(
                content=ft.Text("Sonuçlar burada görünecek", color=colors["text_muted"]),
                bgcolor=colors["glass"],
                border_radius=15,
                padding=15,
                height=120,
            )
            
            # Mod seçici
            mode_dropdown = ft.Dropdown(
                options=[
                    ft.dropdown.Option("ocr", "📝 OCR (Yazı Tanıma)"),
                    ft.dropdown.Option("qr", "📱 QR/Barkod"),
                    ft.dropdown.Option("face", "👤 Yüz Tanıma"),
                    ft.dropdown.Option("color", "🎨 Renk Analizi"),
                ],
                value="ocr",
                border_color=colors["primary"] + "80",
                bgcolor=colors["bg_secondary"],
                text_style=ft.TextStyle(color=colors["text"]),
                width=200,
            )
            
            # Butonlar
            def start_ar(e):
                result = ar_vision.start_camera()
                camera_view.content = ft.Text("📷 Kamera aktif - AR çalışıyor", 
                                             color=colors["success"], weight=ft.FontWeight.BOLD)
                page.update()
                show_notification(result, "info")
            
            def stop_ar(e):
                result = ar_vision.stop_camera()
                camera_view.content = ft.Text("📷 Kamera görüntüsü burada olacak\n(AR aktif değil)", 
                                             color=colors["text_muted"], text_align=ft.TextAlign.CENTER)
                page.update()
                show_notification(result, "info")
            
            def capture_and_scan(e):
                if not ar_vision.camera_active:
                    show_notification("❌ Önce kamerayı başlatın", "error")
                    return
                
                result = ar_vision.take_photo()
                if isinstance(result, dict):
                    scan_result = ""
                    if result.get('scan', {}).get('text'):
                        scan_result = f"📝 {result['scan']['text'][:150]}"
                    elif result.get('scan', {}).get('qr_codes'):
                        qr = result['scan']['qr_codes'][0]['data']
                        scan_result = f"📱 QR: {qr[:100]}"
                    elif result.get('scan', {}).get('colors'):
                        colors_list = [f"{c['name']}(%{c['percent']})" for c in result['scan']['colors'][:3]]
                        scan_result = f"🎨 {', '.join(colors_list)}"
                    else:
                        scan_result = "📸 Fotoğraf çekildi, ancak içerik bulunamadı"
                    
                    result_text.content = ft.Text(scan_result, color=colors["text"], size=12)
                    show_notification("Fotoğraf çekildi ve tarandı", "success")
                page.update()
            
            def change_mode(e):
                mode = mode_dropdown.value
                result = ar_vision.set_mode(mode)
                show_notification(result, "info")
            
            def quick_scan(e):
                """Hızlı OCR taraması"""
                if not ar_vision.camera_active:
                    show_notification("❌ Önce kamerayı başlatın", "error")
                    return
                
                show_notification("📸 Fotoğraf çekiliyor...", "info")
                result = ar_vision.take_photo()
                if isinstance(result, dict) and result.get('scan', {}).get('text'):
                    text = result['scan']['text'][:200]
                    result_text.content = ft.Text(f"📝 {text}", color=colors["text"])
                    
                    # Konuşma ile de söyle
                    voice.speak(f"Okunan metin: {text[:50]}")
                page.update()
            
            return ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Text("🕶️ AR VİZYON", size=18, weight=ft.FontWeight.BOLD, color=colors["text"]),
                        ft.Text("Gelişmiş OCR ve Artırılmış Gerçeklik", size=11, color=colors["text_muted"]),
                        ft.Divider(height=1, color=colors["primary"] + "40"),
                        ft.Container(height=10),
                        
                        # Kamera görüntüsü
                        camera_view,
                        ft.Container(height=10),
                        
                        # Ana kontrol butonları
                        ft.Row([
                            ft.ElevatedButton(
                                "▶️ Başlat",
                                icon=ft.icons.PLAY_ARROW,
                                on_click=start_ar,
                                style=ft.ButtonStyle(
                                    bgcolor=colors["success"],
                                    color=colors["text"],
                                    padding=10,
                                ),
                                expand=True,
                            ),
                            ft.ElevatedButton(
                                "⏹️ Durdur",
                                icon=ft.icons.STOP,
                                on_click=stop_ar,
                                style=ft.ButtonStyle(
                                    bgcolor=colors["error"],
                                    color=colors["text"],
                                    padding=10,
                                ),
                                expand=True,
                            ),
                        ]),
                        
                        ft.Container(height=10),
                        
                        # İşlem butonları
                        ft.Row([
                            ft.ElevatedButton(
                                "📸 Çek & Tara",
                                icon=ft.icons.CAMERA_ALT,
                                on_click=capture_and_scan,
                                style=ft.ButtonStyle(
                                    bgcolor=colors["primary"],
                                    color=colors["text"],
                                ),
                                expand=True,
                            ),
                            ft.ElevatedButton(
                                "⚡ Hızlı OCR",
                                icon=ft.icons.DOCUMENT_SCANNER,
                                on_click=quick_scan,
                                style=ft.ButtonStyle(
                                    bgcolor=colors["accent"],
                                    color=colors["text"],
                                ),
                                expand=True,
                            ),
                        ]),
                        
                        ft.Container(height=10),
                        
                        # Mod seçici
                        ft.Row([
                            ft.Text("Mod:", color=colors["text"], size=12),
                            mode_dropdown,
                            ft.IconButton(
                                icon=ft.icons.CHECK,
                                icon_color=colors["success"],
                                on_click=change_mode,
                                tooltip="Modu uygula",
                            ),
                        ]),
                        
                        ft.Container(height=10),
                        
                        # Sonuçlar
                        ft.Text("📊 TARAMA SONUCU", size=14, weight=ft.FontWeight.BOLD, color=colors["text"]),
                        result_text,
                        
                        ft.Container(height=5),
                        
                        # Bilgi notu
                        ft.Text(
                            "💡 QR kod, barkod, yazı ve renkleri otomatik algılar",
                            color=colors["text_muted"],
                            size=10,
                            italic=True,
                        ),
                    ]),
                    padding=15,
                )
            ], scroll=ft.ScrollMode.AUTO)
        
        # Dialog fonksiyonları
        def show_detail_dialog(title: str, content: str):
            dlg = ft.AlertDialog(
                title=ft.Text(title, color=colors["primary"]),
                content=ft.Text(content, color=colors["text"]),
                actions=[ft.TextButton("Kapat", on_click=lambda _: page.close(dlg))],
            )
            page.open(dlg)
        
        def show_contact_dialog(contact_id: int):
            contact_info = contacts.get_contact_card(contact_id)
            dlg = ft.AlertDialog(
                title=ft.Text("Kişi Detayı", color=colors["primary"]),
                content=ft.Text(contact_info, color=colors["text"]),
                actions=[
                    ft.TextButton("Ara", on_click=lambda _: call_contact(contact_id)),
                    ft.TextButton("Mesaj", on_click=lambda _: message_contact(contact_id)),
                    ft.TextButton("Kapat", on_click=lambda _: page.close(dlg)),
                ],
            )
            page.open(dlg)
        
        def call_contact(contact_id: int):
            result = contacts.call_contact(contact_id)
            add_message("ANNA", result, is_user=False)
        
        def message_contact(contact_id: int):
            msg_input = ft.TextField(hint_text="Mesajınız", multiline=True)
            dlg = ft.AlertDialog(
                title=ft.Text("Mesaj Gönder", color=colors["primary"]),
                content=msg_input,
                actions=[
                    ft.TextButton("Gönder", on_click=lambda _: send_contact_message(contact_id, msg_input.value)),
                    ft.TextButton("İptal", on_click=lambda _: page.close(dlg)),
                ],
            )
            page.open(dlg)
        
        def send_contact_message(contact_id: int, message: str):
            if message:
                result = contacts.message_contact(contact_id, message)
                add_message("ANNA", result, is_user=False)
        
        def show_favorites():
            favorites = contacts.get_favorites()
            fav_text = contacts.format_contact_list(favorites)
            dlg = ft.AlertDialog(
                title=ft.Text("⭐ Favoriler", color=colors["primary"]),
                content=ft.Text(fav_text, color=colors["text"]),
                actions=[ft.TextButton("Kapat", on_click=lambda _: page.close(dlg))],
            )
            page.open(dlg)
        
        def show_notification(message, type="info"):
            color_map = {
                "info": colors["info"],
                "success": colors["success"],
                "warning": colors["warning"],
                "error": colors["error"]
            }
            page.snack_bar = ft.SnackBar(
                content=ft.Row([
                    ft.Icon(ft.icons.INFO, color=color_map[type]),
                    ft.Text(message, color=colors["text"]),
                ]),
                bgcolor=colors["glass_dark"],
                duration=2000,
            )
            page.snack_bar.open = True
            page.update()
        
        # ============================================
        # UI BİLEŞENLERİ
        # ============================================
        
        # Üst bar
        header = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Icon(ft.icons.AUTO_AWESOME, color=colors["accent"], size=24),
                    ft.Text("A.N.N.A", color=colors["text"], size=18, weight=ft.FontWeight.BOLD),
                ]),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.BATTERY_FULL, color=colors["text_muted"], size=14),
                        ft.Text(datetime.now().strftime("%H:%M"), color=colors["text"], size=12),
                    ]),
                    bgcolor=colors["glass"], border_radius=15, padding=5,
                ),
            ]),
            bgcolor=colors["glass"], padding=10,
        )
        
        # Wake word butonu
        wake_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.MIC_OFF, color=colors["text"], size=16),
                ft.Text("Wake Kapalı", color=colors["text"], size=12, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.CENTER),
            padding=8, border=ft.border.all(1, colors["error"] + "80"), border_radius=20,
            on_click=toggle_wake,
        )
        
        # Ses dalgası
        wave_area = ft.Container(content=wave_container, height=50, alignment=ft.alignment.center)
        
        # Mesaj girişi
        message_input = ft.TextField(
            hint_text="Mesaj yazın...",
            border_color=colors["primary"] + "80", focused_border_color=colors["accent"],
            text_style=ft.TextStyle(color=colors["text"]), bgcolor=colors["bg_secondary"],
            border_radius=30, content_padding=15, expand=True, on_submit=send_message,
        )
        
        # Sesli komut butonu
        listen_btn = ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.MIC_NONE, color=colors["text"], size=16),
                ft.Text("Sesli Komut", color=colors["text"], size=12, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.CENTER),
            padding=8, border=ft.border.all(1, colors["primary"] + "80"), border_radius=20,
            on_click=start_listening,
        )
        
        # Gönder butonu
        send_btn = ft.Container(
            content=ft.Icon(ft.icons.SEND, color=colors["primary"], size=20),
            padding=10, on_click=send_message,
        )
        
        # Alt navigasyon (6 sekme - AR EKLENDİ)
        bottom_nav = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.CHAT, color=colors["primary"] if current_tab == 0 else colors["text_muted"], size=20),
                        ft.Text("Sohbet", color=colors["primary"] if current_tab == 0 else colors["text_muted"], size=9),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                    expand=True,
                    on_click=lambda _: change_tab(0),
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.PHONE_ANDROID, color=colors["primary"] if current_tab == 1 else colors["text_muted"], size=20),
                        ft.Text("Telefon", color=colors["primary"] if current_tab == 1 else colors["text_muted"], size=9),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                    expand=True,
                    on_click=lambda _: change_tab(1),
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.WB_SUNNY, color=colors["primary"] if current_tab == 2 else colors["text_muted"], size=20),
                        ft.Text("Hava", color=colors["primary"] if current_tab == 2 else colors["text_muted"], size=9),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                    expand=True,
                    on_click=lambda _: change_tab(2),
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.CONTACTS, color=colors["primary"] if current_tab == 3 else colors["text_muted"], size=20),
                        ft.Text("Rehber", color=colors["primary"] if current_tab == 3 else colors["text_muted"], size=9),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                    expand=True,
                    on_click=lambda _: change_tab(3),
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.VIEW_IN_AR, color=colors["primary"] if current_tab == 5 else colors["text_muted"], size=20),
                        ft.Text("AR", color=colors["primary"] if current_tab == 5 else colors["text_muted"], size=9),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                    expand=True,
                    on_click=lambda _: change_tab(5),
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.SETTINGS, color=colors["primary"] if current_tab == 4 else colors["text_muted"], size=20),
                        ft.Text("Ayarlar", color=colors["primary"] if current_tab == 4 else colors["text_muted"], size=9),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                    expand=True,
                    on_click=lambda _: change_tab(4),
                ),
            ]),
            bgcolor=colors["glass"], padding=8,
        )
        
        # İçerik alanı
        content_area = ft.Container(content=build_chat_tab(), expand=True, padding=10)
        
        # Ana düzen
        page.add(
            ft.Column([
                header,
                wave_area,
                content_area,
                ft.Container(
                    content=ft.Row([
                        wake_btn, ft.Container(width=5),
                        message_input, listen_btn, send_btn,
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    bgcolor=colors["glass"], padding=10,
                ),
                bottom_nav,
            ], expand=True)
        )
        
        # Hoşgeldin mesajı
        add_message("ANNA", f"Merhaba! Ben A.N.N.A Mobile. {ai_name} ile çalışıyorum.", is_user=False)
        add_message("ANNA", "Sesli komut için 🎤 butonuna basın veya 'Jarvis' deyin", is_user=False)
        add_message("ANNA", "Yeni özellik: AR sekmesinde kamera ile QR, yazı ve renkleri tarayın!", is_user=False)
    
    # ============================================
    # BAŞLANGIÇ
    # ============================================
    show_login()


# ============================================
# UYGULAMAYI BAŞLAT
# ============================================
if __name__ == "__main__":
    ft.app(target=main)