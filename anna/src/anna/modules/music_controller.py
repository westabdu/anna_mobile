# modules/music_controller.py
"""
Gelişmiş müzik kontrolü - Spotify, YouTube ve duygu bazlı çalma
"""
import webbrowser
import pyautogui
import time
import subprocess
import requests
from urllib.parse import quote
import random

class MusicController:
    def __init__(self):
        self.current_platform = None
        self.is_playing = False
        self.current_song = None
        self.current_playlist = None
        self.volume = 50
        
        # Duygu bazlı çalma listeleri
        self.mood_playlists = {
            "calm": [
                "lofi hip hop",
                "calm piano",
                "relaxing music",
                "meditation music",
                "rain sounds"
            ],
            "happy": [
                "pop hits",
                "happy songs",
                "upbeat music",
                "dance music",
                "feel good songs"
            ],
            "energetic": [
                "workout music",
                "edm",
                "rock",
                "gym music",
                "motivation music"
            ],
            "sad": [
                "sad songs",
                "melancholic",
                "piano",
                "emotional music",
                "crying songs"
            ],
            "focus": [
                "lofi study",
                "focus music",
                "concentration music",
                "instrumental",
                "classical"
            ]
        }
        
        print("🎵 Müzik kontrol modülü hazır")
    
    def play_on_youtube(self, query):
        """YouTube'da müzik aç"""
        try:
            search_url = f"https://www.youtube.com/results?search_query={quote(query)}"
            webbrowser.open(search_url)
            time.sleep(3)
            
            # İlk videoya tıkla
            pyautogui.click(500, 400)
            
            self.current_platform = "youtube"
            self.is_playing = True
            self.current_song = query
            return f"▶️ YouTube'da '{query}' çalınıyor"
        except Exception as e:
            return f"❌ YouTube hatası: {str(e)}"
    
    def play_on_spotify(self, query):
        """Spotify'da müzik aç"""
        try:
            # Spotify desktop uygulamasını aç
            subprocess.Popen(["start", "spotify:"], shell=True)
            time.sleep(3)
            
            # Ara
            pyautogui.hotkey('ctrl', 'l')
            pyautogui.write(query)
            pyautogui.press('enter')
            time.sleep(2)
            
            # İlk şarkıya tıkla
            pyautogui.click(500, 300)
            pyautogui.doubleClick()
            
            self.current_platform = "spotify"
            self.is_playing = True
            self.current_song = query
            return f"▶️ Spotify'da '{query}' çalınıyor"
        except Exception as e:
            return f"❌ Spotify hatası: {str(e)}"
    
    def play_by_mood(self, mood):
        """Duygu durumuna göre müzik çal"""
        if mood in self.mood_playlists:
            playlists = self.mood_playlists[mood]
            playlist = random.choice(playlists)
            return self.play_on_youtube(playlist)
        else:
            return self.play_on_youtube("popular music")
    
    def pause(self):
        """Müziği durdur/başlat"""
        pyautogui.press('space')
        self.is_playing = not self.is_playing
        return "⏸️ Müzik durduruldu" if not self.is_playing else "▶️ Müzik devam ediyor"
    
    def next(self):
        """Sonraki şarkı"""
        pyautogui.hotkey('shift', 'n')  # YouTube kısayolu
        return "⏭️ Sonraki şarkı"
    
    def previous(self):
        """Önceki şarkı"""
        pyautogui.hotkey('shift', 'p')  # YouTube kısayolu
        return "⏮️ Önceki şarkı"
    
    def set_volume(self, volume):
        """Ses seviyesini ayarla"""
        self.volume = max(0, min(100, volume))
        for i in range(50):
            pyautogui.press('volumeup' if volume > 50 else 'volumedown')
        return f"🔊 Ses: %{self.volume}"
    
    def get_current_status(self):
        """Şu anki çalma durumunu göster"""
        if self.is_playing:
            return f"▶️ Çalıyor: {self.current_song} ({self.current_platform})"
        else:
            return "⏹️ Müzik durduruldu"