"""
Command data structures for Selector CLI (Phase 2)
"""
from dataclasses import dataclass
from typing import Optional, List, Any, Union
from enum import Enum, auto


class TargetType(Enum):
    """Type of command target"""
    ELEMENT_TYPE = auto()  # input, button, etc.
    INDEX = auto()  # [5]
    INDICES = auto()  # [1,2,3]
    RANGE = auto()  # [1-10]
    ALL = auto()  # all or *


class Operator(Enum):
    """Comparison operators"""
    # Equality
    EQUALS = auto()  # =
    NOT_EQUALS = auto()  # !=

    # Comparison (Phase 2)
    GT = auto()  # >
    GTE = auto()  # >=
    LT = auto()  # <
    LTE = auto()  # <=

    # String operators (Phase 2)
    CONTAINS = auto()  # contains
    STARTS = auto()  # starts
    ENDS = auto()  # ends
    MATCHES = auto()  # matches (regex)


class LogicOp(Enum):
    """Logic operators"""
    AND = auto()
    OR = auto()
    NOT = auto()


class ConditionType(Enum):
    """Type of condition node"""
    SIMPLE = auto()  # field op value
    COMPOUND = auto()  # condition logic_op condition
    UNARY = auto()  # not condition


@dataclass
class Target:
    """Command target"""
    type: TargetType
    element_type: Optional[str] = None  # For ELEMENT_TYPE
    indices: Optional[List[int]] = None  # For INDEX/INDICES/RANGE
    range_start: Optional[int] = None  # For RANGE
    range_end: Optional[int] = None  # For RANGE


# Phase 1 simple condition (kept for backward compatibility)
@dataclass
class Condition:
    """Simple WHERE clause condition"""
    field: str
    operator: Operator
    value: Any


# Phase 2 complex condition tree
@dataclass
class ConditionNode:
    """Condition tree node for complex WHERE clauses"""
    type: ConditionType

    # For SIMPLE conditions
    field: Optional[str] = None
    operator: Optional[Operator] = None
    value: Optional[Any] = None

    # For COMPOUND conditions
    left: Optional['ConditionNode'] = None
    right: Optional['ConditionNode'] = None
    logic_op: Optional[LogicOp] = None

    # For UNARY conditions (NOT)
    operand: Optional['ConditionNode'] = None

    def __repr__(self) -> str:
        """String representation for debugging"""
        if self.type == ConditionType.SIMPLE:
            return f"({self.field} {self.operator.name} {self.value})"
        elif self.type == ConditionType.COMPOUND:
            return f"({self.left} {self.logic_op.name} {self.right})"
        elif self.type == ConditionType.UNARY:
            return f"(NOT {self.operand})"
        return "ConditionNode(?)"


@dataclass
class Command:
    """Parsed command"""
    verb: str  # open, scan, add, etc.
    target: Optional[Target] = None

    # Phase 1 simple condition (deprecated, use condition_tree)
    condition: Optional[Condition] = None

    # Phase 2 complex condition tree
    condition_tree: Optional[ConditionNode] = None

    argument: Optional[str] = None  # For open URL, etc.
    raw: str = ""
