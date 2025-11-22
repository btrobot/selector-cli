"""
Element data model for Selector CLI
"""
from dataclasses import dataclass, field
from typing import Dict, Optional, List
from datetime import datetime
from playwright.async_api import Locator, ElementHandle


@dataclass
class Element:
    """Web element representation"""

    # Identification
    index: int
    uuid: str

    # Basic Properties
    tag: str
    type: str = ""
    text: str = ""
    value: str = ""

    # Attributes
    attributes: Dict[str, str] = field(default_factory=dict)

    # Computed Properties
    name: str = ""
    id: str = ""
    classes: List[str] = field(default_factory=list)
    placeholder: str = ""

    # Location
    selector: str = ""
    xpath: str = ""
    path: str = ""

    # State
    visible: bool = True
    enabled: bool = True
    disabled: bool = False

    # Shadow DOM
    in_shadow: bool = False
    shadow_host: Optional[str] = None
    shadow_path: Optional[str] = None

    # Playwright
    locator: Optional[Locator] = None
    handle: Optional[ElementHandle] = None

    # Metadata
    scanned_at: datetime = field(default_factory=datetime.now)
    page_url: str = ""

    def __str__(self) -> str:
        """String representation of element"""
        parts = [f"[{self.index}]", self.tag]

        if self.type:
            parts.append(f'type="{self.type}"')
        if self.id:
            parts.append(f'id="{self.id}"')
        if self.name:
            parts.append(f'name="{self.name}"')
        if self.placeholder:
            parts.append(f'placeholder="{self.placeholder}"')
        if self.text and len(self.text) <= 30:
            parts.append(f'text="{self.text}"')

        return " ".join(parts)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'index': self.index,
            'uuid': self.uuid,
            'tag': self.tag,
            'type': self.type,
            'text': self.text,
            'value': self.value,
            'attributes': self.attributes,
            'name': self.name,
            'id': self.id,
            'classes': self.classes,
            'placeholder': self.placeholder,
            'selector': self.selector,
            'xpath': self.xpath,
            'visible': self.visible,
            'enabled': self.enabled,
            'disabled': self.disabled,
            'in_shadow': self.in_shadow,
            'shadow_host': self.shadow_host,
            'shadow_path': self.shadow_path,
            'scanned_at': self.scanned_at.isoformat(),
            'page_url': self.page_url,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Element':
        """Create Element from dictionary"""
        # Remove locator and handle as they can't be serialized
        data.pop('locator', None)
        data.pop('handle', None)

        # Convert datetime
        if 'scanned_at' in data and isinstance(data['scanned_at'], str):
            data['scanned_at'] = datetime.fromisoformat(data['scanned_at'])

        return cls(**data)
