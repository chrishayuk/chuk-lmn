# file: src/lmn/runtime/host/core/malloc/handler.py

import logging

logger = logging.getLogger(__name__)

# A simple bump-pointer allocator:
CURRENT_OFFSET = 65536  # For example, skip the first 64 KiB
WASM_PAGE_SIZE = 65536  # 64 KiB per page in WebAssembly

def malloc_handler(def_info, store, memory_ref, output_list, *args) -> int:
    """
    Minimal bump-pointer `malloc` that expects a single param: `size`.
    Aligned with your JSON config specifying (param i32) (result i32).
    """
    func_name = def_info["name"]  # e.g. "malloc"
    logger.debug(f"[{func_name}] Called with {args=}")

    # 1) Validate memory reference
    if not memory_ref or memory_ref[0] is None:
        logger.debug(f"[{func_name}] memory_ref is invalid.")
        output_list.append("<no memory>")
        return 0

    mem = memory_ref[0]

    # 2) Ensure exactly one argument: size
    if len(args) < 1:
        logger.debug(f"[{func_name}] No size argument received!")
        output_list.append("<malloc missing size>")
        return 0

    size = args[0]  # The single integer parameter
    logger.debug(f"[{func_name}] Requested allocation of size={size}")

    # 3) Get pointers to the memory data
    mem_data = mem.data_ptr(store)
    mem_size = mem.data_len(store)  # bytes in current memory
    global CURRENT_OFFSET
    new_offset = CURRENT_OFFSET + size

    # Optional: If there's not enough room, try to grow memory
    if new_offset > mem_size:
        needed = new_offset - mem_size
        pages_needed = (needed + WASM_PAGE_SIZE - 1) // WASM_PAGE_SIZE
        logger.debug(
            f"[{func_name}] Not enough memory (have={mem_size}, need={new_offset}), "
            f"trying to grow by {pages_needed} page(s)."
        )
        old_pages = mem.grow(store, pages_needed)
        if old_pages == -1:
            logger.debug(f"[{func_name}] memory.grow failed; out of memory.")
            return 0
        # Refresh pointers after growing
        mem_data = mem.data_ptr(store)
        mem_size = mem.data_len(store)

    # Double-check that we have enough space now
    if new_offset > mem_size:
        logger.debug(
            f"[{func_name}] Still out of memory after grow. "
            f"offset={CURRENT_OFFSET}, size={size}, mem_size={mem_size}"
        )
        return 0

    # 4) Return the old offset, then bump
    allocated_ptr = CURRENT_OFFSET
    CURRENT_OFFSET = new_offset

    logger.debug(
        f"[{func_name}] Allocated block at offset={allocated_ptr}, "
        f"new offset={CURRENT_OFFSET}"
    )
    return allocated_ptr
