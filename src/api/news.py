# src/api/news.py - ANDROID UYUMLU (SENKRON)
"""
Haber modülü - NewsAPI ile güncel haberler
"""

import os
import sys
import requests
from datetime import datetime
from dotenv import load_dotenv

# Android tespiti
IS_ANDROID = 'android' in sys.platform or 'ANDROID_ARGUMENT' in os.environ

# .env dosyasını yükle
if IS_ANDROID:
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    load_dotenv(dotenv_path)
else:
    load_dotenv()


class NewsAPI:
    """Haber API servisi (senkron)"""
    
    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2"
        
        # Kategoriler ve Türkçe karşılıkları
        self.categories = {
            'general': '📰 Genel',
            'business': '💰 Ekonomi',
            'technology': '💻 Teknoloji',
            'science': '🔬 Bilim',
            'health': '🏥 Sağlık',
            'sports': '⚽ Spor',
            'entertainment': '🎬 Eğlence'
        }
        
        if self.api_key:
            print("✅ News API hazır")
        else:
            print("⚠️ NEWS_API_KEY bulunamadı, .env dosyasını kontrol edin")
    
    def get_headlines(self, category: str = 'general', country: str = 'tr', page_size: int = 5) -> str:
        """
        Manşet haberleri getir (senkron)
        """
        if not self.api_key:
            return "❌ News API anahtarı gerekli."
        
        try:
            url = f"{self.base_url}/top-headlines"
            params = {
                'country': country,
                'category': category,
                'apiKey': self.api_key,
                'pageSize': page_size
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['status'] == 'ok' and data['totalResults'] > 0:
                    category_name = self.categories.get(category, '📰 Haberler')
                    result = [f"**{category_name} Manşetleri**\n"]
                    
                    for i, article in enumerate(data['articles'][:page_size], 1):
                        title = article['title']
                        source = article['source']['name']
                        time = article['publishedAt'][:10] if article['publishedAt'] else ''
                        
                        if len(title) > 60:
                            title = title[:57] + "..."
                        
                        result.append(f"\n{i}. **{title}**")
                        result.append(f"   📍 {source} | 📅 {time}")
                    
                    return "\n".join(result)
                else:
                    return f"📭 {category} kategorisinde haber bulunamadı."
            
            elif response.status_code == 426:
                return "⚠️ API sürümü güncellenmeli."
            else:
                return f"❌ Haberler alınamadı (Hata: {response.status_code})"
                
        except requests.exceptions.Timeout:
            return "⏱️ Haber servisi zaman aşımı"
        except requests.exceptions.ConnectionError:
            return "❌ İnternet bağlantısı yok"
        except Exception as e:
            return f"❌ Haber API hatası: {e}"
    
    def search_news(self, query: str, page_size: int = 5) -> str:
        """
        Belirli bir konuda haber ara (senkron)
        """
        if not self.api_key:
            return "❌ News API anahtarı gerekli."
        
        try:
            url = f"{self.base_url}/everything"
            params = {
                'q': query,
                'apiKey': self.api_key,
                'language': 'tr',
                'pageSize': page_size,
                'sortBy': 'publishedAt'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['status'] == 'ok' and data['totalResults'] > 0:
                    result = [f"🔍 **'{query}' ile ilgili {data['totalResults']} haber bulundu**\n"]
                    
                    for i, article in enumerate(data['articles'][:page_size], 1):
                        title = article['title']
                        source = article['source']['name']
                        time = article['publishedAt'][:10] if article['publishedAt'] else ''
                        
                        if len(title) > 60:
                            title = title[:57] + "..."
                        
                        result.append(f"\n{i}. **{title}**")
                        result.append(f"   📍 {source} | 📅 {time}")
                    
                    return "\n".join(result)
                else:
                    return f"📭 '{query}' ile ilgili haber bulunamadı."
            else:
                return f"❌ Arama yapılamadı (Hata: {response.status_code})"
                
        except requests.exceptions.Timeout:
            return "⏱️ Arama zaman aşımı"
        except requests.exceptions.ConnectionError:
            return "❌ İnternet bağlantısı yok"
        except Exception as e:
            return f"❌ Haber arama hatası: {e}"
    
    def get_news_by_source(self, source: str, page_size: int = 5) -> str:
        """
        Belirli bir kaynaktan haberler (senkron)
        """
        if not self.api_key:
            return "❌ News API anahtarı gerekli."
        
        # Popüler Türkçe kaynaklar
        turkish_sources = {
            'cnnturk': 'cnn-turk',
            'ntv': 'ntv',
            'haberturk': 'haberturk',
            'sabah': 'sabah',
            'hurriyet': 'hurriyet',
            'milliyet': 'milliyet',
            'sozcu': 'sozcu',
            'cumhuriyet': 'cumhuriyet'
        }
        
        # Kaynak adını düzenle
        source_lower = source.lower().replace(' ', '')
        if source_lower in turkish_sources:
            source = turkish_sources[source_lower]
        
        try:
            url = f"{self.base_url}/top-headlines"
            params = {
                'sources': source,
                'apiKey': self.api_key,
                'pageSize': page_size
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['status'] == 'ok' and data['totalResults'] > 0:
                    result = [f"📰 **{source.title()} Haberleri**\n"]
                    
                    for i, article in enumerate(data['articles'][:page_size], 1):
                        title = article['title']
                        time = article['publishedAt'][:10] if article['publishedAt'] else ''
                        
                        if len(title) > 60:
                            title = title[:57] + "..."
                        
                        result.append(f"\n{i}. **{title}**")
                        result.append(f"   📅 {time}")
                    
                    return "\n".join(result)
                else:
                    return f"📭 {source} kaynağından haber bulunamadı."
            else:
                return f"❌ Kaynak haberleri alınamadı (Hata: {response.status_code})"
                
        except requests.exceptions.Timeout:
            return "⏱️ Kaynak zaman aşımı"
        except requests.exceptions.ConnectionError:
            return "❌ İnternet bağlantısı yok"
        except Exception as e:
            return f"❌ Kaynak haber hatası: {e}"
    
    def get_category_list(self) -> str:
        """Kullanılabilir kategorileri listele"""
        result = "📋 **Haber Kategorileri**\n\n"
        for key, value in self.categories.items():
            result += f"{value} (`{key}`)\n"
        return result