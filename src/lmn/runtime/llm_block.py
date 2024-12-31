# file: src/lmn/runtime/llm_block.py

import wasmtime

from lmn.compiler.pipeline import compile_code_to_wat
from lmn.runtime.host_functions import define_host_functions_capture_output

def run_lmn_block(code: str) -> list[str]:
    """
    Compiles and runs a block of LMN code in a fresh Wasmtime environment,
    capturing any output from the LMN host functions.

    - We use define_host_functions_capture_output(linker, store, output_list),
      so each 'print' from LMN appends to output_list (rather than printing to stdout).
    - At the end, we return this list.

    :param code: The LMN source code to compile and run.
    :return: A list of strings representing the lines 'printed' by the code.
    """
    # A list that host functions will append to
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

    # 3) Define host functions that capture LMN prints
    define_host_functions_capture_output(linker, store, output_lines)

    # 4) Instantiate module & call __top_level__ if present
    try:
        module = wasmtime.Module(engine, wasm_bytes)
        instance = linker.instantiate(store, module)
    except Exception as e:
        return [f"Instantiation error: {e}"]

    exports = instance.exports(store)
    top_func = exports.get("__top_level__")
    if top_func:
        top_func(store)

    # 5) Return any appended lines
    return output_lines


