#!/usr/bin/env python3

import argparse
import wasmtime

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("wasm_file", help="Path to the .wasm file")
    args = parser.parse_args()

    engine = wasmtime.Engine()
    store = wasmtime.Store(engine)
    module = wasmtime.Module.from_file(engine, args.wasm_file)
    linker = wasmtime.Linker(engine)

    #
    # IMPORTANT: `host_print_i32` must accept two parameters: (caller, x).
    #
    def host_print_i32(caller, x):
        print(x)

    # Alternatively:
    # host_print_i32 = lambda caller, x: print(x)

    linker.define(
        store,
        "env",
        "print_i32",
        wasmtime.Func(
            store,
            wasmtime.FuncType([wasmtime.ValType.i32()], []),
            host_print_i32  # the function with signature (caller, x)
        )
    )

    instance = linker.instantiate(store, module)
    main_func = instance.exports(store).get("main")
    if main_func is None:
        print("Error: No 'main' function found in module exports.")
        return

    result = main_func(store)  # Call the 'main' exported function
    print(f"'main' function returned: {result}")

if __name__ == "__main__":
    main()
