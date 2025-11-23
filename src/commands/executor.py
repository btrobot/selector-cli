"""
Command executor for Selector CLI
"""
from typing import Optional, Any
from src.parser.command import (
    Command, TargetType, Operator,
    ConditionNode, ConditionType, LogicOp  # Phase 2
)
from src.parser.parser import Parser  # For parsing macro commands
from src.core.context import Context
from src.core.scanner import ElementScanner
from src.core.storage import StorageManager  # Phase 4
from src.core.variable_expander import VariableExpander  # Phase 4
from src.core.highlighter import Highlighter  # Phase 5
# Phase 3: Import generators
from src.generators import (
    PlaywrightGenerator, SeleniumGenerator, PuppeteerGenerator,
    JSONExporter, CSVExporter, YAMLExporter
)


class CommandExecutor:
    """Execute parsed commands"""

    def __init__(self):
        self.scanner = ElementScanner()
        self.storage = StorageManager()  # Phase 4
        self.parser = Parser()  # For parsing macro commands

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
        elif command.verb == 'save':
            return await self._execute_save(command, context)
        elif command.verb == 'load':
            return await self._execute_load(command, context)
        elif command.verb == 'saved':
            return await self._execute_saved(command, context)
        elif command.verb == 'delete':
            return await self._execute_delete(command, context)
        elif command.verb == 'set':
            return await self._execute_set(command, context)
        elif command.verb == 'vars':
            return await self._execute_vars(command, context)
        elif command.verb == 'macro':
            return await self._execute_macro(command, context)
        elif command.verb == 'run':
            return await self._execute_run(command, context)
        elif command.verb == 'macros':
            return await self._execute_macros(command, context)
        elif command.verb == 'exec':
            return await self._execute_exec(command, context)
        elif command.verb == 'highlight':
            return await self._execute_highlight(command, context)
        elif command.verb == 'unhighlight':
            return await self._execute_unhighlight(command, context)
        elif command.verb == 'union':
            return await self._execute_union(command, context)
        elif command.verb == 'intersect':
            return await self._execute_intersect(command, context)
        elif command.verb == 'difference':
            return await self._execute_difference(command, context)
        elif command.verb == 'unique':
            return await self._execute_unique(command, context)
        elif command.verb == 'history':
            return await self._execute_history(command, context)
        elif command.verb == 'bang_n':
            return await self._execute_bang_n(command, context)
        elif command.verb == 'bang_last':
            return await self._execute_bang_last(command, context)
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

    # ========== Phase 4: Persistence Commands ==========

    async def _execute_save(self, command: Command, context: Context) -> str:
        """Execute save command - save collection to file"""
        if not command.argument:
            return "Error: No collection name specified"

        name = command.argument
        elements = list(context.collection.elements)

        if not elements:
            return "Error: Collection is empty. Add elements before saving."

        try:
            filepath = self.storage.save_collection(
                name=name,
                elements=elements,
                url=context.current_url
            )
            return f"Saved {len(elements)} element(s) as '{name}'"
        except Exception as e:
            return f"Error saving collection: {e}"

    async def _execute_load(self, command: Command, context: Context) -> str:
        """Execute load command - load collection from file"""
        if not command.argument:
            return "Error: No collection name specified"

        name = command.argument

        try:
            elements, metadata = self.storage.load_collection(name)

            # Replace current collection
            context.collection.clear()
            for elem in elements:
                context.collection.add(elem)

            url_info = f" (from {metadata['url']})" if metadata.get('url') else ""
            return f"Loaded {len(elements)} element(s) from '{name}'{url_info}"
        except FileNotFoundError:
            return f"Error: Collection '{name}' not found"
        except Exception as e:
            return f"Error loading collection: {e}"

    async def _execute_saved(self, command: Command, context: Context) -> str:
        """Execute saved command - list all saved collections"""
        collections = self.storage.list_collections()

        if not collections:
            return "No saved collections"

        lines = ["Saved collections:"]
        for coll in collections:
            saved_at = coll.get('saved_at', '')[:10]  # Date only
            count = coll.get('count', 0)
            url = coll.get('url', '')
            url_short = url[:40] + '...' if len(url) > 40 else url

            line = f"  {coll['name']}: {count} elements"
            if url_short:
                line += f" ({url_short})"
            if saved_at:
                line += f" [{saved_at}]"
            lines.append(line)

        return "\n".join(lines)

    async def _execute_delete(self, command: Command, context: Context) -> str:
        """Execute delete command - delete saved collection"""
        if not command.argument:
            return "Error: No collection name specified"

        name = command.argument

        try:
            self.storage.delete_collection(name)
            return f"Deleted collection '{name}'"
        except FileNotFoundError:
            return f"Error: Collection '{name}' not found"
        except Exception as e:
            return f"Error deleting collection: {e}"

    async def _execute_set(self, command: Command, context: Context) -> str:
        """Execute set command - set a variable"""
        if not command.argument:
            return "Error: No variable specified"

        # Parse "name=value" format
        if '=' not in command.argument:
            return "Error: Invalid set format. Use: set name = value"

        name, value = command.argument.split('=', 1)
        name = name.strip()
        value = value.strip()

        # Try to parse value as appropriate type
        if value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
        elif value.isdigit():
            value = int(value)
        else:
            try:
                value = float(value)
            except ValueError:
                pass  # Keep as string

        context.variables[name] = value
        return f"Set {name} = {value}"

    async def _execute_vars(self, command: Command, context: Context) -> str:
        """Execute vars command - list all variables"""
        if not context.variables:
            return "No variables set"

        lines = ["Variables:"]
        for name, value in context.variables.items():
            value_type = type(value).__name__
            lines.append(f"  {name} = {value} ({value_type})")

        return "\n".join(lines)

    async def _execute_macro(self, command: Command, context: Context) -> str:
        """Execute macro command - define a macro"""
        if not command.argument:
            return "Error: No macro specified"

        # Parse "name:command" format
        if ':' not in command.argument:
            return "Error: Invalid macro format"

        name, macro_command = command.argument.split(':', 1)
        name = name.strip()
        macro_command = macro_command.strip()

        # Define macro (single command for now)
        try:
            context.macro_manager.define(name, [macro_command])
            return f"Macro '{name}' defined"
        except Exception as e:
            return f"Error defining macro: {e}"

    async def _execute_run(self, command: Command, context: Context) -> str:
        """Execute run command - run a macro"""
        if not command.argument:
            return "Error: No macro name specified"

        macro_name = command.argument

        try:
            # Get macro commands
            commands = context.macro_manager.get(macro_name)

            # Execute each command
            results = []
            for cmd_str in commands:
                # Parse and execute command
                try:
                    cmd = self.parser.parse(cmd_str)
                    result = await self.execute(cmd, context)
                    results.append(result)
                except Exception as e:
                    return f"Error in macro '{macro_name}': {e}\nCommand: {cmd_str}"

            return "\n".join(results)

        except KeyError:
            return f"Error: Macro '{macro_name}' not found"
        except Exception as e:
            return f"Error running macro: {e}"

    async def _execute_macros(self, command: Command, context: Context) -> str:
        """Execute macros command - list all macros"""
        macros = context.macro_manager.list_all()

        if not macros:
            return "No macros defined"

        lines = ["Macros:"]
        for name, commands in macros.items():
            cmd_text = "; ".join(commands)
            lines.append(f"  {name}: {cmd_text}")

        return "\n".join(lines)

    async def _execute_exec(self, command: Command, context: Context) -> str:
        """Execute exec command - run script file"""
        if not command.argument:
            return "Error: No filepath specified"

        filepath = command.argument

        try:
            # Read script file
            with open(filepath, 'r', encoding='utf-8') as f:
                script_lines = f.readlines()

            # Execute each line
            results = []
            line_num = 0

            for line in script_lines:
                line_num += 1
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue

                try:
                    # Parse and execute command
                    cmd = self.parser.parse(line)
                    result = await self.execute(cmd, context)
                    if result and result.strip():
                        results.append(f"[{line_num}] {result}")
                except Exception as e:
                    return f"Error at line {line_num}: {e}\nCommand: {line}"

            return "\n".join(results) if results else f"Executed {filepath}"

        except FileNotFoundError:
            return f"Error: File '{filepath}' not found"
        except Exception as e:
            return f"Error executing script: {e}"

    async def _execute_highlight(self, command: Command, context: Context) -> str:
        """Execute highlight command"""
        if not context.browser or not context.browser.page:
            return "Error: No page loaded"

        # Get or create highlighter
        if not hasattr(context, 'highlighter') or context.highlighter is None:
            context.highlighter = Highlighter(context.browser.page)

        # Case 1: highlight (no target) - highlight current collection
        if not command.target:
            elements = context.collection.get_all()
            if not elements:
                return "No elements in collection to highlight"

            # Use verbose mode to get diagnostics
            result = await context.highlighter.highlight_elements(elements, verbose=True)
            count, failed_indices, error_messages = result

            # Build result message
            msg = f"Highlighted {count} element(s) from collection"
            if failed_indices:
                total = len(elements)
                msg += f"\nWarning: {len(failed_indices)} of {total} element(s) could not be highlighted:"
                for err_msg in error_messages[:5]:  # Show first 5 errors
                    msg += f"\n  {err_msg}"
                if len(error_messages) > 5:
                    msg += f"\n  ... and {len(error_messages) - 5} more"
            return msg

        # Case 2: highlight <target> [where <condition>]
        # Get elements from all_elements based on target
        elements = self._resolve_target(command.target, context)

        # Apply condition filter if present
        if command.condition_tree:
            elements = self._filter_by_condition_tree(elements, command.condition_tree)
        elif command.condition:
            elements = self._filter_by_condition(elements, command.condition)

        if not elements:
            return "No elements matched the criteria"

        count = await context.highlighter.highlight_elements(elements)
        return f"Highlighted {count} element(s)"

    async def _execute_unhighlight(self, command: Command, context: Context) -> str:
        """Execute unhighlight command"""
        if not context.browser or not context.browser.page:
            return "Error: No page loaded"

        # Get highlighter if exists
        if not hasattr(context, 'highlighter') or context.highlighter is None:
            return "No elements currently highlighted"

        count = await context.highlighter.unhighlight_all()
        return f"Removed highlights from {count} element(s)"

    async def _execute_union(self, command: Command, context: Context) -> str:
        """Execute union command - combine with saved collection"""
        if not command.argument:
            return "Error: No collection name specified"

        collection_name = command.argument

        # Load the other collection
        try:
            loaded_collection = self.storage.load_collection(collection_name)
        except FileNotFoundError:
            return f"Error: Collection '{collection_name}' not found"
        except Exception as e:
            return f"Error loading collection: {e}"

        # Get current count
        before_count = context.collection.count()

        # Perform union (in-place)
        context.collection.union_in_place(loaded_collection)

        # Calculate added count
        after_count = context.collection.count()
        added = after_count - before_count

        return f"Union with '{collection_name}': Added {added} element(s). Total: {after_count}"

    async def _execute_intersect(self, command: Command, context: Context) -> str:
        """Execute intersect command - keep only common elements"""
        if not command.argument:
            return "Error: No collection name specified"

        collection_name = command.argument

        # Load the other collection
        try:
            loaded_collection = self.storage.load_collection(collection_name)
        except FileNotFoundError:
            return f"Error: Collection '{collection_name}' not found"
        except Exception as e:
            return f"Error loading collection: {e}"

        # Get current count
        before_count = context.collection.count()

        # Perform intersection (in-place)
        context.collection.intersect_in_place(loaded_collection)

        # Calculate result
        after_count = context.collection.count()
        removed = before_count - after_count

        return f"Intersect with '{collection_name}': Removed {removed} element(s). Total: {after_count}"

    async def _execute_difference(self, command: Command, context: Context) -> str:
        """Execute difference command - remove elements in other collection"""
        if not command.argument:
            return "Error: No collection name specified"

        collection_name = command.argument

        # Load the other collection
        try:
            loaded_collection = self.storage.load_collection(collection_name)
        except FileNotFoundError:
            return f"Error: Collection '{collection_name}' not found"
        except Exception as e:
            return f"Error loading collection: {e}"

        # Get current count
        before_count = context.collection.count()

        # Perform difference (in-place)
        context.collection.difference_in_place(loaded_collection)

        # Calculate result
        after_count = context.collection.count()
        removed = before_count - after_count

        return f"Difference with '{collection_name}': Removed {removed} element(s). Total: {after_count}"

    async def _execute_unique(self, command: Command, context: Context) -> str:
        """Execute unique command - remove duplicates"""
        before_count = context.collection.count()

        # ElementCollection already maintains uniqueness via _index
        # So this is mostly a no-op, but we'll report the current state
        # In case we want to add support for different uniqueness criteria later

        after_count = context.collection.count()
        removed = before_count - after_count

        if removed == 0:
            return f"Collection already unique. Total: {after_count}"
        else:
            return f"Removed {removed} duplicate(s). Total: {after_count}"

    async def _execute_history(self, command: Command, context: Context) -> str:
        """Execute history command - show command history"""
        if command.argument:
            # history n - show last n commands
            try:
                count = int(command.argument)
                history = context.get_history(count)
            except ValueError:
                return f"Error: Invalid number '{command.argument}'"
        else:
            # history - show all commands
            history = context.get_history()

        if not history:
            return "No commands in history"

        # Format history with line numbers
        lines = []
        # Calculate starting index (if showing subset)
        total_history = len(context.history)
        start_index = total_history - len(history)

        for i, cmd in enumerate(history):
            index = start_index + i
            lines.append(f"  {index:4d}  {cmd}")

        return "Command History:\n" + "\n".join(lines)

    async def _execute_bang_n(self, command: Command, context: Context) -> str:
        """Execute !n command - execute command at index n"""
        if not command.argument:
            return "Error: No index specified"

        try:
            index = int(command.argument)
        except ValueError:
            return f"Error: Invalid index '{command.argument}'"

        # Get command from history
        cmd_str = context.get_history_command(index)
        if cmd_str is None:
            total = len(context.history)
            return f"Error: No command at index {index}. History has {total} commands (0-{total-1})"

        # Parse and execute the historical command
        try:
            print(f"Executing: {cmd_str}")
            cmd = self.parser.parse(cmd_str)
            result = await self.execute(cmd, context)
            return result
        except Exception as e:
            return f"Error executing command '{cmd_str}': {e}"

    async def _execute_bang_last(self, command: Command, context: Context) -> str:
        """Execute !! command - execute last command"""
        # Get last command (excluding the !! itself)
        # History already contains !!, so we need the one before that
        if len(context.history) < 2:
            return "Error: No previous command to execute"

        # Get second-to-last command (last is the !! itself)
        cmd_str = context.history[-2]

        # Parse and execute
        try:
            print(f"Executing: {cmd_str}")
            cmd = self.parser.parse(cmd_str)
            result = await self.execute(cmd, context)
            return result
        except Exception as e:
            return f"Error executing command '{cmd_str}': {e}"

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

Visual Feedback (Phase 5):
  highlight               Highlight current collection
  highlight <target>      Highlight specific elements
  highlight <target> where <condition>
  unhighlight             Remove all highlights

Set Operations (Phase 5):
  union <collection>      Combine with saved collection
  intersect <collection>  Keep only common elements
  difference <collection> Remove elements in other collection
  unique                  Remove duplicates

Command History (Phase 5):
  history                 Show all commands
  history <n>             Show last n commands
  !n                      Execute command at index n
  !!                      Execute last command

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
  highlight
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
