# src/api/groq.py - MODEL ADI DÜZELTİLDİ
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class GroqAI:
    """Groq API ile ultra hızlı yapay zeka"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = None
        self.available = False
        self.current_model = "llama-3.3-70b-versatile"  # GÜNCELLENMİŞ MODEL
        
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
                self.available = True
                print(f"✅ Groq AI hazır (Model: {self.current_model})")
            except Exception as e:
                print(f"❌ Groq başlatılamadı: {e}")
                self.available = False
        else:
            print("⚠️ GROQ_API_KEY bulunamadı")
    
    def ask(self, prompt: str) -> str:
        """Soru sor (güncel model ile)"""
        if not self.available or not self.client:
            return "Groq API hazır değil."
        
        try:
            completion = self.client.chat.completions.create(
                model=self.current_model,  # Güncellenmiş model adı
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
            # Hata durumunda alternatif model dene
            if "decommissioned" in str(e) or "deprecated" in str(e):
                return self._try_alternative_model(prompt)
            return f"❌ Groq hatası: {e}"
    
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
                self.current_model = model  # Başarılı olan modeli kaydet
                print(f"✅ Yeni model aktif: {model}")
                return completion.choices[0].message.content
            except:
                continue
        
        return "❌ Tüm Groq modelleri denendi ama hiçbiri çalışmadı. Lütfen daha sonra tekrar deneyin."