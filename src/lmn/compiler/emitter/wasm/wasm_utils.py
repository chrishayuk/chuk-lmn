# file: wasm_utils.py
from typing import Optional
from lmn.compiler.typechecker.utils import normalize_type

def annotation_to_wasm_type(annotation: Optional[str]) -> Optional[str]:
    """
    Convert a language-level annotation like 'float.32' to 
    a WASM type 'f32', or None if annotation is None.

    Just calls normalize_type under the hood, but named 
    for clarity in the emitter context.
    """
    return normalize_type(annotation)

def default_zero_for(wasm_type: str) -> str:
    """
    Return a WebAssembly instruction to push a 0 literal of `wasm_type`.
    e.g. 'f32' -> 'f32.const 0'
         'f64' -> 'f64.const 0'
         'i64' -> 'i64.const 0'
         else  -> 'i32.const 0'
    """
    if wasm_type == "f64":
        return "f64.const 0"
    elif wasm_type == "f32":
        return "f32.const 0"
    elif wasm_type == "i64":
        return "i64.const 0"
    else:
        return "i32.const 0"


