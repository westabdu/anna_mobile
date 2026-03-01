# src/modules/about.py - A.N.N.A Mobile Hakkında Sayfası
"""
A.N.N.A Mobile hakkında sayfası - Proje bilgileri, geliştirici notları ve iletişim
Uygulama Bilgileri
- Proje Adı: A.N.N.A Mobile
- Sürüm: 1.0.0
- Geliştirici
- Lisans
"""

import os
import sys
from datetime import datetime

# Android tespiti
IS_ANDROID = 'android' in sys.platform or 'ANDROID_ARGUMENT' in os.environ

class AboutManager:
    """Hakkında sayfası için bilgi yöneticisi"""

    def __init__(self):
        self.app_name = "A.N.N.A Mobile"
        self.version = "1.0.0"
        self.developer = "Westabdu"
        self.license = "MIT Lisansı"
        self.last_updated = datetime.now().strftime("%Y-%m-%d")
        self.contact_email = "abdurahmansabsabi372@gmail.com"

        # Android'de ek bilgiler
        if IS_ANDROID:
            self.platform_info = f"Android - Python {sys.version.split()[0]}"
        else:
            self.platform_info = f"Desktop - Python {sys.version.split()[0]}"
            
        # Android'de platform bilgisi (düzeltildi)
        if IS_ANDROID:
            self.platform = "Android"
        else:
            self.platform = f"{sys.platform} (Test Modu)"

    def get_info(self) -> str:
        """Hakkında bilgilerini formatlı şekilde döndür"""
        return f"""
🤖 **{self.app_name}**

📱 **Versiyon:** {self.version}
📅 **Yapım:** {self.last_updated}
👨‍💻 **Geliştirici:** {self.developer}
📱 **Platform:** {self.platform}

📋 **Özellikler:**
• 🔐 Gelişmiş giriş sistemi
• 🤖 Yapay Zeka (Gemini/Groq)
• 🌤️ Hava durumu
• 📱 Telefon bilgileri
• 👤 Rehber yönetimi
• 📸 OCR ve AR
• ⏰ Hatırlatıcılar
• 📰 Haberler
• 🎤 Sesli komut

📝 **Lisans:** MIT
© 2025 {self.developer}
"""
    
    def get_short_info(self) -> str:
        """Kısa bilgi"""
        return f"🤖 {self.app_name} v{self.version}"
    
    def get_developer_info(self) -> str:
        """Geliştirici bilgileri"""
        return f"""
👨‍💻 **Geliştirici:** {self.developer}
📧 **İletişim:** github.com/westabdu
🐦 **İnstagram:** @westabdu
"""
    
    def get_contact_info(self) -> str:
        """İletişim bilgileri"""
        return f"""
📧 **E-posta:** {self.contact_email}
"""

    def get_license(self) -> str:
        """Lisans bilgisi"""
        return """
📝 **MIT Lisansı**

Copyright (c) 2025 Westabdu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files...
"""