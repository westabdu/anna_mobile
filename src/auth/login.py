# src/auth/login.py - GELİŞMİŞ VERSİYON (Varsayılan Şifre Düzeltildi)
"""
A.N.N.A Mobile - Gelişmiş Giriş Sistemi
- 🔢 PIN Kodu (4-6 haneli)
- 🎨 Desen Kilidi (3x3 nokta)
- 👆 Parmak İzi / Biyometrik
- ❓ Güvenlik Sorusu
- 🔒 Brute-force koruması
- 💾 Çoklu kullanıcı profili
- 🔑 Varsayılan şifre: 0000
"""

import hashlib
import json
import time
import os
import random
from pathlib import Path
from datetime import datetime, timedelta


class MobileAuth:
    """Gelişmiş mobil giriş yöneticisi"""
    
    def __init__(self):
        self.data_dir = Path("data/auth")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Dosyalar
        self.password_file = self.data_dir / "password.hash"
        self.pin_file = self.data_dir / "pin.hash"
        self.pattern_file = self.data_dir / "pattern.hash"
        self.security_file = self.data_dir / "security.json"
        self.settings_file = self.data_dir / "settings.json"
        self.log_file = self.data_dir / "auth.log"
        
        # Güvenlik ayarları
        self.max_attempts = 5
        self.lock_duration = 300  # 5 dakika
        self.login_attempts = 0
        self.locked_until = 0
        self.last_attempt_time = 0
        
        # Varsayılan şifre oluştur (0000)
        self._create_default_password()
        
        # Kullanıcı profili
        self.current_user = "default"
        self.users = self._load_users()
        
        # Yöntemler
        self.methods = {
            "password": bool(self.password_file.exists()),
            "pin": bool(self.pin_file.exists()),
            "pattern": bool(self.pattern_file.exists()),
            "biometric": self._check_biometric_support(),
            "security": bool(self.security_file.exists())
        }
        
        # Ayarlar
        self.settings = self._load_settings()
        
        # Log kaydı
        self._log("Giriş sistemi başlatıldı")
        print(f"🔐 Giriş Yöntemleri: {', '.join([k for k, v in self.methods.items() if v])}")
        if self.methods["password"]:
            print("🔑 Varsayılan şifre: 0000")
    
    def _create_default_password(self):
        """Varsayılan şifre oluştur (0000)"""
        if not self.password_file.exists():
            default_password = "0000"
            password_hash = hashlib.sha256(default_password.encode()).hexdigest()
            with open(self.password_file, 'w') as f:
                f.write(password_hash)
            print("✅ Varsayılan şifre oluşturuldu: 0000")
        
        if not self.pin_file.exists():
            default_pin = "0000"
            pin_hash = hashlib.sha256(default_pin.encode()).hexdigest()
            with open(self.pin_file, 'w') as f:
                f.write(pin_hash)
            print("✅ Varsayılan PIN oluşturuldu: 0000")
    
    def _load_users(self):
        """Kullanıcıları yükle"""
        users_file = self.data_dir / "users.json"
        if users_file.exists():
            with open(users_file, 'r') as f:
                return json.load(f)
        return {"default": {"name": "Ana Kullanıcı", "created": datetime.now().isoformat()}}
    
    def _save_users(self):
        """Kullanıcıları kaydet"""
        users_file = self.data_dir / "users.json"
        with open(users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def _load_settings(self):
        """Ayarları yükle"""
        if self.settings_file.exists():
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        return {
            "biometric_enabled": False,
            "auto_lock": True,
            "lock_timeout": 60,  # saniye
            "theme": "dark",
            "method": "password",  # password, pin, pattern, biometric
            "security_question": "",
            "security_answer": ""
        }
    
    def _save_settings(self):
        """Ayarları kaydet"""
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=2)
    
    def _log(self, message: str):
        """Log kaydı tut"""
        try:
            with open(self.log_file, 'a') as f:
                f.write(f"[{datetime.now().isoformat()}] {message}\n")
        except:
            pass
    
    def _check_biometric_support(self) -> bool:
        """Biyometrik destek kontrolü"""
        try:
            # Android için
            import android
            return True
        except:
            # Bilgisayar için simülasyon
            return True
    
    # ============================================
    # 1. PIN KODU (4-6 HANE)
    # ============================================
    
    def set_pin(self, pin: str) -> tuple:
        """PIN kodu belirle (4-6 hane)"""
        if not pin.isdigit():
            return False, "❌ PIN sadece rakamlardan oluşmalı"
        
        if len(pin) < 4 or len(pin) > 6:
            return False, "❌ PIN 4-6 hane arasında olmalı"
        
        pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        with open(self.pin_file, 'w') as f:
            f.write(pin_hash)
        
        self.methods["pin"] = True
        self._log("PIN kodu oluşturuldu")
        return True, "✅ PIN kodu kaydedildi"
    
    def check_pin(self, pin: str) -> tuple:
        """PIN kodu kontrolü"""
        if not self.pin_file.exists():
            return False, "❌ PIN kodu tanımlanmamış"
        
        # Kilit kontrolü
        if time.time() < self.locked_until:
            remaining = int((self.locked_until - time.time()) // 60)
            return False, f"🔒 {remaining} dakika bekleyin"
        
        with open(self.pin_file, 'r') as f:
            stored_hash = f.read().strip()
        
        pin_hash = hashlib.sha256(pin.encode()).hexdigest()
        
        if pin_hash == stored_hash:
            self.login_attempts = 0
            self._log("PIN ile başarılı giriş")
            return True, "✅ Giriş başarılı"
        else:
            return self._handle_failed_attempt()
    
    # ============================================
    # 2. DESEN KİLİDİ (3x3 NOKTA)
    # ============================================
    
    def set_pattern(self, pattern: str) -> tuple:
        """Desen kilidi belirle (örn: "123456789")"""
        # Desen formatı: 1-9 arası rakamlar, min 4 nokta
        if not pattern.isdigit():
            return False, "❌ Desen rakamlardan oluşmalı"
        
        if len(pattern) < 4 or len(pattern) > 9:
            return False, "❌ Desen 4-9 nokta arasında olmalı"
        
        # Aynı nokta tekrar edemez
        if len(set(pattern)) != len(pattern):
            return False, "❌ Aynı nokta iki kez kullanılamaz"
        
        pattern_hash = hashlib.sha256(pattern.encode()).hexdigest()
        with open(self.pattern_file, 'w') as f:
            f.write(pattern_hash)
        
        self.methods["pattern"] = True
        self._log("Desen kilidi oluşturuldu")
        return True, "✅ Desen kilidi kaydedildi"
    
    def check_pattern(self, pattern: str) -> tuple:
        """Desen kilidi kontrolü"""
        if not self.pattern_file.exists():
            return False, "❌ Desen kilidi tanımlanmamış"
        
        if time.time() < self.locked_until:
            remaining = int((self.locked_until - time.time()) // 60)
            return False, f"🔒 {remaining} dakika bekleyin"
        
        with open(self.pattern_file, 'r') as f:
            stored_hash = f.read().strip()
        
        pattern_hash = hashlib.sha256(pattern.encode()).hexdigest()
        
        if pattern_hash == stored_hash:
            self.login_attempts = 0
            self._log("Desen ile başarılı giriş")
            return True, "✅ Giriş başarılı"
        else:
            return self._handle_failed_attempt()
    
    def get_pattern_grid(self) -> list:
        """Desen grid'i oluştur (karışık sırada)"""
        numbers = list(range(1, 10))
        random.shuffle(numbers)
        return [numbers[i:i+3] for i in range(0, 9, 3)]
    
    # ============================================
    # 3. ŞİFRE (ESKİ, UYUMLULUK İÇİN)
    # ============================================
    
    def set_password(self, password: str) -> tuple:
        """Şifre belirle"""
        if len(password) < 4:
            return False, "❌ Şifre en az 4 karakter olmalı"
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        with open(self.password_file, 'w') as f:
            f.write(password_hash)
        
        self.methods["password"] = True
        self._log("Şifre oluşturuldu")
        return True, "✅ Şifre kaydedildi"
    
    def check_password(self, password: str) -> tuple:
        """Şifre kontrolü"""
        if not self.password_file.exists():
            # Acil durum: dosya yoksa varsayılan oluştur
            self._create_default_password()
        
        # Kilit kontrolü
        if time.time() < self.locked_until:
            remaining = int((self.locked_until - time.time()) // 60)
            return False, f"🔒 {remaining} dakika bekleyin"
        
        with open(self.password_file, 'r') as f:
            stored_hash = f.read().strip()
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if password_hash == stored_hash:
            self.login_attempts = 0
            self._log("Şifre ile başarılı giriş")
            return True, "✅ Giriş başarılı"
        else:
            return self._handle_failed_attempt()
    
    # ============================================
    # 4. GÜVENLİK SORUSU
    # ============================================
    
    def set_security_question(self, question: str, answer: str) -> tuple:
        """Güvenlik sorusu belirle"""
        if not question or not answer:
            return False, "❌ Soru ve cevap boş olamaz"
        
        security = {
            "question": question,
            "answer_hash": hashlib.sha256(answer.lower().strip().encode()).hexdigest()
        }
        
        with open(self.security_file, 'w') as f:
            json.dump(security, f, indent=2)
        
        self.methods["security"] = True
        self._log("Güvenlik sorusu oluşturuldu")
        return True, "✅ Güvenlik sorusu kaydedildi"
    
    def check_security_answer(self, answer: str) -> tuple:
        """Güvenlik sorusu cevabı kontrolü"""
        if not self.security_file.exists():
            return False, "❌ Güvenlik sorusu tanımlanmamış"
        
        if time.time() < self.locked_until:
            remaining = int((self.locked_until - time.time()) // 60)
            return False, f"🔒 {remaining} dakika bekleyin"
        
        with open(self.security_file, 'r') as f:
            security = json.load(f)
        
        answer_hash = hashlib.sha256(answer.lower().strip().encode()).hexdigest()
        
        if answer_hash == security["answer_hash"]:
            self.login_attempts = 0
            self._log("Güvenlik sorusu ile başarılı giriş")
            return True, "✅ Doğru cevap"
        else:
            return self._handle_failed_attempt()
    
    def get_security_question(self) -> str:
        """Güvenlik sorusunu getir"""
        if not self.security_file.exists():
            return None
        with open(self.security_file, 'r') as f:
            security = json.load(f)
        return security["question"]
    
    # ============================================
    # 5. BİYOMETRİK (PARMAK İZİ / YÜZ TANIMA)
    # ============================================
    
    def check_biometric(self) -> bool:
        """Biyometrik kontrol"""
        try:
            # Burada gerçek biyometrik API kullanılır
            # Şimdilik simülasyon
            time.sleep(1)  # Parmak izi okunuyor...
            self._log("Biyometrik ile başarılı giriş")
            return True
        except:
            self._handle_failed_attempt()
            return False
    
    def enable_biometric(self, enable: bool):
        """Biyometrik özelliğini aç/kapa"""
        self.settings["biometric_enabled"] = enable
        self._save_settings()
        self._log(f"Biyometrik {'açıldı' if enable else 'kapatıldı'}")
    
    # ============================================
    # 6. ORTAK FONKSİYONLAR
    # ============================================
    
    def _handle_failed_attempt(self) -> tuple:
        """Başarısız deneme işleyici"""
        self.login_attempts += 1
        remaining = self.max_attempts - self.login_attempts
        
        self._log(f"Başarısız giriş denemesi ({self.login_attempts}/{self.max_attempts})")
        
        if self.login_attempts >= self.max_attempts:
            self.locked_until = time.time() + self.lock_duration
            self._log(f"Hesap kilitlendi ({self.lock_duration//60} dakika)")
            return False, "🔒 Çok fazla hatalı deneme! 5 dakika bekleyin."
        
        return False, f"❌ Hatalı giriş! {remaining} hakkınız kaldı."
    
    def get_remaining_attempts(self) -> int:
        """Kalan deneme hakkı"""
        return max(0, self.max_attempts - self.login_attempts)
    
    def is_locked(self) -> bool:
        """Hesap kilitli mi?"""
        return time.time() < self.locked_until
    
    def get_lock_time(self) -> int:
        """Kilit bitimine kalan süre (saniye)"""
        if self.is_locked():
            return int(self.locked_until - time.time())
        return 0
    
    def reset_attempts(self):
        """Deneme sayacını sıfırla"""
        self.login_attempts = 0
        self.locked_until = 0
        self._log("Deneme sayacı sıfırlandı")
    
    # ============================================
    # 7. KULLANICI YÖNETİMİ
    # ============================================
    
    def add_user(self, username: str, pin: str = None, pattern: str = None) -> tuple:
        """Yeni kullanıcı ekle"""
        if username in self.users:
            return False, "❌ Bu kullanıcı adı zaten var"
        
        self.users[username] = {
            "name": username,
            "created": datetime.now().isoformat(),
            "last_login": None,
            "pin": bool(pin),
            "pattern": bool(pattern)
        }
        
        if pin:
            self.set_pin(pin)  # Ana PIN'i değiştir
        
        self._save_users()
        self._log(f"Yeni kullanıcı eklendi: {username}")
        return True, f"✅ {username} kullanıcısı eklendi"
    
    def switch_user(self, username: str) -> bool:
        """Kullanıcı değiştir"""
        if username in self.users:
            self.current_user = username
            self.users[username]["last_login"] = datetime.now().isoformat()
            self._save_users()
            self._log(f"Kullanıcı değiştirildi: {username}")
            return True
        return False
    
    def get_users(self) -> list:
        """Kullanıcı listesini getir"""
        return list(self.users.keys())
    
    # ============================================
    # 8. DURUM BİLGİSİ
    # ============================================
    
    def get_status(self) -> dict:
        """Giriş sistemi durumu"""
        return {
            "is_locked": self.is_locked(),
            "lock_time": self.get_lock_time(),
            "remaining_attempts": self.get_remaining_attempts(),
            "methods": self.methods,
            "current_user": self.current_user,
            "biometric_enabled": self.settings["biometric_enabled"],
            "auto_lock": self.settings["auto_lock"]
        }
    
    def get_methods(self) -> list:
        """Kullanılabilir giriş yöntemleri"""
        return [m for m, available in self.methods.items() if available]
    
    def get_login_history(self, limit: int = 10) -> list:
        """Son giriş denemeleri"""
        if not self.log_file.exists():
            return []
        
        with open(self.log_file, 'r') as f:
            lines = f.readlines()
        
        return lines[-limit:]
    
    def clear_history(self):
        """Geçmişi temizle"""
        if self.log_file.exists():
            self.log_file.unlink()
        self._log("Geçmiş temizlendi")
    
    # ============================================
    # 9. AYARLAR
    # ============================================
    
    def set_method(self, method: str):
        """Birincil giriş yöntemini belirle"""
        if method in self.methods and self.methods[method]:
            self.settings["method"] = method
            self._save_settings()
            self._log(f"Birincil giriş yöntemi: {method}")
    
    def set_auto_lock(self, enabled: bool, timeout: int = 60):
        """Otomatik kilit ayarla"""
        self.settings["auto_lock"] = enabled
        self.settings["lock_timeout"] = timeout
        self._save_settings()
        self._log(f"Otomatik kilit {'açıldı' if enabled else 'kapatıldı'} (süre: {timeout}s)")
    
    def set_setting(self, key: str, value):
        """Ayar değiştir"""
        self.settings[key] = value
        self._save_settings()
    
    def get_setting(self, key: str, default=None):
        """Ayar oku"""
        return self.settings.get(key, default)