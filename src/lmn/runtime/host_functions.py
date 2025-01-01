# file: src/lmn/runtime/host_functions.py

import wasmtime
import struct

def read_utf8_string(store, memory, offset, max_len=200):
    """
    Reads a UTF-8 string from 'memory' starting at 'offset',
    stopping at a null byte or after max_len bytes.
    Returns the decoded Python string.
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

    return raw_bytes.decode("utf-8", errors="replace")

def parse_i32_array(store, memory, offset):
    """
    Parses an i32 array from memory starting at 'offset'.
    Format: <length:i32> <elem1:i32> <elem2:i32> ...
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
    Parses an i64 array from memory starting at 'offset'.
    Format: <length:i32> <elem1:i64> <elem2:i64> ...
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
    Parses an f32 array from memory starting at 'offset'.
    Format: <length:i32> <elem1:f32> <elem2:f32> ...
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
    Parses an f64 array from memory starting at 'offset'.
    Format: <length:i32> <elem1:f64> <elem2:f64> ...
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

def define_host_functions_capture_output(linker: wasmtime.Linker,
                                         store: wasmtime.Store,
                                         output_list: list,
                                         memory_ref=None):
    """
    Defines host functions that capture output into a provided list (e.g. for REPL).
    Instead of printing each sub-expression with a newline or prefix, we store
    them as raw strings or numbers so they can appear on the same line in the REPL.
    """

    # ------------------------------
    # 1) Numeric scalars
    # ------------------------------
    def host_print_i32(x):
        # Instead of: output_list.append(f"i32: {x}")
        # Use str(x) to preserve the numeric value without a newline
        output_list.append(str(x))

    def host_print_i64(x):
        output_list.append(str(x))

    def host_print_f32(x):
        output_list.append(str(x))

    def host_print_f64(x):
        output_list.append(str(x))

    # ------------------------------
    # 2) Memory-based strings / JSON
    # ------------------------------
    def host_print_string(ptr):
        if not memory_ref or memory_ref[0] is None:
            output_list.append(f"<no memory> ptr={ptr}")
            return
        mem = memory_ref[0]
        s = read_utf8_string(store, mem, ptr)
        # No prefix => store raw string
        output_list.append(s)

    def host_print_json(ptr):
        if not memory_ref or memory_ref[0] is None:
            output_list.append(f"<no memory> ptr={ptr}")
            return
        mem = memory_ref[0]
        s = read_utf8_string(store, mem, ptr)
        output_list.append(s)

    # ------------------------------
    # 3) Typed arrays (numeric)
    # ------------------------------
    def host_print_i32_array(ptr):
        if not memory_ref or memory_ref[0] is None:
            output_list.append(f"<no memory> ptr={ptr}")
            return
        mem = memory_ref[0]
        elements = parse_i32_array(store, mem, ptr)
        # Store as a Python list string: "[1, 2, 3]"
        output_list.append(str(elements))

    def host_print_i64_array(ptr):
        if not memory_ref or memory_ref[0] is None:
            output_list.append(f"<no memory> ptr={ptr}")
            return
        mem = memory_ref[0]
        elements = parse_i64_array(store, mem, ptr)
        output_list.append(str(elements))

    def host_print_f32_array(ptr):
        if not memory_ref or memory_ref[0] is None:
            output_list.append(f"<no memory> ptr={ptr}")
            return
        mem = memory_ref[0]
        elements = parse_f32_array(store, mem, ptr)
        output_list.append(str(elements))

    def host_print_f64_array(ptr):
        if not memory_ref or memory_ref[0] is None:
            output_list.append(f"<no memory> ptr={ptr}")
            return
        mem = memory_ref[0]
        elements = parse_f64_array(store, mem, ptr)
        output_list.append(str(elements))

    # ------------------------------
    # 4) String array (i32_string_array)
    # ------------------------------
    def host_print_string_array(ptr):
        if not memory_ref or memory_ref[0] is None:
            output_list.append(f"<no memory> ptr={ptr}")
            return
        mem = memory_ref[0]
        elements = parse_i32_string_array(store, mem, ptr)
        output_list.append(str(elements))

    # ===============================
    # Linker definitions
    # ===============================
    func_type_i32  = wasmtime.FuncType([wasmtime.ValType.i32()], [])
    func_type_i64  = wasmtime.FuncType([wasmtime.ValType.i64()], [])
    func_type_f32  = wasmtime.FuncType([wasmtime.ValType.f32()], [])
    func_type_f64  = wasmtime.FuncType([wasmtime.ValType.f64()], [])

    # 1) Scalar prints
    linker.define(store, "env", "print_i32",  wasmtime.Func(store, func_type_i32, host_print_i32))
    linker.define(store, "env", "print_i64",  wasmtime.Func(store, func_type_i64, host_print_i64))
    linker.define(store, "env", "print_f32",  wasmtime.Func(store, func_type_f32, host_print_f32))
    linker.define(store, "env", "print_f64",  wasmtime.Func(store, func_type_f64, host_print_f64))

    # 2) Memory-based prints
    linker.define(store, "env", "print_string",
                  wasmtime.Func(store, func_type_i32, host_print_string))
    linker.define(store, "env", "print_json",
                  wasmtime.Func(store, func_type_i32, host_print_json))

    # 3) Numeric arrays
    linker.define(store, "env", "print_i32_array",
                  wasmtime.Func(store, func_type_i32, host_print_i32_array))
    linker.define(store, "env", "print_i64_array",
                  wasmtime.Func(store, func_type_i32, host_print_i64_array))
    linker.define(store, "env", "print_f32_array",
                  wasmtime.Func(store, func_type_i32, host_print_f32_array))
    linker.define(store, "env", "print_f64_array",
                  wasmtime.Func(store, func_type_i32, host_print_f64_array))

    # 4) String array
    linker.define(store, "env", "print_string_array",
                  wasmtime.Func(store, func_type_i32, host_print_string_array))
