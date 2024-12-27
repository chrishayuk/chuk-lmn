# file: lmn/compiler/typechecker/utils.py
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def normalize_type(t: Optional[str]) -> Optional[str]:
    """
    Convert type names to a standard format.
      "float.32" -> "f32"
      "float.64" -> "f64"
      "int.32"   -> "i32"
      "int.64"   -> "i64"
    """
    if t is None:
        return None
    type_map = {
        "float.32": "f32",
        "float.64": "f64",
        "int.32": "i32",
        "int.64": "i64",
    }
    return type_map.get(t, t)

def infer_literal_type(value, target_type: Optional[str] = None) -> str:
    """
    Infer the type of a literal (int/float). Floats default to f64
    unless target is f32. Integers default to i32 unless out of 32-bit range, then i64.
    """
    normalized_target = normalize_type(target_type)

    if isinstance(value, float):
        if normalized_target == "f32":
            return "f32"
        return "f64"

    if isinstance(value, int):
        if -2**31 <= value <= 2**31 - 1:
            return "i32"
        else:
            return "i64"

    return "i32"

def can_assign_to(source: str, target: str) -> bool:
    """
    Check if 'source' can be assigned to 'target'.
      i32 -> i64/f32/f64 => True
      i64 -> f64 => True
      f32 -> f64 => True
      otherwise => False
    """
    if source == target:
        return True

    allowed_conversions = {
        "i32": {"i64", "f32", "f64"},
        "i64": {"f64"},
        "f32": {"f64"},
    }
    return target in allowed_conversions.get(source, set())

def get_binary_op_type(left: str, right: str) -> str:
    """
    For binary ops:
      - if either is float => result is f64
      - else pick higher of i32 vs i64
    """
    priority = {"i32": 1, "i64": 2, "f32": 3, "f64": 4}

    if "f" in left or "f" in right:
        return "f64"

    return left if priority[left] >= priority[right] else right

def unify_types(t1: Optional[str], t2: Optional[str], for_assignment: bool = False) -> str:
    """
    If for_assignment=True:
      - t1 = existing var type (target)
      - t2 = new expr type (source)
      Steps:
        1) if source->target => keep t1
        2) else if target->source => upcast to t2
        3) else raise error
    """
    logger.debug(f"Unifying types t1={t1}, t2={t2}, assignment={for_assignment}")

    if t1 is None and t2 is None:
        return "i32"

    if t1 is None:
        return normalize_type(t2)
    if t2 is None:
        return normalize_type(t1)

    t1_norm = normalize_type(t1)
    t2_norm = normalize_type(t2)

    if for_assignment:
        # 1) if can_assign_to(t2->t1), keep t1
        if can_assign_to(t2_norm, t1_norm):
            logger.debug(f"Assignment {t2_norm} -> {t1_norm} allowed; staying {t1_norm}")
            return t1_norm
        # 2) else if can_assign_to(t1->t2), upcast to t2
        if can_assign_to(t1_norm, t2_norm):
            logger.debug(f"Promoting variable from {t1_norm} -> {t2_norm}")
            return t2_norm
        # 3) otherwise => error
        raise TypeError(f"Cannot unify assignment: {t2_norm} -> {t1_norm}")
    else:
        # binary op scenario
        return get_binary_op_type(t1_norm, t2_norm)
