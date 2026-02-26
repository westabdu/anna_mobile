# modules/face_recognition.py
"""
Yüz tanıma modülü - MediaPipe ile
Model dosyası ile birlikte çalışan versiyon
"""

import cv2
import numpy as np
import time
import os
from pathlib import Path
import pickle
from loguru import logger

try:
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    MEDIAPIPE_AVAILABLE = True
except ImportError as e:
    MEDIAPIPE_AVAILABLE = False
    logger.warning(f"⚠️ MediaPipe hatası: {e}")

class FaceRecognition:
    """
    MediaPipe ile yüz tanıma sistemi
    - Model dosyası ile çalışır
    """
    
    def __init__(self):
        self.data_dir = Path("data/faces")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.faces_file = self.data_dir / "faces.pkl"
        self.known_faces = self._load_faces()
        
        # Model dosyasının yolu
        self.model_path = Path("data/models/blaze_face_short_range.tflite")
        
        if MEDIAPIPE_AVAILABLE and self.model_path.exists():
            try:
                # Model dosyası ile FaceDetector oluştur
                base_options = python.BaseOptions(model_asset_path=str(self.model_path))
                options = vision.FaceDetectorOptions(
                    base_options=base_options,
                    running_mode=vision.RunningMode.IMAGE,
                    min_detection_confidence=0.5,
                    min_suppression_threshold=0.3
                )
                self.face_detector = vision.FaceDetector.create_from_options(options)
                logger.success("✅ Yüz tanıma hazır")
            except Exception as e:
                logger.error(f"❌ FaceDetector oluşturulamadı: {e}")
                self.face_detector = None
        else:
            logger.warning("⚠️ Model dosyası bulunamadı: data/models/blaze_face_short_range.tflite")
            self.face_detector = None
    
    def _load_faces(self):
        """Kayıtlı yüzleri yükle"""
        if self.faces_file.exists():
            try:
                with open(self.faces_file, 'rb') as f:
                    return pickle.load(f)
            except:
                return {}
        return {}
    
    def _save_faces(self):
        """Yüzleri kaydet"""
        try:
            with open(self.faces_file, 'wb') as f:
                pickle.dump(self.known_faces, f)
        except Exception as e:
            logger.error(f"Yüzler kaydedilemedi: {e}")
    
    def detect_faces(self, frame):
        """Yüzleri tespit et"""
        if not MEDIAPIPE_AVAILABLE or not self.face_detector:
            return []
        
        # OpenCV görüntüsünü MediaPipe formatına çevir
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        
        # Yüz tespiti yap
        detection_result = self.face_detector.detect(mp_image)
        
        faces = []
        if detection_result.detections:
            for detection in detection_result.detections:
                bbox = detection.bounding_box
                faces.append({
                    "bbox": {
                        "x": bbox.origin_x,
                        "y": bbox.origin_y,
                        "width": bbox.width,
                        "height": bbox.height
                    },
                    "confidence": detection.categories[0].score
                })
        return faces
    
    def get_face_encoding(self, frame):
        """Yüz embedding'i çıkar (basitleştirilmiş)"""
        faces = self.detect_faces(frame)
        if faces:
            # İlk yüzün bounding box'ını encoding olarak kullan
            bbox = faces[0]["bbox"]
            return np.array([bbox["x"], bbox["y"], bbox["width"], bbox["height"]])
        return None
    
    def register_face(self, user_id, name, num_samples=5):
        """Yeni yüz kaydet"""
        cap = cv2.VideoCapture(0)
        samples = []
        
        logger.info(f"📸 Yüz kaydediliyor: {name}")
        
        for i in range(num_samples):
            logger.info(f"Örnek {i+1}/{num_samples} - Kameraya bakın...")
            time.sleep(1)
            
            ret, frame = cap.read()
            if not ret:
                continue
            
            encoding = self.get_face_encoding(frame)
            if encoding is not None:
                samples.append(encoding)
                logger.info(f"✓ Örnek {i+1} alındı")
        
        cap.release()
        
        if len(samples) < 3:
            logger.error("Yeterli örnek alınamadı!")
            return False
        
        # Ortalama encoding hesapla
        avg_encoding = np.mean(samples, axis=0)
        self.known_faces[user_id] = {
            "name": name,
            "encoding": avg_encoding,
            "timestamp": time.time()
        }
        
        self._save_faces()
        logger.success(f"✅ {name} yüzü kaydedildi")
        return True
    
    def recognize(self, frame=None):
        """Yüz tanı"""
        if frame is None:
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()
            if not ret:
                return None
        
        encoding = self.get_face_encoding(frame)
        if encoding is None:
            return None
        
        if not self.known_faces:
            return None
        
        best_match = None
        best_distance = float('inf')
        
        for user_id, data in self.known_faces.items():
            known_encoding = data["encoding"]
            distance = np.linalg.norm(encoding - known_encoding)
            
            if distance < best_distance and distance < 200:  # Eşik değer
                best_distance = distance
                best_match = user_id
        
        if best_match:
            return self.known_faces[best_match]["name"]
        return None
    
    def recognize_from_camera(self, timeout=5):
        """Kameradan belirli süre yüz tanı"""
        cap = cv2.VideoCapture(0)
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            ret, frame = cap.read()
            if not ret:
                continue
            
            name = self.recognize(frame)
            if name:
                cap.release()
                return name
        
        cap.release()
        return None
    
    def delete_face(self, user_id):
        """Yüz kaydını sil"""
        if user_id in self.known_faces:
            del self.known_faces[user_id]
            self._save_faces()
            logger.info(f"🗑️ Yüz silindi: {user_id}")
            return True
        return False
    
    def list_faces(self):
        """Kayıtlı yüzleri listele"""
        return [
            {"id": uid, "name": data["name"], "timestamp": data["timestamp"]}
            for uid, data in self.known_faces.items()
        ]