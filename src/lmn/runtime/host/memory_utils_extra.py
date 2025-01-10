# file: src/lmn/runtime/host/memory_utils_extra.py

import logging
from lmn.runtime.host.core.malloc.call_malloc import call_malloc

logger = logging.getLogger(__name__)

def store_string_with_malloc(store, memory, output_list, text: str) -> int:
    """
    1) Calls call_malloc(...) to allocate len(text)+1 bytes.
    2) Writes 'text\\0' into that block.
    3) Returns the pointer or 0 on failure.
    """
    # 1) Encode with a null terminator
    encoded = text.encode("utf-8", errors="replace") + b"\0"
    size_needed = len(encoded)

    # 2) Allocate
    ptr = call_malloc(store, memory, output_list, size_needed)
    if ptr == 0:
        return 0  # out of memory / grow failed

    # 3) Ensure the allocated region is in bounds
    mem_data = memory.data_ptr(store)
    mem_size = memory.data_len(store)
    if ptr + size_needed > mem_size:
        logger.debug(
            f"store_string_with_malloc: out-of-bounds even after malloc. "
            f"ptr={ptr}, size={size_needed}, mem_size={mem_size}"
        )
        return 0

    # 4) Write
    for i, b in enumerate(encoded):
        mem_data[ptr + i] = b

    return ptr
