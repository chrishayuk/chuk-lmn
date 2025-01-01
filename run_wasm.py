#!/usr/bin/env python3

import argparse
import struct
import wasmtime

def read_utf8_string(store, memory, offset, max_len=200):
    """
    Reads a UTF-8 string from 'memory' starting at 'offset', stopping at a null byte
    or after max_len bytes. Returns the decoded Python string.
    """
    mem_data = memory.data_ptr(store)
    mem_size = memory.data_len(store)

    if offset < 0 or offset >= mem_size:
        return f"<invalid pointer {offset}>"

    raw_bytes = bytearray()
    end = min(offset + max_len, mem_size)
    for i in range(offset, end):
        b = mem_data[i]
        if b == 0:
            break
        raw_bytes.append(b)

    return raw_bytes.decode('utf-8', errors='replace')

def parse_i32_array(store, memory, offset):
    """
    Layout:
      [ length : i32 ]
      [ elem1 : i32 ]
      [ elem2 : i32 ]
      ...
    """
    mem_data = memory.data_ptr(store)
    mem_size = memory.data_len(store)

    if offset < 0 or offset + 4 > mem_size:
        return ["<array length out-of-bounds>"]

    length_bytes = bytes(mem_data[offset:offset+4])
    length = struct.unpack("<i", length_bytes)[0]
    offset += 4

    elements = []
    for _ in range(length):
        if offset + 4 > mem_size:
            elements.append("<out-of-bounds>")
            break
        elem_bytes = bytes(mem_data[offset:offset+4])
        val = struct.unpack("<i", elem_bytes)[0]
        elements.append(val)
        offset += 4

    return elements

def parse_i64_array(store, memory, offset):
    """
    Layout:
      [ length : i32 ]
      [ elem1 : i64 ]
      [ elem2 : i64 ]
      ...
    """
    mem_data = memory.data_ptr(store)
    mem_size = memory.data_len(store)

    if offset < 0 or offset + 4 > mem_size:
        return ["<array length out-of-bounds>"]

    length_bytes = bytes(mem_data[offset:offset+4])
    length = struct.unpack("<i", length_bytes)[0]
    offset += 4

    elements = []
    for _ in range(length):
        if offset + 8 > mem_size:
            elements.append("<out-of-bounds>")
            break
        elem_bytes = bytes(mem_data[offset:offset+8])
        val = struct.unpack("<q", elem_bytes)[0]
        elements.append(val)
        offset += 8

    return elements

def parse_f32_array(store, memory, offset):
    """
    Layout:
      [ length : i32 ]
      [ elem1 : f32 ]
      [ elem2 : f32 ]
      ...
    """
    mem_data = memory.data_ptr(store)
    mem_size = memory.data_len(store)

    if offset < 0 or offset + 4 > mem_size:
        return ["<array length out-of-bounds>"]

    length_bytes = bytes(mem_data[offset:offset+4])
    length = struct.unpack("<i", length_bytes)[0]
    offset += 4

    elements = []
    for _ in range(length):
        if offset + 4 > mem_size:
            elements.append("<out-of-bounds>")
            break
        elem_bytes = bytes(mem_data[offset:offset+4])
        val = struct.unpack("<f", elem_bytes)[0]
        elements.append(val)
        offset += 4

    return elements

def parse_f64_array(store, memory, offset):
    """
    Layout:
      [ length : i32 ]
      [ elem1 : f64 ]
      [ elem2 : f64 ]
      ...
    """
    mem_data = memory.data_ptr(store)
    mem_size = memory.data_len(store)

    if offset < 0 or offset + 4 > mem_size:
        return ["<array length out-of-bounds>"]

    length_bytes = bytes(mem_data[offset:offset+4])
    length = struct.unpack("<i", length_bytes)[0]
    offset += 4

    elements = []
    for _ in range(length):
        if offset + 8 > mem_size:
            elements.append("<out-of-bounds>")
            break
        elem_bytes = bytes(mem_data[offset:offset+8])
        val = struct.unpack("<d", elem_bytes)[0]
        elements.append(val)
        offset += 8

    return elements

def parse_i32_string_array(store, memory, offset):
    """
    Layout for i32_string_array:
      [ length : i32 ]
      [ pointer1 : i32 ]
      [ pointer2 : i32 ]
      ...
    Each pointer references a null-terminated UTF-8 string.
    """
    mem_data = memory.data_ptr(store)
    mem_size = memory.data_len(store)

    if offset < 0 or offset + 4 > mem_size:
        return ["<array length out-of-bounds>"]

    length_bytes = bytes(mem_data[offset:offset+4])
    length = struct.unpack("<i", length_bytes)[0]
    offset += 4

    strings = []
    for _ in range(length):
        if offset + 4 > mem_size:
            strings.append("<out-of-bounds pointer>")
            break
        ptr_bytes = bytes(mem_data[offset:offset+4])
        ptr_val = struct.unpack("<i", ptr_bytes)[0]
        offset += 4

        text = read_utf8_string(store, memory, ptr_val)
        strings.append(text)

    return strings

