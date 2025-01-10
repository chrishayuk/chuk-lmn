#!/usr/bin/env python3
# src/lmn/cli/typechecker.py
import sys
import os
import json
import argparse
import logging

# Import necessary modules
from lmn.compiler.ast.program import Program
from lmn.compiler.typechecker.ast_type_checker import type_check_program
from lmn.compiler.typechecker.program_checker import ProgramChecker

# Basic config for logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s - %(name)s - %(message)s")

def main():
    # setup the parser
    parser = argparse.ArgumentParser(description="Type-check an LMN AST.")

    # input file
    parser.add_argument("input", help="Path to the input JSON AST file.")

    # output file (optional)
    parser.add_argument("--output", help="Path to write the updated JSON after type-check.")

    # parse arguments
    args = parser.parse_args()

    # 1) Locate input file
    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        print(f"Error: {args.input} not found")
        sys.exit(1)

    # 2) Load JSON
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading/parsing JSON: {e}")
        sys.exit(1)

    # 3) Validate the "raw" JSON structure with ProgramChecker
    program_checker = ProgramChecker()
    try:
        # validate the program structure
        program_checker.validate_program(data)
    except Exception as e:
        print(f"Program structure error: {e}")
        sys.exit(1)

    # 4) Parse as Program (if the JSON structure is valid)
    try:
        # validate the program
        program_node = Program.model_validate(data)
    except Exception as e:
        # error parsing the JSON into a Program node
        print(f"Error parsing JSON into Program: {e}")
        sys.exit(1)

    # 5) Type check the fully parsed Program node
    try:
        type_check_program(program_node)
    except Exception as e:
        print(f"Type error: {e}")
        sys.exit(1)

    print("No type errors found.")

    # 6) If output is specified, write the (possibly annotated) AST
    if args.output:
        output_path = os.path.abspath(args.output)
        with open(output_path, "w", encoding="utf-8") as out_f:
            out_f.write(program_node.to_json())  # or model_dump_json()
        print(f"Annotated AST saved to {output_path}")

if __name__ == "__main__":
    main()
