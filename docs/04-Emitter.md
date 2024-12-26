# WAT Emitter
After parsing, you can emit a WebAssembly-compatible JSON AST or intermediate code. Then, you can convert that JSON AST into a `.wat`. 

You can use the `ast_to_wat.py` script to convert the JSON AST into WebAssembly Text Format (WAT).  

## Print WAT to the screen
The following will take the typechecked input AST and print it to the screen.

```bash
uv run ast-to-wat ./samples/ast_typechecked/sample_program.json
```

**Example Output:**
```wat
(module
  (func $main (result i32)
    i32.const 42
    return
  )
)
```

**Write WAT to a file:**
The following will take the typechecked input AST and write it to a `.wat` file.

```bash
uv run ast-to-wat ./samples/ast_typechecked/sample_program.json --output ./samples/wat/sample_program.wat
```
