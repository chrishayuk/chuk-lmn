#!/usr/bin/env python3
# file: src/lmn/cli/lmn_repl.py
import sys
import os
import logging
import wasmtime

# pipeline
from lmn.compiler.pipeline import compile_code_to_wat

# For colored output
import colorama
from colorama import Fore, Style

# setup logging
logging.basicConfig(
    level=logging.CRITICAL,
    format="%(levelname)s - %(name)s - %(message)s"
)

def main():
    # Initialize colorama for cross-platform color support
    colorama.init(autoreset=True)

    # (A) ASCII Banner for LMN (L M N side by side)
    ascii_banner = f"""{Fore.GREEN}
oo______ooo_____ooo_ooo____oo_
oo______oooo___oooo_oooo___oo_
oo______oo_oo_oo_oo_oo_oo__oo_
oo______oo__ooo__oo_oo__oo_oo_
oo______oo_______oo_oo___oooo_
ooooooo_oo_______oo_oo____ooo_
______________________________
{Style.RESET_ALL}
"""

    # Print the ASCII banner + minimal version/info
    print(ascii_banner)
    print(f"LMN Language Playground  {Fore.WHITE}v0.9.0 (2024-12-01){Style.RESET_ALL}")
    print(f"Type \"?\" for help or \"quit\"/\"exit\" to leave.\n")

    code_buffer = []
    first_line = True  # controls the prompt style

    while True:
        # Decide which prompt text
        prompt_text = "LMN> " if first_line else "... "
        # Add color
        prompt = f"{Fore.CYAN}{prompt_text}{Style.RESET_ALL}"

        try:
            line = input(prompt)
        except EOFError:
            print(f"\n{Fore.CYAN}Exiting LMN. Goodbye!{Style.RESET_ALL}")
            break

        # If user typed "?" => show help
        if line.strip() == "?":
            show_help()
            continue

        # If user typed 'quit' or 'exit' alone
        if line.strip().lower() in ("quit", "exit"):
            print(f"{Fore.CYAN}Exiting LMN. Goodbye!{Style.RESET_ALL}")
            break

        # If line is empty => compile + run the block
        if not line.strip():
            if code_buffer:
                full_code = "\n".join(code_buffer)
                code_buffer.clear()
                run_block(full_code)
            # else: user pressed Enter on empty buffer => do nothing
            first_line = True
        else:
            # Accumulate line
            code_buffer.append(line)
            first_line = False

def run_block(code):
    """
    Compiles and runs a block of LMN code in a fresh environment.
    """
    try:
        wat_text, wasm_bytes = compile_code_to_wat(
            code,
            also_produce_wasm=True,
            import_memory=False  # or True if you have shared memory approach
        )
    except Exception as e:
        print(f"{Fore.RED}Compilation error: {e}{Style.RESET_ALL}")
        return

    if not wasm_bytes:
        print(f"{Fore.RED}No WASM produced (wat2wasm missing?).{Style.RESET_ALL}")
        return

    # Create a Wasmtime engine/store/linker
    engine = wasmtime.Engine()
    store = wasmtime.Store(engine)
    linker = wasmtime.Linker(engine)

    define_colored_host_functions(linker, store)

    try:
        module = wasmtime.Module(engine, wasm_bytes)
        instance = linker.instantiate(store, module)
    except Exception as e:
        print(f"{Fore.RED}Instantiation error: {e}{Style.RESET_ALL}")
        return

    # If there's a __top_level__ function => call it
    exports = instance.exports(store)
    top_func = exports.get("__top_level__")
    if top_func:
        top_func(store)

def define_colored_host_functions(linker, store):
    """
    Host functions that print with color, e.g.:
      => 123
      => string at 1024
    """
    def host_print_i32(x):
        print(f"{Fore.YELLOW}=> {x}{Style.RESET_ALL}")

    def host_print_i64(x):
        print(f"{Fore.YELLOW}=> {x}{Style.RESET_ALL}")

    def host_print_f64(x):
        print(f"{Fore.YELLOW}=> {x}{Style.RESET_ALL}")

    def host_print_string(ptr):
        print(f"{Fore.MAGENTA}=> string at {ptr}{Style.RESET_ALL}")

    def host_print_json(ptr):
        print(f"{Fore.MAGENTA}=> json at {ptr}{Style.RESET_ALL}")

    def host_print_array(ptr):
        print(f"{Fore.MAGENTA}=> array at {ptr}{Style.RESET_ALL}")

    func_type_i32 = wasmtime.FuncType([wasmtime.ValType.i32()], [])
    func_type_i64 = wasmtime.FuncType([wasmtime.ValType.i64()], [])
    func_type_f64 = wasmtime.FuncType([wasmtime.ValType.f64()], [])
    func_type_i32p = wasmtime.FuncType([wasmtime.ValType.i32()], [])

    linker.define(store, "env", "print_i32",  wasmtime.Func(store, func_type_i32,  host_print_i32))
    linker.define(store, "env", "print_i64",  wasmtime.Func(store, func_type_i64,  host_print_i64))
    linker.define(store, "env", "print_f64",  wasmtime.Func(store, func_type_f64,  host_print_f64))
    linker.define(store, "env", "print_string", wasmtime.Func(store, func_type_i32p, host_print_string))
    linker.define(store, "env", "print_json",   wasmtime.Func(store, func_type_i32p, host_print_json))
    linker.define(store, "env", "print_array",  wasmtime.Func(store, func_type_i32p, host_print_array))

def show_help():
    print(f"{Fore.GREEN}\nLMN Playground Help{Style.RESET_ALL}")
    print(" - Type multi-line code, then press Enter on an empty line to run.")
    print(" - 'quit' or 'exit' ends this session.")
    print(" - No persistent memory or variables by default.\n")

if __name__ == "__main__":
    main()
