# modules/emotion_detection.py
"""
Duygu analizi modülü - Yüz ifadelerinden duygu tanıma ve UI senkronizasyonu
"""
import cv2
import numpy as np
import threading
import time
import random
from deepface import DeepFace

class EmotionDetector:
    def __init__(self):
        self.current_emotion = "neutral"
        self.emotion_history = []
        self.last_emotion_time = time.time()
        self.active = False
        self.confidence = 0.0
        self.emotions_colors = {
            "angry": "#ff4444",      # Kırmızı (öfkeli)
            "disgust": "#8B4513",     # Kahverengi (iğrenmiş)
            "fear": "#800080",        # Mor (korkmuş)
            "happy": "#FFD700",       # Sarı (mutlu)
            "sad": "#4169E1",         # Mavi (üzgün)
            "surprise": "#FFA500",    # Turuncu (şaşırmış)
            "neutral": "#A9A9A9",     # Gri (nötr)
            "calm": "#90EE90",        # Açık yeşil (sakin)
            "tired": "#808080"        # Koyu gri (yorgun)
        }
        
        # Duyguya göre yapılacak aksiyonlar
        self.emotion_actions = {
            "angry": {
                "music": "calm music",
                "color": "#87CEEB",  # Açık mavi (sakinleştirici)
                "message": "😤 Öfkeli görünüyorsun. Sakinleşmek için müzik açayım mı?"
            },
            "sad": {
                "music": "happy music",
                "color": "#FFD700",  # Sarı (mutlu edici)
                "message": "😢 Üzgün görünüyorsun. Neşelenmek için bir şarkı açayım mı?"
            },
            "tired": {
                "music": "lofi music",
                "color": "#98FB98",  # Açık yeşil
                "message": "😴 Yorgun görünüyorsun. Dinlendirici müzik açayım mı?"
            },
            "happy": {
                "music": "energetic music",
                "color": "#FF69B4",  # Pembe
                "message": "😊 Mutlu görünüyorsun! Bu havaya uygun bir şarkı açayım mı?"
            },
            "stressed": {
                "music": "meditation music",
                "color": "#98FB98",
                "message": "😰 Stresli görünüyorsun. Meditasyon müziği açayım mı?"
            }
        }
        
        print("😊 Duygu analizi modülü hazır")
    
    def start_detection(self):
        """Duygu analizini başlat"""
        self.active = True
        threading.Thread(target=self._detect_loop, daemon=True).start()
        return "✅ Duygu analizi başlatıldı"
    
    def stop_detection(self):
        """Duygu analizini durdur"""
        self.active = False
        return "⏹️ Duygu analizi durduruldu"
    
    def _detect_loop(self):
        """Ana analiz döngüsü"""
        cap = cv2.VideoCapture(0)
        
        while self.active:
            ret, frame = cap.read()
            if not ret:
                continue
            
            # Her 3 saniyede bir analiz yap
            if time.time() - self.last_emotion_time > 3:
                try:
                    # DeepFace ile duygu analizi
                    result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                    if result and len(result) > 0:
                        emotions = result[0]['emotion']
                        self.current_emotion = max(emotions, key=emotions.get)
                        self.confidence = emotions[self.current_emotion]
                        self.emotion_history.append({
                            'emotion': self.current_emotion,
                            'confidence': self.confidence,
                            'time': time.time()
                        })
                        self.last_emotion_time = time.time()
                except Exception as e:
                    print(f"Duygu analizi hatası: {e}")
            
            # Yüz çerçevesi ve duygu bilgisi çiz
            cv2.putText(frame, f"Duygu: {self.current_emotion} ({self.confidence:.1f}%)", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            cv2.imshow('A.N.N.A Duygu Analizi', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
    
    def get_emotion_color(self):
        """Duyguya göre renk döndür"""
        return self.emotions_colors.get(self.current_emotion, "#FFFFFF")
    
    def should_change_mood(self):
        """Duygu değişikliği varsa true döndür"""
        if len(self.emotion_history) < 2:
            return False
        
        last_two = self.emotion_history[-2:]
        return last_two[0]['emotion'] != last_two[1]['emotion']
    
    def get_suggested_action(self):
        """Duyguya göre önerilen aksiyon"""
        # Eğer 3 kez aynı olumsuz duygu varsa aksiyon öner
        if len(self.emotion_history) < 3:
            return None
        
        last_three = self.emotion_history[-3:]
        emotions = [e['emotion'] for e in last_three]
        
        if all(e in ["angry", "sad", "tired"] for e in emotions):
            most_common = max(set(emotions), key=emotions.count)
            return self.emotion_actions.get(most_common)
        
        return None
    
    def get_emotion_stats(self):
        """Duygu istatistiklerini döndür"""
        if not self.emotion_history:
            return "Henüz veri yok"
        
        total = len(self.emotion_history)
        emotion_counts = {}
        
        for e in self.emotion_history:
            emotion = e['emotion']
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        stats = "📊 **Duygu İstatistikleri**\n"
        for emotion, count in emotion_counts.items():
            percentage = (count / total) * 100
            stats += f"{emotion}: %{percentage:.1f}\n"
        
        return stats