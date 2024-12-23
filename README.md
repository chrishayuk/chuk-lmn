# LMN Compiler Pipeline
This repository demonstrates a sample pipeline for compiling **LMN** code into **WebAssembly (WASM)**. 

The steps in this pipeline include:

1. **Tokenization**  
2. **Parsing**  
3. **WASM Emission**  
4. (Optional) Conversion of WAT to WASM  
5. Running the resulting WASM

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [1. Tokenizer](#1-tokenizer)
  - [2. Parser](#2-parser)
  - [3. WASM Emitter](#3-wasm-emitter)
  - [4. Convert WAT to WASM](#4-convert-wat-to-wasm)
  - [5. Run with Wasmtime](#5-run-with-wasmtime)
  - [6. Run WASM Directly](#6-run-wasm-directly)
  - [7. Inspecting WASM](#7-inspecting-wasm)
- [License](#license)

---

## Prerequisites

- **Python 3.7+** installed and available on your PATH  
- **Homebrew (macOS/Linux)** or the equivalent for your platform  
- (Optional) **wasmtime** for running WASM files  
- (Optional) **wasm-tools** for printing WASM binaries

On macOS (and most Linux systems), you can install these dependencies via Homebrew:
```bash
brew install wasmtime
brew install wasm-tools
```
On Windows or other operating systems, refer to [Wasmtime installation docs](https://wasmtime.dev/) and [Wasm Tools GitHub](https://github.com/WebAssembly/wabt) for details.

---

## Installation

1. **Clone this repository**:
   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```
2. **Install Python dependencies** (if any):
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### 1. Tokenizer
The **tokenizer** breaks down an LMN source file into tokens.

```bash
uv run tokenizer-cli samples/lmn/sample_program.lmn
```

This command will output the tokens found in the provided `.lmn` source file.

---

### 2. Parser
The **parser** converts the stream of tokens into an abstract syntax tree (AST).

**Print AST to the screen:**

```bash
uv run parser-cli ./samples/lmn/sample_program.lmn
```

**Write AST to a file:**
```bash
uv run parser-cli ./samples/lmn/sample_program.lmn --output ./samples/ast/sample_program.json
```

---

### 2.A Typechecker

```bash
uv run typechecker  ./samples/ast/sample_program.json
```

**Write AST to a file:**

```bash
uv run typechecker  ./samples/ast/sample_program.json --output ./samples/ast_typechecked/sample_program.json
```

### 3. WASM Emitter

After parsing, you can emit a WebAssembly-compatible JSON AST or intermediate code. Then, you can convert that JSON AST into a `.wat` or `.wasm`.  

You can use the `ast_to_wat.py` script to convert the JSON AST into WebAssembly Text Format (WAT).  

#### Usage:

**Print WAT to the screen:**
```bash
uv run ast-to-wat ./samples/ast/sample_program.json
```

**Write WAT to a file:**
```bash
uv run ast-to-wat ./samples/ast/sample_program.json --output ./samples/wat/sample_program.wat
```

If the `--output` flag is specified, the WAT file will be saved in the given directory with the same name as the input JSON file, but with a `.wat` extension. If not specified, the WAT will be printed to the screen.  

**Example Output:**
```wat
(module
  (func $main (result i32)
    i32.const 42
    return
  )
)
---

### 4. Convert WAT to WASM

If you have a `.wat` file, you can convert it into a `.wasm` binary using the `wat2wasm` tool:

```bash
wat2wasm ./samples/wat/sample_program.wat -o ./samples/wasm/sample_program.wasm
```

This step is optional if your emitter already produces `.wasm` files.

---

### 5. Run with Wasmtime

To execute the WASM file, use [Wasmtime](https://wasmtime.dev/):

```bash
wasmtime ./samples/wasm/sample_program.wasm
```

---

### 6. Run WASM Directly

This repository provides a Python script to run `.wasm` files:

```bash
./run_wasm.py ./samples/wasm/sample_program.wasm
```

> **Note**: This script may rely on Python libraries or a WebAssembly runtime binding; review it for additional dependencies.

---

### 7. Inspecting WASM

If you’d like to inspect the instructions in a `.wasm` file, use the `wasm-tools print` command:

```bash
wasm-tools print ./samples/wasm/sample_program.wasm
```

### 8. Executing WASM
python run_wasm.py ./samples/wasm/sample_program.wasm

---

## License

[MIT](LICENSE) © Chris Hay 

Feel free to modify and distribute. If you found this project helpful, consider giving it a star on GitHub.

