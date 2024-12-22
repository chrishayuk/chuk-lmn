#!/usr/bin/env python3
import json
import sys
from compiler.emitter.wasm.wasm_emitter import WasmEmitter

def main():
    if len(sys.argv) < 2:
        print("Usage: wasm_emitter_cli.py <ast.json>")
        sys.exit(1)

    json_file = sys.argv[1]

    # 1) Load the AST from JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        ast = json.load(f)

    # 2) Instantiate WasmEmitter
    emitter = WasmEmitter()

    # 3) Emit the WASM module as text
    wasm_text = emitter.emit_program(ast)

    # 4) Print to stdout
    print(wasm_text)

if __name__ == "__main__":
    main()
