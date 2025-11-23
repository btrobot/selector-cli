"""
Macro manager for Selector CLI
"""
from typing import Dict, List, Optional


class Macro:
    """Represents a macro with optional parameters"""

    def __init__(self, name: str, commands: List[str], parameters: Optional[List[str]] = None):
        self.name = name
        self.commands = commands
        self.parameters = parameters or []

    def expand(self, arguments: List[str]) -> List[str]:
        """
        Expand macro commands with provided arguments
        Replace {param1}, {param2}, etc. with actual values
        """
        if len(arguments) < len(self.parameters):
            raise ValueError(
                f"Macro '{self.name}' expects {len(self.parameters)} parameters "
                f"({', '.join(self.parameters)}), but got {len(arguments)}"
            )

        # Create parameter mapping
        param_map = {}
        for i, param in enumerate(self.parameters):
            if i < len(arguments):
                param_map[f"{{{param}}}"] = arguments[i]

        # Replace parameters in all commands
        expanded_commands = []
        for cmd in self.commands:
            expanded_cmd = cmd
            for param_placeholder, value in param_map.items():
                expanded_cmd = expanded_cmd.replace(param_placeholder, value)
            expanded_commands.append(expanded_cmd)

        return expanded_commands

    def __str__(self):
        if self.parameters:
            params_str = " {{" + "}} {{".join(self.parameters) + "}}"
        else:
            params_str = ""
        return f"{self.name}{params_str}: {'; '.join(self.commands)}"


class MacroManager:
    """Manage command macros"""

    def __init__(self):
        self.macros: Dict[str, Macro] = {}

    def define(self, name: str, commands: List[str], parameters: Optional[List[str]] = None):
        """Define a macro with a list of commands and optional parameters"""
        if not name:
            raise ValueError("Macro name cannot be empty")
        if not commands:
            raise ValueError("Macro must contain at least one command")

        self.macros[name] = Macro(name, commands, parameters)

    def get(self, name: str) -> Macro:
        """Get macro by name"""
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

    def list_all(self) -> Dict[str, Macro]:
        """List all macros"""
        return self.macros.copy()

    def clear(self):
        """Clear all macros"""
        self.macros.clear()

    def run(self, name: str, arguments: List[str]) -> List[str]:
        """
        Run a macro with arguments and return expanded commands
        """
        macro = self.get(name)
        return macro.expand(arguments)
