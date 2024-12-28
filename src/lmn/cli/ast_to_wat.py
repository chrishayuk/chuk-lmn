#!/usr/bin/env python3
import logging
import os
import json
import sys
import argparse
from lmn.compiler.emitter.wasm.wasm_emitter import WasmEmitter

# Basic config for logging
logging.basicConfig(
    level=logging.CRITICAL,
    format="%(levelname)s - %(name)s - %(message)s")

def main():
    # Setup argument parser
    parser = argparse.ArgumentParser(description="Convert AST JSON to WAT format.")

    # set the input file
    parser.add_argument(
        "input",
        help="Path to the input AST JSON file (checked in CWD first, then script directory)."
    )

    # set the output file
    parser.add_argument(
        "--output",
        help="Path to the output WAT file. Overwrites if exists. If omitted, prints WAT to stdout."
    )

    # Parse arguments
    args = parser.parse_args()

    # 1) Locate input file: current directory first, then script's directory
    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        fallback_path = os.path.join(script_dir, args.input)
        if os.path.exists(fallback_path):
            input_path = fallback_path
        else:
            print(f"Error: File not found: {args.input} (checked CWD and script directory)")
            sys.exit(1)

    # 2) Load JSON AST
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            ast = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {input_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON file: {e}")
        sys.exit(1)

    # 3) Generate WAT
    emitter = WasmEmitter()
    wasm_text = emitter.emit_program(ast)

    # 4) Output
    if args.output:
        # Interpret --output as the *exact file path*
        output_path = os.path.abspath(args.output)

        # Create all directories needed (excluding the final file component)
        output_dir = os.path.dirname(output_path)
        if output_dir:  # In case user just gave a filename with no directories
            os.makedirs(output_dir, exist_ok=True)

        # Write (overwrite) the file
        try:
            with open(output_path, "w", encoding="utf-8") as out_file:
                out_file.write(wasm_text)
            print(f"WAT file successfully written to {output_path}")
        except OSError as e:
            print(f"Error writing to {output_path}: {e}")
            sys.exit(1)
    else:
        # Print to stdout
        print(wasm_text)

if __name__ == "__main__":
    main()
