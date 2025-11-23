"""
Logging utilities for locator strategy engine
Provides debug and performance logging for strategy selection process
"""

import logging
import sys
import time
from functools import wraps
from typing import Callable, Any, Optional


# Configure logger
logger = logging.getLogger('locator.strategy')
logger.setLevel(logging.DEBUG)

# Create handler if none exists
if not logger.handlers:
    # Create a handler that writes to stderr (for CLI output)
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '[%(levelname)s] %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def log_strategy_attempt(strategy_name: str, selector: str):
    """Log when a strategy is attempted"""
    logger.debug(f'[ATTEMPT] Strategy: {strategy_name}, Selector: {selector}')


def log_strategy_result(strategy_name: str, selector: str, success: bool, reason: Optional[str] = None):
    """Log result of strategy validation"""
    status = '✓ PASS' if success else '✗ FAIL'
    if reason:
        logger.debug(f'[RESULT] {status} {strategy_name}: {reason}')
    else:
        logger.debug(f'[RESULT] {status} {strategy_name}')


def log_strategy_selected(strategy_name: str, selector: str, cost: float):
    """Log when a strategy is selected as the winner"""
    logger.info(f'[SELECTED] {strategy_name} (cost: {cost:.3f}) → {selector}')


def log_validation_start(selector: str, is_xpath: bool = False):
    """Log start of validation process"""
    type_str = 'XPath' if is_xpath else 'CSS'
    logger.debug(f'[VALIDATE] {type_str}: {selector}')


def log_validation_result(is_unique: bool, matches_target: bool):
    """Log validation result"""
    unique_str = 'unique' if is_unique else 'not unique'
    target_str = 'matches target' if matches_target else 'wrong element'
    logger.debug(f'[VALIDATE] Result: {unique_str}, {target_str}')


def perf_timer(func_name: str):
    """Decorator to log function execution time"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start = time.time()
            result = await func(*args, **kwargs)
            duration = (time.time() - start) * 1000  # Convert to ms
            logger.debug(f'[PERF] {func_name} took {duration:.2f}ms')
            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start = time.time()
            result = func(*args, **kwargs)
            duration = (time.time() - start) * 1000  # Convert to ms
            logger.debug(f'[PERF] {func_name} took {duration:.2f}ms')
            return result

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


import inspect

# Convenience logging functions

def log_phase_start(phase_name: str):
    """Log start of a phase"""
    logger.info(f'\n{"="*60}\n[PHASE] {phase_name}\n{"="*60}')


def log_phase_end(phase_name: str):
    """Log end of a phase"""
    logger.info(f'[PHASE] {phase_name} completed\n')


def log_fallback(strategy_name: str, reason: str):
    """Log fallback to another strategy"""
    logger.debug(f'[FALLBACK] {strategy_name} failed: {reason}')


def set_log_level(level: int):
    """Set logging level (DEBUG, INFO, WARNING, ERROR)"""
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)


def enable_debug_logging():
    """Enable debug logging for detailed output"""
    set_log_level(logging.DEBUG)
    logger.info('Debug logging enabled')


def disable_debug_logging():
    """Disable debug logging (show only INFO and above)"""
    set_log_level(logging.INFO)
    logger.info('Debug logging disabled')
