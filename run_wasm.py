#!/usr/bin/env python3

import argparse
import wasmtime

def read_utf8_string(store, memory, offset, max_len=200):
    """
    Reads a UTF-8 string from 'memory' starting at 'offset', stopping at a null byte
    or after max_len bytes (to avoid runaway reads if there's no terminator).
    Returns the decoded Python string.
    """
    # Access the underlying data array of the memory
    mem_data = memory.data_ptr(store)
    mem_size = memory.data_len(store)

    # Make sure offset is in range
    if offset < 0 or offset >= mem_size:
        return f"<invalid pointer {offset}>"

    raw_bytes = bytearray()
    end = min(offset + max_len, mem_size)
    for i in range(offset, end):
        b = mem_data[i]
        if b == 0:
            # Null terminator => stop
            break
        raw_bytes.append(b)

    return raw_bytes.decode('utf-8', errors='replace')

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

    # We'll need to access memory to read strings, so we'll define a placeholder.
    # We'll fill this in after we instantiate the module (chicken-and-egg).
    # But in Wasmtime, we typically instantiate first *after* we define the imports. 
    # So we'll define host_print_string etc. as lambdas that capture the store and instance later.
    # Or we can do a two-step approach: define the host fns with empty placeholders, then update them.
    # The simpler approach is to define them as normal functions that do a "lazy" memory lookup from the instance.
    
    # We'll define host functions with 1 param i32. We'll do the memory reading inside them.
    
    def host_print_i32(x):
        print(f"i32: {x}")

    def host_print_i64(x):
        # wasmtime will pass i64 as Python int if it's in range, or possibly as int anyway
        print(f"i64: {x}")

    def host_print_f32(x):
        # Python doesn't have float32 specifically, so it's just a float
        print(f"f32: {x}")

    def host_print_f64(x):
        print(f"f64: {x}")

    # We define these now, but they need the memory instance. We'll grab it after instantiation.
    def host_print_string(ptr):
        # We'll get the memory from the instance exports
        # If there's no memory export, we can't read the string. 
        memory_export = instance.exports(store).get("memory")
        if memory_export is None:
            print(f"<no memory export, got pointer={ptr}>")
            return
        s = read_utf8_string(store, memory_export, ptr)
        print(f"string: {s}")

    def host_print_json(ptr):
        memory_export = instance.exports(store).get("memory")
        if memory_export is None:
            print(f"<no memory export, got pointer={ptr}>")
            return
        s = read_utf8_string(store, memory_export, ptr)
        print(f"json: {s}")

    def host_print_array(ptr):
        memory_export = instance.exports(store).get("memory")
        if memory_export is None:
            print(f"<no memory export, got pointer={ptr}>")
            return
        s = read_utf8_string(store, memory_export, ptr)
        print(f"array: {s}")

    # Create function signatures
    func_type_i32 = wasmtime.FuncType([wasmtime.ValType.i32()], [])
    func_type_i64 = wasmtime.FuncType([wasmtime.ValType.i64()], [])
    func_type_f32 = wasmtime.FuncType([wasmtime.ValType.f32()], [])
    func_type_f64 = wasmtime.FuncType([wasmtime.ValType.f64()], [])

    # We'll reuse the i32 signature for string/json/array (all param i32).
    # Then define them in the linker:
    linker.define(store, "env", "print_i32",
                  wasmtime.Func(store, func_type_i32, host_print_i32))
    linker.define(store, "env", "print_i64",
                  wasmtime.Func(store, func_type_i64, host_print_i64))
    linker.define(store, "env", "print_f32",
                  wasmtime.Func(store, func_type_f32, host_print_f32))
    linker.define(store, "env", "print_f64",
                  wasmtime.Func(store, func_type_f64, host_print_f64))

    # Similarly for string, json, array => also param i32
    linker.define(store, "env", "print_string",
                  wasmtime.Func(store, func_type_i32, host_print_string))
    linker.define(store, "env", "print_json",
                  wasmtime.Func(store, func_type_i32, host_print_json))
    linker.define(store, "env", "print_array",
                  wasmtime.Func(store, func_type_i32, host_print_array))

    # Instantiate the module
    instance = linker.instantiate(store, module)

    # Now we can run main or __top_level__
    main_func = instance.exports(store).get("main")
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
