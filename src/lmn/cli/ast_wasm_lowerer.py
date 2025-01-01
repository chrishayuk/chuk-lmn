#!/usr/bin/env python3
# src/lmn/cli/ast_wasm_lowerer.py
import sys
import os
import json
import argparse
import logging

from lmn.compiler.ast.program import Program
from lmn.compiler.typechecker.ast_type_checker import type_check_program
from lmn.compiler.typechecker.program_checker import ProgramChecker

# Suppose you create a "lowering" utility module:
from lmn.compiler.lowering.wasm_lowerer import lower_program_to_wasm_types

# Basic config for logging
logging.basicConfig(
    level=logging.CRITICAL,
    format="%(levelname)s - %(name)s - %(message)s"
)

def main():
    # 1) Argument parsing
    parser = argparse.ArgumentParser(description="Lower an LMN AST to WASM-level types.")

    parser.add_argument("input", help="Path to the input JSON AST file.")
    parser.add_argument("--output", help="Path to write the lowered JSON AST.")
    args = parser.parse_args()

    # 2) Load the input JSON
    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        print(f"Error: {args.input} not found")
        sys.exit(1)

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading/parsing JSON: {e}")
        sys.exit(1)

    # 3) Validate the raw JSON structure
    program_checker = ProgramChecker()
    try:
        program_checker.validate_program(data)
    except Exception as e:
        print(f"Program structure error: {e}")
        sys.exit(1)

    # 4) Parse into a Program node
    try:
        program_node = Program.model_validate(data)
    except Exception as e:
        print(f"Error parsing JSON into Program node: {e}")
        sys.exit(1)

    # 5) Type check the Program
    try:
        type_check_program(program_node)
    except Exception as e:
        print(f"Type error: {e}")
        sys.exit(1)

    print("No type errors found. Proceeding to lower to WASM types...")

    # 6) Perform the lowering pass
    try:
        lower_program_to_wasm_types(program_node)
    except Exception as e:
        print(f"Error during WASM type lowering: {e}")
        sys.exit(1)

    print("AST successfully lowered to WASM-level types.")

    # 7) If requested, write out the lowered AST
    if args.output:
        # get the absolute path of the output file
        output_path = os.path.abspath(args.output)
        
        # Pydantic v2 supports `model_dump_json` with an `indent` argument:
        json_str = program_node.model_dump_json(indent=2)
        with open(output_path, "w", encoding="utf-8") as out_f:
            out_f.write(json_str)
        print(f"Lowered AST saved to {output_path}")


if __name__ == "__main__":
    main()
