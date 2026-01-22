"""
Playwright scraper for modern JavaScript-heavy websites
Better performance than Selenium
"""
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
from backend.scrapers.base_scraper import BaseScraper, ScrapeResult
from typing import Optional

class PlaywrightScraper(BaseScraper):
    """Scraper using Playwright for JavaScript-rendered content"""
    
    def can_scrape(self, url: str) -> bool:
        """Playwright can handle any URL"""
        return True
    
    def scrape(self, url: str, selector: Optional[str] = None) -> ScrapeResult:
        """Scrape using Playwright"""
        try:
            with sync_playwright() as p:
                # Launch browser in headless mode
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = context.new_page()
                
                # Navigate to URL
                try:
                    page.goto(url, timeout=self.timeout * 1000, wait_until='networkidle')
                except PlaywrightTimeout:
                    # Try with domcontentloaded instead
                    page.goto(url, timeout=self.timeout * 1000, wait_until='domcontentloaded')
                
                # Wait a bit for dynamic content
                page.wait_for_timeout(2000)
                
                # Get HTML
                if selector:
                    # Target specific element
                    try:
                        element = page.locator(selector).first
                        html = element.inner_html()
                        # For text, we might need to handle just this element
                        text_content = element.inner_text()
                    except Exception as e:
                        # Fallback to full page if selector fails? Or error?
                        # Better to error so user knows selector was wrong
                        raise Exception(f"Selector '{selector}' not found or invalid: {str(e)}")
                else:
                    html = page.content()
                    text_content = None # Will be parsed by BS4 below if not set

                # Get title
                title = page.title()
                
                if selector and text_content:
                     # If we used selector, we already have exact text
                     text = text_content
                else:
                    # Parse with BeautifulSoup (Full Page)
                    soup = BeautifulSoup(html, 'lxml')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style", "noscript"]):
                        script.decompose()
                    
                    # Get text
                    text = soup.get_text(separator='\n', strip=True)
                
                # Clean up text
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                
                # Close browser
                browser.close()
                
                return ScrapeResult(
                    success=True,
                    html=html,
                    text=text,
                    title=title,
                    method="playwright"
                )
                
        except PlaywrightTimeout:
            return ScrapeResult(
                success=False,
                error=f"Page load timeout after {self.timeout} seconds",
                method="playwright"
            )
        except Exception as e:
            return ScrapeResult(
                success=False,
                error=f"Playwright scraping failed: {str(e)}",
                method="playwright"
            )
