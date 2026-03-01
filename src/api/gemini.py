# src/api/gemini.py - ALTERNATİF MODELLER EKLENDİ
import os
import google.generativeai as genai
from dotenv import load_dotenv

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
            except Exception as e:
                self.available = False
                print(f"❌ Gemini başlatılamadı: {e}")
        else:
            print("⚠️ GEMINI_API_KEY bulunamadı")

    def ask(self, prompt: str) -> str:
        if not self.available:
            return "Gemini API anahtarı eksik veya süresi dolmuş."
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            # API key hatası
            if "API_KEY_INVALID" in str(e) or "expired" in str(e):
                return "❌ Gemini API anahtarınızın süresi dolmuş. Lütfen https://aistudio.google.com/app/apikey adresinden yeni bir anahtar alın."
            
            # 404 hatası - model bulunamadı
            if "404" in str(e) or "not found" in str(e).lower():
                return self._try_alternative_model(prompt)
            
            return f"❌ Gemini hatası: {e}"
    
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