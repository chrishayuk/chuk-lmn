#!/usr/bin/env python3
import wasmtime
import ctypes

# Use your host functions snippet (capture_output) so LMN's print i32/string/json, etc. works:
from lmn.runtime.host_functions import define_host_functions_capture_output
# The compiler pipeline:
from lmn.compiler.pipeline import compile_code_to_wat

def main():
    engine = wasmtime.Engine()
    store = wasmtime.Store(engine)
    linker = wasmtime.Linker(engine)

    output_lines = []
    memory_ref = [None]  # We'll fill this with the actual memory after instantiation

    # 1) Register the usual print_i32, print_string, etc. from your host_functions code
    define_host_functions_capture_output(linker, store, output_lines, memory_ref)

    # 2) LMN snippet: a single top-level definition + print, with **no** LMN functions
    #    Because we're using `import_memory=False`, the compiler will embed
    #    "Hello from LMN" in LMN's own memory. We can then patch it from Python.
    lmn_source = r'''
    let mystr = "Hello from LMN"
    print mystr
    '''

    # 3) Compile with import_memory=False => LMN defines + exports its own memory
    try:
        wat_text, wasm_bytes = compile_code_to_wat(
            lmn_source,
            also_produce_wasm=True,
            import_memory=False
        )
    except Exception as e:
        print(f"Compilation error: {e}")
        return

    if not wasm_bytes:
        print("No WASM produced. (Check wat2wasm installation?)")
        return

    # 4) Instantiate. The module should define + export memory that has our literal.
    try:
        module = wasmtime.Module(engine, wasm_bytes)
        instance = linker.instantiate(store, module)
    except Exception as e:
        print(f"Instantiation error: {e}")
        return

    # 5) If the module exports a memory, store it in memory_ref[0] so host_print_string can decode strings
    mem = instance.exports(store).get("memory")
    if mem is not None:
        memory_ref[0] = mem

    # 6) If there's a __top_level__ function, call it => runs the snippet (prints "Hello from LMN")
    exports = instance.exports(store)
    top_func = exports.get("__top_level__")
    if top_func:
        top_func(store)

    # Show what LMN printed
    print("\n=== FIRST PRINT ===")
    for line in output_lines:
        print(line)

    # Now we want to *patch* "Hello from LMN" in memory => "CHANGED from Python!"
    if mem is None:
        print("\nNo exported memory found. Can't patch.")
        return

    # Clear the output for clarity (though we won't re-run LMN code)
    output_lines.clear()

    # 7) Locate the literal in memory
    offset = find_string_in_memory(store, mem, "Hello from LMN")
    if offset < 0:
        print("\nCould not find 'Hello from LMN' in memory. No patch performed.")
    else:
        patch_string_in_memory(store, mem, offset, "CHANGED from Python!")
        print(f"\nPatched memory at offset={offset} with 'CHANGED from Python!'")

        # Let's confirm by reading memory directly:
        changed_text = read_string_at_offset(store, mem, offset, 50)
        print(f"Memory now holds: {changed_text}")

    print("\n=== DONE ===")

def find_string_in_memory(store: wasmtime.Store, memory: wasmtime.Memory,
                          target: str, max_search=65536) -> int:
    """
    Searches the first 'max_search' bytes of 'memory' for `target`.
    Returns the offset or -1 if not found.
    """
    data_ptr = memory.data_ptr(store)
    base_addr = ctypes.cast(data_ptr, ctypes.c_void_p).value  # integer address

    mem_len = min(memory.data_len(store), max_search)
    raw_data = (ctypes.c_char * mem_len).from_address(base_addr)
    mem_slice = bytes(raw_data)

    needle = target.encode('utf-8')
    idx = mem_slice.find(needle)
    return idx  # -1 if not found

def patch_string_in_memory(store: wasmtime.Store, memory: wasmtime.Memory,
                           offset: int, new_text: str):
    """
    Overwrites 'new_text\0' at 'offset' in memory.
    """
    data_ptr = memory.data_ptr(store)
    base_addr = ctypes.cast(data_ptr, ctypes.c_void_p).value

    text_bytes = new_text.encode('utf-8')
    for i, b in enumerate(text_bytes):
        ctypes.c_char.from_address(base_addr + offset + i).value = bytes([b])
    # null-terminate
    ctypes.c_char.from_address(base_addr + offset + len(text_bytes)).value = b'\0'

def read_string_at_offset(store: wasmtime.Store, memory: wasmtime.Memory,
                          offset: int, max_len=200) -> str:
    """
    Reads a UTF-8 string from 'memory' at 'offset', up to max_len or a '\0'.
    """
    data_ptr = memory.data_ptr(store)
    base_addr = ctypes.cast(data_ptr, ctypes.c_void_p).value

    mem_size = memory.data_len(store)
    if offset < 0 or offset >= mem_size:
        return "<invalid pointer>"

    raw_bytes = bytearray()
    end = min(offset + max_len, mem_size)
    for i in range(offset, end):
        b = ctypes.c_char.from_address(base_addr + i).value[0]
        if b == 0:
            break
        raw_bytes.append(b)
    return raw_bytes.decode("utf-8", errors="replace")

if __name__ == "__main__":
    main()
