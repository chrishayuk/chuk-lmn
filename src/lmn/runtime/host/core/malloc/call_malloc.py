# file: src/lmn/runtime/host/core/malloc/call_malloc.py
import logging

# lmn imports
from lmn.runtime.host.core.malloc.handler import malloc_handler

# logger
logger = logging.getLogger(__name__)

def call_malloc(store, memory, output_list, size) -> int:
    """
    A minimal Python helper that calls your 'malloc_handler' 
    with the given 'size', returning a pointer or 0 on failure.
    """
    def_info = {"name": "malloc"}  # used inside malloc_handler for logging
    memory_ref = [memory]          # pass a list with memory[0] = memory
    args = (size,)                 # single argument, matching (param i32)

    ptr = malloc_handler(def_info, store, memory_ref, output_list, *args)
    logger.debug(f"call_malloc: requested size={size} => allocated ptr={ptr}")
    return ptr

def store_string_with_malloc(store, memory, output_list, text: str) -> int:
    """
    1) Calls call_malloc(...) to allocate len(text)+1 bytes.
    2) Writes 'text\\0' into that block.
    3) Returns the pointer or 0 on failure.
    """
    encoded = text.encode("utf-8", errors="replace") + b"\0"
    size_needed = len(encoded)

    # 1) Allocate
    ptr = call_malloc(store, memory, output_list, size_needed)
    if ptr == 0:
        return 0  # out of memory

    # 2) Write
    mem_data = memory.data_ptr(store)
    mem_size = memory.data_len(store)
    if ptr + size_needed > mem_size:
        # even after malloc, we might be out of memory if grow failed?
        return 0

    for i, b in enumerate(encoded):
        mem_data[ptr + i] = b

    return ptr

