# Introduction
The ast wasm lowerer is responsible for taking an AST with language specific types and lowering the types to wasm compatible types.  This is done by replacing all language specific types with wasm compatible types.

## Testing the Lowerer
If you wish to take an existing ast with LMN specific types, and lower it to machine level types, ru the following comman

```bash
uv run ast-wasm-lowerer ./samples/ast_typechecked/sample_program.json --output ./samples/ast_wasm/sample_program.json
```