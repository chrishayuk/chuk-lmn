# file: lmn/compiler/emitter/wasm/wasm_module_builder.py
import logging

# logger
logger = logging.getLogger(__name__)

def build_module(wasm_emitter):
    """
    Given a WasmEmitter that has gathered function lines, data segments, etc.,
    build the final (module ...) WAT output string.
    """
    lines = []
    lines.append('(module')

    # Imports
    lines.append('  (import "env" "print_i32" (func $print_i32 (param i32)))')
    lines.append('  (import "env" "print_i64" (func $print_i64 (param i64)))')
    lines.append('  (import "env" "print_f32" (func $print_f32 (param f32)))')
    lines.append('  (import "env" "print_f64" (func $print_f64 (param f64)))')
    lines.append('  (import "env" "print_string" (func $print_string (param i32)))')
    lines.append('  (import "env" "print_json" (func $print_json (param i32)))')
    lines.append('  (import "env" "print_string_array" (func $print_string_array (param i32)))')
    lines.append('  (import "env" "print_i32_array" (func $print_i32_array (param i32)))')
    lines.append('  (import "env" "print_i64_array" (func $print_i64_array (param i32)))')
    lines.append('  (import "env" "print_f32_array" (func $print_f32_array (param i32)))')
    lines.append('  (import "env" "print_f64_array" (func $print_f64_array (param i32)))')
    lines.append('  (import "env" "llm" (func $llm (param i32 i32) (result i32)))')

    # New import for $malloc:
    lines.append('  (import "env" "malloc" (func $malloc (param i32) (result i32)))')

    # Memory
    if wasm_emitter.import_memory:
        lines.append('  (import "env" "memory" (memory 1))')
    else:
        largest_required = 0
        for (offset, data_bytes) in wasm_emitter.data_segments:
            end_offset = offset + len(data_bytes)
            if end_offset > largest_required:
                largest_required = end_offset
        PAGE_SIZE = 65536
        required_pages = (largest_required + PAGE_SIZE - 1) // PAGE_SIZE
        if required_pages < 1:
            required_pages = 1

        lines.append(f'  (memory (export "memory") {required_pages})')

    # Collected functions
    for f_lines in wasm_emitter.functions:
        for line in f_lines:
            lines.append(f"  {line}")

    # Exports
    for fname in wasm_emitter.function_names:
        lines.append(f'  (export "{fname}" (func ${fname}))')

    # Data segments
    if not wasm_emitter.import_memory:
        for (offset, data_bytes) in wasm_emitter.data_segments:
            escaped = "".join(f"\\{b:02x}" for b in data_bytes)
            lines.append(f'  (data (i32.const {offset}) "{escaped}")')

    # close the brackets
    lines.append(')')

    # end the module string
    module_str = "\n".join(lines) + "\n"

    # debug
    logger.debug("build_module: final module length=%d lines", len(module_str.splitlines()))

    # return the module
    return module_str
