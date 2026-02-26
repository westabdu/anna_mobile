# modules/ar_system.py - HAFİF AR VERSİYON (MediaPipe ile)
"""
A.N.N.A Hafif AR Sistemi - MediaPipe ile
- Nesne tanıma (basit)
- QR/Barkod okuma
- Yüz tanıma ve etiketleme
- El tespiti ve takibi
- OCR (Yazı tanıma)
- Renk analizi
- AR mesajları
"""

import cv2
import numpy as np
import threading
import time
import json
from pathlib import Path
from datetime import datetime

# MediaPipe
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("⚠️ MediaPipe yüklü değil, lütfen kurun: pip install mediapipe")

# QR ve OCR
try:
    from pyzbar.pyzbar import decode
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False
    print("⚠️ pyzbar yüklü değil, QR okuma çalışmaz")

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("⚠️ pytesseract yüklü değil, OCR çalışmaz")

# Yüz tanıma
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("⚠️ face_recognition yüklü değil, yüz tanıma çalışmaz")

class ARSystem:
    """Hafif AR Sistemi - MediaPipe tabanlı"""
    
    def __init__(self):
        self.active = False
        self.camera_active = False
        self.cap = None
        self.frame = None
        self.detected_objects = []      # Basit renk tabanlı nesneler
        self.detected_faces = []         # Yüzler
        self.detected_hands = []         # Eller
        self.detected_codes = []         # QR/Barkod
        self.detected_text = ""          # OCR sonucu
        self.current_mode = "objects"    # objects, faces, hands, qr, ocr, color
        
        # Modül bağlantıları
        self.whatsapp = None
        self.emotion_detector = None
        
        # Veri klasörleri
        self.data_dir = Path("data/ar")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.faces_dir = self.data_dir / "faces"
        self.faces_dir.mkdir(exist_ok=True)
        
        # Nesne bilgi veritabanı (basit)
        self.object_info = {
            "kırmızı": {"name": "🔴 Kırmızı Nesne", "desc": "Kırmızı renkli bir nesne"},
            "yeşil": {"name": "🟢 Yeşil Nesne", "desc": "Yeşil renkli bir nesne"},
            "mavi": {"name": "🔵 Mavi Nesne", "desc": "Mavi renkli bir nesne"},
            "sarı": {"name": "🟡 Sarı Nesne", "desc": "Sarı renkli bir nesne"},
            "mor": {"name": "🟣 Mor Nesne", "desc": "Mor renkli bir nesne"},
            "kitap": {"name": "📖 Kitap", "desc": "Bilgi kaynağı"},
            "telefon": {"name": "📱 Telefon", "desc": "İletişim cihazı"},
            "bardak": {"name": "🥤 Bardak", "desc": "İçecek kabı"},
        }
        
        # Bilinen yüzler
        self.known_faces = []
        self.known_names = []
        self._load_known_faces()
        
        # ---------- MEDIAPIPE MODELLERİ ----------
        if MEDIAPIPE_AVAILABLE:
            self.mp_face_detection = mp.solutions.face_detection
            self.mp_hands = mp.solutions.hands
            self.mp_drawing = mp.solutions.drawing_utils
            
            # Face Detection
            self.face_detection = self.mp_face_detection.FaceDetection(
                model_selection=0,  # 0: yakın mesafe, 1: uzak mesafe
                min_detection_confidence=0.5
            )
            
            # Hand Detection
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            
            print("✅ MediaPipe modelleri yüklendi")
        else:
            self.face_detection = None
            self.hands = None
        
        # Renk aralıkları (basit nesne tanıma için)
        self.color_ranges = {
            "kırmızı": ([0, 50, 50], [10, 255, 255]),
            "yeşil": ([40, 50, 50], [80, 255, 255]),
            "mavi": ([100, 50, 50], [130, 255, 255]),
            "sarı": ([20, 50, 50], [30, 255, 255]),
            "mor": ([130, 50, 50], [160, 255, 255]),
        }
        
        # AR mesajları
        self.ar_messages = []
        
        print("🌟 Hafif AR sistemi başlatıldı (MediaPipe)")
    
    # ============================================
    # YARDIMCI FONKSİYONLAR
    # ============================================
    
    def _load_known_faces(self):
        """Bilinen yüzleri yükle"""
        if not FACE_RECOGNITION_AVAILABLE:
            return
            
        for img_path in self.faces_dir.glob("*.jpg"):
            try:
                image = face_recognition.load_image_file(img_path)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    self.known_faces.append(encodings[0])
                    self.known_names.append(img_path.stem)
            except:
                continue
        
        print(f"👤 {len(self.known_names)} yüz yüklendi")
    
    # ============================================
    # KAMERA KONTROLLERİ
    # ============================================
    
    def start_camera(self):
        """Kamerayı başlat"""
        if not self.camera_active:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Daha düşük çözünürlük
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera_active = True
            self.active = True
            threading.Thread(target=self._process_frames, daemon=True).start()
            return "✅ Kamera başlatıldı"
        return "⚠️ Kamera zaten aktif"
    
    def stop_camera(self):
        """Kamerayı durdur"""
        self.active = False
        self.camera_active = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        return "⏹️ Kamera durduruldu"
    
    def set_mode(self, mode):
        """AR modunu değiştir"""
        modes = ["objects", "faces", "hands", "qr", "ocr", "color"]
        if mode in modes:
            self.current_mode = mode
            return f"🔮 AR modu: {mode}"
        return f"❌ Geçersiz mod. Seçenekler: {', '.join(modes)}"
    
    # ============================================
    # ANA İŞLEME DÖNGÜSÜ
    # ============================================
    
    def _process_frames(self):
        """Ana görüntü işleme döngüsü"""
        while self.active and self.camera_active:
            ret, frame = self.cap.read()
            if not ret:
                continue
            
            self.frame = frame.copy()
            
            # Seçili moda göre işle
            if self.current_mode == "objects":
                self._detect_objects_by_color(frame)
            elif self.current_mode == "faces":
                self._detect_faces_mediapipe(frame)
            elif self.current_mode == "hands":
                self._detect_hands(frame)
            elif self.current_mode == "qr":
                self._detect_qr_codes(frame)
            elif self.current_mode == "ocr":
                self._detect_text(frame)
            elif self.current_mode == "color":
                self._detect_color_at_center(frame)
            
            # AR overlay çiz
            self._draw_overlay(frame)
            
            # Göster
            cv2.imshow('A.N.N.A AR (Hafif)', frame)
            
            # Klavye kontrolleri
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                self._save_snapshot(frame)
            elif key == ord('1'):
                self.set_mode("objects")
            elif key == ord('2'):
                self.set_mode("faces")
            elif key == ord('3'):
                self.set_mode("hands")
            elif key == ord('4'):
                self.set_mode("qr")
            elif key == ord('5'):
                self.set_mode("ocr")
            elif key == ord('6'):
                self.set_mode("color")
            elif key == ord('i'):
                self._show_info()
        
        self.stop_camera()
    
    # ============================================
    # TESPİT FONKSİYONLARI
    # ============================================
    
    def _detect_objects_by_color(self, frame):
        """Renk tabanlı basit nesne tespiti"""
        self.detected_objects = []
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        for color_name, (lower, upper) in self.color_ranges.items():
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 1000:  # Küçük gürültüleri ele
                    x, y, w, h = cv2.boundingRect(contour)
                    self.detected_objects.append({
                        "name": color_name,
                        "confidence": 0.8,
                        "bbox": (x, y, x+w, y+h),
                        "info": self.object_info.get(color_name, {})
                    })
                    
                    # AR mesaj
                    self.ar_messages.append({
                        "text": f"🎨 {color_name} nesne tespit edildi",
                        "time": time.time()
                    })
    
    def _detect_faces_mediapipe(self, frame):
        """MediaPipe ile yüz tespiti"""
        self.detected_faces = []
        
        if not MEDIAPIPE_AVAILABLE or not self.face_detection:
            return
        
        # RGB'ye çevir
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(rgb)
        
        if results.detections:
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                h, w, _ = frame.shape
                
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)
                
                # Güven skoru
                confidence = detection.score[0]
                
                self.detected_faces.append({
                    "name": f"Yüz {len(self.detected_faces)+1}",
                    "bbox": (x, y, x+width, y+height),
                    "confidence": confidence,
                    "color": (0, 255, 0)
                })
    
    def _detect_hands(self, frame):
        """MediaPipe ile el tespiti"""
        self.detected_hands = []
        
        if not MEDIAPIPE_AVAILABLE or not self.hands:
            return
        
        # RGB'ye çevir
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # El koordinatlarını topla
                h, w, _ = frame.shape
                x_coords = [lm.x * w for lm in hand_landmarks.landmark]
                y_coords = [lm.y * h for lm in hand_landmarks.landmark]
                
                x1 = int(min(x_coords))
                y1 = int(min(y_coords))
                x2 = int(max(x_coords))
                y2 = int(max(y_coords))
                
                self.detected_hands.append({
                    "bbox": (x1, y1, x2, y2),
                    "landmarks": hand_landmarks
                })
                
                # Landmark'ları çiz
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
    
    def _detect_qr_codes(self, frame):
        """QR kod ve barkod tespiti"""
        self.detected_codes = []
        
        if not PYZBAR_AVAILABLE:
            return
        
        codes = decode(frame)
        for code in codes:
            code_data = code.data.decode('utf-8')
            code_type = code.type
            
            # Poligon çiz
            pts = code.polygon
            if len(pts) == 4:
                pts = [(pt.x, pt.y) for pt in pts]
                pts = np.array(pts, np.int32).reshape((-1, 1, 2))
                
                self.detected_codes.append({
                    "type": code_type,
                    "data": code_data,
                    "points": pts
                })
                
                self.ar_messages.append({
                    "text": f"📱 {code_type}: {code_data[:30]}...",
                    "time": time.time()
                })
    
    def _detect_text(self, frame):
        """OCR ile yazı tanıma"""
        if not TESSERACT_AVAILABLE:
            return
        
        # Gri tonlamaya çevir
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Threshold uygula
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        try:
            text = pytesseract.image_to_string(thresh, lang='tur+eng')
            if text.strip():
                self.detected_text = text.strip()
        except:
            pass
    
    def _detect_color_at_center(self, frame):
        """Merkezdeki rengi analiz et"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        height, width = frame.shape[:2]
        center_x, center_y = width // 2, height // 2
        
        # Merkezdeki rengi bul
        roi = hsv[center_y-10:center_y+10, center_x-10:center_x+10]
        avg_color = np.mean(roi, axis=(0, 1))
        
        # Renge isim bul
        detected_color = "bilinmiyor"
        for color_name, (lower, upper) in self.color_ranges.items():
            lower = np.array(lower)
            upper = np.array(upper)
            if np.all(avg_color >= lower) and np.all(avg_color <= upper):
                detected_color = color_name
                break
        
        cv2.putText(frame, f"Renk: {detected_color}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    def _draw_overlay(self, frame):
        """AR overlay çiz"""
        height, width = frame.shape[:2]
        
        # Mod bilgisi
        mode_text = f"Mod: {self.current_mode}"
        cv2.putText(frame, mode_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Kontrol bilgileri
        controls = [
            "1:Nesne 2:Yüz 3:El 4:QR 5:OCR 6:Renk",
            "s:Fotoğraf çek q:Çıkış i:Bilgi"
        ]
        y = 60
        for control in controls:
            cv2.putText(frame, control, (10, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y += 20
        
        # Renk tabanlı nesneleri çiz
        for obj in self.detected_objects:
            x1, y1, x2, y2 = obj["bbox"]
            name = obj["name"]
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, name, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Yüzleri çiz
        for face in self.detected_faces:
            x1, y1, x2, y2 = face["bbox"]
            conf = face.get("confidence", 0)
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"Yüz (%{conf*100:.0f})", (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Elleri çiz
        for hand in self.detected_hands:
            x1, y1, x2, y2 = hand["bbox"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(frame, "El", (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        
        # QR kodları çiz
        for code in self.detected_codes:
            pts = code["points"]
            cv2.polylines(frame, [pts], True, (255, 0, 0), 3)
            
            x = pts[0][0][0]
            y = pts[0][0][1] - 10
            cv2.putText(frame, f"{code['type']}", (x, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        
        # AR mesajlarını göster
        current_time = time.time()
        self.ar_messages = [msg for msg in self.ar_messages if current_time - msg["time"] < 3]
        
        y = height - 30
        for msg in reversed(self.ar_messages):
            cv2.putText(frame, msg["text"], (10, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            y -= 20
    
    def _save_snapshot(self, frame):
        """Anlık görüntü kaydet"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.data_dir / f"snapshot_{timestamp}.jpg"
        cv2.imwrite(str(filename), frame)
        self.ar_messages.append({
            "text": f"📸 Fotoğraf kaydedildi",
            "time": time.time()
        })
    
    def _show_info(self):
        """AR bilgi ekranı"""
        info = np.zeros((400, 500, 3), dtype=np.uint8)
        y = 30
        
        cv2.putText(info, "A.N.N.A Hafif AR", (50, y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        y += 40
        
        cv2.putText(info, f"Mod: {self.current_mode}", (50, y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        y += 30
        
        cv2.putText(info, f"Nesneler: {len(self.detected_objects)}", (50, y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        y += 30
        
        cv2.putText(info, f"Yüzler: {len(self.detected_faces)}", (50, y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        y += 30
        
        cv2.putText(info, f"Eller: {len(self.detected_hands)}", (50, y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        y += 30
        
        cv2.putText(info, f"QR Kodlar: {len(self.detected_codes)}", (50, y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        y += 50
        
        cv2.putText(info, "Kontroller:", (50, y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        y += 30
        
        controls = [
            "1: Renkli Nesneler",
            "2: Yüz Tespiti",
            "3: El Tespiti",
            "4: QR/Barkod",
            "5: OCR (Yazı)",
            "6: Renk Analizi",
            "s: Fotoğraf Çek",
            "q: Çıkış"
        ]
        
        for control in controls:
            cv2.putText(info, control, (70, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            y += 25
        
        cv2.imshow('A.N.N.A AR Bilgi', info)
        cv2.waitKey(3000)
        cv2.destroyWindow('A.N.N.A AR Bilgi')
    
    # ============================================
    # DURUM BİLGİLERİ
    # ============================================
    
    def get_status(self):
        """AR durumunu döndür"""
        return {
            "active": self.active,
            "mode": self.current_mode,
            "objects": len(self.detected_objects),
            "faces": len(self.detected_faces),
            "hands": len(self.detected_hands),
            "codes": len(self.detected_codes),
            "text": bool(self.detected_text)
        }
    
    def get_detection_summary(self):
        """Tespit özeti"""
        summary = f"🔮 AR Mod: {self.current_mode}\n\n"
        
        if self.detected_objects:
            summary += f"📦 Nesneler ({len(self.detected_objects)}):\n"
            for obj in self.detected_objects[:5]:
                summary += f"  • {obj['name']}\n"
        
        if self.detected_faces:
            summary += f"👤 Yüzler ({len(self.detected_faces)})\n"
        
        if self.detected_hands:
            summary += f"🤚 Eller ({len(self.detected_hands)})\n"
        
        if self.detected_codes:
            summary += f"📱 Kodlar ({len(self.detected_codes)})\n"
        
        if self.detected_text:
            summary += f"📝 Yazı: {self.detected_text[:100]}...\n"
        
        return summary
