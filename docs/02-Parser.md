# Tokenizer
The **parser** converts the stream of tokens into an abstract syntax tree (AST).

## Print AST to the screen
To run the parser, use the following command:

```bash
uv run parser-cli ./samples/lmn/sample_program.lmn
```

This will take the sample LMN program, tokenize it, parse it, and display the AST on the screen.

## Write AST to a file
```bash
To run the parser, use the following command:

uv run parser-cli ./samples/lmn/sample_program.lmn --output ./samples/ast/sample_program.json
```

This will take the sample LMN program, tokenize it, parse it, and write the AST to a JSON file.