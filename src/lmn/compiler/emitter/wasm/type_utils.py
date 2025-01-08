# file: lmn/compiler/emitter/wasm/type_utils.py
import logging

# logger
logger = logging.getLogger(__name__)

# priority
priority_map = {
    "i32": 1,
    "i64": 2,
    "f32": 3,
    "f64": 4
}

def unify_types(t1, t2):
    """
    Given two types (e.g. 'i32', 'f32'), returns the "wider" one.
    """
    p1 = priority_map.get(t1, 0)
    p2 = priority_map.get(t2, 0)
    if p1 >= p2:
        return t1
    else:
        return t2
