# src/lmn/runtime/wasm_runner.py
import logging
import wasmtime
from lmn.compiler.pipeline import compile_code_to_wat
from lmn.runtime.host.host_initializer import initialize_host_functions

def create_environment():
    """
    Creates a reusable Wasmtime environment.
    """
    engine = wasmtime.Engine()
    store = wasmtime.Store(engine)
    linker = wasmtime.Linker(engine)
    memory_ref = [None]
    output_lines = []
    initialize_host_functions(linker, store, output_lines, memory_ref=memory_ref)
    return {"engine": engine, "store": store, "linker": linker, "memory_ref": memory_ref, "output_lines": output_lines}

def run_wasm(code: str, env: dict = None) -> list[str]:
    """
    Compiles and runs LMN code using a Wasmtime environment.
    If an environment is provided, it reuses the same engine, store, and linker.

    :param code: LMN source code to compile and run.
    :param env: A reusable Wasmtime environment.
    :return: A list of strings representing output from the code execution.
    """
    if not env:
        env = create_environment()

    engine = env["engine"]
    store = env["store"]
    linker = env["linker"]
    memory_ref = env["memory_ref"]
    output_lines = env["output_lines"]

    # Clear previous output
    output_lines.clear()

    # Compile LMN code to WASM
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

    # Instantiate WASM module
    try:
        module = wasmtime.Module(engine, wasm_bytes)
        instance = linker.instantiate(store, module)
        logging.debug("WASM module instantiated successfully.")
    except Exception as e:
        logging.error(f"Instantiation error: {e}")
        return [f"Instantiation error: {e}"]

    # Attach memory export if available
    mem_export = instance.exports(store).get("memory")
    if mem_export is not None:
        memory_ref[0] = mem_export
        logging.debug("Memory export attached to memory_ref.")
    else:
        logging.warning("No memory export found in the WASM module.")

    # Call __top_level__ function if present
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
        logging.error(f"Runtime error during '__top_level__' execution: {e}")
        return [f"Runtime error: {e}"]

    return output_lines
