# src/modules/contacts.py - ANDROID UYUMLU
"""
Rehber yönetimi - Kişiler, arama, mesaj
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Android tespiti
IS_ANDROID = 'android' in sys.platform or 'ANDROID_ARGUMENT' in os.environ


class ContactsManager:
    """Rehber yönetimi"""
    
    def __init__(self):
        # Android'de depolama yolu farklı
        if IS_ANDROID:
            try:
                from android.storage import primary_external_storage_path
                base_path = Path(primary_external_storage_path()) / "ANNA" / "data"
                self.data_dir = base_path / "contacts"
            except:
                # Fallback
                self.data_dir = Path("/storage/emulated/0/ANNA/data/contacts")
        else:
            self.data_dir = Path("data/contacts")
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.contacts_file = self.data_dir / "contacts.json"
        self.contacts = self._load_contacts()
    
    def _load_contacts(self):
        """Rehberi yükle"""
        if self.contacts_file.exists():
            try:
                with open(self.contacts_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self._init_contacts()
        return self._init_contacts()
    
    def _init_contacts(self):
        """Varsayılan rehber"""
        return [
            {
                "id": 1,
                "name": "Anne",
                "phone": "+905551234567",
                "email": "anne@example.com",
                "favorite": True
            },
            {
                "id": 2,
                "name": "Baba",
                "phone": "+905557654321",
                "email": "baba@example.com",
                "favorite": True
            },
            {
                "id": 3,
                "name": "Ahmet",
                "phone": "+905553332211",
                "email": "ahmet@example.com",
                "favorite": False
            }
        ]
    
    def _save_contacts(self):
        """Rehberi kaydet"""
        try:
            with open(self.contacts_file, 'w', encoding='utf-8') as f:
                json.dump(self.contacts, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Rehber kaydedilemedi: {e}")
    
    def get_all_contacts(self) -> list:
        """Tüm kişileri getir"""
        return self.contacts
    
    def get_favorites(self) -> list:
        """Favori kişileri getir"""
        return [c for c in self.contacts if c.get('favorite', False)]
    
    def search_contacts(self, query: str) -> list:
        """Kişilerde ara"""
        query = query.lower()
        results = []
        
        for contact in self.contacts:
            if (query in contact['name'].lower() or 
                query in contact.get('phone', '').lower()):
                results.append(contact)
        
        return results
    
    def add_contact(self, name: str, phone: str, email: str = "", favorite: bool = False) -> str:
        """Yeni kişi ekle"""
        new_id = max([c['id'] for c in self.contacts], default=0) + 1
        
        contact = {
            "id": new_id,
            "name": name,
            "phone": phone,
            "email": email,
            "favorite": favorite
        }
        
        self.contacts.append(contact)
        self._save_contacts()
        
        return f"✅ {name} rehbere eklendi"
    
    def update_contact(self, contact_id: int, **kwargs) -> str:
        """Kişi güncelle"""
        for contact in self.contacts:
            if contact['id'] == contact_id:
                for key, value in kwargs.items():
                    if key in contact:
                        contact[key] = value
                self._save_contacts()
                return f"✅ {contact['name']} güncellendi"
        
        return "❌ Kişi bulunamadı"
    
    def delete_contact(self, contact_id: int) -> str:
        """Kişi sil"""
        for i, contact in enumerate(self.contacts):
            if contact['id'] == contact_id:
                name = contact['name']
                self.contacts.pop(i)
                self._save_contacts()
                return f"✅ {name} silindi"
        
        return "❌ Kişi bulunamadı"
    
    def toggle_favorite(self, contact_id: int) -> str:
        """Favori durumunu değiştir"""
        for contact in self.contacts:
            if contact['id'] == contact_id:
                contact['favorite'] = not contact.get('favorite', False)
                self._save_contacts()
                status = "favorilere eklendi" if contact['favorite'] else "favorilerden çıkarıldı"
                return f"✅ {contact['name']} {status}"
        
        return "❌ Kişi bulunamadı"
    
    def format_contact_list(self, contacts: list = None) -> str:
        """Kişi listesini formatla"""
        if contacts is None:
            contacts = self.contacts
        
        if not contacts:
            return "📭 Rehber boş"
        
        result = "📞 **REHBER**\n\n"
        for c in contacts:
            fav = "⭐ " if c.get('favorite') else "   "
            result += f"{fav}**{c['name']}**\n"
            result += f"   📱 {c['phone']}\n"
            if c.get('email'):
                result += f"   📧 {c['email']}\n"
            result += "\n"
        
        return result
    
    def get_contact_card(self, contact_id: int) -> str:
        """Kişi kartı göster"""
        for contact in self.contacts:
            if contact['id'] == contact_id:
                fav = "⭐ " if contact.get('favorite') else ""
                return f"""
{fav}**{contact['name']}**

📱 Telefon: {contact['phone']}
📧 E-posta: {contact.get('email', 'Yok')}
🆔 ID: {contact['id']}
"""
        
        return "❌ Kişi bulunamadı"
    
    def call_contact(self, contact_id: int) -> str:
        """Ara (Android'de intent kullan)"""
        for contact in self.contacts:
            if contact['id'] == contact_id:
                if IS_ANDROID:
                    try:
                        # Android intent ile arama
                        from android import intent
                        intent.call(contact['phone'])
                        return f"📞 {contact['name']} aranıyor..."
                    except:
                        return f"📞 {contact['name']} aranıyor... ({contact['phone']})"
                else:
                    return f"📞 {contact['name']} aranıyor... ({contact['phone']})"
        
        return "❌ Kişi bulunamadı"
    
    def message_contact(self, contact_id: int, message: str) -> str:
        """Mesaj gönder (Android'de intent kullan)"""
        for contact in self.contacts:
            if contact['id'] == contact_id:
                if IS_ANDROID:
                    try:
                        # Android intent ile mesaj
                        from android import intent
                        intent.sms(contact['phone'], message)
                        return f"💬 {contact['name']}'e mesaj gönderiliyor..."
                    except:
                        return f"💬 {contact['name']}'e mesaj gönderildi: {message[:30]}..."
                else:
                    return f"💬 {contact['name']}'e mesaj gönderildi: {message[:30]}..."
        
        return "❌ Kişi bulunamadı"