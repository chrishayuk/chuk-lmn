# Introduction
The lexer is really responsible for taking an incoming source file and converting it into a set of tokens that will be used as inputs for the parsing stage.

## Testing the Lexer
If you wish to run a basic test of the lexer you can use the following command

```bash
uv run tokenizer-cli
```

If you wish to pass a particular file

```bash
uv run tokenizer-cli --file <filename>
```

For example

```bash
uv run tokenizer-cli --file samples/lmn/fibonacci.lmn
```