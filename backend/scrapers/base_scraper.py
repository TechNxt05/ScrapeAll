"""
Base scraper interface
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class ScrapeResult:
    """Result of a scraping operation"""
    success: bool
    html: Optional[str] = None
    text: Optional[str] = None
    title: Optional[str] = None
    error: Optional[str] = None
    method: Optional[str] = None

class BaseScraper(ABC):
    """Abstract base class for all scrapers"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
    
    @abstractmethod
    def scrape(self, url: str, selector: Optional[str] = None) -> ScrapeResult:
        """Scrape a URL and return the result"""
        pass
    
    @abstractmethod
    def can_scrape(self, url: str) -> bool:
        """Check if this scraper can handle the URL"""
        pass
    
    def get_name(self) -> str:
        """Return the name of this scraper"""
        return self.__class__.__name__
