# src/modules/ocr.py
"""
Optik Karakter Tanıma (OCR) - Fotoğraftan yazı okuma
"""

import os
import tempfile
from pathlib import Path
import base64
import time

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except:
    TESSERACT_AVAILABLE = False

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except:
    CV2_AVAILABLE = False


class OCRManager:
    """OCR ile fotoğraftan yazı okuma"""
    
    def __init__(self):
        self.data_dir = Path("data/ocr")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Tesseract yolunu ayarla (Windows için)
        if os.name == 'nt':
            possible_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break
        
        print(f"📸 OCR Modülü: {'✅' if TESSERACT_AVAILABLE else '❌'}")
        print(f"🎥 OpenCV: {'✅' if CV2_AVAILABLE else '❌'}")
    
    def image_to_text(self, image_path: str, lang: str = 'tur') -> str:
        """Resimdeki yazıyı oku"""
        if not TESSERACT_AVAILABLE:
            return "❌ Tesseract OCR yüklü değil"
        
        try:
            # Resmi aç
            image = Image.open(image_path)
            
            # OCR uygula
            text = pytesseract.image_to_string(image, lang=lang)
            
            if text.strip():
                return f"📝 **Okunan Metin:**\n\n{text.strip()}"
            else:
                return "📭 Resimde yazı bulunamadı"
                
        except Exception as e:
            return f"❌ OCR hatası: {e}"
    
    def image_to_text_with_preprocessing(self, image_path: str, lang: str = 'tur') -> str:
        """Ön işleme ile OCR (daha iyi sonuç)"""
        if not TESSERACT_AVAILABLE or not CV2_AVAILABLE:
            return "❌ Tesseract veya OpenCV yüklü değil"
        
        try:
            # OpenCV ile resmi oku
            img = cv2.imread(image_path)
            
            # Gri tonlamaya çevir
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Gürültü azalt
            denoised = cv2.medianBlur(gray, 3)
            
            # Threshold uygula
            _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Geçici dosyaya kaydet
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as f:
                temp_path = f.name
                cv2.imwrite(temp_path, thresh)
            
            # OCR uygula
            text = pytesseract.image_to_string(temp_path, lang=lang)
            
            # Temizlik
            os.unlink(temp_path)
            
            if text.strip():
                return f"📝 **Okunan Metin (İyileştirilmiş):**\n\n{text.strip()}"
            else:
                return "📭 Resimde yazı bulunamadı"
                
        except Exception as e:
            return f"❌ OCR hatası: {e}"
    
    def camera_to_text(self, duration: int = 3) -> str:
        """Kameradan fotoğraf çek ve oku"""
        if not CV2_AVAILABLE:
            return "❌ OpenCV yüklü değil"
        
        try:
            # Kamerayı aç
            cap = cv2.VideoCapture(0)
            
            # Kameranın ısınmasını bekle
            time.sleep(1)
            
            # Fotoğraf çek
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                return "❌ Kamera açılamadı"
            
            # Geçici dosyaya kaydet
            temp_file = self.data_dir / "camera_capture.jpg"
            cv2.imwrite(str(temp_file), frame)
            
            # OCR uygula
            return self.image_to_text_with_preprocessing(str(temp_file))
            
        except Exception as e:
            return f"❌ Kamera hatası: {e}"
    
    def base64_to_text(self, base64_image: str, lang: str = 'tur') -> str:
        """Base64 formatındaki resmi oku"""
        if not TESSERACT_AVAILABLE:
            return "❌ Tesseract OCR yüklü değil"
        
        try:
            # Base64'ü decode et
            image_data = base64.b64decode(base64_image.split(',')[-1])
            
            # Geçici dosyaya kaydet
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as f:
                f.write(image_data)
                temp_path = f.name
            
            # OCR uygula
            text = self.image_to_text_with_preprocessing(temp_path, lang)
            
            # Temizlik
            os.unlink(temp_path)
            
            return text
            
        except Exception as e:
            return f"❌ OCR hatası: {e}"
    
    def detect_language(self, image_path: str) -> str:
        """Resimdeki dil algılama"""
        if not TESSERACT_AVAILABLE:
            return "❌ Tesseract OCR yüklü değil"
        
        try:
            # Önce Türkçe dene
            text_tr = self.image_to_text(image_path, 'tur')
            
            # Sonra İngilizce dene
            text_en = self.image_to_text(image_path, 'eng')
            
            # Hangi dilde daha çok karakter varsa onu seç
            if len(text_tr) > len(text_en):
                return "🇹🇷 Türkçe"
            else:
                return "🇬🇧 İngilizce"
                
        except Exception as e:
            return f"❌ Dil algılama hatası: {e}"
    
    def get_available_languages(self) -> list:
        """Kullanılabilir dilleri listele"""
        if not TESSERACT_AVAILABLE:
            return []
        
        try:
            languages = pytesseract.get_languages()
            return languages
        except:
            return ['tur', 'eng']