# Tokenizer
The **tokenizer** breaks down an LMN source file into tokens.

## Tokenizer CLI
The tokenizer CLI is a tool that can be used to tokenize an LMN program.  It's worth spending time getting familiar with the tool as it will help understand how the LMN language works.

### Tokenize to StdOut
To run the tokenizer, use the following command:

```bash
uv run tokenizer-cli samples/lmn/sample_program.lmn
```

This will take the sample LMN program and convert into a tokenized form and display it on the screen.

### Tokenize to a Text File
To run the tokenizer, use the following command:

```bash
uv run tokenizer-cli samples/lmn/sample_program.lmn --out samples/tokenized/sample_program.txt
```

This will take the sample LMN program and convert into a tokenized form and store the output in a text file.