# src/api/weather.py - ANDROID UYUMLU
"""
Hava Durumu API - Senkron versiyon
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Android tespiti
IS_ANDROID = 'android' in sys.platform or 'ANDROID_ARGUMENT' in os.environ

# .env dosyasını yükle
if IS_ANDROID:
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    load_dotenv(dotenv_path)
else:
    load_dotenv()


class WeatherAPI:
    """Hava durumu sorgulama (senkron)"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
        if self.api_key:
            print("✅ Weather API hazır")
            print(f"📱 Android: {'✅' if IS_ANDROID else '❌'}")
        else:
            print("⚠️ OPENWEATHER_API_KEY bulunamadı")
    
    def get_weather(self, city: str = "İstanbul") -> str:
        """Şehir için hava durumu (senkron)"""
        if not self.api_key:
            return "❌ OpenWeather API anahtarı gerekli."
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'tr'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                temp = data['main']['temp']
                feels_like = data['main']['feels_like']
                humidity = data['main']['humidity']
                description = data['weather'][0]['description']
                
                # Şehir adını düzgün göster
                city_name = data.get('name', city)
                
                return f"""🌤️ **{city_name} Hava Durumu**

📍 {description.title()}
🌡️ Sıcaklık: {temp:.1f}°C
💧 Nem: %{humidity}
🤔 Hissedilen: {feels_like:.1f}°C"""
            
            elif response.status_code == 404:
                return f"❌ Şehir bulunamadı: {city}"
            else:
                return f"❌ Hava durumu alınamadı (Hata: {response.status_code})"
                
        except requests.exceptions.Timeout:
            return "⏱️ Hava durumu servisi zaman aşımı"
        except requests.exceptions.ConnectionError:
            return "❌ İnternet bağlantısı yok"
        except Exception as e:
            return f"❌ Hava durumu hatası: {e}"
    
    def get_weather_by_location(self, lat: float, lon: float) -> str:
        """Konuma göre hava durumu (senkron)"""
        if not self.api_key:
            return "❌ OpenWeather API anahtarı gerekli."
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'tr'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                city = data.get('name', 'Bulunduğunuz konum')
                temp = data['main']['temp']
                description = data['weather'][0]['description']
                
                return f"""📍 **{city}**
🌤️ {description.title()}
🌡️ {temp:.1f}°C"""
            else:
                return "❌ Konum bilgisi alınamadı"
                
        except Exception as e:
            return f"❌ Hava durumu hatası: {e}"