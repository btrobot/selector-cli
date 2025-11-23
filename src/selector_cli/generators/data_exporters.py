"""
Data exporters for Selector CLI (JSON, CSV, YAML)
"""
import json
import csv
from typing import List, Optional
from io import StringIO
from ..core.element import Element
from .base import CodeGenerator


class JSONExporter(CodeGenerator):
    """Export elements as JSON"""

    def get_format_name(self) -> str:
        return "json"

    def get_file_extension(self) -> str:
        return ".json"

    def generate(self, elements: List[Element], url: Optional[str] = None) -> str:
        """Generate JSON export"""
        if not elements:
            return "[]"

        data = []
        for elem in elements:
            data.append({
                "index": elem.index,
                "tag": elem.tag,
                "type": elem.type,
                "id": elem.id,
                "name": elem.name,
                "selector": elem.selector,
                "xpath": elem.xpath,
                "text": elem.text[:100] if elem.text else "",  # Truncate long text
                "placeholder": elem.placeholder,
                "visible": elem.visible,
                "enabled": elem.enabled,
                "attributes": elem.attributes,
            })

        return json.dumps(data, indent=2, ensure_ascii=False)


class CSVExporter(CodeGenerator):
    """Export elements as CSV"""

    def get_format_name(self) -> str:
        return "csv"

    def get_file_extension(self) -> str:
        return ".csv"

    def generate(self, elements: List[Element], url: Optional[str] = None) -> str:
        """Generate CSV export"""
        if not elements:
            return "index,tag,type,id,name,selector,xpath,text,placeholder,visible,enabled\n"

        output = StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "index", "tag", "type", "id", "name",
            "selector", "xpath", "text", "placeholder",
            "visible", "enabled"
        ])

        # Data rows
        for elem in elements:
            writer.writerow([
                elem.index,
                elem.tag,
                elem.type,
                elem.id,
                elem.name,
                elem.selector,
                elem.xpath,
                elem.text[:100] if elem.text else "",  # Truncate long text
                elem.placeholder,
                elem.visible,
                elem.enabled,
            ])

        return output.getvalue()


class YAMLExporter(CodeGenerator):
    """Export elements as YAML"""

    def get_format_name(self) -> str:
        return "yaml"

    def get_file_extension(self) -> str:
        return ".yaml"

    def generate(self, elements: List[Element], url: Optional[str] = None) -> str:
        """Generate YAML export"""
        if not elements:
            return "[]"

        lines = []
        for i, elem in enumerate(elements):
            if i > 0:
                lines.append("")
            lines.append(f"- index: {elem.index}")
            lines.append(f"  tag: {elem.tag}")
            if elem.type:
                lines.append(f"  type: {elem.type}")
            if elem.id:
                lines.append(f"  id: {elem.id}")
            if elem.name:
                lines.append(f"  name: {elem.name}")
            if elem.selector:
                lines.append(f"  selector: '{elem.selector}'")
            if elem.xpath:
                lines.append(f"  xpath: '{elem.xpath}'")
            if elem.text:
                text = elem.text[:100].replace("'", "''")  # Escape and truncate
                lines.append(f"  text: '{text}'")
            if elem.placeholder:
                lines.append(f"  placeholder: '{elem.placeholder}'")
            lines.append(f"  visible: {str(elem.visible).lower()}")
            lines.append(f"  enabled: {str(elem.enabled).lower()}")

        return "\n".join(lines)
