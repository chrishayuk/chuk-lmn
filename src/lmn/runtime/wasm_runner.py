# file: src/lmn/runtime/wasm_runner.py
import wasmtime
import logging
from lmn.compiler.pipeline import compile_code_to_wat
from lmn.runtime.host.host_initializer import initialize_host_functions

def create_environment():
    """
    Creates a reusable Wasmtime environment.
    """
    # create the wasm engine, stor and linker
    engine = wasmtime.Engine()
    store = wasmtime.Store(engine)
    linker = wasmtime.Linker(engine)

    # clear memory
    memory_ref = [None]

    # clear output
    output_lines = []

    # initialize host functions
    initialize_host_functions(linker, store, output_lines, memory_ref=memory_ref)

    # return the environment
    return {"engine": engine, "store": store, "linker": linker, "memory_ref": memory_ref, "output_lines": output_lines}

def run_wasm(code: str, env: dict = None) -> list[str]:
    """
    Compiles and runs LMN code using a Wasmtime environment.
    If an environment is provided, it reuses the same engine, store, and linker.

    :param code: LMN source code to compile and run.
    :param env: A reusable Wasmtime environment.
    :return: A list of strings representing output from the code execution.
    """
    # check if we have an environment
    if not env:
        # no environment, so create it
        env = create_environment()

    # get the environment
    engine = env["engine"]
    store = env["store"]
    linker = env["linker"]
    memory_ref = env["memory_ref"]
    output_lines = env["output_lines"]

    # Clear previous output
    output_lines.clear()

    # Compile LMN code to WASM
    try:
        # compile to wat and wasm
        wat_text, wasm_bytes = compile_code_to_wat(
            code,
            also_produce_wasm=True,
            import_memory=False
        )

        # debug
        logging.debug("Compilation to WAT and WASM successful.")
    except Exception as e:
        # error in compilation
        logging.error(f"Compilation error: {e}")
        return [f"Compilation error: {e}"]
    
    # check we got wasm
    if not wasm_bytes:
        # no wasm
        logging.error("No WASM produced. Ensure 'wat2wasm' is available.")
        return ["No WASM produced (wat2wasm missing?)."]

    
    try:
        # Instantiate WASM module
        module = wasmtime.Module(engine, wasm_bytes)
        instance = linker.instantiate(store, module)
        logging.debug("WASM module instantiated successfully.")
    except Exception as e:
        # error
        logging.error(f"Instantiation error: {e}")
        return [f"Instantiation error: {e}"]

    # Attach memory export if available
    mem_export = instance.exports(store).get("memory")
    if mem_export is not None:
        memory_ref[0] = mem_export
        logging.debug("Memory export attached to memory_ref.")
    else:
        logging.warning("No memory export found in the WASM module.")

    # Try to execute the entry point function
    try:
        exports = instance.exports(store)

        # get the main and top level functions
        main_func = exports.get("main")
        top_level_func = exports.get("__top_level__")

        # check if we have main
        if main_func is not None:
            # we got main
            logging.info("Found 'main' export, executing it.")

            # execute it
            result = main_func(store)

            # debug
            logging.debug(f"'main' function returned: {result}")
        elif top_level_func is not None:
            # we got top level
            logging.info("No 'main' found, executing '__top_level__' instead.")

            # execute it
            result = top_level_func(store)
            
            # debug
            logging.debug(f"'__top_level__' function returned: {result}")
        else:
            # no entry function
            error_msg = "Neither 'main' nor '__top_level__' function found in module exports."
            logging.error(error_msg)
            output_lines.append(error_msg)
            
    except Exception as e:
        # error
        error_msg = f"Runtime error during execution: {e}"
        logging.error(error_msg)
        output_lines.append(error_msg)

    return output_lines