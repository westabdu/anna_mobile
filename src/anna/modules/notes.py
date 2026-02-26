# modules/notes.py
"""
Not defteri modülü
"""
import json
from datetime import datetime
from pathlib import Path
from loguru import logger

class NotesManager:
    """Not alma ve yönetme"""
    
    def __init__(self):
        self.data_dir = Path("data/notes")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.notes_file = self.data_dir / "notes.json"
        self.notes = self._load_notes()
        logger.info("📝 Not defteri modülü hazır")
    
    def _load_notes(self):
        """Notları yükle"""
        if self.notes_file.exists():
            try:
                with open(self.notes_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_notes(self):
        """Notları kaydet"""
        with open(self.notes_file, 'w', encoding='utf-8') as f:
            json.dump(self.notes, f, indent=2, ensure_ascii=False)
    
    def add_note(self, title, content, category="Genel"):
        """Not ekle"""
        note = {
            "id": len(self.notes) + 1,
            "title": title,
            "content": content,
            "category": category,
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat()
        }
        self.notes.append(note)
        self._save_notes()
        return f"✅ Not eklendi: {title}"
    
    def get_note(self, note_id):
        """Notu getir"""
        for note in self.notes:
            if note["id"] == note_id:
                created = datetime.fromisoformat(note["created"]).strftime("%d.%m.%Y %H:%M")
                return f"""
📝 **{note['title']}**
📂 {note['category']}
📅 {created}

{note['content']}
"""
        return f"❌ Not bulunamadı (ID: {note_id})"
    
    def update_note(self, note_id, content):
        """Notu güncelle"""
        for note in self.notes:
            if note["id"] == note_id:
                note["content"] = content
                note["updated"] = datetime.now().isoformat()
                self._save_notes()
                return f"✅ Not güncellendi: {note['title']}"
        return f"❌ Not bulunamadı (ID: {note_id})"
    
    def delete_note(self, note_id):
        """Notu sil"""
        for i, note in enumerate(self.notes):
            if note["id"] == note_id:
                title = note["title"]
                self.notes.pop(i)
                self._save_notes()
                return f"✅ Not silindi: {title}"
        return f"❌ Not bulunamadı (ID: {note_id})"
    
    def list_notes(self, category=None):
        """Notları listele"""
        notes_to_show = self.notes
        
        if category:
            notes_to_show = [n for n in self.notes if n["category"] == category]
        
        if not notes_to_show:
            return "📭 Not bulunamadı"
        
        result = "📝 **NOTLAR**\n\n"
        for note in notes_to_show[:10]:
            created = datetime.fromisoformat(note["created"]).strftime("%d.%m")
            result += f"📌 [{note['id']}] {note['title']} ({created})\n"
        
        if len(notes_to_show) > 10:
            result += f"\n... ve {len(notes_to_show)-10} not daha"
        
        return result
    
    def search_notes(self, keyword):
        """Notlarda ara"""
        results = []
        for note in self.notes:
            if keyword.lower() in note['title'].lower() or keyword.lower() in note['content'].lower():
                results.append(note)
        
        if not results:
            return f"🔍 '{keyword}' için not bulunamadı"
        
        result = f"🔍 **ARAMA SONUÇLARI** ('{keyword}')\n\n"
        for note in results[:5]:
            result += f"📌 {note['title']}\n"
        
        return result
    
    def get_categories(self):
        """Kategorileri listele"""
        categories = set(note['category'] for note in self.notes)
        return "📂 **KATEGORİLER**\n" + "\n".join(f"• {c}" for c in categories)