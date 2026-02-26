# modules/music.py
"""
Müzik çalar modülü
"""
import os
import random
import threading
import time
from pathlib import Path
import pygame
from loguru import logger

class MusicPlayer:
    """Müzik çalar ve çalma listesi yöneticisi"""
    
    def __init__(self):
        pygame.mixer.init()
        self.music_dir = Path("data/music")
        self.music_dir.mkdir(parents=True, exist_ok=True)
        self.playlist = []
        self.current_index = -1
        self.is_playing = False
        self.is_paused = False
        self.volume = 50
        self._load_playlist()
        logger.info("🎵 Müzik çalar modülü hazır")
    
    def _load_playlist(self):
        """Müzik dosyalarını yükle"""
        self.playlist = []
        for ext in ['*.mp3', '*.wav', '*.ogg', '*.flac']:
            self.playlist.extend(list(self.music_dir.glob(ext)))
        self.playlist = [str(f) for f in self.playlist]
    
    def scan_music(self):
        """Müzik klasörünü tara"""
        self._load_playlist()
        return f"🎵 {len(self.playlist)} şarkı bulundu"
    
    def play(self, index=None):
        """Müzik çal"""
        if not self.playlist:
            return "❌ Çalma listesi boş"
        
        if index is not None:
            self.current_index = index % len(self.playlist)
        
        if self.current_index == -1:
            self.current_index = 0
        
        try:
            pygame.mixer.music.load(self.playlist[self.current_index])
            pygame.mixer.music.set_volume(self.volume / 100)
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
            
            song_name = Path(self.playlist[self.current_index]).stem
            return f"▶️ Çalıyor: {song_name}"
        except Exception as e:
            return f"❌ Çalma hatası: {str(e)}"
    
    def pause(self):
        """Duraklat"""
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            return "⏸️ Duraklatıldı"
        return "❌ Çalan müzik yok"
    
    def resume(self):
        """Devam et"""
        if self.is_playing and self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            return "▶️ Devam ediyor"
        return "❌ Duraklatılmış müzik yok"
    
    def stop(self):
        """Durdur"""
        if self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.is_paused = False
            return "⏹️ Müzik durduruldu"
        return "❌ Çalan müzik yok"
    
    def next(self):
        """Sonraki şarkı"""
        if not self.playlist:
            return "❌ Çalma listesi boş"
        
        self.current_index = (self.current_index + 1) % len(self.playlist)
        return self.play()
    
    def previous(self):
        """Önceki şarkı"""
        if not self.playlist:
            return "❌ Çalma listesi boş"
        
        self.current_index = (self.current_index - 1) % len(self.playlist)
        return self.play()
    
    def set_volume(self, volume):
        """Ses seviyesini ayarla (0-100)"""
        self.volume = max(0, min(100, volume))
        pygame.mixer.music.set_volume(self.volume / 100)
        return f"🔊 Ses: %{self.volume}"
    
    def shuffle(self):
        """Karışık çal"""
        if self.playlist:
            random.shuffle(self.playlist)
            self.current_index = 0
            return self.play()
        return "❌ Çalma listesi boş"
    
    def get_current_song(self):
        """Şu an çalan şarkıyı göster"""
        if self.is_playing and self.current_index >= 0:
            song_path = self.playlist[self.current_index]
            song_name = Path(song_path).stem
            status = "⏸️" if self.is_paused else "▶️"
            return f"{status} {song_name}"
        return "🎵 Çalan müzik yok"
    
    def get_playlist(self):
        """Çalma listesini göster"""
        if not self.playlist:
            return "📭 Çalma listesi boş"
        
        result = "🎵 **ÇALMA LİSTESİ**\n"
        for i, song in enumerate(self.playlist[:10]):
            name = Path(song).stem
            marker = "→ " if i == self.current_index else "  "
            result += f"{marker}{i+1}. {name}\n"
        
        if len(self.playlist) > 10:
            result += f"... ve {len(self.playlist)-10} şarkı daha"
        
        return result