# src/lmn/runtime/host/core/malloc/handler.py

import logging

logger = logging.getLogger(__name__)

# A simple bump-pointer allocator. 
# We'll store 'current_offset' in a global variable or within `store`.
CURRENT_OFFSET = 65536  # for example, start after the first page (64 KiB)

def malloc_handler(def_info, store, memory_ref, output_list, *args) -> int:
    """
    Minimal bump-pointer `malloc` handler that aligns with your 
    existing calling convention.

    :param def_info:    JSON definition (e.g. {"name": "malloc", ...}).
    :param store:       Wasmtime store reference.
    :param memory_ref:  (memory_ptr,) tuple from your engine.
    :param output_list: A list-like object for logging or capturing output.
    :param args:        The actual WASM arguments, e.g. (size,).
    :return:            i32 pointer to allocated block, or 0 on failure.
    """
    func_name = def_info["name"]  # e.g. "malloc"
    logger.debug(f"[{func_name}] Called with {args=}")

    if not memory_ref or memory_ref[0] is None:
        logger.debug(f"[{func_name}] memory_ref is invalid.")
        output_list.append("<no memory>")
        return 0

    mem = memory_ref[0]
    if len(args) < 1:
        logger.debug(f"[{func_name}] No size argument received!")
        output_list.append("<malloc missing size>")
        return 0

    size = args[0]
    logger.debug(f"[{func_name}] Requested allocation of size={size}")

    # 1) Grab a direct pointer to the memory data:
    mem_data = mem.data_ptr(store)
    mem_size = mem.data_len(store)

    global CURRENT_OFFSET  # access or modify the bump pointer

    # 2) Check if we have enough room:
    new_offset = CURRENT_OFFSET + size
    if new_offset > mem_size:
        logger.debug(f"[{func_name}] Out of memory: offset={CURRENT_OFFSET}, size={size}, mem_size={mem_size}")
        return 0

    # 3) Return the old offset and then bump:
    allocated_ptr = CURRENT_OFFSET
    CURRENT_OFFSET = new_offset

    logger.debug(f"[{func_name}] Allocated block at offset={allocated_ptr}, new offset={CURRENT_OFFSET}")
    return allocated_ptr
