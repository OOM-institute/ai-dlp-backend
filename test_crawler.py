import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
from typing import List, Dict
from datetime import datetime


class WebCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def crawl_website(self, base_url: str, max_inner_pages: int = 2) -> Dict:
        """
        Crawl website and return structured data
        
        Args:
            base_url: The website homepage URL
            max_inner_pages: Number of inner pages to crawl (default: 2)
        
        Returns:
            Dictionary with crawled data
        """
        result = {
            "base_url": base_url,
            "crawled_at": datetime.now().isoformat(),
            "pages": [],
            "brand_context": "",
            "metadata": {
                "total_pages_crawled": 0,
                "total_text_length": 0,
                "errors": []
            }
        }
        
        try:
            # Crawl home page
            print(f"Crawling home page: {base_url}")
            home_data = self._fetch_page_data(base_url)
            if home_data:
                result["pages"].append(home_data)
                result["metadata"]["total_pages_crawled"] += 1
                result["metadata"]["total_text_length"] += len(home_data["text_content"])
                
                # Extract inner page links
                inner_links = self._extract_internal_links(base_url, home_data["html"])
                print(f"Found {len(inner_links)} internal links")
                
                # Crawl inner pages
                for i, link in enumerate(inner_links[:max_inner_pages], 1):
                    try:
                        print(f"Crawling page {i}/{max_inner_pages}: {link}")
                        page_data = self._fetch_page_data(link)
                        if page_data:
                            result["pages"].append(page_data)
                            result["metadata"]["total_pages_crawled"] += 1
                            result["metadata"]["total_text_length"] += len(page_data["text_content"])
                    except Exception as e:
                        error_msg = f"Error crawling {link}: {str(e)}"
                        print(error_msg)
                        result["metadata"]["errors"].append(error_msg)
            
            # Build brand context string
            result["brand_context"] = self._build_brand_context(result["pages"])
            
            print(f"\n✓ Crawling complete!")
            print(f"  Pages crawled: {result['metadata']['total_pages_crawled']}")
            print(f"  Total text length: {result['metadata']['total_text_length']} chars")
            print(f"  Errors: {len(result['metadata']['errors'])}")
            
        except Exception as e:
            error_msg = f"Fatal error crawling {base_url}: {str(e)}"
            print(error_msg)
            result["metadata"]["errors"].append(error_msg)
        
        return result
    
    def _fetch_page_data(self, url: str) -> Dict:
        """Fetch and parse a single page"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract metadata
            page_data = {
                "url": url,
                "title": self._get_title(soup),
                "meta_description": self._get_meta_description(soup),
                "headings": self._get_headings(soup),
                "text_content": self._get_clean_text(soup),
                "html": str(soup),  # Store for link extraction
                "word_count": 0
            }
            
            # Calculate word count
            page_data["word_count"] = len(page_data["text_content"].split())
            
            return page_data
            
        except requests.RequestException as e:
            raise Exception(f"HTTP error: {str(e)}")
        except Exception as e:
            raise Exception(f"Parse error: {str(e)}")
    
    def _get_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title_tag = soup.find('title')
        return title_tag.get_text(strip=True) if title_tag else ""
    
    def _get_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        
        # Try og:description as fallback
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()
        
        return ""
    
    def _get_headings(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract all headings"""
        headings = {
            "h1": [],
            "h2": [],
            "h3": []
        }
        
        for level in ["h1", "h2", "h3"]:
            for tag in soup.find_all(level):
                text = tag.get_text(strip=True)
                if text:
                    headings[level].append(text)
        
        return headings
    
    def _get_clean_text(self, soup: BeautifulSoup) -> str:
        """Extract clean text content"""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']):
            element.decompose()
        
        # Get text
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Limit length
        return text[:3000]
    
    def _extract_internal_links(self, base_url: str, html: str) -> List[str]:
        """Extract internal links from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        base_domain = urlparse(base_url).netloc
        base_scheme = urlparse(base_url).scheme
        
        links = set()
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            # Skip anchors, mailto, tel, etc.
            if href.startswith(('#', 'mailto:', 'tel:', 'javascript:')):
                continue
            
            # Convert to absolute URL
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)
            
            # Only include same-domain links
            if parsed.netloc == base_domain:
                # Remove fragments and query params for cleaner URLs
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                
                # Skip if it's the base URL
                if clean_url.rstrip('/') != base_url.rstrip('/'):
                    links.add(clean_url)
        
        return list(links)
    
    def _build_brand_context(self, pages: List[Dict]) -> str:
        """Build brand context string from crawled pages"""
        context_parts = []
        
        for i, page in enumerate(pages):
            if i == 0:
                context_parts.append(f"Home Page ({page['url']}):")
            else:
                context_parts.append(f"\nPage {i} ({page['url']}):")
            
            # Add title
            if page['title']:
                context_parts.append(f"Title: {page['title']}")
            
            # Add meta description
            if page['meta_description']:
                context_parts.append(f"Description: {page['meta_description']}")
            
            # Add main headings
            if page['headings']['h1']:
                context_parts.append(f"Main Heading: {' | '.join(page['headings']['h1'])}")
            
            # Add text content (limited)
            context_parts.append(page['text_content'][:1000])
            context_parts.append("\n" + "-" * 50)
        
        return '\n'.join(context_parts)


def test_crawler(url: str, output_file: str = "crawl_result.json"):
    """Test the crawler and save results to JSON"""
    print(f"Starting crawl of: {url}\n")
    print("=" * 60)
    
    crawler = WebCrawler()
    result = crawler.crawl_website(url, max_inner_pages=2)
    
    # Remove HTML from output (too large)
    for page in result["pages"]:
        page.pop("html", None)
    
    # Save to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'=' * 60}")
    print(f"✓ Results saved to: {output_file}")
    print(f"\nBrand context preview (first 500 chars):")
    print("-" * 60)
    print(result["brand_context"][:500])
    print("...")
    
    return result


if __name__ == "__main__":
    # Test with different websites
    
    # Example 1: Tech company
    test_url = "https://www.dominos.com.my/"
    
    # Example 2: You can test with any URL
    # test_url = "https://www.anthropic.com"
    # test_url = "https://www.shopify.com"
    
    print(f"\nTesting crawler with: {test_url}\n")
    
    try:
        result = test_crawler(test_url)
        
        # Print summary
        print(f"\n{'=' * 60}")
        print("SUMMARY")
        print(f"{'=' * 60}")
        print(f"Total pages: {result['metadata']['total_pages_crawled']}")
        print(f"Total text: {result['metadata']['total_text_length']} characters")
        print(f"Errors: {len(result['metadata']['errors'])}")
        
        if result['metadata']['errors']:
            print("\nErrors encountered:")
            for error in result['metadata']['errors']:
                print(f"  - {error}")
        
        print("\nPages crawled:")
        for page in result['pages']:
            print(f"  - {page['url']}")
            print(f"    Title: {page['title']}")
            print(f"    Words: {page['word_count']}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")