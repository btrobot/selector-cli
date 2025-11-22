"""
Storage manager for Selector CLI - handles persistence of collections
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.core.element import Element


class StorageManager:
    """Manage persistent storage of collections"""

    def __init__(self, storage_dir: Optional[str] = None):
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            # Default: ~/.selector-cli/collections/
            self.storage_dir = Path.home() / ".selector-cli" / "collections"

        # Ensure directory exists
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_collection(self, name: str, elements: List[Element], url: Optional[str] = None) -> str:
        """Save collection to file"""
        if not name:
            raise ValueError("Collection name cannot be empty")

        # Sanitize name
        safe_name = self._sanitize_name(name)
        filepath = self.storage_dir / f"{safe_name}.json"

        # Build save data
        data = {
            "name": name,
            "url": url or "",
            "saved_at": datetime.now().isoformat(),
            "count": len(elements),
            "elements": [self._element_to_dict(elem) for elem in elements]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return str(filepath)

    def load_collection(self, name: str) -> tuple[List[Element], Dict[str, Any]]:
        """Load collection from file. Returns (elements, metadata)"""
        safe_name = self._sanitize_name(name)
        filepath = self.storage_dir / f"{safe_name}.json"

        if not filepath.exists():
            raise FileNotFoundError(f"Collection '{name}' not found")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        elements = [self._dict_to_element(d) for d in data.get("elements", [])]

        metadata = {
            "name": data.get("name", name),
            "url": data.get("url", ""),
            "saved_at": data.get("saved_at", ""),
            "count": data.get("count", len(elements))
        }

        return elements, metadata

    def list_collections(self) -> List[Dict[str, Any]]:
        """List all saved collections"""
        collections = []

        for filepath in self.storage_dir.glob("*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                collections.append({
                    "name": data.get("name", filepath.stem),
                    "url": data.get("url", ""),
                    "saved_at": data.get("saved_at", ""),
                    "count": data.get("count", 0),
                    "file": filepath.name
                })
            except Exception:
                # Skip invalid files
                continue

        # Sort by saved_at descending
        collections.sort(key=lambda x: x.get("saved_at", ""), reverse=True)
        return collections

    def delete_collection(self, name: str) -> bool:
        """Delete a saved collection"""
        safe_name = self._sanitize_name(name)
        filepath = self.storage_dir / f"{safe_name}.json"

        if not filepath.exists():
            raise FileNotFoundError(f"Collection '{name}' not found")

        filepath.unlink()
        return True

    def collection_exists(self, name: str) -> bool:
        """Check if collection exists"""
        safe_name = self._sanitize_name(name)
        filepath = self.storage_dir / f"{safe_name}.json"
        return filepath.exists()

    def _sanitize_name(self, name: str) -> str:
        """Sanitize collection name for filename"""
        # Replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        result = name
        for char in invalid_chars:
            result = result.replace(char, '_')
        return result.strip()

    def _element_to_dict(self, elem: Element) -> Dict[str, Any]:
        """Convert Element to dictionary for JSON storage"""
        return elem.to_dict()

    def _dict_to_element(self, d: Dict[str, Any]) -> Element:
        """Convert dictionary to Element"""
        return Element.from_dict(d)
