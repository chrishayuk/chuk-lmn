#!/usr/bin/env python3
# parser_cli.py

import argparse
import sys
import os

from lmn.compiler.lexer.tokenizer import Tokenizer
from lmn.compiler.parser.parser import Parser

def main():
    # Create an argument parser
    parser = argparse.ArgumentParser(
        description="Parse LMN code and print (or write) the resulting AST (in JSON)."
    )
    
    # add the input file argument
    parser.add_argument(
        "file",
        nargs="?",
        help="Path to an LMN source file. If omitted, uses a default code snippet."
    )

    # add the output file argument
    parser.add_argument(
        "-o", "--output",
        help="Specify an output file for the JSON AST. If omitted, prints to stdout."
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    # -- 1. Handle input (file or default snippet)
    if args.file:
        # Attempt 1: interpret file path relative to current working directory
        potential_path = os.path.abspath(args.file)
        
        if not os.path.exists(potential_path):
            # Attempt 2: interpret file path relative to this script’s directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            potential_path = os.path.join(script_dir, args.file)
            
            if not os.path.exists(potential_path):
                print(f"Error: File '{args.file}' not found in current directory or script directory.")
                sys.exit(1)

        # If we get here, potential_path should be valid
        try:
            with open(potential_path, "r", encoding="utf-8") as f:
                code = f.read()
        except OSError as e:
            print(f"Error reading file '{potential_path}': {e}")
            sys.exit(1)

    else:
        # Default LMN code snippet if no file is provided
        code = r"""
// A simple factorial function for demonstration
function fact(n)
  if (n <= 1)
    return 1
  else
    return n * fact(n - 1)
  end
end
"""

    # -- 2. Tokenize
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()

    # -- 3. Parse
    parser_obj = Parser(tokens)
    ast_program = parser_obj.parse()

    # -- 4. Get AST as JSON
    ast_json = ast_program.to_json()  # Ensure `.to_json()` exists in your AST implementation

    # -- 5. Output: file or stdout
    if args.output:
        # The output path is interpreted relative to the current working directory by default.
        output_path = args.output
        try:
            with open(output_path, "w", encoding="utf-8") as out_file:
                out_file.write(ast_json)
            print(f"AST written to '{output_path}'")
        except OSError as e:
            print(f"Error writing to '{output_path}': {e}")
            sys.exit(1)
    else:
        print(ast_json)

if __name__ == "__main__":
    main()
