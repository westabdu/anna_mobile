# src/modules/ocr.py - ANDROID UYUMLU
"""
Optik Karakter Tanıma (OCR) - Fotoğraftan yazı okuma
"""

import os
import sys
import tempfile
from pathlib import Path
import base64
import time

# Android tespiti
IS_ANDROID = 'android' in sys.platform or 'ANDROID_ARGUMENT' in os.environ

# EasyOCR (Android'de çalışır)
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except:
    EASYOCR_AVAILABLE = False

# Tesseract (Android'de zor)
try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except:
    TESSERACT_AVAILABLE = False

# OpenCV (Android'de çalışır)
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except:
    CV2_AVAILABLE = False


class OCRManager:
    """OCR ile fotoğraftan yazı okuma"""
    
    def __init__(self):
        # Android'de depolama yolu farklı
        if IS_ANDROID:
            try:
                from android.storage import primary_external_storage_path
                base_path = Path(primary_external_storage_path()) / "ANNA" / "data"
                self.data_dir = base_path / "ocr"
            except:
                self.data_dir = Path("/storage/emulated/0/ANNA/data/ocr")
        else:
            self.data_dir = Path("data/ocr")
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # EasyOCR (birincil)
        self.easyocr_reader = None
        if EASYOCR_AVAILABLE:
            try:
                self.easyocr_reader = easyocr.Reader(['tr', 'en'], gpu=False)
                print("✅ EasyOCR hazır (Türkçe + İngilizce)")
            except Exception as e:
                print(f"⚠️ EasyOCR yüklenemedi: {e}")
        
        # Tesseract (ikincil)
        if not EASYOCR_AVAILABLE and TESSERACT_AVAILABLE:
            if IS_ANDROID:
                # Android'de Tesseract yolu
                possible_paths = [
                    '/data/data/org.anna.mobile/files/tesseract/tesseract',
                    '/storage/emulated/0/ANNA/tesseract/tesseract'
                ]
            else:
                possible_paths = [
                    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
                ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break
            print("✅ Tesseract OCR hazır")
        
        print(f"📸 OCR Modülü: {'✅ EasyOCR' if EASYOCR_AVAILABLE else '✅ Tesseract' if TESSERACT_AVAILABLE else '❌'}")
        print(f"🎥 OpenCV: {'✅' if CV2_AVAILABLE else '❌'}")
        print(f"📱 Android: {'✅' if IS_ANDROID else '❌'}")
    
    def image_to_text(self, image_path: str, lang: str = 'tr') -> dict:
        """Resimdeki yazıyı oku (gelişmiş)"""
        result = {
            'success': False,
            'text': '',
            'method': 'none',
            'error': None
        }
        
        # EasyOCR dene
        if EASYOCR_AVAILABLE and self.easyocr_reader:
            try:
                img = cv2.imread(image_path)
                if img is not None:
                    results = self.easyocr_reader.readtext(img)
                    if results:
                        texts = [r[1] for r in results]
                        result['text'] = " ".join(texts)
                        result['success'] = True
                        result['method'] = 'easyocr'
                        return result
            except Exception as e:
                result['error'] = str(e)
        
        # Tesseract dene
        if TESSERACT_AVAILABLE and not result['success']:
            try:
                from PIL import Image
                image = Image.open(image_path)
                text = pytesseract.image_to_string(image, lang='tur+eng')
                if text.strip():
                    result['text'] = text.strip()
                    result['success'] = True
                    result['method'] = 'tesseract'
            except Exception as e:
                result['error'] = str(e)
        
        if not result['success']:
            result['text'] = "📭 Resimde yazı bulunamadı"
        
        return result
    
    def camera_to_text(self, duration: int = 3) -> dict:
        """Kameradan fotoğraf çek ve oku"""
        if not CV2_AVAILABLE:
            return {'success': False, 'text': "❌ OpenCV yüklü değil"}
        
        try:
            # Kamerayı aç
            cap = cv2.VideoCapture(0)
            
            # Kameranın ısınmasını bekle
            time.sleep(1)
            
            # Fotoğraf çek
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                return {'success': False, 'text': "❌ Kamera açılamadı"}
            
            # Geçici dosyaya kaydet
            temp_file = self.data_dir / "camera_capture.jpg"
            cv2.imwrite(str(temp_file), frame)
            
            # OCR uygula
            result = self.image_to_text(str(temp_file))
            
            # Geçici dosyayı temizle
            try:
                temp_file.unlink()
            except:
                pass
            
            return result
            
        except Exception as e:
            return {'success': False, 'text': f"❌ Kamera hatası: {e}"}
    
    def scan_image_file(self, image_path: str) -> dict:
        """Resim dosyasını tara"""
        return self.image_to_text(image_path)
    
    def get_available_languages(self) -> list:
        """Kullanılabilir dilleri listele"""
        if EASYOCR_AVAILABLE:
            return ['tr', 'en', 'de', 'fr', 'es']
        return ['tur', 'eng']