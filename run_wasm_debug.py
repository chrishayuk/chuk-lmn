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

    # 3) Create a Linker
    linker = wasmtime.Linker(engine)

    #----------------------------------------------------
    # 4) Define host functions for each numeric type
    #    (import "env" "print_i32" (func (param i32)))
    #    (import "env" "print_i64" (func (param i64)))
    #    (import "env" "print_f32" (func (param f32)))
    #    (import "env" "print_f64" (func (param f64)))
    #----------------------------------------------------

    # i32
    def host_print_i32(x):
        print(f"i32: {x}")

    # i64
    def host_print_i64(x):
        print(f"i64: {x}")

    # f32
    def host_print_f32(x):
        # Python doesn't distinguish float32 vs float64; 
        # it's just a Python float. But we label it "f32:" for clarity.
        print(f"f32: {x}")

    # f64
    def host_print_f64(x):
        print(f"f64: {x}")

    # Print debug info about these host functions
    print("=== DEBUG: Checking host_print_i32 signature ===")
    print("host_print_i32:", host_print_i32)
    code_obj = host_print_i32.__code__
    print(f"Argcount: {code_obj.co_argcount}")
    print(f"Arg names: {code_obj.co_varnames[:code_obj.co_argcount]}")
    print()

    #----------------------------------------------
    # 5) Provide the imports to the linker
    #----------------------------------------------
    func_type_i32 = wasmtime.FuncType([wasmtime.ValType.i32()], [])
    func_type_i64 = wasmtime.FuncType([wasmtime.ValType.i64()], [])
    func_type_f32 = wasmtime.FuncType([wasmtime.ValType.f32()], [])
    func_type_f64 = wasmtime.FuncType([wasmtime.ValType.f64()], [])

    try:
        linker.define(store, "env", "print_i32", wasmtime.Func(store, func_type_i32, host_print_i32))
        linker.define(store, "env", "print_i64", wasmtime.Func(store, func_type_i64, host_print_i64))
        linker.define(store, "env", "print_f32", wasmtime.Func(store, func_type_f32, host_print_f32))
        linker.define(store, "env", "print_f64", wasmtime.Func(store, func_type_f64, host_print_f64))
    except Exception as e:
        print(f"ERROR: Failed to define imports: {e}")
        sys.exit(1)

    # 6) Instantiate the module
    print("=== DEBUG: Instantiating module ===")
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
