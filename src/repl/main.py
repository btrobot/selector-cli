"""
REPL (Read-Eval-Print Loop) for Selector CLI
"""
import asyncio
from ..parser.parser import Parser
from ..commands.executor import CommandExecutor
from ..core.context import Context
from ..core.browser import BrowserManager


class SelectorREPL:
    """Interactive REPL for Selector CLI"""

    def __init__(self):
        self.parser = Parser()
        self.executor = CommandExecutor()
        self.context = Context()
        self.running = False

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
