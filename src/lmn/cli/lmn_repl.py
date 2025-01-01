#!/usr/bin/env python3
# file: src/lmn/cli/lmn_repl.py

import os
import logging
import colorama
import wasmtime
from colorama import Fore, Style

# lmn modules
from lmn.cli.utils.banner import get_ascii_banner
from lmn.compiler.pipeline import compile_code_to_wat
from lmn.runtime.host_functions import define_host_functions_capture_output

logging.basicConfig(
    level=logging.CRITICAL,
    format="%(levelname)s - %(name)s - %(message)s"
)

def main():
    colorama.init(autoreset=True)

    ascii_banner = get_ascii_banner()
    print(ascii_banner)
    print(f"LMN Language Playground  {Fore.WHITE}v0.0.1 (2024-12-30){Style.RESET_ALL}")
    print("Type \"?\" for help or \"quit\"/\"exit\" to leave.\n")

    # All snippets from this session
    accumulated_code = []
    # Current snippet lines
    code_buffer = []
    first_line = True

    while True:
        prompt_text = "LMN> " if first_line else "... "
        prompt = f"{Fore.CYAN}{prompt_text}{Style.RESET_ALL}"

        try:
            line = input(prompt)
        except EOFError:
            print(f"\n{Fore.CYAN}Exiting LMN. Goodbye!{Style.RESET_ALL}")
            break

        # Check commands
        if line.strip() == "?":
            show_help()
            continue

        if line.strip().lower() in ("quit", "exit"):
            print(f"{Fore.CYAN}Exiting LMN. Goodbye!{Style.RESET_ALL}")
            break

        if line.strip().lower() == "clear":
            clear_screen()
            print(ascii_banner)
            print(f"LMN Language Playground  {Fore.WHITE}v0.9.0 (2024-12-01){Style.RESET_ALL}")
            print("Type \"?\" for help or \"quit\"/\"exit\" to leave.\n")
            accumulated_code.clear()
            code_buffer.clear()
            print(f"{Fore.YELLOW}(Cleared screen and reset entire code session){Style.RESET_ALL}\n")
            first_line = True
            continue

        # If user presses Enter on an empty line => finalize snippet
        if not line.strip():
            if code_buffer:
                snippet = "\n".join(code_buffer)
                code_buffer.clear()

                # Accumulate + run everything
                accumulated_code.append(snippet)
                full_code = "\n\n".join(accumulated_code)

                outputs = compile_and_run(full_code)

                # ------------------------------------------------
                # NEW LOGIC: Join the outputs on one line
                # ------------------------------------------------
                cleaned = [item.strip() for item in outputs if item.strip()]
                single_line = " ".join(cleaned).strip()

                # Optional: filter out trailing "0" if you don't want function return
                if single_line.endswith(" 0"):
                    single_line = single_line[:-2].strip()

                if single_line:
                    print(f"{Fore.CYAN}{single_line}{Style.RESET_ALL}")

            first_line = True
        else:
            code_buffer.append(line)
            first_line = False


def compile_and_run(code: str):
    """
    Compile + run the entire LMN session code in a fresh environment,
    capturing output lines via define_host_functions_capture_output,
    and properly setting memory_ref so string pointers can be read.
    """

    output_lines = []

    # 1) Compile
    try:
        wat_text, wasm_bytes = compile_code_to_wat(
            code,
            also_produce_wasm=True,
            import_memory=False
        )
    except Exception as e:
        return [f"Compilation error: {e}"]

    if not wasm_bytes:
        return ["No WASM produced (wat2wasm missing?)."]

    # 2) Fresh Wasmtime environment
    engine = wasmtime.Engine()
    store = wasmtime.Store(engine)
    linker = wasmtime.Linker(engine)

    # The memory reference we'll set after instantiation
    memory_ref = [None]

    # 3) Define host functions with memory_ref
    define_host_functions_capture_output(linker, store, output_lines, memory_ref=memory_ref)

    # 4) Instantiate
    try:
        module = wasmtime.Module(engine, wasm_bytes)
        instance = linker.instantiate(store, module)
    except Exception as e:
        return [f"Instantiation error: {e}"]

    # 5) Attach the memory export
    mem = instance.exports(store).get("memory")
    if mem is not None:
        memory_ref[0] = mem

    # 6) Call __top_level__ if present
    exports = instance.exports(store)
    top_func = exports.get("__top_level__")
    if top_func:
        top_func(store)

    return output_lines

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_help():
    print(f"{Fore.GREEN}\nLMN Playground Help (Accumulate & Recompile){Style.RESET_ALL}")
    print(" - Type multi-line code, then press Enter on an empty line to run.")
    print(" - We recompile the entire session each time, so variables persist across snippets.")
    print(" - If you define strings, you can see them as raw text in the output.")
    print(" - 'clear' resets everything (including variables).")
    print(" - 'quit' or 'exit' ends this session.\n")

if __name__ == "__main__":
    main()
