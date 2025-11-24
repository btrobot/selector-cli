"""
Autocomplete support for Selector CLI
"""
from typing import List, Optional
import os


class SelectorCompleter:
    """Provides tab completion for Selector CLI commands"""

    # Command keywords
    COMMANDS = [
        'open', 'scan', 'add', 'remove', 'clear', 'list', 'ls', 'show',
        'count', 'help', 'quit', 'exit', 'q',
        # Phase 3
        'export',
        # Phase 4
        'save', 'load', 'saved', 'delete', 'set', 'vars',
        'macro', 'run', 'macros', 'exec',
        # Phase 5
        'highlight', 'unhighlight', 'union', 'intersect', 'difference',
        'unique', 'history',
    ]

    # Element types
    ELEMENT_TYPES = ['input', 'button', 'select', 'textarea', 'a', 'link', 'all']

    # Export formats
    EXPORT_FORMATS = ['playwright', 'selenium', 'puppeteer', 'json', 'csv', 'yaml']

    # Keywords
    KEYWORDS = ['where', 'and', 'or', 'not']

    # Field names (for WHERE clauses)
    FIELDS = [
        'type', 'id', 'name', 'text', 'value', 'placeholder', 'role',
        'visible', 'enabled', 'disabled', 'required', 'readonly',
        'index', 'tag'
    ]

    # String operators
    STRING_OPS = ['contains', 'starts', 'ends', 'matches']

    def __init__(self, context=None, storage=None):
        """
        Initialize completer

        Args:
            context: Execution context (for dynamic completions)
            storage: StorageManager (for collection name completions)
        """
        self.context = context
        self.storage = storage

    def complete(self, text: str, state: int) -> Optional[str]:
        """
        Completion function for readline

        Args:
            text: Current text being completed
            state: Iteration state (0, 1, 2, ...)

        Returns:
            Completion option or None
        """
        if state == 0:
            # First call - generate completions
            import readline
            line = readline.get_line_buffer()
            begin = readline.get_begidx()
            end = readline.get_endidx()

            # Get completions based on context
            self.matches = self._get_completions(line, text, begin, end)

        # Return next match
        if state < len(self.matches):
            return self.matches[state]
        return None

    def _get_completions(self, line: str, text: str, begin: int, end: int) -> List[str]:
        """
        Get completion options based on current input

        Args:
            line: Full input line
            text: Text being completed
            begin: Start position of text in line
            end: End position of text in line

        Returns:
            List of completion options
        """
        # Get words before current position
        before_text = line[:begin].strip()
        words = before_text.split()

        # Determine what to complete
        if not words:
            # Completing first word - show all commands
            return self._match(text, self.COMMANDS)

        first_word = words[0].lower()

        # Command-specific completions
        if first_word in ('add', 'remove', 'list', 'show', 'highlight'):
            return self._complete_add_remove(words, text)
        elif first_word == 'export':
            return self._complete_export(words, text)
        elif first_word in ('union', 'intersect', 'difference', 'load', 'delete'):
            return self._complete_collection_name(words, text)
        elif first_word == 'exec':
            return self._complete_filepath(text)
        elif first_word == 'open':
            return []  # No completion for URLs
        else:
            # Default: try to complete commands
            return self._match(text, self.COMMANDS)

    def _complete_add_remove(self, words: List[str], text: str) -> List[str]:
        """Complete add/remove/list/show/highlight commands"""
        # Check if we're after 'where'
        if 'where' in words:
            # After where, complete field names or operators
            if len(words) >= 2 and words[-1] in self.FIELDS:
                # After field name, complete operators
                return self._match(text, ['=', '!=', '>', '>=', '<', '<='] + self.STRING_OPS)
            elif any(op in words for op in ['and', 'or']):
                # After and/or, complete field names
                return self._match(text, self.FIELDS)
            else:
                # Complete field names
                return self._match(text, self.FIELDS + ['not'])
        else:
            # Before where, complete element types or 'where' keyword
            completions = self.ELEMENT_TYPES + ['where']
            return self._match(text, completions)

    def _complete_export(self, words: List[str], text: str) -> List[str]:
        """Complete export command"""
        if len(words) == 1:
            # After 'export', show formats
            return self._match(text, self.EXPORT_FORMATS)
        return []

    def _complete_collection_name(self, words: List[str], text: str) -> List[str]:
        """Complete saved collection names"""
        if not self.storage:
            return []

        try:
            # Get list of saved collections
            collections = self.storage.list_collections()
            names = [c['name'] for c in collections]
            return self._match(text, names)
        except:
            return []

    def _complete_filepath(self, text: str) -> List[str]:
        """Complete file paths"""
        # Get directory and partial filename
        if '/' in text or '\\' in text:
            dirname = os.path.dirname(text) or '.'
            partial = os.path.basename(text)
        else:
            dirname = '.'
            partial = text

        try:
            # List files in directory
            if not os.path.exists(dirname):
                return []

            files = os.listdir(dirname)
            # Filter by partial match
            matches = [f for f in files if f.startswith(partial)]

            # Add directory separator for directories
            results = []
            for match in matches:
                full_path = os.path.join(dirname, match)
                if os.path.isdir(full_path):
                    results.append(match + os.sep)
                else:
                    results.append(match)

            return results
        except:
            return []

    def _match(self, text: str, options: List[str]) -> List[str]:
        """
        Filter options that start with text

        Args:
            text: Text to match
            options: List of possible completions

        Returns:
            Filtered list of completions
        """
        if not text:
            return sorted(options)
        return sorted([opt for opt in options if opt.startswith(text.lower())])
