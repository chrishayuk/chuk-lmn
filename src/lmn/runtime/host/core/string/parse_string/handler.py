# file: src/lmn/runtime/host/core/string/parse_string/handler.py

import logging

logger = logging.getLogger(__name__)

def parse_string_to_i32(def_info, store, memory_ref, output_list, *args) -> int:
    """
    A minimal "parse_string_to_i32" function that expects one param: the pointer to
    a zero-terminated UTF-8 string in WASM memory. It then returns an integer
    parsed from that text.

    If the text can't be parsed, we return 0 as a fallback.
    """

    func_name = def_info["name"]  # e.g., "parse_string_to_i32"
    logger.debug(f"[{func_name}] Called with {args=}")

    # 1) Validate memory reference
    if not memory_ref or memory_ref[0] is None:
        logger.debug(f"[{func_name}] memory_ref is invalid.")
        output_list.append("<no memory>")
        return 0

    mem = memory_ref[0]

    # 2) Ensure exactly one argument: the pointer
    if len(args) < 1:
        logger.debug(f"[{func_name}] No pointer argument received!")
        output_list.append("<parse_string_to_i32 missing pointer>")
        return 0

    pointer = args[0]
    logger.debug(f"[{func_name}] Parsing string at pointer={pointer}")

    # 3) Access the raw bytes of WASM memory
    mem_data = mem.data_ptr(store)
    mem_size = mem.data_len(store)

    # 4) Read bytes until we find a 0 byte (C-style string terminator) or run out of memory
    byte_buffer = []
    i = pointer
    while i < mem_size:
        b = mem_data[i]
        if b == 0:
            break
        byte_buffer.append(b)
        i += 1

    # 5) Decode to Python string
    text = bytes(byte_buffer).decode("utf-8", errors="replace").strip()
    logger.debug(f"[{func_name}] Raw text => '{text}'")

    # 6) Try to parse as integer
    #    If your string is something like "what's 10+5?", you'll need more logic.
    try:
        val = int(text)
    except ValueError:
        logger.debug(f"[{func_name}] Failed to parse '{text}' as integer. Returning 0.")
        val = 0

    # 7) Return the integer result to WebAssembly
    logger.debug(f"[{func_name}] Returning integer={val}")
    return val
