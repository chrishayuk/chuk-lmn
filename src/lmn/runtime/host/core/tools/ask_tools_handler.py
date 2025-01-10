# file: src/lmn/runtime/core/tools/ask_tools_handler.py

import logging
from lmn.runtime.host.memory_utils import read_utf8_string
from lmn.runtime.host.core.llm.adapters.llm_adapter import LLMAdapter
from lmn.runtime.host.memory_utils_extra import store_string_with_malloc

logger = logging.getLogger(__name__)

def ask_or_call_tools_handler(def_info, store, memory_ref, output_list, *args) -> int:
    """
    A single handler for both 'ask_tools' and 'call_tools'. Each expects:
      - One i32 argument => question_ptr (for ask_tools) or command_ptr (for call_tools).
      - We'll pass the question/command to the LLM with context about available tools,
        call our LLM adapter, and store its response in WASM memory using store_string_with_malloc().
    """
    # 1) Ensure memory is valid
    if not memory_ref or memory_ref[0] is None:
        logger.debug("memory_ref is None or invalid.")
        output_list.append("<no memory>")
        return 0

    mem = memory_ref[0]
    func_name = def_info["name"]  # e.g. 'ask_tools' or 'call_tools'

    # 2) Check argument count
    if len(args) != 1:
        logger.debug(f"[{func_name}] Invalid arguments. Expected 1, got {len(args)} => {args}")
        output_list.append(f"<{func_name} argument mismatch>")
        return 0

    # 3) Read the user’s question/command from WASM memory
    question_ptr = args[0]
    logger.debug(f"[{func_name}] question_ptr={question_ptr}")
    question_str = read_utf8_string(store, mem, question_ptr)
    logger.debug(f"[{func_name}] question='{question_str}'")

    # 4) Build a system prompt describing the available tools
    context_str = """
You are a helpful AI that knows how to use the following tools:
- get_internet_time(): returns the current time from an internet time API (int)
- get_system_time(): returns the local system time in seconds (int)
- get_weather(lat: double, lon: double): returns JSON weather data
- get_joke(): returns a joke as a string.
To call a tool manually you would just call it like any other function e.g. get_joke()

If the user calls 'ask_tools', they want general info about which tools exist or how to call them.
If the user calls 'call_tools', they want you to parse the command and decide which tool to call.
"""

    if func_name == "ask_tools":
        system_prompt = f"{context_str}\nUser just asked: '{question_str}'\n"
    else:
        system_prompt = f"{context_str}\nUser wants to execute: '{question_str}'\n"

    # 5) Call the LLM adapter (like llm_handler)
    llm_adapter = LLMAdapter(output_list)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": question_str},
    ]
    provider_str = "ollama"   # or whichever LLM provider
    model_str    = "llama3.2" # or whichever model is installed

    response_text = llm_adapter.chat(provider_str, model_str, messages)
    logger.debug(f"[{func_name}] Raw LLM response => {repr(response_text)}")

    # 6) If the LLM returns empty, fallback
    if not response_text.strip():
        response_text = "No response from LLM"

    # 7) Store the final string in WASM memory using malloc
    #    This approach allocates enough space automatically.
    ptr = store_string_with_malloc(store, mem, output_list, response_text)
    logger.debug(f"[{func_name}] => stored response at ptr={ptr}")

    # 8) Return the pointer
    return ptr
