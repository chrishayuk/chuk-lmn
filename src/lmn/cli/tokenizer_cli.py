#!/usr/bin/env python3
# lmn/cli/tokenizer_cli.py
import argparse
import sys
import os
from lmn.compiler.lexer.tokenizer import Tokenizer

def main():
    # setup the parser
    parser = argparse.ArgumentParser(
        description="Tokenize LMN code and print out the resulting tokens."
    )
    
    # add the input argument
    parser.add_argument(
        "file",
        nargs="?",
        help="Path to an LMN source file (relative to CWD or script directory). "
             "If omitted, uses a default code snippet."
    )

    # add the optional output argument
    parser.add_argument(
        "--output",
        "-o",
        help="Path to a file where tokens will be written. If omitted, prints to stdout."
    )

    # parse the arguments
    args = parser.parse_args()
    
    # If a file argument is given, try to locate it
    if args.file:
        # 1. First try interpreting path relative to the current working directory
        potential_path = os.path.abspath(args.file)
        
        if not os.path.exists(potential_path):
            # 2. If not found, try relative to the script's directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            potential_path = os.path.join(script_dir, args.file)
            
            if not os.path.exists(potential_path):
                print(f"Error: File '{args.file}' not found in current directory or script directory.")
                sys.exit(1)

        # If we reach here, potential_path is valid
        try:
            with open(potential_path, "r", encoding="utf-8") as f:
                code = f.read()
        except Exception as e:
            print(f"Error reading file '{potential_path}': {e}")
            sys.exit(1)

    else:
        # Default LMN code snippet if no file is provided
        code = r"""
// A simple factorial
function fact(n)
  if (n <= 1)
    return 1
  else
    return n * fact(n - 1)
  end
end
"""

    # Tokenize the code
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()

    # Output tokens: either to a file (if provided) or to stdout
    if args.output:
        try:
            # open the file
            with open(args.output, "w", encoding="utf-8") as out_file:
                # loop through each token
                for t in tokens:
                    # write the token
                    out_file.write(str(t) + "\n")

            # written to the file
            print(f"Tokens written to {args.output}")
        except Exception as e:
            print(f"Error writing to file '{args.output}': {e}")
            sys.exit(1)
    else:
        # Print each token to stdout
        for t in tokens:
            print(t)

if __name__ == "__main__":
    main()
