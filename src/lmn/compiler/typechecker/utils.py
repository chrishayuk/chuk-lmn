# file: lmn/compiler/typechecker/utils.py
import logging
from typing import Dict, Optional, Tuple

# logger
logger = logging.getLogger(__name__)

def normalize_type(t: Optional[str]) -> Optional[str]:
    """
    Convert type names to a standard format.

    Examples:
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
    Infer the type of a literal (int/float), optionally 
    considering a 'target_type' to refine the inference.

    - Floats default to "f64" unless target is "f32".
    - Integers default to "i32" unless outside 32-bit range, then "i64".
    """
    normalized_target = normalize_type(target_type)

    if isinstance(value, float):
        # If the target is f32, prefer f32
        if normalized_target == "f32":
            return "f32"
        return "f64"  # default for float literals

    if isinstance(value, int):
        # If within 32-bit range => i32, else i64
        if -2**31 <= value <= 2**31 - 1:
            return "i32"
        else:
            return "i64"

    # Fallback if it's neither int nor float
    return "i32"

def can_assign_to(source: str, target: str) -> bool:
    """
    Check if 'source' type can be assigned to 'target' type 
    under language rules, e.g.:

    - same type => True
    - i32 -> i64/f32/f64 => True
    - i64 -> f64 => True
    - f32 -> f64 => True
    - otherwise => False
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
    For a binary operation with left/right typed values,
    produce the resulting type. E.g.:
      - i64 + i32 => i64
      - i32 + f32 => f64 (since any float => f64 in these rules)
      - f64 + f32 => f64
    """
    priority = {
        "i32": 1,
        "i64": 2,
        "f32": 3,
        "f64": 4,
    }

    # If either is a float => result is f64 (your language rule)
    # or you might refine to: if either is 'f64', => 'f64'; 
    # else if either is 'f32', => 'f32'
    if "f" in left or "f" in right:
        return "f64"

    # otherwise pick the higher priority integer
    return left if priority[left] >= priority[right] else right

def unify_types(t1: Optional[str], t2: Optional[str], for_assignment: bool = False) -> str:
    """
    Unify t1 and t2. If for_assignment=True, we treat t2 as 
    the source and t1 as the target. Otherwise, it's a binary op context.
    """
    logger.debug(f"Unifying types t1={t1}, t2={t2}, assignment={for_assignment}")

    if t1 is None and t2 is None:
        return "i32"  # fallback

    if t1 is None:
        return normalize_type(t2)

    if t2 is None:
        return normalize_type(t1)

    t1_norm = normalize_type(t1)
    t2_norm = normalize_type(t2)

    if for_assignment:
        # check if t2_norm can assign to t1_norm
        if can_assign_to(t2_norm, t1_norm):
            return t1_norm
        raise TypeError(f"Cannot assign {t2_norm} to {t1_norm}")
    else:
        # unify for a binary operation
        return get_binary_op_type(t1_norm, t2_norm)
