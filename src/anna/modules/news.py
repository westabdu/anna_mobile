# modules/news.py
import requests
import os
from datetime import datetime
from loguru import logger

class NewsAPI:
    """Güncel haberler - NewsAPI Gelişmiş"""
    
    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2"
        logger.info("📰 Haber modülü hazır")
    
    def get_headlines(self, category: str = "general", country: str = "tr", page_size: int = 5) -> str:
        """Manşet haberleri getir - Kategorili"""
        categories = {
            'general': '📰 Genel',
            'business': '💰 Ekonomi',
            'technology': '💻 Teknoloji',
            'science': '🔬 Bilim',
            'health': '🏥 Sağlık',
            'sports': '⚽ Spor',
            'entertainment': '🎬 Eğlence'
        }
        
        category_name = categories.get(category, '📰 Haberler')
        
        try:
            url = f"{self.base_url}/top-headlines"
            params = {
                'country': country,
                'category': category,
                'apiKey': self.api_key,
                'pageSize': page_size
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == 'ok' and data['totalResults'] > 0:
                headlines = []
                for i, article in enumerate(data['articles'], 1):
                    title = article['title']
                    source = article['source']['name']
                    time = article['publishedAt'][:10] if article['publishedAt'] else ''
                    
                    # Başlığı kısalt
                    if len(title) > 70:
                        title = title[:67] + "..."
                    
                    headlines.append(f"{i}. {title}")
                    headlines.append(f"   📍 {source} | 📅 {time}")
                
                return f"{category_name} Manşetleri:\n" + "\n".join(headlines)
            else:
                return f"📭 {category_name} haber bulunamadı."
                
        except Exception as e:
            logger.error(f"Haber hatası: {e}")
            return f"❌ Haberler alınamadı: {str(e)}"
    
    def search_news(self, query: str, page_size: int = 5) -> str:
        """Belirli konuda haber ara"""
        try:
            url = f"{self.base_url}/everything"
            params = {
                'q': query,
                'apiKey': self.api_key,
                'language': 'tr',
                'pageSize': page_size,
                'sortBy': 'publishedAt'
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == 'ok' and data['totalResults'] > 0:
                results = []
                for i, article in enumerate(data['articles'], 1):
                    title = article['title']
                    source = article['source']['name']
                    time = article['publishedAt'][:10] if article['publishedAt'] else ''
                    description = article['description'] or ''
                    
                    # Açıklamayı kısalt
                    if len(description) > 80:
                        description = description[:77] + "..."
                    
                    results.append(f"{i}. {title}")
                    results.append(f"   📍 {source} | 📅 {time}")
                    if description:
                        results.append(f"   📝 {description}")
                
                return f"🔍 '{query}' ile ilgili {len(data['articles'])} haber:\n" + "\n".join(results)
            else:
                return f"📭 '{query}' ile ilgili haber bulunamadı."
                
        except Exception as e:
            logger.error(f"Haber arama hatası: {e}")
            return f"❌ Haberler alınamadı: {str(e)}"
    
    def get_news_by_source(self, source: str, page_size: int = 5) -> str:
        """Belirli kaynaktan haberler"""
        sources = {
            'bbc': 'bbc-news',
            'cnn': 'cnn',
            'haberturk': 'haberturk',
            'ntv': 'ntv',
            'sabah': 'sabah',
            'hurriyet': 'hurriyet'
        }
        
        source_id = sources.get(source.lower(), source)
        
        try:
            url = f"{self.base_url}/top-headlines"
            params = {
                'sources': source_id,
                'apiKey': self.api_key,
                'pageSize': page_size
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == 'ok' and data['totalResults'] > 0:
                results = []
                for i, article in enumerate(data['articles'], 1):
                    title = article['title']
                    results.append(f"{i}. {title}")
                
                return f"📰 {source.title()} Haberleri:\n" + "\n".join(results)
            else:
                return f"📭 {source} kaynağından haber bulunamadı."
                
        except Exception as e:
            logger.error(f"Kaynak haber hatası: {e}")
            return f"❌ Haberler alınamadı: {str(e)}"