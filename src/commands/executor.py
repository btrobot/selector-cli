"""
Command executor for Selector CLI
"""
from typing import Optional, Any
from src.parser.command import (
    Command, TargetType, Operator,
    ConditionNode, ConditionType, LogicOp  # Phase 2
)
from src.core.context import Context
from src.core.scanner import ElementScanner
# Phase 3: Import generators
from src.generators import (
    PlaywrightGenerator, SeleniumGenerator, PuppeteerGenerator,
    JSONExporter, CSVExporter, YAMLExporter
)


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
        elif command.verb == 'export':
            return await self._execute_export(command, context)
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

            # Clear previous page's elements and collection
            context.all_elements.clear()
            context.collection.clear()
            context.last_scan_time = None

            # Auto-scan after opening page
            page = context.browser.get_page()
            elements = await self.scanner.scan(page)
            context.update_elements(elements)

            return f"Opened: {url}\nAuto-scanned {len(elements)} elements"
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

        # Apply condition if present (Phase 2 or Phase 1)
        if command.condition_tree:
            elements_to_add = self._filter_by_condition_tree(elements_to_add, command.condition_tree)
        elif command.condition:
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

        # Apply condition if present (Phase 2 or Phase 1)
        if command.condition_tree:
            elements_to_remove = self._filter_by_condition_tree(elements_to_remove, command.condition_tree)
        elif command.condition:
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

        # Apply condition if present (Phase 2 or Phase 1)
        if command.condition_tree:
            elements = self._filter_by_condition_tree(elements, command.condition_tree)
        elif command.condition:
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

    async def _execute_export(self, command: Command, context: Context) -> str:
        """Execute export command"""
        if not command.argument:
            return "Error: No export format specified"

        # Parse argument: format or format:filename
        parts = command.argument.split(':', 1)
        export_format = parts[0]
        filename = parts[1] if len(parts) > 1 else None

        # Get elements to export (collection)
        elements = list(context.collection.elements)
        if not elements:
            return "Error: Collection is empty. Add elements before exporting."

        # Get URL
        url = context.current_url if context.current_url else None

        # Select appropriate generator
        generator_map = {
            'playwright': PlaywrightGenerator(),
            'selenium': SeleniumGenerator(),
            'puppeteer': PuppeteerGenerator(),
            'json': JSONExporter(),
            'csv': CSVExporter(),
            'yaml': YAMLExporter(),
        }

        generator = generator_map.get(export_format)
        if not generator:
            return f"Error: Unknown export format '{export_format}'"

        # Generate code/data
        output = generator.generate(elements, url)

        # Write to file or return output
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(output)
                return f"Exported {len(elements)} element(s) to '{filename}' ({export_format} format)"
            except Exception as e:
                return f"Error writing to file '{filename}': {e}"
        else:
            # Return output directly (will be printed to console)
            return f"# Export: {export_format}\n\n{output}"

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
        """Evaluate if element matches condition (Phase 1)"""
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

    # ========== Phase 2: Complex Condition Evaluation ==========

    def _filter_by_condition_tree(self, elements, condition_tree: ConditionNode):
        """Filter elements by condition tree (Phase 2)"""
        result = []
        for elem in elements:
            if self._evaluate_condition_tree(elem, condition_tree):
                result.append(elem)
        return result

    def _evaluate_condition_tree(self, elem, condition: ConditionNode) -> bool:
        """Evaluate complex condition tree recursively"""

        if condition.type == ConditionType.SIMPLE:
            return self._evaluate_simple_condition(elem, condition)

        elif condition.type == ConditionType.COMPOUND:
            left_result = self._evaluate_condition_tree(elem, condition.left)
            right_result = self._evaluate_condition_tree(elem, condition.right)

            if condition.logic_op == LogicOp.AND:
                return left_result and right_result
            elif condition.logic_op == LogicOp.OR:
                return left_result or right_result

        elif condition.type == ConditionType.UNARY:
            operand_result = self._evaluate_condition_tree(elem, condition.operand)
            return not operand_result

        return False

    def _evaluate_simple_condition(self, elem, condition: ConditionNode) -> bool:
        """Evaluate simple condition with Phase 2 operators"""
        # Get field value
        field_value = self._get_field_value(elem, condition.field)
        compare_value = condition.value
        operator = condition.operator

        # Comparison operators
        if operator == Operator.EQUALS:
            return str(field_value) == str(compare_value)
        elif operator == Operator.NOT_EQUALS:
            return str(field_value) != str(compare_value)
        elif operator == Operator.GT:
            return self._to_number(field_value) > self._to_number(compare_value)
        elif operator == Operator.GTE:
            return self._to_number(field_value) >= self._to_number(compare_value)
        elif operator == Operator.LT:
            return self._to_number(field_value) < self._to_number(compare_value)
        elif operator == Operator.LTE:
            return self._to_number(field_value) <= self._to_number(compare_value)

        # String operators
        elif operator == Operator.CONTAINS:
            return str(compare_value) in str(field_value)
        elif operator == Operator.STARTS:
            return str(field_value).startswith(str(compare_value))
        elif operator == Operator.ENDS:
            return str(field_value).endswith(str(compare_value))
        elif operator == Operator.MATCHES:
            import re
            return bool(re.search(str(compare_value), str(field_value)))

        return False

    def _get_field_value(self, elem, field: str) -> Any:
        """Get field value from element"""
        # Direct attribute
        if hasattr(elem, field):
            return getattr(elem, field)

        # From attributes dict
        if field in elem.attributes:
            return elem.attributes[field]

        # Boolean fields (treat as boolean if field name is a boolean keyword)
        if field in ['visible', 'enabled', 'disabled', 'required', 'readonly']:
            if field == 'visible':
                return elem.visible if hasattr(elem, 'visible') else True
            elif field == 'enabled':
                return elem.enabled if hasattr(elem, 'enabled') else True
            elif field == 'disabled':
                return elem.disabled if hasattr(elem, 'disabled') else False
            elif field == 'required':
                return elem.required if hasattr(elem, 'required') else False
            elif field == 'readonly':
                return elem.readonly if hasattr(elem, 'readonly') else False

        return ""

    def _to_number(self, value: Any) -> float:
        """Convert value to number for comparison"""
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
