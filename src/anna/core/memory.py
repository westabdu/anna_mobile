# core/memory.py
"""
JARVIS'in hafıza sistemi
- Kullanıcı bilgilerini hatırla
- Konuşma geçmişini sakla
- Önemli notları tut
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from loguru import logger

class Memory:
    """
    JARVIS'in uzun süreli hafızası
    - SQLite veritabanı kullanır
    - Kullanıcı profili
    - Konuşma geçmişi
    - Önemli notlar
    """
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        logger.success(f"✅ Hafıza sistemi başlatıldı: {db_path}")
    
    def _init_database(self):
        """Veritabanı tablolarını oluştur"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Kullanıcı profili tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profile (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Konuşma geçmişi tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_input TEXT,
                jarvis_response TEXT,
                mood TEXT
            )
        ''')
        
        # Önemli notlar tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                title TEXT,
                content TEXT,
                category TEXT
            )
        ''')
        
        # İstatistikler tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE,
                conversations_count INTEGER DEFAULT 0,
                commands_used TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ---------- KULLANICI PROFİLİ ----------
    
    def set_profile(self, key: str, value: str):
        """Kullanıcı bilgisi kaydet"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO profile (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (key, value))
        conn.commit()
        conn.close()
        logger.debug(f"📝 Profil kaydedildi: {key}={value}")
    
    def get_profile(self, key: str) -> Optional[str]:
        """Kullanıcı bilgisi oku"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM profile WHERE key = ?', (key,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def get_all_profile(self) -> Dict[str, str]:
        """Tüm profil bilgilerini al"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('SELECT key, value FROM profile')
        results = cursor.fetchall()
        conn.close()
        return {key: value for key, value in results}
    
    # ---------- KONUŞMA GEÇMİŞİ ----------
    
    def add_conversation(self, user_input: str, jarvis_response: str, mood: str = "professional"):
        """Konuşmayı kaydet"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO conversations (user_input, jarvis_response, mood)
            VALUES (?, ?, ?)
        ''', (user_input, jarvis_response, mood))
        conn.commit()
        conn.close()
        
        # İstatistikleri güncelle
        self._update_stats()
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """Son konuşmaları getir"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp, user_input, jarvis_response, mood
            FROM conversations
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                "timestamp": row[0],
                "user": row[1],
                "jarvis": row[2],
                "mood": row[3]
            }
            for row in results
        ]
    
    def search_conversations(self, keyword: str) -> List[Dict]:
        """Konuşmalarda ara"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp, user_input, jarvis_response
            FROM conversations
            WHERE user_input LIKE ? OR jarvis_response LIKE ?
            ORDER BY timestamp DESC
            LIMIT 20
        ''', (f'%{keyword}%', f'%{keyword}%'))
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                "timestamp": row[0],
                "user": row[1],
                "jarvis": row[2]
            }
            for row in results
        ]
    
    # ---------- NOTLAR ----------
    
    def add_note(self, title: str, content: str, category: str = "general"):
        """Not ekle"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO notes (title, content, category)
            VALUES (?, ?, ?)
        ''', (title, content, category))
        conn.commit()
        note_id = cursor.lastrowid
        conn.close()
        logger.info(f"📌 Not eklendi: {title}")
        return note_id
    
    def get_notes(self, category: Optional[str] = None) -> List[Dict]:
        """Notları getir"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        if category:
            cursor.execute('''
                SELECT id, timestamp, title, content, category
                FROM notes
                WHERE category = ?
                ORDER BY timestamp DESC
            ''', (category,))
        else:
            cursor.execute('''
                SELECT id, timestamp, title, content, category
                FROM notes
                ORDER BY timestamp DESC
            ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "timestamp": row[1],
                "title": row[2],
                "content": row[3],
                "category": row[4]
            }
            for row in results
        ]
    
    # ---------- İSTATİSTİKLER ----------
    
    def _update_stats(self):
        """Günlük konuşma sayısını güncelle"""
        today = datetime.now().date()
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO stats (date, conversations_count)
            VALUES (?, 1)
            ON CONFLICT(date) DO UPDATE SET
                conversations_count = conversations_count + 1
        ''', (today.isoformat(),))
        
        conn.commit()
        conn.close()
    
    def get_stats(self, days: int = 7) -> Dict:
        """İstatistikleri getir"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Toplam konuşma
        cursor.execute('SELECT COUNT(*) FROM conversations')
        total_conversations = cursor.fetchone()[0]
        
        # Son 7 günlük konuşma sayısı
        week_ago = (datetime.now() - timedelta(days=days)).date()
        cursor.execute('''
            SELECT SUM(conversations_count)
            FROM stats
            WHERE date >= ?
        ''', (week_ago.isoformat(),))
        weekly_conversations = cursor.fetchone()[0] or 0
        
        # En çok konuşulan saat
        cursor.execute('''
            SELECT strftime('%H', timestamp) as hour, COUNT(*)
            FROM conversations
            GROUP BY hour
            ORDER BY COUNT(*) DESC
            LIMIT 1
        ''')
        peak_hour = cursor.fetchone()
        
        conn.close()
        
        return {
            "total_conversations": total_conversations,
            f"last_{days}_days": weekly_conversations,
            "peak_hour": peak_hour[0] if peak_hour else "00",
            "peak_hour_count": peak_hour[1] if peak_hour else 0
        }
    
    def clear_history(self, days: Optional[int] = None):
        """Geçmişi temizle"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        if days:
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            cursor.execute('DELETE FROM conversations WHERE timestamp < ?', (cutoff,))
        else:
            cursor.execute('DELETE FROM conversations')
        
        conn.commit()
        deleted = cursor.rowcount
        conn.close()
        
        logger.info(f"🗑️ {deleted} konuşma silindi")