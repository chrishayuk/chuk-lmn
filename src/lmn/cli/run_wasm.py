import logging
import wasmtime

# Import necessary modules
from lmn.compiler.pipeline import compile_code_to_wat
from lmn.runtime.host.host_initializer import initialize_host_functions

def run_wasm(code: str, use_existing_environment: bool = False, existing_env: dict = None) -> list[str]:
    """
    Compiles and runs LMN code using a Wasmtime environment. Allows reusing the same
    environment (engine, store, linker, etc.) to avoid recreating them multiple times.

    :param code: LMN source code to compile and run.
    :param use_existing_environment: Whether to reuse an existing environment.
    :param existing_env: A dictionary containing the existing environment components.
    :return: A list of strings representing everything 'printed' by the code.
    """
    output_lines = []

    # Initialize environment components
    engine = None
    store = None
    linker = None
    memory_ref = None

    if use_existing_environment and existing_env:
        engine = existing_env.get("engine")
        store = existing_env.get("store")
        linker = existing_env.get("linker")
        memory_ref = existing_env.get("memory_ref")

    # Create new environment if not reusing
    if not engine or not store or not linker or not memory_ref:
        engine = wasmtime.Engine()
        store = wasmtime.Store(engine)
        linker = wasmtime.Linker(engine)
        memory_ref = [None]
        initialize_host_functions(linker, store, output_lines, memory_ref=memory_ref)
        logging.debug("New Wasmtime environment initialized.")

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

    # 2) Instantiate the module
    try:
        module = wasmtime.Module(engine, wasm_bytes)
        instance = linker.instantiate(store, module)
        logging.debug("WASM module instantiated successfully.")
    except Exception as e:
        logging.error(f"Instantiation error: {e}")
        return [f"Instantiation error: {e}"]

    # 3) Attach the memory export if present
    mem_export = instance.exports(store).get("memory")
    if mem_export is not None:
        memory_ref[0] = mem_export
        logging.debug("Memory export attached to memory_ref.")
    else:
        logging.warning("No memory export found in the WASM module.")

    # 4) Call __top_level__ if present
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

    # Return output lines
    return output_lines

# Example of creating and reusing the environment
def create_environment():
    engine = wasmtime.Engine()
    store = wasmtime.Store(engine)
    linker = wasmtime.Linker(engine)
    memory_ref = [None]
    output_lines = []
    initialize_host_functions(linker, store, output_lines, memory_ref=memory_ref)
    return {"engine": engine, "store": store, "linker": linker, "memory_ref": memory_ref}

# Example usage
if __name__ == "__main__":
    # Reusable environment
    env = create_environment()

    # First run
    print(run_wasm("your LMN code here", use_existing_environment=True, existing_env=env))

    # Second run with the same environment
    print(run_wasm("additional LMN code", use_existing_environment=True, existing_env=env))
