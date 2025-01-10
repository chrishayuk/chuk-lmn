# file: src/lmn/runtime/core/llm/handler.py

import logging
from lmn.runtime.host.memory_utils import read_utf8_string
from lmn.runtime.host.core.llm.adapters.llm_adapter import LLMAdapter

logger = logging.getLogger(__name__)

def llm_handler(def_info, store, memory_ref, output_list, *args) -> int:
    """
    A single, catch-all LLM handler that:
      - Expects exactly 2 i32 arguments: (prompt_ptr, model_ptr).
      - Stores the response in WASM memory using a simple bump offset.
    """

    if not memory_ref or memory_ref[0] is None:
        logger.debug("memory_ref is None or invalid.")
        output_list.append("<no memory>")
        return 0

    mem = memory_ref[0]
    func_name = def_info["name"]

    # 1) We expect exactly 2 items in `args`, e.g. (1026, 1029).
    if len(args) != 2:
        logger.debug(f"[LLM] Invalid arguments. Expected 2 items, got {len(args)} => {args}")
        output_list.append("<llm argument mismatch>")
        return 0

    # 2) Unpack them directly
    prompt_ptr, model_ptr = args
    logger.debug(f"[LLM] prompt_ptr={prompt_ptr}, model_ptr={model_ptr}")

    if func_name == "llm":
        # 3) Read the prompt/model strings from WASM memory
        prompt_str = read_utf8_string(store, mem, prompt_ptr)
        model_str  = read_utf8_string(store, mem, model_ptr)
        provider_str = "ollama"  # Hard-coded or read from def_info, etc.

        logger.debug(f"[LLM] Called with prompt='{prompt_str}', model='{model_str}', provider='{provider_str}'")

        # 4) Get a response from your LLM adapter
        llm_adapter = LLMAdapter(output_list)
        messages = [{"role": "user", "content": prompt_str}]
        response_text = llm_adapter.chat(provider_str, model_str, messages)

        # 5) Null-terminate the response and encode it
        response_text += "\0"
        encoded = response_text.encode("utf-8")

        # 6) Use a simple bump-pointer offset (old approach).
        #    If you prefer to call your WASM malloc, you'd do:
        #       offset = wasm_malloc(len(encoded))
        offset = getattr(llm_handler, "current_offset", 4096)
        next_offset = offset + len(encoded)

        mem_data = mem.data_ptr(store)
        mem_size = mem.data_len(store)

        # 7) Bounds check
        if next_offset > mem_size:
            logger.debug("[LLM] <out-of-bounds for LLM response>")
            output_list.append("<response out-of-bounds>")
            return 0

        # 8) Write the response bytes into WASM memory
        for i, byte_val in enumerate(encoded):
            mem_data[offset + i] = byte_val

        logger.debug(f"[LLM] Response written at offset {offset}")
        # Update the static offset
        llm_handler.current_offset = next_offset

        # 9) Return the pointer to that string
        return offset

    else:
        # If the function is not "llm", handle it
        logger.debug(f"[LLM Handler] Unrecognized LLM function '{func_name}'")
        output_list.append("<unrecognized LLM function>")
        return 0
a