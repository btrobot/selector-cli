"""
ElementCollection data model for Selector CLI
"""
from typing import List, Dict, Optional, Callable
from datetime import datetime
from src.core.element import Element


class ElementCollection:
    """Collection of elements with filtering and set operations"""

    def __init__(self, name: Optional[str] = None):
        self.elements: List[Element] = []
        self._index: Dict[int, Element] = {}
        self.name = name
        self.created_at = datetime.now()
        self.modified_at = datetime.now()

    def add(self, element: Element) -> None:
        """Add element to collection"""
        if element.index not in self._index:
            self.elements.append(element)
            self._index[element.index] = element
            self.modified_at = datetime.now()

    def remove(self, element: Element) -> None:
        """Remove element from collection"""
        if element.index in self._index:
            self.elements.remove(element)
            del self._index[element.index]
            self.modified_at = datetime.now()

    def clear(self) -> None:
        """Clear all elements"""
        self.elements.clear()
        self._index.clear()
        self.modified_at = datetime.now()

    def filter(self, condition: Callable[[Element], bool]) -> 'ElementCollection':
        """Filter elements by condition, returns new collection"""
        result = ElementCollection(name=f"{self.name}_filtered" if self.name else None)
        for elem in self.elements:
            if condition(elem):
                result.add(elem)
        return result

    def contains(self, element: Element) -> bool:
        """Check if element is in collection"""
        return element.index in self._index

    def get(self, index: int) -> Optional[Element]:
        """Get element by index"""
        return self._index.get(index)

    def count(self) -> int:
        """Get element count"""
        return len(self.elements)

    def is_empty(self) -> bool:
        """Check if collection is empty"""
        return len(self.elements) == 0

    def union(self, other: 'ElementCollection') -> 'ElementCollection':
        """Union with another collection"""
        result = ElementCollection()
        for elem in self.elements:
            result.add(elem)
        for elem in other.elements:
            result.add(elem)
        return result

    def intersection(self, other: 'ElementCollection') -> 'ElementCollection':
        """Intersection with another collection"""
        result = ElementCollection()
        for elem in self.elements:
            if other.contains(elem):
                result.add(elem)
        return result

    def difference(self, other: 'ElementCollection') -> 'ElementCollection':
        """Difference with another collection"""
        result = ElementCollection()
        for elem in self.elements:
            if not other.contains(elem):
                result.add(elem)
        return result

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat(),
            'elements': [elem.to_dict() for elem in self.elements]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ElementCollection':
        """Create ElementCollection from dictionary"""
        collection = cls(name=data.get('name'))
        collection.created_at = datetime.fromisoformat(data['created_at'])
        collection.modified_at = datetime.fromisoformat(data['modified_at'])

        for elem_data in data.get('elements', []):
            elem = Element.from_dict(elem_data)
            collection.add(elem)

        return collection

    def __len__(self) -> int:
        """Length of collection"""
        return len(self.elements)

    def __iter__(self):
        """Iterate over elements"""
        return iter(self.elements)

    def __str__(self) -> str:
        """String representation"""
        return f"ElementCollection(name={self.name}, count={self.count()})"
