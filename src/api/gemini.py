# src/api/gemini.py - ANDROID UYUMLU
"""
Google Gemini API - A.N.N.A Mobile için
"""

import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv

# Android tespiti
IS_ANDROID = 'android' in sys.platform or 'ANDROID_ARGUMENT' in os.environ

# .env dosyasını yükle (Android'de farklı yollar)
if IS_ANDROID:
    # Android'de .env dosyası APK içinde
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    load_dotenv(dotenv_path)
else:
    load_dotenv()


class GeminiAI:
    """Gemini API - Otomatik Model Seçimli"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = 'gemini-1.5-flash'
        self.model = None
        self.chat_session = None
        self.available = False
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(self.model_name)
                self.available = True
                print(f"✅ Gemini AI hazır (Model: {self.model_name})")
                print(f"📱 Android: {'✅' if IS_ANDROID else '❌'}")
            except Exception as e:
                self.available = False
                print(f"❌ Gemini başlatılamadı: {e}")
        else:
            print("⚠️ GEMINI_API_KEY bulunamadı")

    def ask(self, prompt: str) -> str:
        """Soru sor (senkron)"""
        if not self.available:
            return "Gemini API anahtarı eksik veya süresi dolmuş."
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_str = str(e)
            
            # API key hatası
            if "API_KEY_INVALID" in error_str or "expired" in error_str:
                return "❌ Gemini API anahtarınızın süresi dolmuş. Lütfen yeni bir anahtar alın."
            
            # 404 hatası - model bulunamadı
            if "404" in error_str or "not found" in error_str.lower():
                return self._try_alternative_model(prompt)
            
            # Network hatası
            if "connection" in error_str.lower() or "timeout" in error_str.lower():
                return "❌ İnternet bağlantısı yok veya API'ye erişilemiyor."
            
            return f"❌ Gemini hatası: {error_str[:100]}"
    
    def _try_alternative_model(self, prompt: str) -> str:
        """Alternatif Gemini modellerini dene"""
        alternative_models = ['gemini-pro', 'gemini-1.0-pro']
        
        for model_name in alternative_models:
            try:
                print(f"🔄 Alternatif Gemini modeli deneniyor: {model_name}")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                self.model = model
                self.model_name = model_name
                print(f"✅ Yeni Gemini model aktif: {model_name}")
                return response.text
            except:
                continue
        
        return "❌ Hiçbir Gemini modeli çalışmadı."