# file: lmn/compiler/pipeline.py

import logging
import subprocess
import tempfile
import os
import json
from typing import Optional, Tuple

from lmn.compiler.lexer.tokenizer import Tokenizer
from lmn.compiler.parser.parser import Parser

from lmn.compiler.typechecker.program_checker import ProgramChecker
from lmn.compiler.ast.program import Program
from lmn.compiler.typechecker.ast_type_checker import type_check_program
from lmn.compiler.lowering.wasm_lowerer import lower_program_to_wasm_types
from lmn.compiler.emitter.wasm.wasm_emitter import WasmEmitter

logger = logging.getLogger(__name__)

def compile_code_to_wat(
    code: str,
    also_produce_wasm: bool = False,
    import_memory: bool = False
) -> Tuple[str, Optional[bytes]]:
    """
    EXACT 4-step pipeline:
      1) parser-cli: parse => AST => JSON
      2) typechecker: read JSON => Program => type_check => JSON
      3) ast-wasm-lowerer: read JSON => type_check => lower => JSON
      4) ast-to-wat: read JSON => emit WAT
      Optionally run wat2wasm.
    """

    logger.debug("Starting compile_code_to_wat with code length=%d", len(code))

    # ------------------- Step 1: parser-cli -------------------
    tokenizer = Tokenizer(code)
    tokens = tokenizer.tokenize()
    logger.debug("Step1: parser-cli => got %d tokens.", len(tokens))

    parser_obj = Parser(tokens)
    ast_program = parser_obj.parse()
    logger.debug("Step1: parsed AST => %r", ast_program)

    # “Write” it to JSON (in-memory dict)
    ast_dict_1 = ast_program.to_dict()

    # ------------------- Step 2: typechecker -------------------
    checker = ProgramChecker()
    checker.validate_program(ast_dict_1)  # like reading parsed.json in typechecker
    program_node_2 = Program.model_validate(ast_dict_1)
    type_check_program(program_node_2)
    ast_dict_2 = program_node_2.to_dict()

    # ------------------- Step 3: ast-wasm-lowerer -------------------
    checker.validate_program(ast_dict_2)
    program_node_3 = Program.model_validate(ast_dict_2)
    type_check_program(program_node_3)   # re-check
    lower_program_to_wasm_types(program_node_3)
    ast_dict_3 = program_node_3.to_dict()

    # ------------------- Step 4: ast-to-wat -------------------
    emitter = WasmEmitter(import_memory=import_memory)
    wat_text = emitter.emit_program(ast_dict_3)
    logger.debug("Step4: Emitted WAT => length=%d chars", len(wat_text))

    # (Optional) run wat2wasm
    wasm_bytes = None
    if also_produce_wasm:
        with tempfile.NamedTemporaryFile(suffix=".wat", delete=False) as tmp_wat:
            tmp_wat.write(wat_text.encode("utf-8"))
            wat_path = tmp_wat.name
        wasm_path = wat_path.replace(".wat", ".wasm")

        try:
            subprocess.run(["wat2wasm", wat_path, "-o", wasm_path], check=True)
            logger.debug("wat2wasm succeeded.")
        except FileNotFoundError:
            logger.error("Error: 'wat2wasm' not found in PATH.")
            raise RuntimeError("Error: 'wat2wasm' not found in PATH.")
        except subprocess.CalledProcessError as e:
            logger.error("wat2wasm failed: %s", e)
            raise RuntimeError(f"wat2wasm failed: {e}")
        finally:
            try:
                os.remove(wat_path)
            except OSError:
                pass

        # read .wasm
        try:
            with open(wasm_path, "rb") as f_wasm:
                wasm_bytes = f_wasm.read()
            logger.debug("Read .wasm => size=%d bytes", len(wasm_bytes))
        finally:
            try:
                os.remove(wasm_path)
            except OSError:
                pass

    return wat_text, wasm_bytes
