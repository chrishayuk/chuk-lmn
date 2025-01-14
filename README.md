# LMN Compiler Pipeline
This repository demonstrates a sample pipeline for compiling **LMN** code into **WebAssembly (WASM)**. 


# Just compile to WAT, print on stdout:
uv run lmn-compiler samples/lmn/sample_program.lmn

# Save WAT to out.wat but no .wasm:
uv run lmn-compiler samples/lmn/sample_program.lmn --wat ./samples/wat/sample_program.wat

# Directly compile to .wasm with no .wat left behind:
uv run lmn-compiler samples/lmn/sample_program.lmn --wasm ./samples/wasm/sample_program.wasm

# Compile to .wat AND .wasm
uv run lmn-compiler samples/lmn/sample_program.lmn --wat ./samples/wat/sample_program.wat --wasm ./samples/wasm/sample_program.wasm



### Step 1: Tokenize
This will convert the program to tokens and output them in a text file.

```bash
uv run tokenizer-cli samples/lmn/sample_program.lmn --out samples/tokenized/sample_program.txt
```

### Step 2: Parse
This will convert the program to tokens, and parse into an untyped AST.

```bash
uv run parser-cli ./samples/lmn/sample_program.lmn --output ./samples/ast/sample_program.json 
```

### Step 3: Typecheck
This will typecheck the parsed AST, and output a typed AST.

```bash
uv run typechecker  ./samples/ast/sample_program.json --output ./samples/ast_typechecked/sample_program.json
```

## Step 4: Lowering to WASM types
This will lower the typed AST into an intermediate representation that is closer to WASM.

```bash
uv run ast-wasm-lowerer ./samples/ast_typechecked/sample_program.json --output ./samples/ast_wasm/sample_program.json
```
## Step 5: Emitting Web Assembly Text (WAT) code
This will emit the WAT code from the intermediate representation.

```bash
uv run ast-to-wat ./samples/ast_wasm/sample_program.json --output ./samples/wat/sample_program.wat
```

## Step 6: Generating Web Assembly Binary (WASM) code
This will generate the WASM binary code from the WAT file.

```bash
wat2wasm ./samples/wat/sample_program.wat -o ./samples/wasm/sample_program.wasm
```

### Step 7: Running the generated WASM program

```bash
uv run run-wasm ./samples/wasm/sample_program.wasm
```