def main():
    parser = argparse.ArgumentParser(
        description="Run a WebAssembly module with Wasmtime and call its '__top_level__' if 'main' not found."
    )
    parser.add_argument("wasm_file", help="Path to the .wasm file.")
    args = parser.parse_args()

    engine = wasmtime.Engine()
    store = wasmtime.Store(engine)
    module = wasmtime.Module.from_file(engine, args.wasm_file)

    linker = wasmtime.Linker(engine)

    # We'll assign memory after instantiation
    global memory_ref
    memory_ref = [None]

    # ========================
    #   Host print functions
    # ========================

    def host_print_i32(x):
        print(f"i32: {x}")

    def host_print_i64(x):
        print(f"i64: {x}")

    def host_print_f32(x):
        print(f"f32: {x}")

    def host_print_f64(x):
        print(f"f64: {x}")

    def host_print_string(ptr):
        mem = memory_ref[0]
        if mem is None:
            print(f"<no memory, pointer={ptr}>")
            return
        text = read_utf8_string(store, mem, ptr)
        print(f"string: {text}")

    def host_print_json(ptr):
        mem = memory_ref[0]
        if mem is None:
            print(f"<no memory, pointer={ptr}>")
            return
        text = read_utf8_string(store, mem, ptr)
        print(f"json: {text}")

    def host_print_i32_array(ptr):
        mem = memory_ref[0]
        if mem is None:
            print(f"<no memory, pointer={ptr}>")
            return
        elements = parse_i32_array(store, mem, ptr)
        print(f"array => {elements}")

    def host_print_i64_array(ptr):
        mem = memory_ref[0]
        if mem is None:
            print(f"<no memory, pointer={ptr}>")
            return
        elements = parse_i64_array(store, mem, ptr)
        print(f"array => {elements}")

    def host_print_f32_array(ptr):
        mem = memory_ref[0]
        if mem is None:
            print(f"<no memory, pointer={ptr}>")
            return
        elements = parse_f32_array(store, mem, ptr)
        print(f"array => {elements}")

    def host_print_f64_array(ptr):
        mem = memory_ref[0]
        if mem is None:
            print(f"<no memory, pointer={ptr}>")
            return
        elements = parse_f64_array(store, mem, ptr)
        print(f"array => {elements}")

    # *** NEW: print_string_array
    def host_print_string_array(ptr):
        mem = memory_ref[0]
        if mem is None:
            print(f"<no memory, pointer={ptr}>")
            return
        strings = parse_i32_string_array(store, mem, ptr)
        print(f"string array => {strings}")

    # ===============================
    #   Link the host functions
    # ===============================
    # We define a helper for easy i32 param => no return
    func_type_i32 = wasmtime.FuncType([wasmtime.ValType.i32()], [])
    func_type_i64 = wasmtime.FuncType([wasmtime.ValType.i64()], [])
    func_type_f32 = wasmtime.FuncType([wasmtime.ValType.f32()], [])
    func_type_f64 = wasmtime.FuncType([wasmtime.ValType.f64()], [])

    # numeric scalars
    linker.define(store, "env", "print_i32",  wasmtime.Func(store, func_type_i32, host_print_i32))
    linker.define(store, "env", "print_i64",  wasmtime.Func(store, func_type_i64, host_print_i64))
    linker.define(store, "env", "print_f32",  wasmtime.Func(store, func_type_f32, host_print_f32))
    linker.define(store, "env", "print_f64",  wasmtime.Func(store, func_type_f64, host_print_f64))

    # textual
    linker.define(store, "env", "print_string", wasmtime.Func(store, func_type_i32, host_print_string))
    linker.define(store, "env", "print_json",   wasmtime.Func(store, func_type_i32, host_print_json))

    # typed arrays
    linker.define(store, "env", "print_i32_array", wasmtime.Func(store, func_type_i32, host_print_i32_array))
    linker.define(store, "env", "print_i64_array", wasmtime.Func(store, func_type_i32, host_print_i64_array))
    linker.define(store, "env", "print_f32_array", wasmtime.Func(store, func_type_i32, host_print_f32_array))
    linker.define(store, "env", "print_f64_array", wasmtime.Func(store, func_type_i32, host_print_f64_array))

    # *** Link string array print
    linker.define(store, "env", "print_string_array",
                  wasmtime.Func(store, func_type_i32, host_print_string_array))

    # ================
    #  Instantiate
    # ================
    instance = linker.instantiate(store, module)

    # fetch memory
    mem_export = instance.exports(store).get("memory")
    if isinstance(mem_export, wasmtime.Memory):
        memory_ref[0] = mem_export

    # Attempt to call main or __top_level__
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
