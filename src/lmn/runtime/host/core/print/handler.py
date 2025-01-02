# src/lmn/runtime/core/print/handler.py
import logging

# import memory utils
from lmn.runtime.host.memory_utils import (
    parse_f32_array, parse_f64_array, parse_i32_array, parse_i32_string_array,
    parse_i64_array, read_utf8_string
)

# logging
logger = logging.getLogger(__name__)

def print_handler(def_info, store, memory_ref, output_list, *args):
    """
    A single, catch-all print handler for all print_* functions.
    We decide how to parse 'args' and memory based on def_info["name"].
    
    - We keep output_list clean (no function names in the final output).
    - We log debug-level messages with function names or other helpful context.
    """

    if not memory_ref or memory_ref[0] is None:
        logger.debug("memory_ref is None or invalid.")
        output_list.append("<no memory>")
        return

    mem = memory_ref[0]
    func_name = def_info["name"]  # e.g. "print_i32", "print_string"

    # For "print_i32", we expect one i32 param in *args, etc.
    # We'll log the function name and output but only append the "clean" value to output_list.
    if func_name == "print_i32":
        x = args[0]
        logger.debug(f"Called {func_name} with: {x}")
        output_list.append(str(x))

    elif func_name == "print_i64":
        x = args[0]
        logger.debug(f"Called {func_name} with: {x}")
        output_list.append(str(x))

    elif func_name == "print_f32":
        x = args[0]
        logger.debug(f"Called {func_name} with: {x}")
        output_list.append(str(x))

    elif func_name == "print_f64":
        x = args[0]
        logger.debug(f"Called {func_name} with: {x}")
        output_list.append(str(x))

    elif func_name == "print_string":
        ptr = args[0]
        s = read_utf8_string(store, mem, ptr)
        logger.debug(f"Called {func_name} with string: {s!r}")
        output_list.append(s)

    elif func_name == "print_json":
        ptr = args[0]
        s = read_utf8_string(store, mem, ptr)
        logger.debug(f"Called {func_name} with JSON: {s!r}")
        output_list.append(s)

    elif func_name == "print_i32_array":
        ptr = args[0]
        elements = parse_i32_array(store, mem, ptr)
        logger.debug(f"Called {func_name} with array: {elements}")
        output_list.append(str(elements))

    elif func_name == "print_i64_array":
        ptr = args[0]
        elements = parse_i64_array(store, mem, ptr)
        logger.debug(f"Called {func_name} with array: {elements}")
        output_list.append(str(elements))

    elif func_name == "print_f32_array":
        ptr = args[0]
        elements = parse_f32_array(store, mem, ptr)
        logger.debug(f"Called {func_name} with array: {elements}")
        output_list.append(str(elements))

    elif func_name == "print_f64_array":
        ptr = args[0]
        elements = parse_f64_array(store, mem, ptr)
        logger.debug(f"Called {func_name} with array: {elements}")
        output_list.append(str(elements))

    elif func_name == "print_string_array":
        ptr = args[0]
        elements = parse_i32_string_array(store, mem, ptr)
        logger.debug(f"Called {func_name} with string array: {elements}")
        output_list.append(str(elements))

    else:
        logger.debug(f"Unrecognized print function: {func_name}")
        output_list.append("<unrecognized print function>")

    # Producing no return value (None) keeps "results" empty in the JSON signature context.
