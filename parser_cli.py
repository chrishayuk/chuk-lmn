#!/usr/bin/env python3
import argparse
import sys
from compiler.lexer.tokenizer import Tokenizer
from compiler.parser.parser import Parser

def main():
    parser = argparse.ArgumentParser(
        description="Parse LMN code and print the resulting AST (in JSON)."
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="Path to an LMN source file. If omitted, reads from stdin."
    )
    args = parser.parse_args()

    # Read code from a file or stdin
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            code = f.read()
    else:
        # No file given: read from stdin
        code = sys.stdin.read()

    # Tokenize
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()

    # Parse
    parser_obj = Parser(tokens)
    ast_program = parser_obj.parse()

    # Print AST as JSON
    # Assuming Program has a to_json() method (or you can do to_dict() then json.dumps)
    print(ast_program.to_json())

if __name__ == "__main__":
    main()
