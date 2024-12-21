#!/usr/bin/env python3
# tokenizer_cli.py
import argparse
import sys
from compiler.lexer.tokenizer import Tokenizer

def main():
    # setup the parser
    parser = argparse.ArgumentParser(
        description="Tokenize LMN code and print out the resulting tokens."
    )

    # Optional positional argument for a file path
    parser.add_argument(
        "file",
        nargs="?",
        help="Path to an LMN source file. If omitted, uses a default code snippet."
    )

    # parse
    args = parser.parse_args()

    if args.file:
        # Read code from the specified file
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                code = f.read()
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found.")
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

    # Create the tokenizer and get tokens
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()

    # Print each token
    for t in tokens:
        print(t)

if __name__ == "__main__":
    main()
