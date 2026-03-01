# src/api/news.py
"""
Haber modülü - NewsAPI ile güncel haberler
"""

import os
import aiohttp
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class NewsAPI:
    """Haber API servisi"""
    
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
    
    async def get_headlines(self, category: str = 'general', country: str = 'tr', page_size: int = 5) -> str:
        """
        Manşet haberleri getir
        
        Args:
            category: general, business, technology, science, health, sports, entertainment
            country: tr, us, de, fr, gb, etc.
            page_size: kaç haber gösterileceği
        """
        if not self.api_key:
            return "❌ News API anahtarı gerekli. Lütfen .env dosyasına NEWS_API_KEY ekleyin."
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/top-headlines"
                params = {
                    'country': country,
                    'category': category,
                    'apiKey': self.api_key,
                    'pageSize': page_size
                }
                
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        if data['status'] == 'ok' and data['totalResults'] > 0:
                            category_name = self.categories.get(category, '📰 Haberler')
                            result = [f"**{category_name} Manşetleri**\n"]
                            
                            for i, article in enumerate(data['articles'], 1):
                                title = article['title']
                                source = article['source']['name']
                                time = article['publishedAt'][:10] if article['publishedAt'] else ''
                                description = article['description'] or ''
                                
                                # Başlığı kısalt
                                if len(title) > 60:
                                    title = title[:57] + "..."
                                
                                result.append(f"\n{i}. **{title}**")
                                result.append(f"   📍 {source} | 📅 {time}")
                                if description and len(description) > 80:
                                    result.append(f"   📝 {description[:77]}...")
                                elif description:
                                    result.append(f"   📝 {description}")
                            
                            return "\n".join(result)
                        else:
                            return f"📭 {category} kategorisinde haber bulunamadı."
                    
                    elif resp.status == 426:
                        return "⚠️ API sürümü güncellenmeli. Lütfen API anahtarınızı kontrol edin."
                    else:
                        return f"❌ Haberler alınamadı (Hata: {resp.status})"
                        
        except Exception as e:
            return f"❌ Haber API hatası: {e}"
    
    async def search_news(self, query: str, page_size: int = 5) -> str:
        """
        Belirli bir konuda haber ara
        
        Args:
            query: aranacak kelime
            page_size: kaç haber gösterileceği
        """
        if not self.api_key:
            return "❌ News API anahtarı gerekli."
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/everything"
                params = {
                    'q': query,
                    'apiKey': self.api_key,
                    'language': 'tr',
                    'pageSize': page_size,
                    'sortBy': 'publishedAt'
                }
                
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        if data['status'] == 'ok' and data['totalResults'] > 0:
                            result = [f"🔍 **'{query}' ile ilgili {data['totalResults']} haber bulundu**\n"]
                            
                            for i, article in enumerate(data['articles'][:page_size], 1):
                                title = article['title']
                                source = article['source']['name']
                                time = article['publishedAt'][:10] if article['publishedAt'] else ''
                                description = article['description'] or ''
                                
                                if len(title) > 60:
                                    title = title[:57] + "..."
                                
                                result.append(f"\n{i}. **{title}**")
                                result.append(f"   📍 {source} | 📅 {time}")
                                if description:
                                    result.append(f"   📝 {description[:100]}")
                            
                            return "\n".join(result)
                        else:
                            return f"📭 '{query}' ile ilgili haber bulunamadı."
                    else:
                        return f"❌ Arama yapılamadı (Hata: {resp.status})"
                        
        except Exception as e:
            return f"❌ Haber arama hatası: {e}"
    
    async def get_news_by_source(self, source: str, page_size: int = 5) -> str:
        """
        Belirli bir kaynaktan haberler
        
        Args:
            source: haber kaynağı (bbc-news, cnnturk, haberturk, ntv, etc.)
            page_size: kaç haber gösterileceği
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
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/top-headlines"
                params = {
                    'sources': source,
                    'apiKey': self.api_key,
                    'pageSize': page_size
                }
                
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
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
                        return f"❌ Kaynak haberleri alınamadı (Hata: {resp.status})"
                        
        except Exception as e:
            return f"❌ Kaynak haber hatası: {e}"
    
    def get_category_list(self) -> str:
        """Kullanılabilir kategorileri listele"""
        result = "📋 **Haber Kategorileri**\n\n"
        for key, value in self.categories.items():
            result += f"{value} (`{key}`)\n"
        return result