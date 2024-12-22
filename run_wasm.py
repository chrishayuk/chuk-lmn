#!/usr/bin/env python3

import argparse
import wasmtime

def main():
    parser = argparse.ArgumentParser(
        description="Run a WebAssembly module with Wasmtime and call its 'main' export."
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

    # Define a host function for (import "env" "print_i32" (func (param i32))).
    # Wasmtime < 3.0 only passes 1 argument, so we define it with a single param.
    def host_print_i32(x):
        print(x)

    # Provide the import to the linker
    func_type = wasmtime.FuncType([wasmtime.ValType.i32()], [])
    linker.define(store, "env", "print_i32", wasmtime.Func(store, func_type, host_print_i32))

    # Instantiate the module
    instance = linker.instantiate(store, module)

    # Find the "main" export
    main_func = instance.exports(store).get("main")
    if main_func is None:
        print("Error: No 'main' function found in module exports.")
        return

    # Call "main" and print the return value
    result = main_func(store)
    print(f"'main' returned: {result}")

if __name__ == "__main__":
    main()
