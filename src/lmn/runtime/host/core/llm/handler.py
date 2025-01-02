# src/lmn/runtime/core/llm/handler.py

from lmn.runtime.host.memory_utils import read_utf8_string
from lmn.runtime.host.core.llm.adapters.llm_adapter import LLMAdapter

def llm_handler(def_info, store, memory_ref, output_list, *args) -> int:
    """
    A single, catch-all LLM handler. 
    It checks `def_info["name"]` to decide which LLM function was invoked 
    and parses the WASM arguments accordingly.
    
    :param def_info:    The JSON definition (e.g. {"name": "llm", ...}).
    :param store:       The Wasmtime store.
    :param memory_ref:  Reference to the WASM memory.
    :param output_list: A list or logger for capturing output logs.
    :param args:        The WASM arguments. For "llm", we expect (prompt_ptr, model_ptr).
    :return:            Typically an i32 pointer or 0 on failure, depending on the function.
    """
    if not memory_ref or memory_ref[0] is None:
        return 0

    mem = memory_ref[0]
    func_name = def_info["name"]  # e.g. "llm"

    output_list.append(f"[LLM Handler] Invoked for function '{func_name}'")

    # If you have multiple LLM functions, switch on func_name
    if func_name == "llm":
        # Expect two i32 pointers: (prompt_ptr, model_ptr)
        prompt_ptr, model_ptr = args
        prompt_str = read_utf8_string(store, mem, prompt_ptr)
        model_str  = read_utf8_string(store, mem, model_ptr)
        provider_str = "ollama"  # Hard-coded, or read from def_info, etc.

        output_list.append(
            f"[LLM] Called with prompt='{prompt_str}', model='{model_str}', provider='{provider_str}'"
        )

        llm_adapter = LLMAdapter(output_list)
        messages = [{"role": "user", "content": prompt_str}]

        response_text = llm_adapter.chat(provider_str, model_str, messages)
        response_text += "\0"  # null-terminate

        # Write the response at a fixed offset (or manage memory more dynamically)
        offset = 4096
        mem_data = mem.data_ptr(store)
        mem_size = mem.data_len(store)

        if offset + len(response_text) > mem_size:
            output_list.append("[LLM] <out-of-bounds for LLM response>")
            return 0

        for i, byte_val in enumerate(response_text.encode("utf-8")):
            mem_data[offset + i] = byte_val

        return offset

    else:
        # If you add future LLM functions like "llm_generate", "llm_summarize", etc.,
        # handle them here with a new elif block:
        output_list.append(f"[LLM Handler] Unrecognized LLM function '{func_name}'")
        return 0
