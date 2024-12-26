# Wat2Wasm
This tool will take an input .wat file and output a .wasm file.

## Pre-Requisites
The wat2wasm tool will need to be installed on your machine.
This can be performed via brew

```bash
brew install wat2wasm
```

## Usage
The following command will take the input .wat file and output a .wasm file.

```bash
wat2wasm ./samples/wat/sample_program.wat -o ./samples/wasm/sample_program.wasm
```