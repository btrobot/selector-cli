#!/usr/bin/env python
"""
Phase 4 - Test Coverage Analysis
Analyze current test coverage and identify gaps
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

# Modules to analyze
from src.core.locator import strategy, cost, validator, logging
from src.core.locator.scanner_integration import LocatorIntegrationEngine

def analyze_module_methods(module, module_name):
    """Analyze methods/functions in a module"""
    import inspect

    print(f"\n{'='*60}")
    print(f"Module: {module_name}")
    print(f"{'='*60}")

    # Get all functions/classes
    functions = []
    classes = []

    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj) and not name.startswith('_'):
            # Public function
            functions.append(name)
        elif inspect.isclass(obj) and not name.startswith('_'):
            # Public class
            classes.append(name)

    print(f"Public functions: {len(functions)}")
    for f in functions:
        print(f"  - {f}")

    print(f"\nPublic classes: {len(classes)}")
    for c in classes:
        cls = getattr(module, c)
        methods = []
        for name, obj in inspect.getmembers(cls):
            if inspect.ismethod(obj) or inspect.isfunction(obj):
                if not name.startswith('_') or name in ['__init__']:
                    methods.append(name)
        print(f"  - {c}: {len(methods)} methods")
        for m in methods:
            print(f"      - {m}")

    return len(functions) + sum(len([m for m in dir(getattr(module, c)) if not m.startswith('_') or m in ['__init__']]) for c in classes)

def test_coverage_summary():
    """Generate test coverage summary"""
    print("="*60)
    print("Phase 4 - Test Coverage Analysis")
    print("="*60)

    total_items = 0

    # Analyze core modules
    modules = [
        (cost, "cost.py"),
        (validator, "validator.py"),
        (logging, "logging.py"),
    ]

    for module, name in modules:
        count = analyze_module_methods(module, name)
        total_items += count

    # Strategy module is large, analyze separately
    print(f"\n{'='*60}")
    print("Module: strategy.py (LARGE)")
    print(f"{'='*60}")

    # Count strategy generators
    engine = strategy.LocationStrategyEngine()
    css_strategies = len(engine.css_strategies)
    xpath_strategies = len(engine.xpath_strategies)
    print(f"CSS strategies: {css_strategies}")
    print(f"XPath strategies: {xpath_strategies}")
    total_items += css_strategies + xpath_strategies

    # Scanner integration
    print(f"\n{'='*60}")
    print("Module: scanner_integration.py")
    print(f"{'='*60}")
    count = analyze_module_methods(LocatorIntegrationEngine, "LocatorIntegrationEngine")
    total_items += count

    print(f"\n{'='*60}")
    print(f"Total API surface: ~{total_items} functions/methods")
    print(f"{'='*60}")

    print("\nCoverage Estimates:")
    print("  - cost.py: 估计 80% (基本成本计算已测试)")
    print("  - validator.py: 估计 20% (需要大量测试)")
    print("  - logging.py: 估计 50% (基础功能已测试)")
    print("  - strategy.py: 估计 40% (策略已加载但生成器未充分测试)")
    print("  - scanner_integration.py: 估计 30% (基础流程已测试)")

    return 0

if __name__ == '__main__':
    sys.exit(test_coverage_summary())
