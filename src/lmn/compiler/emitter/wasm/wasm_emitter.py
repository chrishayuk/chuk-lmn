# file: lmn/compiler/emitter/wasm/wasm_emitter.py

import logging

# -------------------------------------------------------------------------
#  Import your various emitter classes for statements & expressions
# -------------------------------------------------------------------------
from lmn.compiler.emitter.wasm.expressions.array_literal_expression_emitter import ArrayLiteralExpressionEmitter
from lmn.compiler.emitter.wasm.expressions.array_int_literal_expression_emitter import IntArrayLiteralEmitter
from lmn.compiler.emitter.wasm.expressions.array_long_literal_expression_emitter import LongArrayLiteralEmitter
from lmn.compiler.emitter.wasm.expressions.array_float_literal_emitter import FloatArrayLiteralEmitter
from lmn.compiler.emitter.wasm.expressions.array_double_literal_emitter import DoubleArrayLiteralEmitter
from lmn.compiler.emitter.wasm.expressions.array_string_literal_emitter import StringArrayLiteralEmitter
from lmn.compiler.emitter.wasm.expressions.assignment_expression_emitter import AssignmentExpressionEmitter
from lmn.compiler.emitter.wasm.expressions.conversion_expression_emitter import ConversionExpressionEmitter
from lmn.compiler.emitter.wasm.expressions.json_literal_expression_emitter import JsonLiteralExpressionEmitter
from lmn.compiler.emitter.wasm.expressions.postfix_expression_emitter import PostfixExpressionEmitter

from lmn.compiler.emitter.wasm.program_emitter import ProgramEmitter
from lmn.compiler.emitter.wasm.statements.if_emitter import IfEmitter
from lmn.compiler.emitter.wasm.statements.let_emitter import LetEmitter
from lmn.compiler.emitter.wasm.statements.assignment_emitter import AssignmentEmitter
from lmn.compiler.emitter.wasm.statements.print_emitter import PrintEmitter
from lmn.compiler.emitter.wasm.statements.return_emitter import ReturnEmitter
from lmn.compiler.emitter.wasm.statements.for_emitter import ForEmitter
from lmn.compiler.emitter.wasm.statements.call_emitter import CallEmitter
from lmn.compiler.emitter.wasm.statements.function_emitter import FunctionEmitter

from lmn.compiler.emitter.wasm.expressions.binary_expression_emitter import BinaryExpressionEmitter
from lmn.compiler.emitter.wasm.expressions.fn_expression_emitter import FnExpressionEmitter
from lmn.compiler.emitter.wasm.expressions.unary_expression_emitter import UnaryExpressionEmitter
from lmn.compiler.emitter.wasm.expressions.literal_expression_emitter import LiteralExpressionEmitter
from lmn.compiler.emitter.wasm.expressions.variable_expression_emitter import VariableExpressionEmitter

# -------------------------------------------------------------------------
#  External module builder for final (module ...) construction
# -------------------------------------------------------------------------
from lmn.compiler.emitter.wasm.wasm_module_builder import build_module

# -------------------------------------------------------------------------
#  Helper imports (if you have unify_types, normalize_params, etc.)
# -------------------------------------------------------------------------
from lmn.compiler.emitter.wasm.type_utils import unify_types
from lmn.compiler.emitter.wasm.param_utils import normalize_params

logger = logging.getLogger(__name__)

