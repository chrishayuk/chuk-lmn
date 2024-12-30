# file: lmn/compiler/pipeline.py

import logging
import subprocess
import tempfile
import os

from lmn.compiler.lexer.tokenizer import Tokenizer
from lmn.compiler.parser.parser import Parser
from lmn.compiler.typechecker.ast_type_checker import type_check_program
from lmn.compiler.lowering.wasm_lowerer import lower_program_to_wasm_types
from lmn.compiler.emitter.wasm.wasm_emitter import WasmEmitter

logger = logging.getLogger(__name__)

def compile_code_to_wat(
    code: str,
    also_produce_wasm: bool = False,
    import_memory: bool = False
) -> (str, bytes or None):
    """
    End-to-end compiler pipeline:
      1) Lex & parse the LMN source code => AST (object)
      2) Type-check => modifies AST with inferred types
      3) Lower => converts language-level types in the AST to WASM-level
      4) Convert the final AST object to a dict for emission
      5) Emit => produce .wat text from the dict-based AST
      6) (Optional) Convert the WAT to WASM bytes in-memory.

    :param code: The LMN source code as a string.
    :param also_produce_wasm: If True, also run 'wat2wasm' to produce WASM bytes in memory.
    :param import_memory: If True, the WasmEmitter will import memory from "env"
                         instead of defining it. 
                         This allows multiple modules to share one memory in the host environment.
    :return: A tuple (wat_text, wasm_bytes)
             - wat_text is the final .wat string
             - wasm_bytes is the compiled WASM binary or None if also_produce_wasm=False
    :raises: Exceptions on parse/type/lowering errors; or if 'wat2wasm' fails.
    """

    # 1) Lex
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    logger.debug(f"compile_code_to_wat: got {len(tokens)} tokens.")

    # 2) Parse => AST object
    parser = Parser(tokens)
    ast_program_obj = parser.parse()
    logger.debug("compile_code_to_wat: parsed AST object: %r", ast_program_obj)

    # 3) Type-check
    type_check_program(ast_program_obj)

    # 4) Lower
    lower_program_to_wasm_types(ast_program_obj)

    # 5) Convert the now-lowered AST object to a dict (the emitter is dict-based)
    ast_dict = ast_program_obj.to_dict()

    # 6) Emit WAT
    # Pass `import_memory` to the emitter’s constructor
    emitter = WasmEmitter(import_memory=import_memory)
    wat_text = emitter.emit_program(ast_dict)

    # 7) If also_produce_wasm => run wat2wasm in memory
    wasm_bytes = None
    if also_produce_wasm:
        with tempfile.NamedTemporaryFile(suffix=".wat", delete=False) as tmp_wat:
            tmp_wat.write(wat_text.encode("utf-8"))
            tmp_wat_path = tmp_wat.name

        wasm_path = tmp_wat_path.replace(".wat", ".wasm")

        try:
            subprocess.run(["wat2wasm", tmp_wat_path, "-o", wasm_path], check=True)
        except FileNotFoundError:
            raise RuntimeError("Error: 'wat2wasm' not found in PATH.")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"wat2wasm failed: {e}")
        finally:
            # remove the .wat file
            try:
                os.remove(tmp_wat_path)
            except OSError:
                pass

        try:
            with open(wasm_path, "rb") as f_wasm:
                wasm_bytes = f_wasm.read()
        finally:
            # remove .wasm file
            try:
                os.remove(wasm_path)
            except OSError:
                pass

    return wat_text, wasm_bytes
