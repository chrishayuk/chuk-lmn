#!/usr/bin/env python3
# file: src/lmn/cli/lmn_repl.py
import os
import logging
import colorama
from colorama import Fore, Style

# lmn modules
from lmn.cli.utils.banner import get_ascii_banner
from lmn.runtime.wasm_runner import run_wasm, create_environment

# setup logging
logging.basicConfig(
    level=logging.CRITICAL,
    format="%(levelname)s - %(name)s - %(message)s"
)

# Initialize environment at the start of the REPL session
env = create_environment()

def main():
    # setup colorama
    colorama.init(autoreset=True)

    # setup the ascii banner
    ascii_banner = get_ascii_banner()
    print(ascii_banner)
    print(f"LMN Language Playground  {Fore.WHITE}v0.0.1 (2024-12-30){Style.RESET_ALL}")
    print("Type \"?\" for help or \"quit\"/\"exit\" to leave.\n")

    # All snippets from this session
    accumulated_code = []
    code_buffer = []
    first_line = True

    # loop
    while True:
        # show the prompt
        prompt_text = "LMN> " if first_line else "... "
        prompt = f"{Fore.CYAN}{prompt_text}{Style.RESET_ALL}"

        try:
            # get the input
            line = input(prompt)
        except EOFError:
            print(f"\n{Fore.CYAN}Exiting LMN. Goodbye!{Style.RESET_ALL}")
            break

        # Check commands
        if line.strip() == "?":
            # show help
            show_help()
            continue

        if line.strip().lower() in ("quit", "exit"):
            # quit
            print(f"{Fore.CYAN}Exiting LMN. Goodbye!{Style.RESET_ALL}")
            break

        if line.strip().lower() == "clear":
            # clear screen
            clear_screen()

            # reshow ascii banner
            print(ascii_banner)
            print(f"LMN Language Playground  {Fore.WHITE}v0.9.0 (2024-12-01){Style.RESET_ALL}")
            print("Type \"?\" for help or \"quit\"/\"exit\" to leave.\n")

            # clear the buffer
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
    return run_wasm(code, env=env)

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
