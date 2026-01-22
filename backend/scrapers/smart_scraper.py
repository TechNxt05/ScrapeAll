"""
Smart scraper that tries multiple methods with fallback
Priority: Static -> Playwright -> Selenium
"""
from backend.scrapers.base_scraper import BaseScraper, ScrapeResult
from backend.scrapers.static_scraper import StaticScraper
from backend.scrapers.playwright_scraper import PlaywrightScraper
from backend.scrapers.selenium_scraper import SeleniumScraper
from typing import List, Tuple, Optional

class SmartScraper(BaseScraper):
    """
    Intelligent scraper that tries multiple methods
    Returns detailed error if all methods fail
    """
    
    def __init__(self, timeout: int = 30):
        super().__init__(timeout)
        # Initialize all scrapers
        self.scrapers = [
            StaticScraper(timeout),
            PlaywrightScraper(timeout),
            SeleniumScraper(timeout)
        ]
    
    def can_scrape(self, url: str) -> bool:
        """Smart scraper can try any URL"""
        return True
    
    def scrape(self, url: str, selector: Optional[str] = None) -> ScrapeResult:
        """
        Try scraping with multiple methods
        Returns first successful result or detailed error
        """
        errors = []
        
        print(f"🔍 Smart scraping: {url} {f'[Target: {selector}]' if selector else ''}")
        
        for scraper in self.scrapers:
            scraper_name = scraper.get_name()
            # If selector is used, maybe ONLY use Playwright/Selenium? 
            # Static scraper can technically do selectors with BS4 but logic needs update.
            # For MVP, let's pass it to all.
            
            print(f"  Trying {scraper_name}...")
            
            try:
                result = scraper.scrape(url, selector)
                
                if result.success:
                    print(f"  ✅ Success with {scraper_name}")
                    return result
                else:
                    error_msg = f"{scraper_name}: {result.error}"
                    errors.append(error_msg)
                    print(f"  ❌ {error_msg}")
            except TypeError:
                # If child scraper doesn't support selector yet (legacy safety)
                result = scraper.scrape(url)
                if result.success: return result
                errors.append(f"{scraper_name}: failed (signature mismatch)")
        
        # All methods failed - create detailed error report
        error_report = self._create_error_report(url, errors)
        
        return ScrapeResult(
            success=False,
            error=error_report,
            method="smart_scraper_all_failed"
        )
    
    def _create_error_report(self, url: str, errors: List[str]) -> str:
        """Create a detailed error report explaining why scraping failed"""
        
        report = f"❌ Unable to scrape {url}\n\n"
        report += "Attempted methods:\n"
        
        for i, error in enumerate(errors, 1):
            report += f"{i}. {error}\n"
        
        report += "\n🔍 Possible reasons:\n"
        
        # Analyze errors to provide helpful suggestions
        error_text = " ".join(errors).lower()
        
        if "403" in error_text or "forbidden" in error_text:
            report += "• Website is blocking automated access (403 Forbidden)\n"
            report += "• Suggestion: The site may require authentication or has anti-bot protection\n"
        
        elif "404" in error_text:
            report += "• Page not found (404)\n"
            report += "• Suggestion: Check if the URL is correct\n"
        
        elif "timeout" in error_text:
            report += "• Connection timeout\n"
            report += "• Suggestion: The website may be slow or temporarily unavailable\n"
        
        elif "captcha" in error_text:
            report += "• CAPTCHA detected\n"
            report += "• Suggestion: This site requires human verification\n"
        
        elif "connection" in error_text:
            report += "• Connection error\n"
            report += "• Suggestion: Check your internet connection or the website may be down\n"
        
        elif "ssl" in error_text or "certificate" in error_text:
            report += "• SSL/Certificate error\n"
            report += "• Suggestion: The website may have an invalid SSL certificate\n"
        
        else:
            report += "• Unknown error\n"
            report += "• Suggestion: The website may have special protection or require login\n"
        
        report += "\n💡 What you can try:\n"
        report += "• Check if the website requires login\n"
        report += "• Verify the URL is accessible in a browser\n"
        report += "• Try again later if the site is temporarily down\n"
        
        return report

# Global instance
smart_scraper = SmartScraper()
