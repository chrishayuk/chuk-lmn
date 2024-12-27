import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

def normalize_type(t: Optional[str]) -> Optional[str]:
    """
    Convert type names to a standard format.

    Args:
        t: Type name to normalize, can be None

    Returns:
        Normalized type name or None if input was None

    Examples from AST:
        >>> normalize_type("float.32")
        'f32'
        >>> normalize_type("float.64")
        'f64'
        >>> normalize_type("int.32")
        'i32'
        >>> normalize_type("int.64")
        'i64'
    """
    if t is None:
        return None

    type_map = {
        "float.32": "f32",
        "float.64": "f64",
        "int.32": "i32",
        "int.64": "i64"
    }
    return type_map.get(t, t)

def infer_literal_type(value, target_type: Optional[str] = None) -> str:
    """
    Infer type of literal values, considering the target type for assignments.
    Integer literals default to i32 unless too large.
    Float literals default to f64 but can be f32 if the target type is f32.

    Args:
        value: The literal value to type check
        target_type: The target type for assignment, if applicable

    Returns:
        Inferred type name

    Examples from AST:
        >>> infer_literal_type(42)
        'i32'
        >>> infer_literal_type(2.718)
        'f64'
        >>> infer_literal_type(2.718, 'f32')
        'f32'
        >>> infer_literal_type(10000000000)
        'i64'
    """
    normalized_target_type = normalize_type(target_type)

    if isinstance(value, float):
        if normalized_target_type == 'f32':
            return "f32"
        return "f64"  # Default to f64 for float literals
    if isinstance(value, int):
        if -2**31 <= value <= 2**31-1:
            return "i32"
        return "i64"
    return "i32"  # Default case

def can_assign_to(source: str, target: str) -> bool:
    """
    Check if source type can be assigned to target type.
    Rules from AST:
    - Same type always allowed
    - Widen to larger type allowed
    - Integers can widen to floats

    Args:
        source: Source type name
        target: Target type name

    Returns:
        True if assignment is valid, False otherwise
    """
    # Same types can always be assigned
    if source == target:
        return True

    # Define allowed conversions (source -> set of allowed target types)
    allowed_conversions = {
        'i32': {'i64', 'f32', 'f64'},  # i32 can widen to any larger type
        'i64': {'f64'},                # i64 can become f64
        'f32': {'f64'},                # f32 can widen to f64
    }

    return target in allowed_conversions.get(source, set())

def get_binary_op_type(left: str, right: str) -> str:
    """
    Get result type for binary operation between two types.
    Rules from AST:
    - Operations between same types preserve the type
    - Mixed integer ops promote to largest integer
    - Any float operand makes result float64

    Args:
        left: Type of left operand
        right: Type of right operand

    Returns:
        Resulting type after binary operation

    Examples from AST:
        >>> get_binary_op_type('i64', 'i32')
        'i64'
        >>> get_binary_op_type('f64', 'f64')
        'f64'
    """
    # Priority ordering (higher = wider type)
    priority = {
        'i32': 1,   # 32-bit integer (lowest)
        'i64': 2,   # 64-bit integer
        'f32': 3,   # 32-bit float
        'f64': 4    # 64-bit float (highest)
    }

    # If either type is float, result is f64
    if 'f' in left or 'f' in right:
        return 'f64'

    # Otherwise use highest priority type
    return left if priority[left] >= priority[right] else right

def unify_types(t1: Optional[str], t2: Optional[str], for_assignment: bool = False) -> str:
    """
    Unify types according to context-specific rules.
    Key behaviors from AST:
    - Float literals are f32 if assigned to an f32 target
    - Integer literals adapt to target type when possible
    - Binary ops between floats always yield f64

    Args:
        t1: First type (target type in assignments)
        t2: Second type (source type in assignments)
        for_assignment: True if unifying for assignment context

    Returns:
        Unified type

    Raises:
        TypeError: If types cannot be unified
    """
    logger.debug(f"Unifying types t1={t1} t2={t2} (assignment={for_assignment})")

    # Handle None cases
    if t1 is None and t2 is None:
        return "i32"  # Default type when both unknown
    if t1 is None:
        return normalize_type(t2)
    if t2 is None:
        return normalize_type(t1)

    # Normalize types
    t1_norm = normalize_type(t1)
    t2_norm = normalize_type(t2)
    logger.debug(f"Normalized types: t1_norm={t1_norm} t2_norm={t2_norm}")

    if for_assignment:
        # For assignments: Check if source type can be assigned to target
        if can_assign_to(t2_norm, t1_norm):
            return t1_norm
        raise TypeError(f"Cannot assign {t2} to {t1}")

    # For binary operations: Promote according to rules
    return get_binary_op_type(t1_norm, t2_norm)