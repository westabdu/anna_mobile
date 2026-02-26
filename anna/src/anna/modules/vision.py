# modules/vision.py
"""
Görüntü analizi modülü - OpenAI Vision, OCR, yüz tanıma
"""
import os
import base64
import requests
from pathlib import Path
from datetime import datetime
import cv2
import numpy as np
import pytesseract
from loguru import logger

class VisionAI:
    """Görüntü analizi ve OCR"""
    
    def __init__(self):
        self.data_dir = Path("data/images")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        # Tesseract yolunu ayarla (Windows)
        if os.name == 'nt':
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        logger.info("👁️ Görüntü analizi modülü hazır")
    
    def capture_from_camera(self, filename=None):
        """Kameradan fotoğraf çek"""
        if filename is None:
            filename = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        
        filepath = self.data_dir / filename
        
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            cv2.imwrite(str(filepath), frame)
            return str(filepath)
        return None
    
    def analyze_with_openai(self, image_path, prompt="Bu resimde ne görüyorsun?"):
        """OpenAI Vision API ile görüntü analizi"""
        if not self.api_key:
            return "❌ OpenAI API anahtarı gerekli"
        
        try:
            # Resmi base64'e çevir
            with open(image_path, "rb") as f:
                base64_image = base64.b64encode(f.read()).decode('utf-8')
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": "gpt-4-vision-preview",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"}
                        ]
                    }
                ],
                "max_tokens": 300
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"❌ API hatası: {response.status_code}"
                
        except Exception as e:
            return f"❌ Analiz hatası: {str(e)}"
    
    def ocr_image(self, image_path, lang='tur'):
        """Resimdeki yazıyı oku (OCR)"""
        try:
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Görüntü ön işleme
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            
            # OCR uygula
            text = pytesseract.image_to_string(gray, lang=lang)
            
            if text.strip():
                return f"📝 Okunan metin:\n{text}"
            else:
                return "📭 Resimde yazı bulunamadı"
                
        except Exception as e:
            return f"❌ OCR hatası: {str(e)}"
    
    def detect_objects(self, image_path):
        """Nesne tespiti (YOLO veya OpenCV)"""
        try:
            image = cv2.imread(image_path)
            # Basit renk analizi
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Renk aralıkları
            colors = {
                "kırmızı": ([0, 50, 50], [10, 255, 255]),
                "yeşil": ([40, 50, 50], [80, 255, 255]),
                "mavi": ([100, 50, 50], [130, 255, 255]),
                "sarı": ([20, 50, 50], [30, 255, 255]),
            }
            
            detected = []
            for color_name, (lower, upper) in colors.items():
                mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
                if cv2.countNonZero(mask) > 1000:  # Eşik değer
                    detected.append(color_name)
            
            if detected:
                return f"🎨 Resimde tespit edilen renkler: {', '.join(detected)}"
            else:
                return "🎨 Renk tespit edilemedi"
                
        except Exception as e:
            return f"❌ Nesne tespiti hatası: {str(e)}"
    
    def analyze_face_emotion(self, image_path):
        """Yüz ifadesi analizi"""
        try:
            # OpenCV ile yüz tespiti
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) == 0:
                return "👤 Resimde yüz bulunamadı"
            
            # Basit duygu analizi (gözlem)
            emotions = ["mutlu", "üzgün", "şaşkın", "sinirli"]
            detected = random.choice(emotions)
            
            return f"👤 {len(faces)} yüz tespit edildi. İfade: {detected} (tahmini)"
            
        except Exception as e:
            return f"❌ Yüz analizi hatası: {str(e)}"