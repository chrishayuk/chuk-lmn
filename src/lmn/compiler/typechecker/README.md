# Introduction
The AST typechecker is responsible for typechecking a program. It is responsible for checking that all variables are declared before they are used, and that all operations are valid.  It's also responsible for infering the types of variables.

The typechecker will take an AST and convert to an AST with types.

## Running the Typechecker
If you wish to run the typechecker, you can use the following command:

```bash
uv run typechecker  ./samples/ast/sample_program.json --output ./samples/ast_typechecked/sample_program.json
```