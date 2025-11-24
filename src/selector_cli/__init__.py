"""
Selector CLI v2.0 - Three-layer architecture with exploration workflow
"""

__version__ = "2.0.0"

# V2 Core exports
from .core.context_v2 import ContextV2
from .parser.command_v2 import CommandV2
from .parser.parser_v2 import ParserV2
from .commands.executor_v2 import ExecutorV2

# REPL export
from .repl.main_v2 import SelectorREPLV2 as SelectorREPL

__all__ = [
    'ContextV2', 'CommandV2', 'ParserV2', 'ExecutorV2',
    'SelectorREPL', '__version__'
]
