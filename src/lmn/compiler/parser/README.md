# Introduction
The lexer is really responsible for taking an incoming source file and converting it into a set of tokens and then parsing the tokens into an abstract syntax tree.

## Testing the Lexer
If you wish to run a basic test of the lexer you can use the following command

```bash
uv run parser-cli
```

If you wish to pass a particular file

```bash
uv run parser-cli --file <filename>
```

For example

```bash
uv run parser-cli --file samples/lmn/fibonacci.lmn
```

If you wish to output to a file

```bash
uv run parser-cli samples/lmn/fibonacci.lmn --output ../../cli/samples/ast/fibonacci_ast.json
```

or


```bash
uv run parser-cli samples/lmn/factorial.lmn --output ../../cli/samples/ast/factorial_ast.json
```