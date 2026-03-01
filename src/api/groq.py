# src/api/groq.py - ANDROID UYUMLU
"""
Groq API ile ultra hızlı yapay zeka
"""

import os
import sys
from groq import Groq
from dotenv import load_dotenv

# Android tespiti
IS_ANDROID = 'android' in sys.platform or 'ANDROID_ARGUMENT' in os.environ

# .env dosyasını yükle
if IS_ANDROID:
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    load_dotenv(dotenv_path)
else:
    load_dotenv()


class GroqAI:
    """Groq API ile ultra hızlı yapay zeka"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = None
        self.available = False
        self.current_model = "llama-3.3-70b-versatile"
        
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
                self.available = True
                print(f"✅ Groq AI hazır (Model: {self.current_model})")
                print(f"📱 Android: {'✅' if IS_ANDROID else '❌'}")
            except Exception as e:
                print(f"❌ Groq başlatılamadı: {e}")
                self.available = False
        else:
            print("⚠️ GROQ_API_KEY bulunamadı")
    
    def ask(self, prompt: str) -> str:
        """Soru sor (senkron)"""
        if not self.available or not self.client:
            return "Groq API hazır değil."
        
        try:
            completion = self.client.chat.completions.create(
                model=self.current_model,
                messages=[
                    {
                        "role": "system", 
                        "content": "Sen A.N.N.A'sın. Yardımsever, zeki ve karizmatik bir asistansın. Cevapların kısa ve öz olsun."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1024
            )
            return completion.choices[0].message.content
        except Exception as e:
            error_str = str(e)
            
            # Hata durumunda alternatif model dene
            if "decommissioned" in error_str or "deprecated" in error_str:
                return self._try_alternative_model(prompt)
            
            # Network hatası
            if "connection" in error_str.lower() or "timeout" in error_str.lower():
                return "❌ İnternet bağlantısı yok veya API'ye erişilemiyor."
            
            return f"❌ Groq hatası: {error_str[:100]}"
    
    def _try_alternative_model(self, prompt: str) -> str:
        """Alternatif modelleri dene"""
        alternative_models = [
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ]
        
        for model in alternative_models:
            try:
                print(f"🔄 Alternatif model deneniyor: {model}")
                completion = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "Sen A.N.N.A'sın, yardımsever bir asistansın."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.6,
                    max_tokens=1024
                )
                self.current_model = model
                print(f"✅ Yeni model aktif: {model}")
                return completion.choices[0].message.content
            except:
                continue
        
        return "❌ Tüm Groq modelleri denendi ama hiçbiri çalışmadı."