#!/usr/bin/env python3
# file: src/lmn/cli/lmn_compiler.py
import argparse
import logging
import sys
import os

# Make sure this import pulls in your updated 4-step pipeline code:
from lmn.compiler.pipeline import compile_code_to_wat

logging.basicConfig(
    level=logging.CRITICAL,
    format="%(levelname)s - %(name)s - %(message)s"
)

DEFAULT_SNIPPET = r"""
function fact(n)
  if n <= 1
    return 1
  else
    return n * fact(n - 1)
  end
end

function main()
  print "Factorial of 5 is "
  print fact(5)
  return 0
end
"""

def main():
    parser = argparse.ArgumentParser(
        description="Compile LMN code from source to .wat and/or .wasm using the 4-step pipeline."
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="Path to an LMN source file. If omitted, uses a default snippet."
    )
    parser.add_argument(
        "--wat",
        help="Path to write the .wat file. If omitted, prints WAT to stdout unless --wasm is given."
    )
    parser.add_argument(
        "--wasm",
        help="Path to write the .wasm file. If omitted, no .wasm is produced."
    )
    args = parser.parse_args()

    # 1) Gather LMN source
    if args.file:
        file_path = os.path.abspath(args.file)
        if not os.path.exists(file_path):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            alt_path = os.path.join(script_dir, args.file)
            if not os.path.exists(alt_path):
                print(f"Error: file '{args.file}' not found.")
                sys.exit(1)
            file_path = alt_path
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
        except OSError as e:
            print(f"Error reading file '{file_path}': {e}")
            sys.exit(1)
    else:
        code = DEFAULT_SNIPPET

    # 2) Decide if we want WASM bytes
    also_produce_wasm = bool(args.wasm)

    # 3) Compile code using the updated pipeline
    try:
        wat_text, wasm_bytes = compile_code_to_wat(code, also_produce_wasm=also_produce_wasm)
    except Exception as e:
        print(f"Compilation error: {e}")
        sys.exit(1)

    # 4) Output WAT
    if args.wat:
        wat_path = os.path.abspath(args.wat)
        try:
            with open(wat_path, "w", encoding="utf-8") as f_wat:
                f_wat.write(wat_text)
            print(f"Wrote WAT to '{wat_path}'")
        except OSError as e:
            print(f"Error writing .wat file: {e}")
            sys.exit(1)
    else:
        # If no .wat and no .wasm requested, just print WAT
        if not args.wasm:
            print(wat_text)

    # 5) Output WASM
    if args.wasm:
        if not wasm_bytes:
            print("Error: 'wasm_bytes' is None. Possibly wat2wasm wasn't found?")
            sys.exit(1)
        wasm_path = os.path.abspath(args.wasm)
        try:
            with open(wasm_path, "wb") as f_wasm:
                f_wasm.write(wasm_bytes)
            print(f"Wrote WASM to '{wasm_path}'")
        except OSError as e:
            print(f"Error writing .wasm file: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
