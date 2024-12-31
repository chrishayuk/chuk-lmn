# file: src/lmn/runtime/host_functions.py

import wasmtime

def read_utf8_string(store, memory, offset, max_len=200):
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

def define_host_functions_capture_output(linker: wasmtime.Linker,
                                         store: wasmtime.Store,
                                         output_list: list,
                                         memory_ref=None):
    """
    :param memory_ref: optional [None] if we want to read from memory after instantiation.
                       If memory_ref[0] is set to a wasmtime.Memory after instantiation,
                       we can read actual strings. Otherwise, we just show ptr=xxx.
    """
    def host_print_i32(x):
        output_list.append(f"i32 => {x}")

    def host_print_i64(x):
        output_list.append(f"i64 => {x}")

    def host_print_f64(x):
        output_list.append(f"f64 => {x}")

    def host_print_string(ptr):
        if not memory_ref or memory_ref[0] is None:
            # we only know the pointer
            output_list.append(f"string ptr={ptr}")
            return
        mem = memory_ref[0]
        s = read_utf8_string(store, mem, ptr)
        output_list.append(f"string => {s}")

    def host_print_json(ptr):
        if not memory_ref or memory_ref[0] is None:
            output_list.append(f"json ptr={ptr}")
            return
        mem = memory_ref[0]
        s = read_utf8_string(store, mem, ptr)
        output_list.append(f"json => {s}")

    def host_print_array(ptr):
        if not memory_ref or memory_ref[0] is None:
            output_list.append(f"array ptr={ptr}")
            return
        mem = memory_ref[0]
        s = read_utf8_string(store, mem, ptr)
        output_list.append(f"array => {s}")

    func_type_i32  = wasmtime.FuncType([wasmtime.ValType.i32()], [])
    func_type_i64  = wasmtime.FuncType([wasmtime.ValType.i64()], [])
    func_type_f64  = wasmtime.FuncType([wasmtime.ValType.f64()], [])
    func_type_i32p = wasmtime.FuncType([wasmtime.ValType.i32()], [])

    linker.define(store, "env", "print_i32",
                  wasmtime.Func(store, func_type_i32, host_print_i32))
    linker.define(store, "env", "print_i64",
                  wasmtime.Func(store, func_type_i64, host_print_i64))
    linker.define(store, "env", "print_f64",
                  wasmtime.Func(store, func_type_f64, host_print_f64))

    linker.define(store, "env", "print_string",
                  wasmtime.Func(store, func_type_i32p, host_print_string))
    linker.define(store, "env", "print_json",
                  wasmtime.Func(store, func_type_i32p, host_print_json))
    linker.define(store, "env", "print_array",
                  wasmtime.Func(store, func_type_i32p, host_print_array))
