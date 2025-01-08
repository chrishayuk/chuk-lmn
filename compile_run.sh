#!/usr/bin/env bash

# First, compile everything
./compile.sh

# Then, run the resulting wasm
echo -e "\n=== Running the compiled WebAssembly ==="
uv run run-wasm samples/wasm/sample_program.wasm
