# file: src/lmn/runtime/host/core/malloc/call_malloc.py

import logging
from lmn.runtime.host.core.malloc.handler import malloc_handler

logger = logging.getLogger(__name__)

def call_malloc(store, memory, output_list, size) -> int:
    """
    Minimal Python helper that calls your 'malloc_handler'
    with the given 'size', returning a pointer or 0 on failure.
    """
    def_info = {"name": "malloc"}  # used inside malloc_handler for logging
    memory_ref = [memory]          # pass a list with memory[0] = memory
    args = (size,)                 # single argument, matching (param i32)

    ptr = malloc_handler(def_info, store, memory_ref, output_list, *args)
    logger.debug(f"call_malloc: requested size={size} => allocated ptr={ptr}")
    return ptr
