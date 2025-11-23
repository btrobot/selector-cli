"""
Execution context for Selector CLI
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path
from src.core.element import Element
from src.core.collection import ElementCollection
from src.core.browser import BrowserManager
from src.core.macro import MacroManager


class Context:
    """Execution context/state"""

    # History file configuration
    HISTORY_FILE = Path.home() / '.selector-cli' / 'history'
    MAX_HISTORY_SIZE = 1000  # Maximum number of commands to keep

    def __init__(self, enable_history_file: bool = True):
        """
        Initialize context

        Args:
            enable_history_file: If True, persist history to file.
                                Set to False for testing.
        """
        # Browser state
        self.browser: Optional[BrowserManager] = None
        self.current_url: Optional[str] = None

        # Elements
        self.all_elements: List[Element] = []
        self.collection: ElementCollection = ElementCollection()

        # Variables
        self.variables: Dict[str, Any] = {}

        # Macros
        self.macro_manager = MacroManager()

        # History - load from file
        self.history: List[str] = []
        self.enable_history_file = enable_history_file
        if self.enable_history_file:
            self._load_history()

        # State
        self.last_scan_time: Optional[datetime] = None
        self.is_page_loaded: bool = False

    def _load_history(self):
        """Load command history from file"""
        try:
            if self.HISTORY_FILE.exists():
                with open(self.HISTORY_FILE, 'r', encoding='utf-8') as f:
                    self.history = [line.rstrip('\n') for line in f.readlines()]
                    # Trim to max size
                    if len(self.history) > self.MAX_HISTORY_SIZE:
                        self.history = self.history[-self.MAX_HISTORY_SIZE:]
        except Exception:
            # If loading fails, start with empty history
            self.history = []

    def _save_history(self):
        """Save command history to file"""
        if not self.enable_history_file:
            return

        try:
            # Ensure directory exists
            self.HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

            # Trim history to max size before saving
            history_to_save = self.history[-self.MAX_HISTORY_SIZE:]

            # Write to file
            with open(self.HISTORY_FILE, 'w', encoding='utf-8') as f:
                for cmd in history_to_save:
                    f.write(cmd + '\n')
        except Exception:
            # Silently fail if we can't save history
            pass

    def add_to_history(self, command: str):
        """Add command to history and persist to file"""
        self.history.append(command)
        if self.enable_history_file:
            self._save_history()

    def get_history(self, count: Optional[int] = None) -> List[str]:
        """Get command history

        Args:
            count: Number of recent commands to return. If None, returns all.

        Returns:
            List of command strings
        """
        if count is None:
            return self.history.copy()
        else:
            return self.history[-count:] if count > 0 else []

    def get_history_command(self, index: int) -> Optional[str]:
        """Get command at specific history index (0-based)

        Args:
            index: Index in history (0 = first command)

        Returns:
            Command string or None if index out of range
        """
        if 0 <= index < len(self.history):
            return self.history[index]
        return None

    def get_last_command(self) -> Optional[str]:
        """Get the last command in history

        Returns:
            Last command string or None if history is empty
        """
        if self.history:
            return self.history[-1]
        return None

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
