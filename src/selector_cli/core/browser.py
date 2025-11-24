"""
Browser manager for Selector CLI
"""
from typing import Optional
from playwright.async_api import Browser, Page, Playwright, async_playwright
import asyncio


class BrowserManager:
    """Manage Playwright browser and page"""

    def __init__(self):
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.current_url: Optional[str] = None
        self.is_page_loaded: bool = False

    async def initialize(self, headless: bool = False):
        """Initialize browser"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=headless)
        self.page = await self.browser.new_page()
        print("Browser initialized")

    async def open(self, url: str, timeout: int = 60000) -> bool:
        """Open URL"""
        if not self.page:
            raise RuntimeError("Browser not initialized")

        try:
            print(f"Opening: {url}")
            await self.page.goto(url, timeout=timeout)
            await self.page.wait_for_load_state('networkidle', timeout=30000)
            self.current_url = url
            self.is_page_loaded = True
            print(f"Page loaded: {url}")
            return True
        except Exception as e:
            print(f"Error loading page: {e}")
            self.is_page_loaded = False
            return False

    async def refresh(self):
        """Refresh current page"""
        if not self.page:
            raise RuntimeError("Browser not initialized")

        await self.page.reload()
        await self.page.wait_for_load_state('networkidle')
        print("Page refreshed")

    async def back(self):
        """Navigate back"""
        if not self.page:
            raise RuntimeError("Browser not initialized")

        await self.page.go_back()
        self.current_url = self.page.url
        print("Navigated back")

    async def forward(self):
        """Navigate forward"""
        if not self.page:
            raise RuntimeError("Browser not initialized")

        await self.page.go_forward()
        self.current_url = self.page.url
        print("Navigated forward")

    async def wait(self, seconds: float):
        """Wait for specified seconds"""
        await asyncio.sleep(seconds)
        print(f"Waited {seconds} seconds")

    async def query_selector_all(self, selector: str):
        """Query all elements matching selector"""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        try:
            elements = await self.page.query_selector_all(selector)
            return elements
        except Exception as e:
            raise RuntimeError(f"query_selector_all error: {e}")

    async def close(self):
        """Close browser"""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print("Browser closed")

    def get_page(self) -> Page:
        """Get current page"""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        return self.page
