"""
REPL (Read-Eval-Print Loop) for Selector CLI
"""
import asyncio
import sys
import logging
from ..parser.parser import Parser
from ..commands.executor import CommandExecutor
from ..core.context import Context
from ..core.browser import BrowserManager
from ..core.variable_expander import VariableExpander
from ..core.completer import SelectorCompleter
from ..core.storage import StorageManager
from ..core.locator.logging import enable_debug_logging, disable_debug_logging

# Try to import readline for autocomplete
try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    READLINE_AVAILABLE = False
    print("Warning: readline not available. Tab completion disabled.")


class SelectorREPL:
    """Interactive REPL for Selector CLI"""

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.parser = Parser()
        self.executor = CommandExecutor()
        self.context = Context()
        self.variable_expander = VariableExpander()
        self.storage = StorageManager()
        self.running = False
        self.logger = logging.getLogger('selector.repl')

        # Setup locator logging based on debug flag
        if self.debug:
            enable_debug_logging()
            self.logger.debug("SelectorREPL initialized in debug mode")
        else:
            disable_debug_logging()

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
                # macOS uses libedit
                readline.parse_and_bind("bind ^I rl_complete")
            else:
                # Linux/Windows use GNU readline
                readline.parse_and_bind("tab: complete")
        except:
            # Fallback
            readline.parse_and_bind("tab: complete")

    async def run(self):
        """Main REPL loop"""
        await self._initialize()

        print("\nSelector CLI - Phase 1 MVP")
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

                # Add to history
                self.context.add_to_history(line)

                # Expand variables
                try:
                    if self.variable_expander.has_variables(line):
                        line = self.variable_expander.expand(line, self.context.variables)
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
                    result = await self.executor.execute(command, self.context)
                    print(result)
                except Exception as e:
                    print(f"Execution error: {e}")

            except KeyboardInterrupt:
                print("\nUse 'quit' to exit")
                continue
            except EOFError:
                break
            except Exception as e:
                print(f"Error: {e}")

        await self._cleanup()

    async def _initialize(self):
        """Initialize REPL"""
        # Initialize browser
        self.context.browser = BrowserManager()
        await self.context.browser.initialize(headless=False)

    async def _cleanup(self):
        """Cleanup resources"""
        print("\nShutting down...")
        if self.context.browser:
            await self.context.browser.close()
        print("Goodbye!")

    def _get_prompt(self) -> str:
        """Get prompt string"""
        parts = ["selector"]

        # Add URL if page loaded
        if self.context.current_url:
            # Get domain from URL
            url = self.context.current_url
            if '://' in url:
                domain = url.split('://')[1].split('/')[0]
            else:
                domain = url.split('/')[0]
            parts.append(f"({domain})")

        # Add collection count if non-empty
        if self.context.collection.count() > 0:
            parts.append(f"[{self.context.collection.count()}]")

        return "".join(parts) + "> "


async def main():
    """Entry point"""
    repl = SelectorREPL()
    await repl.run()


if __name__ == '__main__':
    asyncio.run(main())
