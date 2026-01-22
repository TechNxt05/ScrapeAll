"""
Static HTML scraper using requests + BeautifulSoup
Fastest method for static websites
"""
import requests
from bs4 import BeautifulSoup
from backend.scrapers.base_scraper import BaseScraper, ScrapeResult
from backend.config import settings
from typing import Optional

class StaticScraper(BaseScraper):
    """Scraper for static HTML websites"""
    
    def __init__(self, timeout: int = 30):
        super().__init__(timeout)
        self.headers = {
            'User-Agent': settings.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    def can_scrape(self, url: str) -> bool:
        """Static scraper can try any URL"""
        return True
    
    def scrape(self, url: str, selector: Optional[str] = None) -> ScrapeResult:
        """Scrape using requests + BeautifulSoup"""
        try:
            # Make request
            response = requests.get(
                url, 
                headers=self.headers, 
                timeout=self.timeout,
                allow_redirects=True
            )
            
            # Check status
            if response.status_code != 200:
                return ScrapeResult(
                    success=False,
                    error=f"HTTP {response.status_code}: {response.reason}",
                    method="static"
                )
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract title
            title = soup.title.string if soup.title else None
            
            # Remove script and style elements
            for script in soup(["script", "style", "noscript"]):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator='\n', strip=True)
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return ScrapeResult(
                success=True,
                html=response.text,
                text=text,
                title=title,
                method="static"
            )
            
        except requests.exceptions.Timeout:
            return ScrapeResult(
                success=False,
                error=f"Request timeout after {self.timeout} seconds",
                method="static"
            )
        except requests.exceptions.ConnectionError:
            return ScrapeResult(
                success=False,
                error="Connection error - unable to reach the website",
                method="static"
            )
        except requests.exceptions.TooManyRedirects:
            return ScrapeResult(
                success=False,
                error="Too many redirects",
                method="static"
            )
        except Exception as e:
            return ScrapeResult(
                success=False,
                error=f"Static scraping failed: {str(e)}",
                method="static"
            )
