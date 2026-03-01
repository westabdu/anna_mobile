# src/utils/theme.py
"""
A.N.N.A Mobile - Tema Yönetimi
3 Farklı Mobil Tema
"""

class MobileTheme:
    """3 farklı mobil tema"""
    
    DARK = {
        "name": "🌙 Koyu Mavi",
        "bg_primary": "#0A0F1F",
        "bg_secondary": "#141B2B",
        "surface": "#1E2A3A",
        "surface_light": "#2A3A4A",
        "primary": "#2A6DFF",
        "primary_light": "#5B8CFF",
        "secondary": "#3A7BFF",
        "accent": "#00E5FF",
        "accent_light": "#70FFFF",
        "glass": "rgba(20, 30, 50, 0.8)",
        "glass_light": "rgba(30, 40, 60, 0.9)",
        "text": "#FFFFFF",
        "text_secondary": "#B0C4DE",
        "text_muted": "#6B7F8F",
        "success": "#00E676",
        "warning": "#FFD600",
        "error": "#FF5252",
        "card_bg": "#1E2A3A",
    }
    
    OCEAN = {
        "name": "🌊 Okyanus",
        "bg_primary": "#0A1A2A",
        "bg_secondary": "#1A2A3A",
        "surface": "#2A3A4A",
        "surface_light": "#3A4A5A",
        "primary": "#00A8E8",
        "primary_light": "#4AC7FF",
        "secondary": "#00B4D8",
        "accent": "#00FFE5",
        "accent_light": "#70FFF0",
        "glass": "rgba(0, 20, 30, 0.8)",
        "glass_light": "rgba(10, 30, 40, 0.9)",
        "text": "#FFFFFF",
        "text_secondary": "#C0F0FF",
        "text_muted": "#80A0B0",
        "success": "#00E676",
        "warning": "#FFD600",
        "error": "#FF5252",
        "card_bg": "#1A2A3A",
    }
    
    ICE = {
        "name": "❄️ Buz Mavisi",
        "bg_primary": "#E0F0FF",
        "bg_secondary": "#F0F8FF",
        "surface": "#FFFFFF",
        "surface_light": "#F5F5F5",
        "primary": "#0096FF",
        "primary_light": "#4AB8FF",
        "secondary": "#00A3FF",
        "accent": "#00CCFF",
        "accent_light": "#80E5FF",
        "glass": "rgba(255, 255, 255, 0.8)",
        "glass_light": "rgba(255, 255, 255, 0.9)",
        "text": "#0A1A2A",
        "text_secondary": "#1A2A3A",
        "text_muted": "#4A5A6A",
        "success": "#00C853",
        "warning": "#FFC107",
        "error": "#FF3D00",
        "card_bg": "#FFFFFF",
    }
    
    current = DARK
    
    @classmethod
    def set_theme(cls, theme_name: str):
        if theme_name == "dark":
            cls.current = cls.DARK
        elif theme_name == "ocean":
            cls.current = cls.OCEAN
        elif theme_name == "ice":
            cls.current = cls.ICE
        return cls.current