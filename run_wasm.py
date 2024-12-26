#!/usr/bin/env python3

import argparse
import wasmtime

def main():
    parser = argparse.ArgumentParser(
        description="Run a WebAssembly module with Wasmtime and call its 'main' or '__top_level__' export."
    )
    parser.add_argument("wasm_file", help="Path to the .wasm file.")
    args = parser.parse_args()

    # Create engine/store
    engine = wasmtime.Engine()
    store = wasmtime.Store(engine)

    # Load the module from file
    module = wasmtime.Module.from_file(engine, args.wasm_file)

    # Create a Linker
    linker = wasmtime.Linker(engine)

    #--------------------------
    # 1. Define host functions
    #--------------------------
    def host_print_i32(x):
        print(f"i32: {x}")

    def host_print_i64(x):
        print(f"i64: {x}")

    def host_print_f32(x):
        # Python doesn't have a direct float32 type, but wasmtime will pass it as Python float
        print(f"f32: {x}")

    def host_print_f64(x):
        print(f"f64: {x}")

    #----------------------------------------------
    # 2. Create matching function signatures/types
    #----------------------------------------------
    func_type_i32 = wasmtime.FuncType([wasmtime.ValType.i32()], [])
    func_type_i64 = wasmtime.FuncType([wasmtime.ValType.i64()], [])
    func_type_f32 = wasmtime.FuncType([wasmtime.ValType.f32()], [])
    func_type_f64 = wasmtime.FuncType([wasmtime.ValType.f64()], [])

    #--------------------------------------------------
    # 3. Link each import to the corresponding function
    #--------------------------------------------------
    linker.define(store, "env", "print_i32", wasmtime.Func(store, func_type_i32, host_print_i32))
    linker.define(store, "env", "print_i64", wasmtime.Func(store, func_type_i64, host_print_i64))
    linker.define(store, "env", "print_f32", wasmtime.Func(store, func_type_f32, host_print_f32))
    linker.define(store, "env", "print_f64", wasmtime.Func(store, func_type_f64, host_print_f64))

    # Instantiate the module
    instance = linker.instantiate(store, module)

    # Try to find 'main'
    main_func = instance.exports(store).get("main")
    # If no 'main', try '__top_level__'
    top_level_func = instance.exports(store).get("__top_level__")

    if main_func is not None:
        print("Found 'main' export, calling it now.")
        result = main_func(store)
        print(f"'main' returned: {result}")
    elif top_level_func is not None:
        print("No 'main' found, calling '__top_level__' instead.")
        result = top_level_func(store)
        print(f"'__top_level__' returned: {result}")
    else:
        print("Error: Neither 'main' nor '__top_level__' was found in module exports.")

if __name__ == "__main__":
    main()
