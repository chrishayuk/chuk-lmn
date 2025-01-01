# file: lmn/compiler/typechecker/utils.py

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Priority for numeric types: int < long < float < double
TYPE_PRIORITY = {
    "int": 1,
    "long": 2,
    "float": 3,
    "double": 4
    # We won't put "json" or "array" in this numeric priority table,
    # because they're not numeric. We'll handle them as special cases below.
}

def normalize_type(t: Optional[str]) -> Optional[str]:
    """
    Optionally, you can keep this as a no-op if your parser
    already provides "int", "long", "float", "double", "json", "array".
    """
    return t

def infer_literal_type(value, target_type: Optional[str] = None) -> str:
    """
    Infer the type of a literal based on its Python value and 
    an optional 'target_type' from context.

    - If 'value' is int => default "int" (or "long" if target_type suggests).
      *But if the value is out of 32-bit range, treat as "long".*
    - If 'value' is float => default "double" (or "float" if target_type suggests).
    - If 'value' is str => "string".
    - etc.
    """
    normalized_target = normalize_type(target_type)

    # 1) Float => "double" by default, or "float" if the target specifically suggests it
    if isinstance(value, float):
        if normalized_target in ("float", "double"):
            return normalized_target
        return "double"

    # 2) Integer => check 32-bit range 
    if isinstance(value, int):
        # If context says 'long', keep it as 'long'
        # or if context says 'int' and it's in 32-bit range => 'int'
        if normalized_target in ("int", "long"):
            # If target is 'long', we definitely use 'long'
            if normalized_target == "long":
                return "long"
            # else if target is 'int', we check if it's in 32-bit range
            if -2**31 <= value <= 2**31 - 1:
                return "int"
            else:
                return "long"

        # If no target_type or it's something else => do range check
        if -2**31 <= value <= 2**31 - 1:
            return "int"
        else:
            return "long"

    # 3) String => "string"
    if isinstance(value, str):
        return "string"

    # 4) Boolean or other => do what you like, or default to "int"
    return "int"


def can_assign_to(source: str, target: str) -> bool:
    """
    Check if 'source' can be assigned to 'target'.
    
      - int -> long, float, double
      - long -> float, double
      - float -> double
      - double -> double

    Then we handle special types 'json' and 'array' in a simplistic way:
      - 'json' -> 'json' (only)
      - 'array' -> 'array' (only)
    """
    if source == target:
        return True

    # Handle 'json' => it only can assign to 'json'
    if source == "json":
        return (target == "json")

    # Handle 'array' => it only can assign to 'array'
    if source == "array":
        return (target == "array")

    # Allowed numeric upward conversions
    allowed_conversions = {
        "int":    {"long", "float", "double"},
        "long":   {"float", "double"},
        "float":  {"double"},
        # Now we explicitly allow narrowing from double -> float
        "double": {"float"},
    }


    # If not found in table => no conversions
    return target in allowed_conversions.get(source, set())

def unify_types(t1: Optional[str], t2: Optional[str], for_assignment: bool = False) -> str:
    """
    Unifies two types (e.g., left and right side of an expression).

    If 'for_assignment' is True:
      - We want to see if 't2' (RHS) can be assigned to 't1' (LHS).
      - If so, keep t1. If not, see if we can promote t1 to t2.
      - Otherwise error.

    If 'for_assignment' is False:
      - E.g. a binary expression. We pick the "larger" type among numeric,
        or handle special types like 'json' or 'array' with custom logic.
    """

    logger.debug(f"Unifying types t1={t1}, t2={t2}, assignment={for_assignment}")

    # 1) Both None => default to "int"
    if t1 is None and t2 is None:
        return "int"  
        # Or raise an error if you want to forbid two unknowns:
        # raise TypeError("Cannot unify 'None' with 'None'")

    # 2) If one is None => pick the other
    if t1 is None:
        return t2  # guaranteed not None
    if t2 is None:
        return t1  # guaranteed not None

    # 3) If either is 'json', unify to 'json' in non-assignment contexts
    #    For assignment, we check can_assign_to or attempt promotions.
    if not for_assignment:
        # Non-assignment (like a binary expression)
        # If either is 'json', result => 'json'
        if t1 == "json" or t2 == "json":
            return "json"

        # If either is 'array' but not 'json', handle 'array' vs numeric or string
        if t1 == "array" and t2 == "array":
            return "array"
        if t1 == "array" and t2 != "array":
            # e.g. array + int => likely an error
            raise TypeError(f"Cannot unify 'array' with '{t2}' in a binary expression.")
        if t2 == "array" and t1 != "array":
            raise TypeError(f"Cannot unify '{t1}' with 'array' in a binary expression.")

        # If both numeric => pick the larger
        p1 = TYPE_PRIORITY.get(t1, 0)
        p2 = TYPE_PRIORITY.get(t2, 0)
        if p1 >= p2:
            return t1
        else:
            return t2

    else:
        # 4) for_assignment == True
        #    We want to see if 't2' (RHS) can be assigned to 't1' (LHS).
        if can_assign_to(t2, t1):
            logger.debug(f"Assignment {t2} -> {t1} allowed; staying {t1}")
            return t1
        if can_assign_to(t1, t2):
            # promote variable from t1 -> t2
            logger.debug(f"Promoting variable from {t1} -> {t2}")
            return t2

        raise TypeError(f"Cannot unify assignment: {t2} -> {t1}")

        # 4) for_assignment == True
        #    We want to see if 't2' (RHS) can be assigned to 't1' (LHS).
        if can_assign_to(t2, t1):
            logger.debug(f"Assignment {t2} -> {t1} allowed; staying {t1}")
            return t1
        if can_assign_to(t1, t2):
            # promote variable from t1 -> t2
            logger.debug(f"Promoting variable from {t1} -> {t2}")
            return t2

        raise TypeError(f"Cannot unify assignment: {t2} -> {t1}")
