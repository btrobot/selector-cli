"""
Test REPL startup with v2
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from selector_cli import SelectorREPL


async def test_repl_startup():
    """Test that REPL can be instantiated"""
    print("Testing REPL instantiation...")
    repl = SelectorREPL(debug=False)
    print("✓ REPL created successfully")

    # Check components
    assert hasattr(repl, 'parser')
    assert hasattr(repl, 'context')
    assert hasattr(repl, 'executor')
    print("✓ All components present")

    # Check types
    from selector_cli import ParserV2, ContextV2, ExecutorV2
    assert isinstance(repl.parser, ParserV2)
    assert isinstance(repl.context, ContextV2)
    assert isinstance(repl.executor, ExecutorV2)
    print("✓ Correct types")


if __name__ == "__main__":
    asyncio.run(test_repl_startup())
    print("All tests passed!")
