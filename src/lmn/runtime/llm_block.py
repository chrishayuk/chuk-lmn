# file: src/lmn/runtime/llm_block.py

import logging
import wasmtime

# Import necessary modules
from lmn.compiler.pipeline import compile_code_to_wat
from lmn.runtime.host.host_initializer import initialize_host_functions  # Updated import

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
        logging.debug("Compilation to WAT and WASM successful.")
    except Exception as e:
        logging.error(f"Compilation error: {e}")
        return [f"Compilation error: {e}"]

    if not wasm_bytes:
        logging.error("No WASM produced. Ensure 'wat2wasm' is available.")
        return ["No WASM produced (wat2wasm missing?)."]

    # 2) Set up Wasmtime runtime
    engine = wasmtime.Engine()
    store = wasmtime.Store(engine)
    linker = wasmtime.Linker(engine)
    logging.debug("Wasmtime engine, store, and linker initialized.")

    # A small mutable reference that host functions will use to read from memory
    memory_ref = [None]

    # 3) Define host functions that capture LMN prints, referencing memory_ref
    initialize_host_functions(linker, store, output_lines, memory_ref=memory_ref)
    logging.debug("Host functions initialized and linked.")

    # 4) Instantiate the module
    try:
        module = wasmtime.Module(engine, wasm_bytes)
        instance = linker.instantiate(store, module)
        logging.debug("WASM module instantiated successfully.")
    except Exception as e:
        logging.error(f"Instantiation error: {e}")
        return [f"Instantiation error: {e}"]

    # 5) Attach the memory export if present
    mem_export = instance.exports(store).get("memory")
    if mem_export is not None:
        memory_ref[0] = mem_export
        logging.debug("Memory export attached to memory_ref.")
    else:
        logging.warning("No memory export found in the WASM module.")

    # 6) Call __top_level__ if present
    try:
        exports = instance.exports(store)
        top_func = exports.get("__top_level__")
        if top_func:
            logging.debug("Calling '__top_level__' function.")
            top_func(store)
            logging.debug("'__top_level__' function executed successfully.")
        else:
            logging.warning("'__top_level__' function not found in the WASM module.")
    except Exception as e:
        logging.error(f"Error during '__top_level__' execution: {e}")
        return [f"Runtime error: {e}"]

    return output_lines
