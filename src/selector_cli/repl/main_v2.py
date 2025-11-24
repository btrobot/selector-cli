"""
V2 REPL (Read-Eval-Print Loop) - Integrated with three-layer architecture
"""
import asyncio
import sys
import logging

from selector_cli.core.browser import BrowserManager
from selector_cli.core.completer import SelectorCompleter
from selector_cli.core.variable_expander import VariableExpander
from selector_cli.core.storage import StorageManager
from selector_cli.core.locator.logging import enable_debug_logging, disable_debug_logging

# V2 imports
from selector_cli.core.context_v2 import ContextV2
from selector_cli.parser.parser_v2 import ParserV2
from selector_cli.commands.executor_v2 import ExecutorV2

# Try to import readline for autocomplete
try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    READLINE_AVAILABLE = False


class SelectorREPLV2:
    """V2 Interactive REPL with three-layer architecture support"""

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.parser = ParserV2()
        self.context = ContextV2()
        self.executor = ExecutorV2(self.context)
        self.variable_expander = VariableExpander()
        self.storage = StorageManager()
        self.running = False

        # Setup locator logging based on debug flag
        if self.debug:
            enable_debug_logging()
            print("V2 REPL initialized in debug mode")
        else:
            disable_debug_logging()

    async def run(self):
        """Main REPL loop"""
        await self._initialize()

        print("\n" + "=" * 60)
        print("Selector CLI v2.0 - Three-Layer Architecture")
        print("=" * 60)
        print("New features:")
        print("  • find div where role='button'  - Query DOM directly")
        print("  • .find where visible           - Refine results")
        print("  • add from temp                 - Add from temp layer")
        print("  • list temp / list candidates   - View different layers")
        print("  • scan button, input, div       - Multiple types")
        print("=" * 60)
        print("Type 'help' for commands, 'quit' to exit\n")

        self.running = True

        while self.running:
            try:
                # Get prompt
                prompt = self._get_prompt()

                # Read input
                line = await asyncio.get_event_loop().run_in_executor(
                    None, input, prompt
                )

                # Skip empty lines
                if not line.strip():
                    continue

                # Add to history (even if it fails, we want to record attempts)
                self.context.add_to_history(line.strip())

                # Expand variables
                try:
                    if self.variable_expander.has_variables(line):
                        line = self.variable_expander.expand(line, self.context.variables)
                        print(f"Expanded to: {line}")
                except ValueError as e:
                    print(f"Variable error: {e}")
                    continue

                # Parse command
                try:
                    command = self.parser.parse(line)
                except Exception as e:
                    print(f"Parse error: {e}")
                    continue

                # Check for quit
                if command.verb == 'quit':
                    self.running = False
                    break

                # Execute
                try:
                    success, result = await self.executor.execute(command)
                    if success:
                        if result is not None:
                            print(result)
                    else:
                        print(f"Execution error: {result}")
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    if self.debug:
                        import traceback
                        traceback.print_exc()

                # Show temp expiration warning (if applicable)
                if command.verb == 'list' and command.source is None:
                    # list workspace - check if temp is about to expire
                    if self.context.has_temp_results():
                        import time
                        if self.context._last_find_time:
                            age = time.time() - self.context._last_find_time.timestamp()
                            if age > 25:  # Warn when temp is 5+ seconds old
                                print(f"\n[Hint] Temp results are {int(age)}s old (expire in {30-int(age)}s)")

            except KeyboardInterrupt:
                print("\nUse 'quit' to exit")
                continue
            except EOFError:
                break
            except Exception as e:
                print(f"Error: {e}")
                if self.debug:
                    import traceback
                    traceback.print_exc()

        await self._cleanup()

    async def _initialize(self):
        """Initialize REPL"""
        print("\nInitializing browser...", end=" ", flush=True)

        # Initialize browser
        try:
            self.context.browser = BrowserManager()
            await self.context.browser.initialize(headless=False)
            print("✓ Browser ready")
        except Exception as e:
            print(f"✗ Failed: {e}")
            print("\nContinuing without browser (some commands may not work)")

        # Setup readline
        if READLINE_AVAILABLE:
            self._setup_readline()

    def _setup_readline(self):
        """Setup readline for autocomplete"""
        # Create completer
        self.completer = SelectorCompleter(
            context=self.context,
            storage=self.storage
        )

        # Set completer
        readline.set_completer(self.completer.complete)

        # Set delimiters (what breaks words)
        readline.set_completer_delims(' \t\n=!<>()[]{}')

        # Enable tab completion
        try:
            if readline.__doc__ and 'libedit' in readline.__doc__:
                readline.parse_and_bind("bind ^I rl_complete")
            else:
                readline.parse_and_bind("tab: complete")

            # Load history
            if self.context.HISTORY_FILE.exists():
                readline.read_history_file(str(self.context.HISTORY_FILE))
        except Exception:
            pass

    async def _cleanup(self):
        """Cleanup resources"""
        print("\nShutting down...")

        # Save history
        if READLINE_AVAILABLE:
            try:
                self.context.HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
                readline.write_history_file(str(self.context.HISTORY_FILE))
            except Exception:
                pass

        # Close browser
        if self.context.browser:
            await self.context.browser.close()

        print("Goodbye!")

    def _get_prompt(self) -> str:
        """Get prompt string showing current state"""
        parts = ["selector"]

        # Add URL if page loaded
        if self.context.current_url:
            url = self.context.current_url
            if '://' in url:
                domain = url.split('://')[1].split('/')[0]
            else:
                domain = url.split('/')[0]
            parts.append(f"({domain})")

        # Show focused layer (if not default)
        if self.context.focus != 'workspace':
            parts.append(f"[{self.context.focus}]")

        # Add collection counts
        counts = []
        if len(self.context.candidates) > 0:
            counts.append(f"c:{len(self.context.candidates)}")
        if len(self.context.temp) > 0:
            counts.append(f"t:{len(self.context.temp)}")
        if len(self.context.workspace) > 0:
            counts.append(f"w:{len(self.context.workspace)}")

        if counts:
            parts.append(f"({' '.join(counts)})")

        return " ".join(parts) + "> "


async def main():
    """Entry point"""
    # Check for debug flag
    debug = '--debug' in sys.argv or '-d' in sys.argv

    repl = SelectorREPLV2(debug=debug)
    await repl.run()


if __name__ == '__main__':
    asyncio.run(main())
