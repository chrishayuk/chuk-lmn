#!/usr/bin/env python3
# src/lmn/cli/run_wasm.py
import sys
import logging
import wasmtime
from lmn.runtime.wasm_runner import create_environment

def main():
    # Setup logging
    logging.basicConfig(
        level=logging.CRITICAL,
        format="%(levelname)s - %(name)s - %(message)s"
    )

    # Check arguments
    if len(sys.argv) != 2:
        print("Usage: run_wasm.py <wasm_file>")
        sys.exit(1)

    # Create environment (this sets up all host functions)
    env = create_environment()

    try:
        # Get environment components
        engine = env["engine"]
        store = env["store"]
        linker = env["linker"]
        memory_ref = env["memory_ref"]
        output_lines = env["output_lines"]

        # Load and instantiate the WASM module directly
        module = wasmtime.Module.from_file(engine, sys.argv[1])
        instance = linker.instantiate(store, module)

        # Get memory if available
        mem_export = instance.exports(store).get("memory")
        if isinstance(mem_export, wasmtime.Memory):
            memory_ref[0] = mem_export
            
        # Try to call main or __top_level__
        exports = instance.exports(store)
        main_func = exports.get("main")
        top_level_func = exports.get("__top_level__")

        if main_func is not None:
            print("Found 'main' export, calling it now.")
            result = main_func(store)
            
            # Print captured output
            for line in output_lines:
                print(line, end="")
                
            print(f"\n'main' returned: {result}")
        elif top_level_func is not None:
            print("No 'main' found, calling '__top_level__' instead.")
            result = top_level_func(store)
            
            # Print captured output
            for line in output_lines:
                print(line, end="")
                
            print(f"\n'__top_level__' returned: {result}")
        else:
            print("Error: Neither 'main' nor '__top_level__' was found in module exports.")
            sys.exit(1)

    except Exception as e:
        print(f"Error running WASM file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()