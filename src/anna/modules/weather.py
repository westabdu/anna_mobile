# modules/weather.py
import requests
import os
from datetime import datetime
from loguru import logger

class WeatherAPI:
    """Hava durumu sorgulama - OpenWeatherMap Gelişmiş"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5"
        logger.info("🌤️ Hava durumu modülü hazır")
    
    def get_weather(self, city: str) -> str:
        """Şehir için hava durumu getir - Detaylı"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'tr'
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if response.status_code == 200:
                # Ana bilgiler
                temp = data['main']['temp']
                feels_like = data['main']['feels_like']
                temp_min = data['main']['temp_min']
                temp_max = data['main']['temp_max']
                humidity = data['main']['humidity']
                pressure = data['main']['pressure']
                
                # Hava durumu
                weather = data['weather'][0]
                main = weather['main']
                description = weather['description']
                icon = weather['icon']
                
                # Rüzgar
                wind_speed = data['wind']['speed']
                wind_deg = data['wind'].get('deg', 0)
                
                # Rüzgar yönü
                directions = ['Kuzey', 'Kuzeydoğu', 'Doğu', 'Güneydoğu', 
                             'Güney', 'Güneybatı', 'Batı', 'Kuzeybatı']
                wind_dir = directions[int((wind_deg + 22.5) / 45) % 8]
                
                # Görüş mesafesi
                visibility = data.get('visibility', 10000) / 1000  # km
                
                # Güneş doğuş/batış
                sunrise = datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M')
                sunset = datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M')
                
                # Emoji seçimi
                emoji = self._get_weather_emoji(main)
                
                return (f"{emoji} {city} Hava Durumu\n"
                        f"📊 Durum: {description.title()}\n"
                        f"🌡️ Sıcaklık: {temp:.1f}°C (Hissedilen: {feels_like:.1f}°C)\n"
                        f"📈 Min/Max: {temp_min:.1f}°C / {temp_max:.1f}°C\n"
                        f"💧 Nem: %{humidity}\n"
                        f"🌬️ Rüzgar: {wind_speed} m/s ({wind_dir})\n"
                        f"👁️ Görüş: {visibility:.1f} km\n"
                        f"🌅 Güneş: {sunrise} / {sunset}")
            else:
                error_msg = data.get('message', 'Bilinmeyen hata')
                return f"❌ Şehir bulunamadı: {city} ({error_msg})"
                
        except Exception as e:
            logger.error(f"Hava durumu hatası: {e}")
            return f"❌ Hava durumu alınamadı: {str(e)}"
    
    def get_forecast(self, city: str, days: int = 5) -> str:
        """Günlük hava tahmini"""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'tr',
                'cnt': days * 8  # 3 saatlik periyotlar, günde 8 veri
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if response.status_code == 200:
                forecasts = []
                current_date = None
                day_data = []
                
                for item in data['list']:
                    date = item['dt_txt'][:10]
                    
                    if date != current_date:
                        if day_data:
                            # Günlük ortalama hesapla
                            avg_temp = sum(d['temp'] for d in day_data) / len(day_data)
                            conditions = [d['weather'][0]['main'] for d in day_data]
                            most_common = max(set(conditions), key=conditions.count)
                            
                            date_str = datetime.strptime(date, '%Y-%m-%d').strftime('%d %B')
                            emoji = self._get_weather_emoji(most_common)
                            
                            forecasts.append(f"{emoji} {date_str}: {avg_temp:.1f}°C")
                        
                        current_date = date
                        day_data = []
                    
                    day_data.append({
                        'temp': item['main']['temp'],
                        'weather': item['weather']
                    })
                
                # Son günü ekle
                if day_data:
                    avg_temp = sum(d['temp'] for d in day_data) / len(day_data)
                    conditions = [d['weather'][0]['main'] for d in day_data]
                    most_common = max(set(conditions), key=conditions.count)
                    date_str = datetime.strptime(current_date, '%Y-%m-%d').strftime('%d %B')
                    emoji = self._get_weather_emoji(most_common)
                    forecasts.append(f"{emoji} {date_str}: {avg_temp:.1f}°C")
                
                return f"📅 {city} {days} Günlük Tahmin:\n" + "\n".join(forecasts)
            else:
                return f"❌ Tahmin alınamadı: {city}"
                
        except Exception as e:
            logger.error(f"Tahmin hatası: {e}")
            return f"❌ Tahmin alınamadı: {str(e)}"
    
    def _get_weather_emoji(self, weather_main: str) -> str:
        """Hava durumu emojisi"""
        emoji_map = {
            'Clear': '☀️',
            'Clouds': '☁️',
            'Rain': '🌧️',
            'Drizzle': '🌦️',
            'Thunderstorm': '⛈️',
            'Snow': '❄️',
            'Mist': '🌫️',
            'Fog': '🌫️',
            'Haze': '🌫️',
            'Smoke': '💨',
            'Dust': '💨',
            'Sand': '💨',
            'Ash': '🌋',
            'Squall': '💨',
            'Tornado': '🌪️'
        }
        return emoji_map.get(weather_main, '🌡️')