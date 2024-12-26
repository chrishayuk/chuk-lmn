# Typechecker
The **typechecker** performs a typecheck of the abstract syntax tree (AST), and ensures that all expressions are valid.
It will also infer types for all expressions.

## Print AST to the screen
To run the typechecker, use the following command:

```bash
uv run typechecker  ./samples/ast/sample_program.json
```

This will take the AST, typecheck it, infer types, and print the transformed AST to the screen.

## Write AST to a file
To run the typechecker, use the following command:

```bash
To run the parser, use the following command:

uv run parser-cli ./samples/lmn/sample_program.lmn --output ./samples/ast/sample_program.json
```

This will take the AST, typecheck it, infer types, and write the transformed AST to a JSON file.