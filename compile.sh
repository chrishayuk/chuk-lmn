#!/usr/bin/env bash
echo "=== Running tokenizer-cli ==="
uv run tokenizer-cli samples/lmn/sample_program.lmn --out samples/tokenized/sample_program.txt
echo "Tokens written to samples/tokenized/sample_program.txt"

echo -e "\n=== Running parser-cli ==="
uv run parser-cli samples/lmn/sample_program.lmn --output samples/ast/sample_program.json
echo "AST written to samples/ast/sample_program.json"

echo -e "\n=== Running typechecker ==="
uv run typechecker samples/ast/sample_program.json --output samples/ast_typechecked/sample_program.json
echo "Typechecking complete. Annotated AST saved to samples/ast_typechecked/sample_program.json"

echo -e "\n=== Running ast-wasm-lowerer ==="
uv run ast-wasm-lowerer samples/ast_typechecked/sample_program.json --output samples/ast_wasm/sample_program.json
echo "AST lowered to WASM types. Lowered AST saved to samples/ast_wasm/sample_program.json"

echo -e "\n=== Running ast-to-wat ==="
uv run ast-to-wat samples/ast_wasm/sample_program.json --output samples/wat/sample_program.wat
echo "WAT file successfully written to samples/wat/sample_program.wat"

echo -e "\n=== Converting .wat to .wasm ==="
wat2wasm samples/wat/sample_program.wat -o samples/wasm/sample_program.wasm
echo "WASM file generated at samples/wasm/sample_program.wasm"

echo -e "\n=== Compilation steps complete! ==="
