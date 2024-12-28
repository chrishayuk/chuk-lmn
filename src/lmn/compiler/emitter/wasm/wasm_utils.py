# file: wasm_utils.py

from typing import Optional
from lmn.compiler.typechecker.utils import normalize_type

def annotation_to_wasm_type(annotation: Optional[str]) -> Optional[str]:
    """
    Convert a language-level annotation (e.g., 'float.32', 'double', 'int')
    to a WASM type ('f32', 'f64', 'i32', 'i64') or None.
    It just calls normalize_type() under the hood, 
    but is named for clarity in an emitter context.
    """
    return normalize_type(annotation)

def default_zero_for(wasm_type: str) -> str:
    """
    Return a WebAssembly instruction that pushes a zero literal
    for the given wasm_type:
       - 'void' => ''  # no push
       - 'f64' => 'f64.const 0'
       - 'f32' => 'f32.const 0'
       - 'i64' => 'i64.const 0'
       - anything else => 'i32.const 0'
    """
    if wasm_type == "void":
        return ""  # no push
    elif wasm_type == "f64":
        return "f64.const 0"
    elif wasm_type == "f32":
        return "f32.const 0"
    elif wasm_type == "i64":
        return "i64.const 0"
    else:
        # default fallback => i32
        return "i32.const 0"

