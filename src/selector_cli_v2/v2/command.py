"""
V2 Command data structures with extended fields for three-layer architecture
"""
from dataclasses import dataclass, field
from typing import Optional, List, Any, Dict

# Import v1 Command structure
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from selector_cli.parser.command import Command


@dataclass
class CommandV2(Command):
    """
    V2 Command with extended fields for three-layer architecture

    Extends the base Command with additional fields needed for v2 features:
    - element_types: List of element types for find/scan operations
    - source: Source layer for operations (candidates, temp, workspace)
    - mode: Operation mode (overwrite, append, etc.)
    - variant: Command variant (e.g., 'refine' for .find commands)
    - options: Additional options and flags
    """

    # Element types for find/scan (e.g., ['button', 'input', 'div'])
    element_types: Optional[List[str]] = None

    # Source layer for operations
    # - "candidates": from scan results
    # - "temp": from find results
    # - "workspace": from workspace
    # - None: use default based on convention
    source: Optional[str] = None

    # Operation mode
    # - "overwrite": replace destination content
    # - "append": add to destination content
    # - "refine": filter existing content
    mode: str = "overwrite"

    # Command variant
    # - None: normal command
    # - "refine": .find command (refines temp)
    # - Other variants as needed
    variant: Optional[str] = None

    # Additional options and flags
    options: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization to set up defaults"""
        # Ensure options dict exists
        if self.options is None:
            self.options = {}

    def is_refine_command(self) -> bool:
        """Check if this is a refine command (.find)"""
        return self.variant == "refine"

    def is_append_mode(self) -> bool:
        """Check if this is append mode"""
        return self.mode == "append"

    def is_overwrite_mode(self) -> bool:
        """Check if this is overwrite mode"""
        return self.mode == "overwrite"

    def get_source_layer(self) -> Optional[str]:
        """Get the source layer, respecting conventions"""
        # If source is explicitly set, use it
        if self.source:
            return self.source

        # Apply conventions based on verb and variant
        if self.is_refine_command():
            # .find commands default to temp
            return "temp"
        elif self.verb == "add":
            # add commands default to candidates
            return "candidates"

        # Default to None (let the executor decide)
        return None

    def get_target_layer(self) -> str:
        """Get the target layer based on convention"""
        if self.verb in ["list", "preview", "export", "remove", "clear"]:
            # These commands default to workspace
            return "workspace"
        elif self.verb == "find":
            # find commands target temp
            return "temp"
        elif self.verb == "add":
            # add commands target workspace
            return "workspace"
        elif self.verb == "scan":
            # scan commands target candidates
            return "candidates"

        # Default for unknown commands
        return "workspace"

    def has_condition(self) -> bool:
        """Check if command has any condition (simple or tree)"""
        return self.condition is not None or self.condition_tree is not None

    def to_dict(self) -> Dict[str, Any]:
        """Convert command to dictionary for serialization"""
        result = {
            'verb': self.verb,
            'element_types': self.element_types,
            'source': self.source,
            'mode': self.mode,
            'variant': self.variant,
            'options': self.options,
            'raw': self.raw,
        }

        # Add target if present
        if self.target:
            result['target'] = {
                'type': self.target.type.name if self.target.type else None,
                'element_type': self.target.element_type,
                'indices': self.target.indices,
                'range_start': self.target.range_start,
                'range_end': self.target.range_end,
            }

        # Add argument if present
        if self.argument:
            result['argument'] = self.argument

        # Add condition if present
        if self.condition:
            result['condition'] = {
                'field': self.condition.field,
                'operator': self.condition.operator.name if self.condition.operator else None,
                'value': self.condition.value,
            }

        # Add condition_tree if present
        if self.condition_tree:
            result['condition_tree'] = str(self.condition_tree)

        return result
