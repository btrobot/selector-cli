"""
V2 Execution Context - Three-layer model (candidates → temp → workspace)
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Add parent directory to path to import existing modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from selector_cli.core.element import Element
from selector_cli.core.collection import ElementCollection
from selector_cli.core.browser import BrowserManager


class ContextV2:
    """V2 execution context with three-layer element management"""

    # History file configuration
    HISTORY_FILE = Path.home() / '.selector-cli' / 'history'
    MAX_HISTORY_SIZE = 1000

    # Variables file configuration
    VARS_FILE = Path.home() / '.selector-cli' / 'vars.json'

    # Temp state TTL (30 seconds)
    TEMP_TTL = 30

    def __init__(self, enable_history_file: bool = True):
        """
        Initialize v2 context

        Args:
            enable_history_file: If True, persist history and variables to file
        """
        # Browser state
        self.browser: Optional[BrowserManager] = None
        self.current_url: Optional[str] = None

        # Three-layer element management
        self._candidates: List[Element] = []
        self._temp: List[Element] = []
        self._workspace: ElementCollection = ElementCollection(name="workspace")

        # Focus tracking (which layer is currently being viewed/operated on)
        self._focus: str = 'candidates'  # candidates | temp | workspace

        # Temp state expiration tracking
        self._last_find_time: Optional[datetime] = None

        # Variables
        self.variables: Dict[str, Any] = {}
        self.enable_history_file = enable_history_file
        if self.enable_history_file:
            self._load_variables()

        # History
        self.history: List[str] = []
        if self.enable_history_file:
            self._load_history()

        # State
        self.last_scan_time: Optional[datetime] = None
        self.is_page_loaded: bool = False

    # =========================================================================
    # Three-layer state management
    # =========================================================================

    @property
    def candidates(self) -> List[Element]:
        """Get candidates (SCAN results)"""
        return self._candidates.copy()

    @candidates.setter
    def candidates(self, elements: List[Element]):
        """Set candidates (SCAN results)"""
        self._candidates = elements
        self.last_scan_time = datetime.now()

    @property
    def temp(self) -> List[Element]:
        """Get temp (FIND results) - may be expired"""
        if self._is_temp_expired():
            return []
        return self._temp.copy()

    @temp.setter
    def temp(self, elements: List[Element]):
        """Set temp (FIND results)"""
        self._temp = elements
        self._last_find_time = datetime.now()

    def clear_temp(self) -> None:
        """Clear temp state"""
        self._temp.clear()
        self._last_find_time = None
        self._focus = 'candidates'  # Reset focus when temp is cleared

    def _is_temp_expired(self) -> bool:
        """Check if temp state has expired"""
        if self._last_find_time is None:
            return True
        age = datetime.now() - self._last_find_time
        return age.total_seconds() > self.TEMP_TTL

    @property
    def workspace(self) -> ElementCollection:
        """Get workspace (user collection)"""
        return self._workspace

    @property
    def focus(self) -> str:
        """Get current focus (which layer is active)"""
        return self._focus

    @focus.setter
    def focus(self, value: str):
        """Set focus"""
        if value in ['candidates', 'temp', 'workspace']:
            self._focus = value
        else:
            raise ValueError(f"Invalid focus value: {value}")

    def get_focused_elements(self) -> List[Element]:
        """Get elements from the currently focused layer"""
        if self._focus == 'candidates':
            return self.candidates
        elif self._focus == 'temp':
            return self.temp
        elif self._focus == 'workspace':
            return self.workspace.get_all()
        else:
            return []

    # =========================================================================
    # Element retrieval methods
    # =========================================================================

    def get_element_by_index(self, index: int, layer: str = 'candidates') -> Optional[Element]:
        """
        Get element by index from specified layer

        Args:
            index: Element index
            layer: Layer to search ('candidates', 'temp', 'workspace')

        Returns:
            Element or None
        """
        if layer == 'candidates':
            for elem in self._candidates:
                if elem.index == index:
                    return elem
        elif layer == 'temp':
            for elem in self.temp:  # Use property to check expiration
                if elem.index == index:
                    return elem
        elif layer == 'workspace':
            return self._workspace.get(index)

        return None

    def get_elements_by_type(self, elem_type: str, layer: str = 'candidates') -> List[Element]:
        """
        Get all elements of a specific type from specified layer

        Args:
            elem_type: Element tag name (button, input, div, etc.)
            layer: Layer to search ('candidates', 'temp', 'workspace')

        Returns:
            List of elements
        """
        if layer == 'candidates':
            return [elem for elem in self._candidates if elem.tag == elem_type]
        elif layer == 'temp':
            return [elem for elem in self.temp if elem.tag == elem_type]
        elif layer == 'workspace':
            return [elem for elem in self._workspace if elem.tag == elem_type]

        return []

    # =========================================================================
    # Add/remove operations
    # =========================================================================

    def add_to_workspace(self, element: Element) -> bool:
        """
        Add element to workspace

        Returns:
            True if added, False if already exists
        """
        if not self._workspace.contains(element):
            self._workspace.add(element)
            return True
        return False

    def add_many_to_workspace(self, elements: List[Element]) -> int:
        """
        Add multiple elements to workspace

        Returns:
            Number of elements actually added
        """
        added = 0
        for elem in elements:
            if self.add_to_workspace(elem):
                added += 1
        return added

    def remove_from_workspace(self, element: Element) -> bool:
        """
        Remove element from workspace

        Returns:
            True if removed, False if not found
        """
        if self._workspace.contains(element):
            self._workspace.remove(element)
            return True
        return False

    def clear_workspace(self) -> None:
        """Clear workspace"""
        self._workspace.clear()

    # =========================================================================
    # Helper methods for common operations
    # =========================================================================

    def count_elements(self, layer: str = 'candidates') -> int:
        """
        Count elements in specified layer

        Args:
            layer: Layer to count ('candidates', 'temp', 'workspace')

        Returns:
            Element count
        """
        if layer == 'candidates':
            return len(self._candidates)
        elif layer == 'temp':
            return len(self.temp)
        elif layer == 'workspace':
            return len(self._workspace)

        return 0

    def is_empty(self, layer: str = 'candidates') -> bool:
        """
        Check if specified layer is empty

        Args:
            layer: Layer to check ('candidates', 'temp', 'workspace')

        Returns:
            True if empty
        """
        return self.count_elements(layer) == 0

    def has_temp_results(self) -> bool:
        """Check if temp has valid (non-expired) results"""
        return len(self.temp) > 0

    # =========================================================================
    # History management
    # =========================================================================

    def _load_history(self):
        """Load command history from file"""
        try:
            if self.HISTORY_FILE.exists():
                with open(self.HISTORY_FILE, 'r', encoding='utf-8') as f:
                    self.history = [line.rstrip('\n') for line in f.readlines()]
                    if len(self.history) > self.MAX_HISTORY_SIZE:
                        self.history = self.history[-self.MAX_HISTORY_SIZE:]
        except Exception:
            self.history = []

    def _save_history(self):
        """Save command history to file"""
        if not self.enable_history_file:
            return

        try:
            self.HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
            history_to_save = self.history[-self.MAX_HISTORY_SIZE:]
            with open(self.HISTORY_FILE, 'w', encoding='utf-8') as f:
                for cmd in history_to_save:
                    f.write(cmd + '\n')
        except Exception:
            pass

    def add_to_history(self, command: str):
        """Add command to history"""
        self.history.append(command)
        if self.enable_history_file:
            self._save_history()

    def get_history(self, count: Optional[int] = None) -> List[str]:
        """Get command history"""
        if count is None:
            return self.history.copy()
        else:
            return self.history[-count:] if count > 0 else []

    def get_last_command(self) -> Optional[str]:
        """Get the last command in history

        Returns:
            Last command string or None if history is empty
        """
        if self.history:
            return self.history[-1]
        return None

    # =========================================================================
    # Variable management
    # =========================================================================

    def _load_variables(self):
        """Load variables from JSON file"""
        try:
            import json
            if self.VARS_FILE.exists():
                with open(self.VARS_FILE, 'r', encoding='utf-8') as f:
                    self.variables = json.load(f)
            else:
                self.variables = {}
        except Exception:
            self.variables = {}

    def _save_variables(self):
        """Save variables to JSON file"""
        if not self.enable_history_file:
            return

        try:
            import json
            self.VARS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(self.VARS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.variables, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def set_variable(self, name: str, value: Any) -> bool:
        """Set a variable"""
        try:
            self.variables[name] = value
            self._save_variables()
            return True
        except Exception:
            return False

    def get_variable(self, name: str) -> Optional[Any]:
        """Get a variable value"""
        return self.variables.get(name)

    def delete_variable(self, name: str) -> bool:
        """Delete a variable"""
        try:
            if name in self.variables:
                del self.variables[name]
                self._save_variables()
                return True
            return False
        except Exception:
            return False

    # =========================================================================
    # Debug methods
    # =========================================================================

    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of current state for debugging"""
        return {
            'candidates_count': len(self._candidates),
            'temp_count': len(self._temp),
            'workspace_count': len(self._workspace),
            'focus': self._focus,
            'temp_expired': self._is_temp_expired(),
            'temp_age_seconds': (
                (datetime.now() - self._last_find_time).total_seconds()
                if self._last_find_time else None
            ),
            'last_scan_time': self.last_scan_time.isoformat() if self.last_scan_time else None,
        }
