# src/lmn/runtime/core/llm/llm_functions.py
import wasmtime
from lmn.runtime.host.memory_utils import read_utf8_string


class LLMHostFunctions:
    """
    Provides a stub 'llm' host function to demonstrate hooking up a custom
    function that returns a string in WebAssembly memory.
    """

    def __init__(self, linker: wasmtime.Linker, store: wasmtime.Store, output_list: list, memory_ref=None):
        """
        :param linker:      The Wasmtime linker.
        :param store:       The Wasmtime store.
        :param output_list: A list to capture or log messages.
        :param memory_ref:  A reference to the memory export, e.g. [memory_obj].
        """
        self.linker = linker
        self.store = store
        self.output_list = output_list
        self.memory_ref = memory_ref

        self.define_host_functions()

    def define_host_functions(self):
        """
        Registers the 'llm' host function with the Wasmtime linker.
        The signature is (i32, i32, f64) -> i32, meaning:
          - i32 = pointer to 'prompt' (null-terminated string)
          - i32 = pointer to 'model'  (null-terminated string)
          - returns i32 = pointer to the LLM response
        """
        func_type_llm = wasmtime.FuncType(
            [wasmtime.ValType.i32(), wasmtime.ValType.i32()],
            [wasmtime.ValType.i32()]
        )

        # Bind the function name 'llm' in the "env" namespace
        self.linker.define(
            self.store, "env", "llm",
            wasmtime.Func(self.store, func_type_llm, self.host_llm)
        )

    def host_llm(self, prompt_ptr: int, model_ptr: int) -> int:
        """
        A stub LLM function that:
          1) Reads the 'prompt' and 'model' from Wasm memory (if memory_ref is valid).
          2) Logs them to output_list for debugging.
          3) Writes a hardcoded string "Hello from LLM!" into memory at a fixed offset.
          4) Returns that offset as an i32 pointer.

        In a real implementation, you'd call an actual model API here.
        """
        # If we don't have memory, return 0 to indicate a null pointer
        if not self.memory_ref or self.memory_ref[0] is None:
            return 0

        mem = self.memory_ref[0]

        # 1) Read the prompt & model from memory for demonstration/logging
        prompt_str = read_utf8_string(self.store, mem, prompt_ptr)
        model_str = read_utf8_string(self.store, mem, model_ptr)
        self.output_list.append(
            f"[LLM] Called with prompt='{prompt_str}', model='{model_str}'"
        )

        # 2) Hardcode the response in linear memory
        offset = 4096  # Some offset not used by your data segments
        response_text = "Hello from LLM!\0"  # Null-terminated
        mem_data = mem.data_ptr(self.store)
        mem_size = mem.data_len(self.store)

        if offset + len(response_text) > mem_size:
            self.output_list.append("<out-of-bounds for LLM response>")
            return 0

        for i, byte_val in enumerate(response_text.encode("utf-8")):
            mem_data[offset + i] = byte_val

        # 3) Return the offset pointer to the response
        return offset
