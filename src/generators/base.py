"""
Code generator base class for Selector CLI
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from src.core.element import Element


class CodeGenerator(ABC):
    """Base class for code generators"""

    def __init__(self):
        self.url: Optional[str] = None

    @abstractmethod
    def generate(self, elements: List[Element], url: Optional[str] = None) -> str:
        """
        Generate code for the given elements

        Args:
            elements: List of elements to generate code for
            url: Optional URL of the page

        Returns:
            Generated code as string
        """
        pass

    @abstractmethod
    def get_format_name(self) -> str:
        """Return the name of this format (e.g., 'playwright', 'selenium')"""
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        """Return the file extension for this format (e.g., '.py', '.js')"""
        pass

    def format_selector(self, element: Element) -> str:
        """
        Format element selector for use in generated code

        Args:
            element: Element to format selector for

        Returns:
            Formatted selector string
        """
        # Prefer CSS selector, fallback to generated selector
        if element.selector:
            return element.selector

        # Build selector from element properties
        if element.id:
            return f"#{element.id}"
        elif element.tag and element.type:
            return f"{element.tag}[type='{element.type}']"
        elif element.tag and element.name:
            return f"{element.tag}[name='{element.name}']"
        elif element.tag:
            return element.tag

        return "*"  # Fallback

    def generate_variable_name(self, element: Element) -> str:
        """
        Generate a Python/JavaScript-friendly variable name from element

        Args:
            element: Element to generate name for

        Returns:
            Valid variable name
        """
        # Priority: name > id > type
        if element.name:
            name = element.name
        elif element.id:
            name = element.id
        elif element.type:
            name = f"{element.tag}_{element.type}"
        else:
            name = f"{element.tag}_{element.index}"

        # Sanitize: replace invalid chars with underscore
        name = name.replace("-", "_").replace(".", "_").replace("[", "_").replace("]", "_")
        name = "".join(c if c.isalnum() or c == "_" else "_" for c in name)

        # Ensure it doesn't start with a number
        if name and name[0].isdigit():
            name = f"elem_{name}"

        return name or f"elem_{element.index}"
