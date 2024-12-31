# file: src/lmn/runtime/llm_block.py

import wasmtime

from lmn.compiler.pipeline import compile_code_to_wat
from lmn.runtime.host_functions import define_host_functions_capture_output

def run_lmn_block(code: str) -> list[str]:
    """
    Compiles and runs a block of LMN code in a fresh Wasmtime environment,
    capturing any output from the LMN host functions.

    This version uses a two-step approach so that if LMN calls 'print_string(ptr)',
    we have attached the WASM memory reference, and can read actual string content.

    :param code: LMN source code to compile and run.
    :return: A list of strings representing everything 'printed' by the code.
    """
    output_lines = []

    # 1) Compile LMN => WAT => WASM
    try:
        wat_text, wasm_bytes = compile_code_to_wat(
            code,
            also_produce_wasm=True,
            import_memory=False
        )
    except Exception as e:
        return [f"Compilation error: {e}"]

    if not wasm_bytes:
        return ["No WASM produced (wat2wasm missing?)."]

    # 2) Set up Wasmtime runtime
    engine = wasmtime.Engine()
    store = wasmtime.Store(engine)
    linker = wasmtime.Linker(engine)

    # A small mutable reference that host functions will use to read from memory
    memory_ref = [None]

    # 3) Define host functions that capture LMN prints, referencing memory_ref
    define_host_functions_capture_output(linker, store, output_lines, memory_ref=memory_ref)

    # 4) Instantiate
    try:
        module = wasmtime.Module(engine, wasm_bytes)
        instance = linker.instantiate(store, module)
    except Exception as e:
        return [f"Instantiation error: {e}"]

    # 5) Attach the memory to memory_ref if present
    mem_export = instance.exports(store).get("memory")
    if mem_export is not None:
        memory_ref[0] = mem_export

    # 6) Call __top_level__ if present
    exports = instance.exports(store)
    top_func = exports.get("__top_level__")
    if top_func:
        top_func(store)

    return output_lines
