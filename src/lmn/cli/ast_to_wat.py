#!/usr/bin/env python3
import os
import json
import sys
import argparse
from lmn.compiler.emitter.wasm.wasm_emitter import WasmEmitter

def main():
    # Setup argument parser
    parser = argparse.ArgumentParser(description="Convert AST JSON to WAT format.")
    parser.add_argument("input", help="Path to the input AST JSON file.")
    parser.add_argument("--output", help="Directory to save the output WAT file. If not specified, output will be printed to the screen.")

    # Parse arguments
    args = parser.parse_args()

    # Input path
    # Resolve the file path relative to this script’s directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(script_dir, args.input)

    # Determine if output is specified
    output_dir = args.output

    try:
        # Load the AST from JSON
        with open(json_file, 'r', encoding='utf-8') as f:
            ast = json.load(f)

        # Instantiate WasmEmitter
        emitter = WasmEmitter()

        # Emit the WASM module as text
        wasm_text = emitter.emit_program(ast)

        if output_dir:
            # Ensure the output directory exists
            os.makedirs(output_dir, exist_ok=True)

            # Determine the output file name
            input_filename = os.path.basename(json_file)
            base_name = os.path.splitext(input_filename)[0].rstrip("_ast")
            output_filename = base_name + ".wat"
            output_file_path = os.path.join(output_dir, output_filename)

            # Write the output to the specified file
            with open(output_file_path, 'w', encoding='utf-8') as out_file:
                out_file.write(wasm_text)

            print(f"WAT file successfully written to {output_file_path}")
        else:
            # Print the output to the screen
            print(wasm_text)

    except FileNotFoundError:
        print(f"Error: File not found: {json_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()