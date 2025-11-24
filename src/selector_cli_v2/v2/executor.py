"""
ExecutorV2 - Execute v2 commands with three-layer architecture
"""
from typing import List, Optional, Dict, Any, Tuple
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from selector_cli.core.element import Element
from selector_cli.core.scanner import ElementScanner
from selector_cli_v2.v2.context import ContextV2
from selector_cli_v2.v2.command import CommandV2
from selector_cli.parser.command import ConditionNode, ConditionType, Operator


class ExecutorV2:
    """Execute v2 commands"""

    def __init__(self, ctx: ContextV2):
        self.ctx = ctx

    async def execute(self, cmd: CommandV2) -> Tuple[bool, Any]:
        """
        Execute a command and return (success, result)

        Args:
            cmd: CommandV2 to execute

        Returns:
            (success: bool, result: Any) - result depends on command type
        """
        try:
            if cmd.verb == "find":
                result = await self.execute_find(cmd)
                return True, result

            elif cmd.verb == "add":
                result = await self.execute_add(cmd)
                return True, result

            elif cmd.verb == "list":
                result = await self.execute_list(cmd)
                return True, result

            elif cmd.verb == "scan":
                result = await self.execute_scan(cmd)
                return True, result

            elif cmd.verb == "preview":
                result = await self.execute_preview(cmd)
                return True, result

            elif cmd.verb == "export":
                result = await self.execute_export(cmd)
                return True, result

            elif cmd.verb == "remove":
                result = await self.execute_remove(cmd)
                return True, result

            elif cmd.verb == "clear":
                result = await self.execute_clear(cmd)
                return True, result

            else:
                return False, f"Unsupported command verb: {cmd.verb}"

        except Exception as e:
            return False, f"Error executing command: {str(e)}"

    async def execute_find(self, cmd: CommandV2) -> List[Element]:
        """
        Execute find command - query DOM and store results in temp

        Args:
            cmd: CommandV2 with verb="find"

        Returns:
            List of found elements (also stored in ctx.temp)
        """
        if not self.ctx.browser or not self.ctx.browser.get_page():
            raise ValueError("No browser/page loaded")

        page = self.ctx.browser.get_page()

        # Determine source
        source_layer = cmd.get_source_layer()

        # If this is a refine command (.find), source is temp
        if cmd.is_refine_command():
            # Start from current temp results
            elements = self.ctx.temp.copy()
        elif source_layer == "temp":
            # Find from temp (shouldn't happen for top-level find, but support it)
            elements = self.ctx.temp.copy()
        elif source_layer == "candidates":
            # Find from candidates
            elements = self.ctx.candidates.copy()
        elif source_layer == "workspace":
            # Find from workspace
            elements = self.ctx.workspace.get_all()
        else:
            # Default: query from DOM
            elements = await self._query_dom(page, cmd)

        # Apply WHERE conditions if present
        if cmd.condition_tree:
            elements = self._filter_elements(elements, cmd.condition_tree)

        # Store in temp
        self.ctx.temp = elements

        return elements

    async def execute_add(self, cmd: CommandV2) -> int:
        """
        Execute add command - add elements to workspace

        Args:
            cmd: CommandV2 with verb="add"

        Returns:
            Number of elements added
        """
        # Determine source (candidates is default)
        source = cmd.source or "candidates"

        # Get source elements
        if source == "candidates":
            source_elements = self.ctx.candidates
        elif source == "temp":
            source_elements = self.ctx.temp
        elif source == "workspace":
            source_elements = self.ctx.workspace.get_all()
        else:
            raise ValueError(f"Invalid source: {source}")

        # Filter by element types if specified
        if cmd.element_types:
            elements_to_add = []
            for elem_type in cmd.element_types:
                if elem_type == "*":
                    elements_to_add.extend(source_elements)
                else:
                    elements_to_add.extend([e for e in source_elements if e.tag == elem_type])
        else:
            # Add all from source
            elements_to_add = source_elements

        # Apply WHERE conditions if present
        if cmd.condition_tree:
            elements_to_add = self._filter_elements(elements_to_add, cmd.condition_tree)

        # Add to workspace
        added_count = 0
        if cmd.is_append_mode():
            # Append mode: add all (no deduplication)
            for elem in elements_to_add:
                if not self.ctx.workspace.contains(elem):
                    self.ctx.add_to_workspace(elem)
                    added_count += 1
        else:
            # Overwrite mode: smart add (check if exists)
            added_count = self.ctx.add_many_to_workspace(elements_to_add)

        return added_count

    async def execute_list(self, cmd: CommandV2) -> str:
        """
        Execute list command - format and return elements

        Args:
            cmd: CommandV2 with verb="list"

        Returns:
            Formatted string of elements
        """
        # Determine source (workspace is default)
        source = cmd.source or "workspace"

        # Get elements
        if source == "candidates":
            elements = self.ctx.candidates
        elif source == "temp":
            elements = self.ctx.temp
        elif source == "workspace":
            elements = self.ctx.workspace.get_all()
        else:
            raise ValueError(f"Invalid source: {source}")

        # Filter by target if specified
        if cmd.target:
            if cmd.target.type.value == "ELEMENT_TYPE":
                elements = [e for e in elements if e.tag == cmd.target.element_type]
            elif cmd.target.type.value == "INDEX":
                elements = [e for e in elements if e.index in (cmd.target.indices or [])]

        # Apply WHERE conditions if present
        if cmd.condition_tree:
            elements = self._filter_elements(elements, cmd.condition_tree)

        # Format output
        return self._format_elements(elements, source)

    async def execute_scan(self, cmd: CommandV2) -> List[Element]:
        """
        Execute scan command - scan page for elements

        Args:
            cmd: CommandV2 with verb="scan"

        Returns:
            List of scanned elements (stored in ctx.candidates)
        """
        if not self.ctx.browser or not self.ctx.browser.get_page():
            raise ValueError("No browser/page loaded")

        page = self.ctx.browser.get_page()
        scanner = ElementScanner()

        # Get element types to scan
        element_types = cmd.element_types or scanner.DEFAULT_ELEMENT_TYPES

        # Scan for elements
        elements = await scanner.scan(page, element_types=element_types)

        # Store in candidates
        self.ctx.candidates = elements

        return elements

    async def execute_preview(self, cmd: CommandV2) -> str:
        """
        Execute preview command - highlight elements in browser

        Args:
            cmd: CommandV2 with verb="preview"

        Returns:
            Success message
        """
        if not self.ctx.browser or not self.ctx.browser.get_page():
            raise ValueError("No browser/page loaded")

        page = self.ctx.browser.get_page()

        # Determine source (workspace is default)
        source = cmd.source or "workspace"

        # Get elements
        if source == "candidates":
            elements = self.ctx.candidates
        elif source == "temp":
            elements = self.ctx.temp
        elif source == "workspace":
            elements = self.ctx.workspace.get_all()
        else:
            raise ValueError(f"Invalid source: {source}")

        # Filter by target if specified
        if cmd.target:
            if cmd.target.type.value == "ELEMENT_TYPE":
                elements = [e for e in elements if e.tag == cmd.target.element_type]

        # Import Highlighter
        from selector_cli.core.highlighter import Highlighter

        # Create or reuse highlighter
        if not hasattr(self, '_highlighter'):
            self._highlighter = Highlighter(page)

        # Clear previous highlights
        await self._highlighter.unhighlight_all()

        # Highlight elements
        try:
            count = await self._highlighter.highlight_elements(elements, color='info')
            return f"Highlighted {count} elements from {source}"
        except Exception as e:
            return f"Preview failed: {e}"

    async def execute_export(self, cmd: CommandV2) -> str:
        """
        Execute export command

        Args:
            cmd: CommandV2 with verb="export"

        Returns:
            Export result
        """
        # TODO: Implement export logic
        return f"Export command received: {cmd.argument}"

    async def execute_remove(self, cmd: CommandV2) -> int:
        """
        Execute remove command - remove elements from workspace

        Args:
            cmd: CommandV2 with verb="remove"

        Returns:
            Number of elements removed
        """
        # Determine source (workspace is default)
        source = cmd.source or "workspace"

        # Get source elements
        if source == "workspace":
            source_elements = self.ctx.workspace.get_all()
        elif source == "temp":
            source_elements = self.ctx.temp
        elif source == "candidates":
            source_elements = self.ctx.candidates
        else:
            raise ValueError(f"Invalid source: {source}")

        # Filter by target if specified
        elements_to_remove = source_elements
        if cmd.target:
            if cmd.target.type.value == "ELEMENT_TYPE":
                elements_to_remove = [e for e in elements_to_remove if e.tag == cmd.target.element_type]

        # Apply WHERE conditions if present
        if cmd.condition_tree:
            elements_to_remove = self._filter_elements(elements_to_remove, cmd.condition_tree)

        # Remove from workspace (only workspace is valid target for remove)
        removed_count = 0
        if source == "workspace":
            for elem in elements_to_remove:
                if self.ctx.remove_from_workspace(elem):
                    removed_count += 1

        return removed_count

    async def execute_clear(self, cmd: CommandV2) -> str:
        """
        Execute clear command - clear workspace

        Args:
            cmd: CommandV2 with verb="clear"

        Returns:
            Success message
        """
        # Clear any highlights first
        if hasattr(self, '_highlighter'):
            try:
                await self._highlighter.unhighlight_all()
            except Exception:
                pass

        self.ctx.clear_workspace()
        return "Workspace cleared"

    # =========================================================================
    # Helper Methods
    # =========================================================================

    async def _query_dom(self, page, cmd: CommandV2) -> List[Element]:
        """Query DOM for elements matching command criteria"""
        elements = []

        if not cmd.element_types:
            return elements

        # Query each element type
        element_index = 0
        for elem_type in cmd.element_types:
            if elem_type == "*":
                # Query all elements - NOT IMPLEMENTED YET
                continue

            # Query elements by tag name
            locators = await page.locator(elem_type).all()

            for locator in locators:
                try:
                    # Build element (reuse scanner logic)
                    scanner = ElementScanner()
                    element = await scanner._build_element(
                        locator, element_index, elem_type, page.url, page
                    )
                    elements.append(element)
                    element_index += 1
                except Exception:
                    # Skip if we can't build element
                    continue

        return elements

    def _filter_elements(self, elements: List[Element], condition_tree) -> List[Element]:
        """Filter elements based on condition tree"""
        return [e for e in elements if self._evaluate_condition(e, condition_tree)]

    def _evaluate_condition(self, element: Element, condition_node) -> bool:
        """Evaluate condition tree against element"""
        from selector_cli.parser.command import ConditionType, LogicOp, Operator

        if condition_node.type == ConditionType.SIMPLE:
            return self._evaluate_simple_condition(element, condition_node)

        elif condition_node.type == ConditionType.COMPOUND:
            left_result = self._evaluate_condition(element, condition_node.left)
            right_result = self._evaluate_condition(element, condition_node.right)

            if condition_node.logic_op == LogicOp.AND:
                return left_result and right_result
            elif condition_node.logic_op == LogicOp.OR:
                return left_result or right_result

        elif condition_node.type == ConditionType.UNARY:
            operand_result = self._evaluate_condition(element, condition_node.operand)
            return not operand_result

        return False

    def _evaluate_simple_condition(self, element: Element, condition_node) -> bool:
        """Evaluate simple condition against element"""
        field = condition_node.field
        operator = condition_node.operator
        value = condition_node.value

        # Get field value from element
        field_value = self._get_field_value(element, field)

        # Evaluate based on operator
        if operator == Operator.EQUALS:
            return field_value == value
        elif operator == Operator.NOT_EQUALS:
            return field_value != value
        elif operator == Operator.CONTAINS:
            return value in str(field_value)
        elif operator == Operator.GT:
            return field_value > value
        elif operator == Operator.GTE:
            return field_value >= value
        elif operator == Operator.LT:
            return field_value < value
        elif operator == Operator.LTE:
            return field_value <= value

        return False

    def _get_field_value(self, element: Element, field: str):
        """Get field value from element"""
        if field == "tag":
            return element.tag
        elif field == "type":
            return element.type
        elif field == "text":
            return element.text
        elif field == "value":
            return element.value
        elif field == "id":
            return element.id
        elif field == "name":
            return element.name
        elif field == "visible":
            return element.visible
        elif field == "enabled":
            return element.enabled
        elif field == "disabled":
            return element.disabled
        elif field in element.attributes:
            return element.attributes[field]
        else:
            # Default to attribute or empty string
            return element.attributes.get(field, "")

    def _format_elements(self, elements: List[Element], source: str) -> str:
        """Format elements for display"""
        if not elements:
            return f"No elements in {source}"

        lines = [f"Found {len(elements)} elements in {source}:", ""]

        for elem in elements:
            # Basic info
            parts = [f"[{elem.index}] <{elem.tag}>"]

            # Add type if present
            if elem.type:
                parts.append(f'type="{elem.type}"')

            # Add id if present
            if elem.id:
                parts.append(f'id="{elem.id}"')

            # Add name if present
            if elem.name:
                parts.append(f'name="{elem.name}"')

            # Add role if present
            if elem.attributes.get("role"):
                parts.append(f"role='{elem.attributes['role']}'")

            # Add text (truncated)
            if elem.text:
                text_preview = elem.text[:50].replace('\n', ' ')
                if len(elem.text) > 50:
                    text_preview += "..."
                parts.append(f'text="{text_preview}"')

            # Add state
            if not elem.visible:
                parts.append("(hidden)")
            if not elem.enabled:
                parts.append("(disabled)")

            lines.append(" ".join(parts))

            # Add selector
            if elem.selector:
                lines.append(f"      Selector: {elem.selector}")

        return "\n".join(lines)
