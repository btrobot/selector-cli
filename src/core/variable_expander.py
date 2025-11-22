"""
Variable expander for Selector CLI
"""
import re
from typing import Dict, Any


class VariableExpander:
    """Expand variables in command strings"""

    def expand(self, text: str, variables: Dict[str, Any]) -> str:
        """
        Expand variables in text.

        Supports:
        - $var - simple variable reference
        - ${var} - variable with explicit boundary

        Args:
            text: Command string with possible variable references
            variables: Dictionary of variable name -> value

        Returns:
            Text with variables expanded

        Raises:
            ValueError: If undefined variable is referenced
        """
        if not text or not variables:
            return text

        # Pattern for ${var} and $var
        # ${var} takes priority
        pattern = r'\$\{([a-zA-Z_][a-zA-Z0-9_]*)\}|\$([a-zA-Z_][a-zA-Z0-9_]*)'

        def replace_var(match):
            # Try ${var} first (group 1), then $var (group 2)
            var_name = match.group(1) if match.group(1) else match.group(2)

            if var_name not in variables:
                raise ValueError(f"Undefined variable: {var_name}")

            value = variables[var_name]
            return str(value)

        try:
            expanded = re.sub(pattern, replace_var, text)
            return expanded
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Error expanding variables: {e}")

    def has_variables(self, text: str) -> bool:
        """Check if text contains variable references"""
        pattern = r'\$\{[a-zA-Z_][a-zA-Z0-9_]*\}|\$[a-zA-Z_][a-zA-Z0-9_]*'
        return bool(re.search(pattern, text))

    def get_variable_names(self, text: str) -> list:
        """Extract all variable names from text"""
        pattern = r'\$\{([a-zA-Z_][a-zA-Z0-9_]*)\}|\$([a-zA-Z_][a-zA-Z0-9_]*)'
        matches = re.findall(pattern, text)
        # Flatten tuples and filter empty strings
        names = [name for match in matches for name in match if name]
        return list(set(names))  # Return unique names
