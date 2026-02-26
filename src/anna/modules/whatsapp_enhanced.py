# modules/whatsapp_enhanced.py
"""
Gelişmiş WhatsApp modülü - AR bildirimleri, web kontrolü, OCR entegrasyonu
"""
import webbrowser
import time
import pyautogui
import subprocess
import os
from datetime import datetime
import threading
import requests
from bs4 import BeautifulSoup

class WhatsAppEnhanced:
    def __init__(self):
        self.web_whatsapp_url = "https://web.whatsapp.com"
        self.is_web_open = False
        self.contacts = {}  # Rehber
        self.notifications = []
        self.last_check = datetime.now()
        print("📱 Gelişmiş WhatsApp modülü hazır")
    
    def open_web_whatsapp(self):
        """WhatsApp Web'i aç"""
        webbrowser.open(self.web_whatsapp_url)
        self.is_web_open = True
        time.sleep(5)  # Yüklenmesini bekle
        return "✅ WhatsApp Web açıldı"
    
    def search_and_send(self, contact_name, message):
        """WhatsApp Web'de kişi ara ve mesaj gönder"""
        if not self.is_web_open:
            self.open_web_whatsapp()
            time.sleep(3)
        
        try:
            # Arama kutusuna tıkla
            pyautogui.click(200, 150)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.write(contact_name)
            time.sleep(2)
            
            # Kişiye tıkla
            pyautogui.click(200, 250)
            time.sleep(1)
            
            # Mesaj kutusuna tıkla ve yaz
            pyautogui.click(500, 800)
            pyautogui.write(message)
            time.sleep(1)
            
            # Gönder
            pyautogui.press('enter')
            
            return f"✅ {contact_name}'e mesaj gönderildi: {message[:30]}..."
        except Exception as e:
            return f"❌ Hata: {str(e)}"
    
    def send_with_ocr(self, contact_name, ocr_text):
        """OCR'den gelen metni WhatsApp'tan gönder"""
        return self.search_and_send(contact_name, f"📝 OCR ile okunan metin:\n\n{ocr_text}")
    
    def check_new_messages(self):
        """Yeni mesajları kontrol et (AR için)"""
        # Bu fonksiyon AR modülü tarafından çağrılacak
        if not self.is_web_open:
            return []
        
        # Ekran görüntüsü al ve yeni mesajları bul
        # (gerçek uygulamada selenium kullanılabilir)
        return self.notifications
    
    def show_ar_notification(self, frame, sender, message):
        """AR'da süzülen bildirim göster"""
        import cv2
        
        # Bildirim kutusu çiz
        x, y = 50, 50
        w, h = 400, 80
        
        # Arka plan
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 150, 0), -1)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Metinler
        cv2.putText(frame, f"📱 WhatsApp - {sender}", (x + 10, y + 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, message[:40] + "...", (x + 10, y + 55),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
    
    def add_contact(self, name, number):
        """Rehbere kişi ekle"""
        self.contacts[name] = number
        return f"✅ {name} rehbere eklendi"