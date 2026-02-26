# modules/web_search.py
import os
import requests
from duckduckgo_search import DDGS
from serpapi import GoogleSearch
from loguru import logger

class WebSearch:
    """İnternette arama yap - Gelişmiş Çoklu Kaynak"""
    
    def __init__(self):
        self.serpapi_key = os.getenv("SERPAPI_API_KEY")
        self.brave_key = os.getenv("BRAVE_API_KEY")
        logger.info("🌐 Web arama modülü hazır")
    
    def search(self, query: str, num_results: int = 3) -> str:
        """İnternette ara - Otomatik yedekli"""
        
        # 1. DuckDuckGo (ücretsiz, hızlı)
        result = self._search_duckduckgo(query, num_results)
        if result and "❌" not in result:
            return result
        
        # 2. Brave Search (ücretsiz, alternatif)
        result = self._search_brave(query, num_results)
        if result and "❌" not in result:
            return result
        
        # 3. SerpAPI (API key gerektirir)
        result = self._search_serpapi(query, num_results)
        if result and "❌" not in result:
            return result
        
        return "❌ Arama yapılamadı. Tüm kaynaklar başarısız."
    
    def _search_duckduckgo(self, query: str, num_results: int) -> str:
        """DuckDuckGo ile ara"""
        try:
            with DDGS() as ddgs:
                results = []
                for r in ddgs.text(query, max_results=num_results):
                    title = r.get('title', 'Başlık yok')
                    body = r.get('body', '')
                    href = r.get('href', '')
                    
                    # Başlığı kısalt
                    if len(title) > 60:
                        title = title[:57] + "..."
                    
                    # Açıklamayı kısalt
                    if len(body) > 80:
                        body = body[:77] + "..."
                    
                    results.append(f"🔍 {title}")
                    if body:
                        results.append(f"   📝 {body}")
                    results.append(f"   🔗 {href[:50]}..." if len(href) > 50 else f"   🔗 {href}")
                
                if results:
                    return f"📊 '{query}' için sonuçlar:\n" + "\n".join(results)
                return None
                    
        except Exception as e:
            logger.warning(f"DuckDuckGo hatası: {e}")
            return None
    
    def _search_brave(self, query: str, num_results: int) -> str:
        """Brave Search ile ara"""
        if not self.brave_key:
            return None
            
        try:
            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": self.brave_key
            }
            params = {
                "q": query,
                "count": num_results
            }
            
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            
            if response.status_code == 200 and 'web' in data:
                results = []
                for r in data['web']['results'][:num_results]:
                    title = r.get('title', 'Başlık yok')
                    description = r.get('description', '')
                    url = r.get('url', '')
                    
                    if len(title) > 60:
                        title = title[:57] + "..."
                    if len(description) > 80:
                        description = description[:77] + "..."
                    
                    results.append(f"🔍 {title}")
                    if description:
                        results.append(f"   📝 {description}")
                    results.append(f"   🔗 {url[:50]}..." if len(url) > 50 else f"   🔗 {url}")
                
                if results:
                    return f"📊 '{query}' için Brave sonuçları:\n" + "\n".join(results)
            return None
            
        except Exception as e:
            logger.warning(f"Brave Search hatası: {e}")
            return None
    
    def _search_serpapi(self, query: str, num_results: int) -> str:
        """SerpAPI ile ara"""
        if not self.serpapi_key:
            return None
            
        try:
            params = {
                "q": query,
                "api_key": self.serpapi_key,
                "num": num_results,
                "hl": "tr",
                "gl": "tr"
            }
            search = GoogleSearch(params)
            results = search.get_dict().get("organic_results", [])
            
            if results:
                snippets = []
                for r in results:
                    title = r.get('title', 'Başlık yok')
                    snippet = r.get('snippet', '')
                    link = r.get('link', '')
                    
                    if len(title) > 60:
                        title = title[:57] + "..."
                    if len(snippet) > 80:
                        snippet = snippet[:77] + "..."
                    
                    snippets.append(f"🔍 {title}")
                    if snippet:
                        snippets.append(f"   📝 {snippet}")
                    snippets.append(f"   🔗 {link[:50]}..." if len(link) > 50 else f"   🔗 {link}")
                
                return f"📊 '{query}' için Google sonuçları:\n" + "\n".join(snippets)
            return None
            
        except Exception as e:
            logger.warning(f"SerpAPI hatası: {e}")
            return None
    
    def search_images(self, query: str, num_results: int = 3) -> str:
        """Görsel arama"""
        try:
            with DDGS() as ddgs:
                results = []
                for r in ddgs.images(query, max_results=num_results):
                    title = r.get('title', 'Görsel')
                    image_url = r.get('image', '')
                    source = r.get('source', '')
                    
                    results.append(f"🖼️ {title}")
                    results.append(f"   🔗 {image_url[:50]}...")
                
                if results:
                    return f"📸 '{query}' için görsel sonuçlar:\n" + "\n".join(results)
                return "📭 Görsel bulunamadı."
                    
        except Exception as e:
            logger.error(f"Görsel arama hatası: {e}")
            return f"❌ Görsel arama yapılamadı: {str(e)}"
    
    def search_videos(self, query: str, num_results: int = 3) -> str:
        """Video arama"""
        try:
            with DDGS() as ddgs:
                results = []
                for r in ddgs.videos(query, max_results=num_results):
                    title = r.get('title', 'Video')
                    duration = r.get('duration', '')
                    views = r.get('views', '')
                    
                    results.append(f"🎥 {title}")
                    if duration:
                        results.append(f"   ⏱️ {duration}")
                    if views:
                        results.append(f"   👁️ {views} izlenme")
                
                if results:
                    return f"🎬 '{query}' için video sonuçlar:\n" + "\n".join(results)
                return "📭 Video bulunamadı."
                    
        except Exception as e:
            logger.error(f"Video arama hatası: {e}")
            return f"❌ Video arama yapılamadı: {str(e)}"