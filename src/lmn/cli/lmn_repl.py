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

# setup logging
logging.basicConfig(
    level=logging.CRITICAL,
    format="%(levelname)s - %(name)s - %(message)s"
)

def main():
    # setup colorama
    colorama.init(autoreset=True)

    # Print banner
    ascii_banner = get_ascii_banner()
    print(ascii_banner)
    print(f"LMN Language Playground  {Fore.WHITE}v0.9.0 (2024-12-01){Style.RESET_ALL}")
    print("Type \"?\" for help or \"quit\"/\"exit\" to leave.\n")

    # (1) A list of *all* snippets entered so far in this session
    accumulated_code = []

    # (2) A buffer for the current multi-line snippet
    code_buffer = []
    first_line = True

    while True:
        # setup the prompt
        prompt_text = "LMN> " if first_line else "... "
        prompt = f"{Fore.CYAN}{prompt_text}{Style.RESET_ALL}"

        try:
            # get the input
            line = input(prompt)
        except EOFError:
            # exiting
            print(f"\n{Fore.CYAN}Exiting LMN. Goodbye!{Style.RESET_ALL}")
            break

        # Check for Help command
        if line.strip() == "?":
            # show help
            show_help()
            continue

        # check for quit or exist
        if line.strip().lower() in ("quit", "exit"):
            # exit
            print(f"{Fore.CYAN}Exiting LMN. Goodbye!{Style.RESET_ALL}")
            break

        # check for clear
        if line.strip().lower() == "clear":
            # clear screen
            clear_screen()
            print(ascii_banner)
            print(f"LMN Language Playground  {Fore.WHITE}v0.9.0 (2024-12-01){Style.RESET_ALL}")
            print("Type \"?\" for help or \"quit\"/\"exit\" to leave.\n")
            
            # Reset entire session
            accumulated_code.clear()
            code_buffer.clear()
            print(f"{Fore.YELLOW}(Cleared screen and reset entire code session){Style.RESET_ALL}\n")
            first_line = True
            continue

        # If user presses Enter on an empty line => finalize the snippet
        if not line.strip():
            if code_buffer:
                # (a) Convert the snippet lines into a single string
                snippet = "\n".join(code_buffer)
                code_buffer.clear()

                # (b) Append to the entire session code
                accumulated_code.append(snippet)

                # (c) Recompile + run all code so far
                full_code = "\n\n".join(accumulated_code)
                outputs = compile_and_run(full_code)

                # (d) Print each captured line
                for out_line in outputs:
                    print(f"{Fore.CYAN}{out_line}{Style.RESET_ALL}")

            first_line = True
        else:
            code_buffer.append(line)
            first_line = False

def compile_and_run(code: str):
    """
    Compile + run the entire LMN session code in a fresh environment,
    capturing output lines via define_host_functions_capture_output.
    """
    output_lines = []

    # 1) Compile LMN => WAT => WASM
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

    # Host functions will append output to output_lines
    define_host_functions_capture_output(linker, store, output_lines)

    # 3) Instantiate
    try:
        module = wasmtime.Module(engine, wasm_bytes)
        instance = linker.instantiate(store, module)
    except Exception as e:
        return [f"Instantiation error: {e}"]

    # 4) Call __top_level__ if present
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
    print(" - 'clear' resets everything (including variables).")
    print(" - 'quit' or 'exit' ends this session.\n")

if __name__ == "__main__":
    main()
