# src/lmn/runtime/core/print/print_functions.py
import wasmtime
from lmn.runtime.host.memory_utils import (
    parse_f32_array, parse_f64_array, parse_i32_array, parse_i32_string_array,
    parse_i64_array, read_utf8_string
)


class PrintHostFunctions:
    def __init__(self, linker: wasmtime.Linker, store: wasmtime.Store, output_list: list, memory_ref=None):
        """
        Initializes the PrintHostFunctions with the necessary context and defines host functions.
        
        :param linker: The Wasmtime linker.
        :param store: The Wasmtime store.
        :param output_list: The list to capture output.
        :param memory_ref: Reference to memory, if applicable.
        """
        self.linker = linker
        self.store = store
        self.output_list = output_list
        self.memory_ref = memory_ref

        self.define_host_functions()

    # ------------------------------
    # 1) Numeric scalars
    # ------------------------------
    def host_print_i32(self, x):
        self.output_list.append(str(x))

    def host_print_i64(self, x):
        self.output_list.append(str(x))

    def host_print_f32(self, x):
        self.output_list.append(str(x))

    def host_print_f64(self, x):
        self.output_list.append(str(x))

    # ------------------------------
    # 2) Memory-based strings / JSON
    # ------------------------------
    def host_print_string(self, ptr):
        if not self.memory_ref or self.memory_ref[0] is None:
            self.output_list.append(f"<no memory> ptr={ptr}")
            return
        mem = self.memory_ref[0]
        s = read_utf8_string(self.store, mem, ptr)
        self.output_list.append(s)

    def host_print_json(self, ptr):
        if not self.memory_ref or self.memory_ref[0] is None:
            self.output_list.append(f"<no memory> ptr={ptr}")
            return
        mem = self.memory_ref[0]
        s = read_utf8_string(self.store, mem, ptr)
        self.output_list.append(s)

    # ------------------------------
    # 3) Typed arrays (numeric)
    # ------------------------------
    def host_print_i32_array(self, ptr):
        if not self.memory_ref or self.memory_ref[0] is None:
            self.output_list.append(f"<no memory> ptr={ptr}")
            return
        mem = self.memory_ref[0]
        elements = parse_i32_array(self.store, mem, ptr)
        self.output_list.append(str(elements))

    def host_print_i64_array(self, ptr):
        if not self.memory_ref or self.memory_ref[0] is None:
            self.output_list.append(f"<no memory> ptr={ptr}")
            return
        mem = self.memory_ref[0]
        elements = parse_i64_array(self.store, mem, ptr)
        self.output_list.append(str(elements))

    def host_print_f32_array(self, ptr):
        if not self.memory_ref or self.memory_ref[0] is None:
            self.output_list.append(f"<no memory> ptr={ptr}")
            return
        mem = self.memory_ref[0]
        elements = parse_f32_array(self.store, mem, ptr)
        self.output_list.append(str(elements))

    def host_print_f64_array(self, ptr):
        if not self.memory_ref or self.memory_ref[0] is None:
            self.output_list.append(f"<no memory> ptr={ptr}")
            return
        mem = self.memory_ref[0]
        elements = parse_f64_array(self.store, mem, ptr)
        self.output_list.append(str(elements))

    # ------------------------------
    # 4) String array (i32_string_array)
    # ------------------------------
    def host_print_string_array(self, ptr):
        if not self.memory_ref or self.memory_ref[0] is None:
            self.output_list.append(f"<no memory> ptr={ptr}")
            return
        mem = self.memory_ref[0]
        elements = parse_i32_string_array(self.store, mem, ptr)
        self.output_list.append(str(elements))

    def define_host_functions(self):
        """
        Defines and registers all host print functions with the Wasmtime linker.
        """
        # Define function types
        func_type_i32 = wasmtime.FuncType([wasmtime.ValType.i32()], [])
        func_type_i64 = wasmtime.FuncType([wasmtime.ValType.i64()], [])
        func_type_f32 = wasmtime.FuncType([wasmtime.ValType.f32()], [])
        func_type_f64 = wasmtime.FuncType([wasmtime.ValType.f64()], [])

        # 1) Scalar prints
        self.linker.define(
            self.store, "env", "print_i32",
            wasmtime.Func(self.store, func_type_i32, self.host_print_i32)
        )
        self.linker.define(
            self.store, "env", "print_i64",
            wasmtime.Func(self.store, func_type_i64, self.host_print_i64)
        )
        self.linker.define(
            self.store, "env", "print_f32",
            wasmtime.Func(self.store, func_type_f32, self.host_print_f32)
        )
        self.linker.define(
            self.store, "env", "print_f64",
            wasmtime.Func(self.store, func_type_f64, self.host_print_f64)
        )

        # 2) Memory-based prints
        self.linker.define(
            self.store, "env", "print_string",
            wasmtime.Func(self.store, func_type_i32, self.host_print_string)
        )
        self.linker.define(
            self.store, "env", "print_json",
            wasmtime.Func(self.store, func_type_i32, self.host_print_json)
        )

        # 3) Numeric arrays
        self.linker.define(
            self.store, "env", "print_i32_array",
            wasmtime.Func(self.store, func_type_i32, self.host_print_i32_array)
        )
        self.linker.define(
            self.store, "env", "print_i64_array",
            wasmtime.Func(self.store, func_type_i32, self.host_print_i64_array)
        )
        self.linker.define(
            self.store, "env", "print_f32_array",
            wasmtime.Func(self.store, func_type_i32, self.host_print_f32_array)
        )
        self.linker.define(
            self.store, "env", "print_f64_array",
            wasmtime.Func(self.store, func_type_i32, self.host_print_f64_array)
        )

        # 4) String array
        self.linker.define(
            self.store, "env", "print_string_array",
            wasmtime.Func(self.store, func_type_i32, self.host_print_string_array)
        )
