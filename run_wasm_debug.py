#!/usr/bin/env python3

import argparse
import wasmtime
import sys
import os

def main():
    # Print debug info about Python environment
    print("=== DEBUG: Running run_wasm.py ===")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script location: {__file__}\n")

    parser = argparse.ArgumentParser(
        description="Run a WASM module with Wasmtime and call its 'main' export."
    )
    parser.add_argument("wasm_file", help="Path to the .wasm file.")
    args = parser.parse_args()

    wasm_path = os.path.abspath(args.wasm_file)
    print(f"=== DEBUG: wasm_file = {wasm_path} ===")

    # 1) Create the engine and store
    engine = wasmtime.Engine()
    store = wasmtime.Store(engine)

    # 2) Load the module from file
    print("=== DEBUG: Loading module ===")
    try:
        module = wasmtime.Module.from_file(engine, wasm_path)
    except Exception as e:
        print(f"ERROR: Could not load Wasm module: {e}")
        sys.exit(1)

    # Debug: Inspect the module’s imports/exports
    print("\n=== DEBUG: Module Imports ===")
    for imp in module.imports:
        print(f"  import: module='{imp.module}', name='{imp.name}', type='{imp.type}'")

    print("\n=== DEBUG: Module Exports ===")
    for exp in module.exports:
        print(f"  export: name='{exp.name}', type='{exp.type}'")
    print()

    # 3) Create a Linker to define the `print_i32` import
    linker = wasmtime.Linker(engine)

    # 4) Define the host function. Must accept two params: (caller, x)
    def host_print_i32(x):
        print(x)

    # Print debug info about this function
    print("=== DEBUG: Checking host_print_i32 signature ===")
    print("host_print_i32:", host_print_i32)
    code_obj = host_print_i32.__code__
    print(f"Argcount: {code_obj.co_argcount}")
    print(f"Arg names: {code_obj.co_varnames[:code_obj.co_argcount]}")
    print()

    # 5) Provide the import
    #    (import "env" "print_i32" (func (param i32)))
    #    => must define wasmtime.Func(...) with one i32 param
    print("=== DEBUG: Defining linker import for env.print_i32 ===")
    func_type = wasmtime.FuncType([wasmtime.ValType.i32()], [])
    host_func = wasmtime.Func(store, func_type, host_print_i32)
    try:
        linker.define(store, "env", "print_i32", host_func)
    except Exception as e:
        print(f"ERROR: Failed to define env.print_i32: {e}")
        sys.exit(1)

    # 6) Instantiate the module
    print("\n=== DEBUG: Instantiating module ===")
    try:
        instance = linker.instantiate(store, module)
    except Exception as e:
        print(f"ERROR: Could not instantiate the module: {e}")
        sys.exit(1)

    # 7) Look up "main" export
    main_func = instance.exports(store).get("main")
    if main_func is None:
        print("Error: No 'main' function found in module exports.")
        return

    print("\n=== DEBUG: Found 'main' export, calling it now ===")
    # 8) Call the function
    try:
        result = main_func(store)
        print(f"\n=== SUCCESS: 'main' returned: {result} ===")
    except Exception as e:
        print("=== ERROR while calling 'main' ===")
        print(e)

if __name__ == "__main__":
    main()
