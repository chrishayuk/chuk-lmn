# file: src/lmn/runtime/host_functions.py

import wasmtime

def define_host_functions_capture_output(linker: wasmtime.Linker, store: wasmtime.Store, output_list: list):
    """
    Defines LMN's host functions. Instead of printing, each function
    appends a string to 'output_list'. The caller handles whether or
    how to colorize or display this text.
    """
    def host_print_i32(x):
        output_list.append(f"i32 => {x}")

    def host_print_i64(x):
        output_list.append(f"i64 => {x}")

    def host_print_f64(x):
        output_list.append(f"f64 => {x}")

    def host_print_string(ptr):
        output_list.append(f"string at {ptr}")

    def host_print_json(ptr):
        output_list.append(f"json at {ptr}")

    def host_print_array(ptr):
        output_list.append(f"array at {ptr}")

    func_type_i32  = wasmtime.FuncType([wasmtime.ValType.i32()], [])
    func_type_i64  = wasmtime.FuncType([wasmtime.ValType.i64()], [])
    func_type_f64  = wasmtime.FuncType([wasmtime.ValType.f64()], [])
    func_type_i32p = wasmtime.FuncType([wasmtime.ValType.i32()], [])

    # Register each function
    linker.define(store, "env", "print_i32",    wasmtime.Func(store, func_type_i32,  host_print_i32))
    linker.define(store, "env", "print_i64",    wasmtime.Func(store, func_type_i64,  host_print_i64))
    linker.define(store, "env", "print_f64",    wasmtime.Func(store, func_type_f64,  host_print_f64))
    linker.define(store, "env", "print_string", wasmtime.Func(store, func_type_i32p, host_print_string))
    linker.define(store, "env", "print_json",   wasmtime.Func(store, func_type_i32p, host_print_json))
    linker.define(store, "env", "print_array",  wasmtime.Func(store, func_type_i32p, host_print_array))
