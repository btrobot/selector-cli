"""
Macro manager for Selector CLI
"""
from typing import Dict, List


class MacroManager:
    """Manage command macros"""

    def __init__(self):
        self.macros: Dict[str, List[str]] = {}

    def define(self, name: str, commands: List[str]):
        """Define a macro with a list of commands"""
        if not name:
            raise ValueError("Macro name cannot be empty")
        if not commands:
            raise ValueError("Macro must contain at least one command")

        self.macros[name] = commands

    def get(self, name: str) -> List[str]:
        """Get macro commands by name"""
        if name not in self.macros:
            raise KeyError(f"Macro '{name}' not found")
        return self.macros[name]

    def exists(self, name: str) -> bool:
        """Check if macro exists"""
        return name in self.macros

    def delete(self, name: str):
        """Delete a macro"""
        if name not in self.macros:
            raise KeyError(f"Macro '{name}' not found")
        del self.macros[name]

    def list_all(self) -> Dict[str, List[str]]:
        """List all macros"""
        return self.macros.copy()

    def clear(self):
        """Clear all macros"""
        self.macros.clear()
