"""
Command data structures for Selector CLI
"""
from dataclasses import dataclass
from typing import Optional, List, Any
from enum import Enum, auto


class TargetType(Enum):
    """Type of command target"""
    ELEMENT_TYPE = auto()  # input, button, etc.
    INDEX = auto()  # [5]
    INDICES = auto()  # [1,2,3]
    ALL = auto()  # all or *


class Operator(Enum):
    """Comparison operators"""
    EQUALS = auto()  # =
    NOT_EQUALS = auto()  # !=


class LogicOp(Enum):
    """Logic operators"""
    AND = auto()
    OR = auto()


@dataclass
class Target:
    """Command target"""
    type: TargetType
    element_type: Optional[str] = None  # For ELEMENT_TYPE
    indices: Optional[List[int]] = None  # For INDEX/INDICES


@dataclass
class Condition:
    """WHERE clause condition (simple for Phase 1)"""
    field: str
    operator: Operator
    value: Any


@dataclass
class Command:
    """Parsed command"""
    verb: str  # open, scan, add, etc.
    target: Optional[Target] = None
    condition: Optional[Condition] = None
    argument: Optional[str] = None  # For open URL, etc.
    raw: str = ""
