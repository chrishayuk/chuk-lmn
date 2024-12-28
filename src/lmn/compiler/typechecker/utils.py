# file: lmn/compiler/typechecker/utils.py

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Priority for types: int < long < float < double
TYPE_PRIORITY = {
    "int": 1,
    "long": 2,
    "float": 3,
    "double": 4
}

def normalize_type(t: Optional[str]) -> Optional[str]:
    """
    Optionally, you can keep this as a no-op if your parser
    already provides "int", "long", "float", "double".
    
    If you never need to convert them to something else,
    just return 't' unchanged or remove this function entirely.
    """
    # For now, do nothing:
    return t

def infer_literal_type(value, target_type: Optional[str] = None) -> str:
    """
    Infer the type of a literal based on its Python value and 
    an optional 'target_type' from context.
    
    - If 'value' is an integer, default to "int".
      But if the target is "long", use "long".
    - If 'value' is a float, default to "double".
      But if the target is "float", use that.
    - Otherwise, fallback to "int".
    """
    normalized_target = normalize_type(target_type)

    if isinstance(value, float):
        # If the user wanted a float, use float; otherwise default to double
        if normalized_target in ("float", "double"):
            return normalized_target
        return "double"

    if isinstance(value, int):
        # If the user wanted a long, use long; otherwise default to int
        if normalized_target in ("int", "long"):
            return normalized_target
        return "int"

    # For strings or other cases, you might do something else.
    return "int"

def can_assign_to(source: str, target: str) -> bool:
    """
    Check if 'source' can be assigned to 'target'.
    
      - int  -> long, float, double
      - long -> float, double
      - float -> double
      - double -> double
    
    You can adjust these rules as needed.
    """
    if source == target:
        return True

    # Allowed upward conversions
    allowed_conversions = {
        "int":    {"long", "float", "double"},
        "long":   {"float", "double"},
        "float":  {"double"},
        "double": set()
    }

    return target in allowed_conversions.get(source, set())

def unify_types(t1: Optional[str], t2: Optional[str], for_assignment: bool = False) -> str:
    """
    Unifies two types (e.g., left and right side of an expression).
    
    If 'for_assignment' is True:
      - We want to see if 't2' (RHS) can be assigned to 't1' (LHS).
      - If so, keep t1. If not, see if we can promote t1 to t2. 
      - Otherwise error.
    If 'for_assignment' is False:
      - For example, a binary expression. 
      - We'll pick the "larger" type, e.g., (int + float) => float.
    """

    logger.debug(f"Unifying types t1={t1}, t2={t2}, assignment={for_assignment}")

    # 1) If both are None, default to int
    if t1 is None and t2 is None:
        return "int"

    # 2) If one is None, pick the other
    if t1 is None:
        return t2
    if t2 is None:
        return t1

    # 3) Both are non-null, do the actual unification
    if for_assignment:
        # Example: var_type = t1, expr_type = t2
        if can_assign_to(t2, t1):
            # no conversion needed, keep t1
            logger.debug(f"Assignment {t2} -> {t1} allowed; staying {t1}")
            return t1
        if can_assign_to(t1, t2):
            # promote the variable to t2
            logger.debug(f"Promoting variable from {t1} -> {t2}")
            return t2
        # Otherwise error
        raise TypeError(f"Cannot unify assignment: {t2} -> {t1}")
    else:
        # For a binary expression, pick the "larger" type
        # e.g., (int + float) => float, (long + double) => double
        p1 = TYPE_PRIORITY.get(t1, 0)
        p2 = TYPE_PRIORITY.get(t2, 0)

        if p1 >= p2:
            return t1
        else:
            return t2