class WasmEmitter:
    def __init__(self, import_memory=False):
        """
        Orchestrates the WASM (WAT) code emission from the typed AST,
        including top-level Program logic AND function-level logic.
        """
        self.import_memory = import_memory

        # A) We'll collect strings of WAT lines for each function
        self.functions = []
        self.function_names = []
        self.function_counter = 0

        # B) Track local variables inside the *current* function
        self.new_locals = set()
        self.func_local_map = {}
        self.local_counter = 0

        # C) Data segments for strings, arrays, etc.
        self.data_segments = []
        self.current_data_offset = 1024

        # D) Emitter classes for statements & expressions
        self.if_emitter = IfEmitter(self)
        self.let_emitter = LetEmitter(self)
        self.assignment_emitter = AssignmentEmitter(self)
        self.print_emitter = PrintEmitter(self)
        self.return_emitter = ReturnEmitter(self)
        self.for_emitter = ForEmitter(self)
        self.call_emitter = CallEmitter(self)
        self.function_emitter = FunctionEmitter(self)

        self.binary_expr_emitter = BinaryExpressionEmitter(self)
        self.fn_expr_emitter = FnExpressionEmitter(self)
        self.unary_expr_emitter = UnaryExpressionEmitter(self)
        self.literal_expr_emitter = LiteralExpressionEmitter(self)
        self.variable_expr_emitter = VariableExpressionEmitter(self)
        self.conversion_expr_emitter = ConversionExpressionEmitter(self)
        self.postfix_expression_emitter = PostfixExpressionEmitter(self)
        self.assignment_expression_emitter = AssignmentExpressionEmitter(self)
        self.json_literal_expression_emitter = JsonLiteralExpressionEmitter(self)

        # 1) Generic array-literal => textual fallback
        self.array_literal_expression_emitter = ArrayLiteralExpressionEmitter(self)

        # 2) Specialized typed-array emitters
        self.int_array_literal_emitter = IntArrayLiteralEmitter(self)
        self.long_array_literal_emitter = LongArrayLiteralEmitter(self)
        self.float_array_literal_emitter = FloatArrayLiteralEmitter(self)
        self.double_array_literal_emitter = DoubleArrayLiteralEmitter(self)
        self.string_array_literal_emitter = StringArrayLiteralEmitter(self)

        # Track inlined function aliases (e.g. sum_func -> anon_0)
        self.func_alias_map = {}

        # Create the ProgramEmitter, passing self
        self.program_emitter = ProgramEmitter(self)

    # -------------------------------------------------------------------------
    # (A) Program-Level Emission
    # -------------------------------------------------------------------------
    def emit_program(self, ast):
        """
        Delegates to the ProgramEmitter. 
        This is called from ast_to_wat.py.
        """
        # emit program
        return self.program_emitter.emit_program(ast)
    
    # -------------------------------------------------------------------------
    # (B) Statement & Expression Emission
    # -------------------------------------------------------------------------
    def emit_statement(self, stmt, out_lines):
        """
        Dispatch a single statement node to the correct emitter.
        """
        stype = stmt["type"]
        logger.debug("emit_statement: %s => %s", stype, stmt)
        if stype == "IfStatement":
            self.if_emitter.emit_if(stmt, out_lines)
        elif stype == "LetStatement":
            self.let_emitter.emit_let(stmt, out_lines)
        elif stype == "PrintStatement":
            self.print_emitter.emit_print(stmt, out_lines)
        elif stype == "ReturnStatement":
            self.return_emitter.emit_return(stmt, out_lines)
        elif stype == "ForStatement":
            self.for_emitter.emit_for(stmt, out_lines)
        elif stype == "CallStatement":
            self.call_emitter.emit_call(stmt, out_lines)
        elif stype == "AssignmentStatement":
            self.assignment_emitter.emit_assignment(stmt, out_lines)
        elif stype == "FunctionDefinition":
            # Already handled in top-level rewriting => do nothing
            pass
        else:
            logger.debug("emit_statement: no special handler, ignoring or fallback")
            pass

    def emit_expression(self, expr, out_lines):
        """
        Dispatch a single expression node to the correct expression emitter.
        """
        etype = expr["type"]
        logger.debug("emit_expression: %s => %s", etype, expr)
        if etype == "BinaryExpression":
            self.binary_expr_emitter.emit(expr, out_lines)
        elif etype == "FnExpression":
            self.fn_expr_emitter.emit_fn(expr, out_lines)
        elif etype == "UnaryExpression":
            self.unary_expr_emitter.emit(expr, out_lines)
        elif etype == "LiteralExpression":
            self.literal_expr_emitter.emit(expr, out_lines)
        elif etype == "VariableExpression":
            self.variable_expr_emitter.emit(expr, out_lines)
        elif etype == "ConversionExpression":
            self.conversion_expr_emitter.emit(expr, out_lines)
        elif etype == "PostfixExpression":
            self.postfix_expression_emitter.emit(expr, out_lines)
        elif etype == "AssignmentExpression":
            self.assignment_expression_emitter.emit(expr, out_lines)
        elif etype == "JsonLiteralExpression":
            self.json_literal_expression_emitter.emit(expr, out_lines)
        elif etype == "ArrayLiteralExpression":
            self._emit_array_literal(expr, out_lines)
        else:
            # fallback => i32.const 0
            logger.debug("emit_expression: fallback => i32.const 0")
            out_lines.append('  i32.const 0')

    def _emit_array_literal(self, expr, out_lines):
        """
        Distinguish different array-literal types by `expr.get("inferred_type")`.
        """
        inferred_type = expr.get("inferred_type", "")
        logger.debug("_emit_array_literal: inferred_type='%s'", inferred_type)
        if inferred_type == "i32_string_array":
            self.string_array_literal_emitter.emit_string_array(expr, out_lines)
        elif inferred_type == "i32_json_array":
            self.array_literal_expression_emitter.emit(expr, out_lines)
        elif inferred_type in ("i32_ptr",):
            self.int_array_literal_emitter.emit_int_array(expr, out_lines)
        elif inferred_type in ("i64_ptr",):
            self.long_array_literal_emitter.emit_long_array(expr, out_lines)
        elif inferred_type in ("f32_ptr",):
            self.float_array_literal_emitter.emit_float_array(expr, out_lines)
        elif inferred_type in ("f64_ptr",):
            self.double_array_literal_emitter.emit_double_array(expr, out_lines)
        else:
            # fallback => generic array literal
            self.array_literal_expression_emitter.emit(expr, out_lines)

    # -------------------------------------------------------------------------
    # (C) Build Final (module ...)
    # -------------------------------------------------------------------------
    def build_module(self):
        """
        Calls the external wasm_module_builder to produce the final (module ...) text.
        """
        logger.debug("build_module: generating final WAT module")

        # build the module
        return build_module(self)

    # -------------------------------------------------------------------------
    # (D) Data Segment Helpers
    # -------------------------------------------------------------------------
    def _add_data_segment(self, text: str) -> int:
        """
        Store text in a data segment, returning the linear-memory offset.
        """
        data_bytes = text.encode('utf-8', errors='replace') + b'\0'
        offset = self.current_data_offset
        self.data_segments.append((offset, data_bytes))
        logger.debug(f"_add_data_segment: Stored '{text}' at offset {offset}, bytes={data_bytes}")
        self.current_data_offset += len(data_bytes)
        logger.debug(f"_add_data_segment: Updated current_data_offset to {self.current_data_offset}")
        return offset

    # -------------------------------------------------------------------------
    # (E) Type Helpers
    # -------------------------------------------------------------------------
    def _wasm_basetype(self, t: str) -> str:
        """
        Convert a higher-level type string (e.g. 'int') into the actual WASM base type (e.g. 'i32').
        """
        pointer_types = {
            "i32_ptr", "i64_ptr", "f32_ptr", "f64_ptr",
            "i32_json", "i32_json_array",
            "i32_string", "i32_string_array"
        }
        if t in pointer_types:
            return "i32"

        basic_type_map = {
            "int":   "i32",
            "i32":   "i32",
            "long":  "i64",
            "i64":   "i64",
            "float": "f32",
            "f32":   "f32",
            "double": "f64",
            "f64":    "f64",
        }
        return basic_type_map.get(t, "i32")

    # -------------------------------------------------------------------------
    # (F) Utility
    # -------------------------------------------------------------------------
    def _normalize_local_name(self, name: str) -> str:
        """
        Convert 'foo' => '$foo', or '$$bar' => '$bar',
        so we can reference them properly in WAT.
        """
        if name.startswith('$$'):
            return '$' + name[2:]
        elif not name.startswith('$'):
            return f'${name}'
        else:
            return name

    def get_emitted_function_name(self, raw_name: str) -> str:
        """
        If 'raw_name' was mapped to an inline-lifted function (e.g. 'anon_0'),
        return that new name. Else keep the same.
        """
        return self.func_alias_map.get(raw_name, raw_name)
