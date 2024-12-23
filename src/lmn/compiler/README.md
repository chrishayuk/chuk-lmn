# Introduction
The following is the compiler for CHUK-BASIC.
As it stands CHUK-BASIC should be compatible largely with dartmouth basic and vintage basic.

## Lexer, AST, Parser
As it stands today the lexer, AST and Parser should be complete and will work with all statements in dartmouth basic with exception to the following keywords

- READ, DATA, MAT

I will implement them in a future version.

### Non Dartmouth Enhancements
In order to be compatible with vintage basic, there is a few things i will need to support in the Parser

- Assignment without LET statement
- Functions that don't begin with FN

## Utilities
I will need a few utilities before emitting WebAssembly

- Print AST Tree

## Web Assembly Emitter
I have not yet start the emittance of webassembly code.
I will now do this prior to finishing the parser