"""
Command executor for Selector CLI
"""
from typing import Optional
from ..parser.command import Command, TargetType, Operator
from ..core.context import Context
from ..core.scanner import ElementScanner


class CommandExecutor:
    """Execute parsed commands"""

    def __init__(self):
        self.scanner = ElementScanner()

    async def execute(self, command: Command, context: Context) -> str:
        """Execute command and return result message"""

        if command.verb == 'open':
            return await self._execute_open(command, context)
        elif command.verb == 'scan':
            return await self._execute_scan(command, context)
        elif command.verb == 'add':
            return await self._execute_add(command, context)
        elif command.verb == 'remove':
            return await self._execute_remove(command, context)
        elif command.verb == 'clear':
            return await self._execute_clear(command, context)
        elif command.verb == 'list':
            return await self._execute_list(command, context)
        elif command.verb == 'show':
            return await self._execute_show(command, context)
        elif command.verb == 'count':
            return await self._execute_count(command, context)
        elif command.verb == 'help':
            return await self._execute_help(command, context)
        else:
            return f"Unknown command: {command.verb}"

    async def _execute_open(self, command: Command, context: Context) -> str:
        """Execute open command"""
        if not context.browser:
            return "Error: Browser not initialized"

        url = command.argument
        if not url:
            return "Error: No URL provided"

        # Add https:// if no protocol
        if not url.startswith(('http://', 'https://', 'file://')):
            url = 'https://' + url

        success = await context.browser.open(url)
        if success:
            context.current_url = url
            context.is_page_loaded = True
            return f"Opened: {url}"
        else:
            return f"Failed to open: {url}"

    async def _execute_scan(self, command: Command, context: Context) -> str:
        """Execute scan command"""
        if not context.browser or not context.is_page_loaded:
            return "Error: No page loaded. Use 'open <url>' first."

        page = context.browser.get_page()
        elements = await self.scanner.scan(page)
        context.update_elements(elements)

        return f"Scanned {len(elements)} elements"

    async def _execute_add(self, command: Command, context: Context) -> str:
        """Execute add command"""
        if not command.target:
            return "Error: No target specified"

        # Get elements to add based on target
        elements_to_add = self._resolve_target(command.target, context)

        # Apply condition if present
        if command.condition:
            elements_to_add = self._filter_by_condition(elements_to_add, command.condition)

        # Add to collection
        added_count = 0
        for elem in elements_to_add:
            if not context.collection.contains(elem):
                context.collection.add(elem)
                added_count += 1

        return f"Added {added_count} element(s) to collection. Total: {context.collection.count()}"

    async def _execute_remove(self, command: Command, context: Context) -> str:
        """Execute remove command"""
        if not command.target:
            return "Error: No target specified"

        # Get elements to remove
        elements_to_remove = self._resolve_target(command.target, context)

        # Apply condition if present
        if command.condition:
            elements_to_remove = self._filter_by_condition(elements_to_remove, command.condition)

        # Remove from collection
        removed_count = 0
        for elem in elements_to_remove:
            if context.collection.contains(elem):
                context.collection.remove(elem)
                removed_count += 1

        return f"Removed {removed_count} element(s). Remaining: {context.collection.count()}"

    async def _execute_clear(self, command: Command, context: Context) -> str:
        """Execute clear command"""
        count = context.collection.count()
        context.collection.clear()
        return f"Cleared {count} element(s) from collection"

    async def _execute_list(self, command: Command, context: Context) -> str:
        """Execute list command"""
        # Determine what to list
        if command.target:
            elements = self._resolve_target(command.target, context)
        else:
            # List collection if no target
            elements = list(context.collection.elements)

        # Apply condition if present
        if command.condition:
            elements = self._filter_by_condition(elements, command.condition)

        # Format output
        if not elements:
            return "No elements found"

        lines = []
        for elem in elements:
            lines.append(f"  {elem}")

        return f"Elements ({len(elements)}):\n" + "\n".join(lines)

    async def _execute_show(self, command: Command, context: Context) -> str:
        """Execute show command"""
        if command.target:
            # Show specific elements
            elements = self._resolve_target(command.target, context)
        else:
            # Show collection
            elements = list(context.collection.elements)

        if not elements:
            return "No elements to show"

        lines = []
        for elem in elements:
            lines.append(f"\n[{elem.index}] {elem.tag}")
            lines.append(f"  Selector: {elem.selector}")
            if elem.type:
                lines.append(f"  Type: {elem.type}")
            if elem.id:
                lines.append(f"  ID: {elem.id}")
            if elem.name:
                lines.append(f"  Name: {elem.name}")
            if elem.placeholder:
                lines.append(f"  Placeholder: {elem.placeholder}")
            if elem.text:
                lines.append(f"  Text: {elem.text[:50]}")

        return "".join(lines)

    async def _execute_count(self, command: Command, context: Context) -> str:
        """Execute count command"""
        return f"Collection contains {context.collection.count()} element(s)"

    async def _execute_help(self, command: Command, context: Context) -> str:
        """Execute help command"""
        return """
Selector CLI - Phase 1 MVP Commands:

Browser Commands:
  open <url>              Open a URL

Scan Commands:
  scan                    Scan page for elements

Collection Commands:
  add <target>            Add elements to collection
  add <target> where <condition>
  remove <target>         Remove elements from collection
  clear                   Clear collection

Query Commands:
  list                    List collection
  list <target>           List specific elements
  show                    Show collection details
  show <target>           Show element details
  count                   Count collection elements

Targets:
  input, button, select, textarea, a
  [5]                     Single index
  [1,2,3]                 Multiple indices
  all                     All elements

WHERE Conditions (Phase 1):
  where type="email"
  where id="submit-btn"
  where name!="hidden"

Utility:
  help                    Show this help
  quit, exit, q          Exit CLI

Examples:
  open https://example.com
  scan
  add input
  add button where type="submit"
  list
  show [0]
  count
"""

    def _resolve_target(self, target, context):
        """Resolve target to list of elements"""
        if target.type == TargetType.ALL:
            return context.all_elements

        elif target.type == TargetType.ELEMENT_TYPE:
            return context.get_elements_by_type(target.element_type)

        elif target.type == TargetType.INDEX:
            elem = context.get_element_by_index(target.indices[0])
            return [elem] if elem else []

        elif target.type == TargetType.INDICES:
            elements = []
            for idx in target.indices:
                elem = context.get_element_by_index(idx)
                if elem:
                    elements.append(elem)
            return elements

        return []

    def _filter_by_condition(self, elements, condition):
        """Filter elements by condition"""
        result = []
        for elem in elements:
            if self._evaluate_condition(elem, condition):
                result.append(elem)
        return result

    def _evaluate_condition(self, elem, condition) -> bool:
        """Evaluate if element matches condition"""
        # Get field value
        field_value = getattr(elem, condition.field, None)
        if field_value is None:
            field_value = elem.attributes.get(condition.field, "")

        # Compare
        if condition.operator == Operator.EQUALS:
            return str(field_value) == str(condition.value)
        elif condition.operator == Operator.NOT_EQUALS:
            return str(field_value) != str(condition.value)

        return False
