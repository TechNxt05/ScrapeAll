"""
Selenium scraper as fallback for difficult websites
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from backend.scrapers.base_scraper import BaseScraper, ScrapeResult
from typing import Optional
import time

class SeleniumScraper(BaseScraper):
    """Scraper using Selenium WebDriver"""
    
    def can_scrape(self, url: str) -> bool:
        """Selenium can handle any URL"""
        return True
    
    def scrape(self, url: str, selector: Optional[str] = None) -> ScrapeResult:
        """Scrape using Selenium"""
        driver = None
        try:
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # Initialize driver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(self.timeout)
            
            # Navigate to URL
            driver.get(url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Get HTML
            html = driver.page_source
            
            # Get title
            title = driver.title
            
            # Parse with BeautifulSoup
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
            
            return ScrapeResult(
                success=True,
                html=html,
                text=text,
                title=title,
                method="selenium"
            )
            
        except TimeoutException:
            return ScrapeResult(
                success=False,
                error=f"Page load timeout after {self.timeout} seconds",
                method="selenium"
            )
        except WebDriverException as e:
            return ScrapeResult(
                success=False,
                error=f"WebDriver error: {str(e)}",
                method="selenium"
            )
        except Exception as e:
            return ScrapeResult(
                success=False,
                error=f"Selenium scraping failed: {str(e)}",
                method="selenium"
            )
        finally:
            if driver:
                driver.quit()
