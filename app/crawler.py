# crawler.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class WebCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def crawl_website(self, base_url: str, max_inner_pages: int = 2) -> Optional[str]:
        """
        Crawl website and return brand context string for LLM
        
        Args:
            base_url: The website homepage URL
            max_inner_pages: Number of inner pages to crawl
        
        Returns:
            String with brand context, or None if crawl fails
        """
        try:
            pages_data = []
            
            # Crawl home page
            logger.info(f"Crawling: {base_url}")
            home_data = self._fetch_page_data(base_url)
            
            if not home_data:
                logger.warning("Failed to crawl home page")
                return None
            
            pages_data.append(home_data)
            
            # Extract and crawl inner pages
            try:
                inner_links = self._extract_internal_links(base_url, home_data["html"])
                
                for link in inner_links[:max_inner_pages]:
                    try:
                        logger.info(f"Crawling inner page: {link}")
                        page_data = self._fetch_page_data(link)
                        if page_data:
                            pages_data.append(page_data)
                    except Exception as e:
                        logger.warning(f"Failed to crawl {link}: {str(e)}")
                        continue
            except Exception as e:
                logger.warning(f"Failed to extract inner links: {str(e)}")
            
            # Build and return brand context
            brand_context = self._build_brand_context(pages_data)
            logger.info(f"✓ Crawled {len(pages_data)} pages successfully")
            return brand_context
            
        except Exception as e:
            logger.error(f"Crawl failed: {str(e)}")
            return None
    
    def _fetch_page_data(self, url: str) -> Optional[Dict]:
        """Fetch and parse a single page"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            page_data = {
                "url": url,
                "title": self._get_title(soup),
                "meta_description": self._get_meta_description(soup),
                "headings": self._get_headings(soup),
                "text_content": self._get_clean_text(soup),
                "html": str(soup)
            }
            
            return page_data
            
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def _get_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title_tag = soup.find('title')
        return title_tag.get_text(strip=True) if title_tag else ""
    
    def _get_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()
        
        return ""
    
    def _get_headings(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract all headings"""
        headings = {"h1": [], "h2": [], "h3": []}
        
        for level in ["h1", "h2", "h3"]:
            for tag in soup.find_all(level):
                text = tag.get_text(strip=True)
                if text:
                    headings[level].append(text)
        
        return headings
    
    def _get_clean_text(self, soup: BeautifulSoup) -> str:
        """Extract clean text content"""
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']):
            element.decompose()
        
        text = soup.get_text(separator=' ', strip=True)
        
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text[:3000]
    
    def _extract_internal_links(self, base_url: str, html: str) -> List[str]:
        """Extract internal links from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        base_domain = urlparse(base_url).netloc
        
        links = set()
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            if href.startswith(('#', 'mailto:', 'tel:', 'javascript:')):
                continue
            
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)
            
            if parsed.netloc == base_domain:
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                
                if clean_url.rstrip('/') != base_url.rstrip('/'):
                    links.add(clean_url)
        
        return list(links)[:5]  # Limit to 5 links
    
    def _build_brand_context(self, pages: List[Dict]) -> str:
        """Build brand context string from crawled pages"""
        context_parts = []
        
        for i, page in enumerate(pages):
            if i == 0:
                context_parts.append(f"=== HOME PAGE ===\nURL: {page['url']}")
            else:
                context_parts.append(f"\n=== PAGE {i} ===\nURL: {page['url']}")
            
            if page['title']:
                context_parts.append(f"Title: {page['title']}")
            
            if page['meta_description']:
                context_parts.append(f"Description: {page['meta_description']}")
            
            if page['headings']['h1']:
                context_parts.append(f"Main Headings: {', '.join(page['headings']['h1'][:3])}")
            
            context_parts.append(f"Content Preview:\n{page['text_content'][:800]}")
        
        return '\n'.join(context_parts)