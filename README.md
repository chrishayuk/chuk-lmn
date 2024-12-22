# Introduction

## Tokenizer
The following will allow you to run a tokenizer against a sample lmn file.

```bash
python tokenizer_cli.py ./samples/lmn/factorial.lmn
```

## Parser
The following will allow you to run the parser against a sample lmn file.

```bash
python parser_cli.py ./samples/lmn/factorial.lmn
```

## WASM Emitter

```bash
python wasm_emitter_cli.py ./samples/ast/sample_program_ast.json
```

# WAT2WASM

```bash
wat2wasm ./samples/wat/factorial.wat -o ./samples/wasm/factorial.wasm
```

# run wasm
```bash
./run_wasm.py ./samples/wasm/factorial.wasm
```