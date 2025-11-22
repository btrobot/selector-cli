"""
Execution context for Selector CLI
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
from src.core.element import Element
from src.core.collection import ElementCollection
from src.core.browser import BrowserManager


class Context:
    """Execution context/state"""

    def __init__(self):
        # Browser state
        self.browser: Optional[BrowserManager] = None
        self.current_url: Optional[str] = None

        # Elements
        self.all_elements: List[Element] = []
        self.collection: ElementCollection = ElementCollection()

        # Variables
        self.variables: Dict[str, Any] = {}

        # Macros
        self.macros: Dict[str, Any] = {}

        # History
        self.history: List[str] = []

        # State
        self.last_scan_time: Optional[datetime] = None
        self.is_page_loaded: bool = False

    def add_to_history(self, command: str):
        """Add command to history"""
        self.history.append(command)

    def update_elements(self, elements: List[Element]):
        """Update all elements from scan"""
        self.all_elements = elements
        self.last_scan_time = datetime.now()

    def get_element_by_index(self, index: int) -> Optional[Element]:
        """Get element by index from all elements"""
        for elem in self.all_elements:
            if elem.index == index:
                return elem
        return None

    def get_elements_by_type(self, elem_type: str) -> List[Element]:
        """Get all elements of a specific type"""
        return [elem for elem in self.all_elements if elem.tag == elem_type]
