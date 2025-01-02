# src/lmn/runtime/core/print/handler.py

from lmn.runtime.host.memory_utils import (
    parse_f32_array, parse_f64_array, parse_i32_array, parse_i32_string_array,
    parse_i64_array, read_utf8_string
)

def print_handler(def_info, store, memory_ref, output_list, *args):
    """
    A single, catch-all print handler for all print_* functions.
    We decide how to parse 'args' and memory based on def_info["name"].
    """
    if not memory_ref or memory_ref[0] is None:
        output_list.append("<no memory>")
        # Return nothing (or just 'return')
        return

    mem = memory_ref[0]
    func_name = def_info["name"]  # e.g. "print_i32", "print_string"
    # For "print_i32", we expect one i32 param in *args, etc.

    if func_name == "print_i32":
        x = args[0]
        output_list.append(f"[{func_name}] {x}")

    elif func_name == "print_i64":
        x = args[0]
        output_list.append(f"[{func_name}] {x}")

    elif func_name == "print_f32":
        x = args[0]
        output_list.append(f"[{func_name}] {x}")

    elif func_name == "print_f64":
        x = args[0]
        output_list.append(f"[{func_name}] {x}")

    elif func_name == "print_string":
        ptr = args[0]
        s = read_utf8_string(store, mem, ptr)
        output_list.append(f"[{func_name}] {s}")

    elif func_name == "print_json":
        ptr = args[0]
        s = read_utf8_string(store, mem, ptr)
        output_list.append(f"[{func_name}] {s}")

    elif func_name == "print_i32_array":
        ptr = args[0]
        elements = parse_i32_array(store, mem, ptr)
        output_list.append(f"[{func_name}] {elements}")

    elif func_name == "print_i64_array":
        ptr = args[0]
        elements = parse_i64_array(store, mem, ptr)
        output_list.append(f"[{func_name}] {elements}")

    elif func_name == "print_f32_array":
        ptr = args[0]
        elements = parse_f32_array(store, mem, ptr)
        output_list.append(f"[{func_name}] {elements}")

    elif func_name == "print_f64_array":
        ptr = args[0]
        elements = parse_f64_array(store, mem, ptr)
        output_list.append(f"[{func_name}] {elements}")

    elif func_name == "print_string_array":
        ptr = args[0]
        elements = parse_i32_string_array(store, mem, ptr)
        output_list.append(f"[{func_name}] {elements}")

    else:
        output_list.append(f"[{func_name}] <unrecognized print function>")

    # Because our JSON signature lists "results": [],
    # we produce no return value (implicitly None).
    # That ensures we don't trigger "callback produced results" errors.
    return
