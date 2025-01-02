# file: lmn/compiler/emitter/wasm/wasm_emitter.py
import logging
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

logger = logging.getLogger(__name__)

class WasmEmitter:
    def __init__(self, import_memory=False):
        """
        Orchestrates the WASM (WAT) code emission from the typed AST.
        
        :param import_memory: If True, we'll import "env" "memory" (memory 1) instead
                              of defining our own memory + data segments. 
        """
        self.import_memory = import_memory

        # For code generation:
        self.functions = []
        self.function_names = []
        self.function_counter = 0

        # Track new locals for the current function
        self.new_locals = set()
        self.func_local_map = {}
        self.local_counter = 0

        # Data segments (for storing strings, arrays, etc.)
        self.data_segments = []            # list of (offset, bytes)
        self.current_data_offset = 1024    # start storing data at some offset

        # Statement emitters
        self.if_emitter = IfEmitter(self)
        self.let_emitter = LetEmitter(self)
        self.assignment_emitter = AssignmentEmitter(self)
        self.print_emitter = PrintEmitter(self)
        self.return_emitter = ReturnEmitter(self)
        self.for_emitter = ForEmitter(self)
        self.call_emitter = CallEmitter(self)
        self.function_emitter = FunctionEmitter(self)

        # Expression emitters
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

        # 2) Specialized typed-array emitters (int, long, float, double)
        self.int_array_literal_emitter = IntArrayLiteralEmitter(self)
        self.long_array_literal_emitter = LongArrayLiteralEmitter(self)
        self.float_array_literal_emitter = FloatArrayLiteralEmitter(self)
        self.double_array_literal_emitter = DoubleArrayLiteralEmitter(self)
        self.string_array_literal_emitter = StringArrayLiteralEmitter(self)

    # -------------------------------------------------------------------------
    # Program-level Emission
    # -------------------------------------------------------------------------

    def emit_program(self, ast):
        """
        Accepts a Program node with .body => top-level statements.
        Some of them might be FunctionDefinition, others might be statements.
        If there's top-level code, we generate a special __top_level__ function.
        """
        if ast["type"] != "Program":
            raise ValueError("AST root must be a Program")

        top_level_statements = []
        for node in ast["body"]:
            if node["type"] == "FunctionDefinition":
                self.emit_function_definition(node)
            else:
                top_level_statements.append(node)

        # If there's any top-level code, we create a special function for it
        if top_level_statements:
            self.emit_top_level_statements_function(top_level_statements)

        return self.build_module()

    def emit_function_definition(self, node):
        """
        Delegates to self.function_emitter, exports function by name.
        """
        func_name = node.get("name", f"fn_{self.function_counter}")
        self.function_counter += 1
        self.function_names.append(func_name)

        func_lines = []
        self.function_emitter.emit_function(node, func_lines)
        self.functions.append(func_lines)

    def emit_top_level_statements_function(self, statements):
        func_name = "__top_level__"
        self.function_names.append(func_name)

        self.new_locals = set()
        self.func_local_map = {}
        self.local_counter = 0

        func_lines = []
        func_lines.append(f'(func ${func_name}')

        # 1) Emit each statement, collecting new_locals
        for stmt in statements:
            self.emit_statement(stmt, func_lines)

        # 2) Insert local declarations
        local_decls = []
        for var_name in self.new_locals:
            if var_name not in self.func_local_map:
                # fallback => auto-declare as i32 or another default
                self.func_local_map[var_name] = {
                    "index": self.local_counter,
                    "type": "i32"
                }
                self.local_counter += 1

            internal_type = self.func_local_map[var_name]["type"]
            wat_type = self._wasm_basetype(internal_type)
            norm_name = self._normalize_local_name(var_name)
            local_decls.append(f'  (local {norm_name} {wat_type})')

        func_lines[1:1] = local_decls
        func_lines.append(')')
        self.functions.append(func_lines)



    def build_module(self):
        """
        Builds the final .wat module with imports, function definitions,
        memory (either imported or exported), data segments (if not importing),
        plus function exports.
        """
        lines = []
        lines.append('(module')

        # Basic numeric scalar printing imports
        lines.append('  (import "env" "print_i32" (func $print_i32 (param i32)))')
        lines.append('  (import "env" "print_i64" (func $print_i64 (param i64)))')
        lines.append('  (import "env" "print_f32" (func $print_f32 (param f32)))')
        lines.append('  (import "env" "print_f64" (func $print_f64 (param f64)))')

        # Basic textual printing imports
        lines.append('  (import "env" "print_string" (func $print_string (param i32)))')
        lines.append('  (import "env" "print_json" (func $print_json (param i32)))')
        lines.append('  (import "env" "print_string_array" (func $print_string_array (param i32)))')

        # Specialized typed-array imports
        lines.append('  (import "env" "print_i32_array" (func $print_i32_array (param i32)))')
        lines.append('  (import "env" "print_i64_array" (func $print_i64_array (param i32)))')
        lines.append('  (import "env" "print_f32_array" (func $print_f32_array (param i32)))')
        lines.append('  (import "env" "print_f64_array" (func $print_f64_array (param i32)))')

        # --------------------------------------------------------------
        # NEW: Import the llm function
        # --------------------------------------------------------------
        # For the signature (prompt_ptr: i32, model_ptr: i32) -> i32
        lines.append('  (import "env" "llm" (func $llm (param i32 i32) (result i32)))')

        if self.import_memory:
            # (A) Import memory => no data segments
            lines.append('  (import "env" "memory" (memory 1))')
        else:
            # (B) Own memory => define pages, emit data segments
            largest_required = 0
            for (offset, data_bytes) in self.data_segments:
                end_offset = offset + len(data_bytes)
                if end_offset > largest_required:
                    largest_required = end_offset

            PAGE_SIZE = 65536
            required_pages = (largest_required + (PAGE_SIZE - 1)) // PAGE_SIZE
            if required_pages < 1:
                required_pages = 1

            lines.append(f'  (memory (export "memory") {required_pages})')

        # Insert function lines
        for f_lines in self.functions:
            for line in f_lines:
                lines.append(f"  {line}")

        # Export each function by name
        for fname in self.function_names:
            lines.append(f'  (export "{fname}" (func ${fname}))')

        # Data segments only if we own memory
        if not self.import_memory:
            for (offset, data_bytes) in self.data_segments:
                escaped = "".join(f"\\{b:02x}" for b in data_bytes)
                lines.append(f'  (data (i32.const {offset}) "{escaped}")')

        lines.append(')')
        return "\n".join(lines) + "\n"



    # -------------------------------------------------------------------------
    #  Statement & Expression Emission
    # -------------------------------------------------------------------------

    def emit_statement(self, stmt, out_lines):
        stype = stmt["type"]
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
        else:
            # fallback => do nothing or i32.const 0
            pass

    def emit_expression(self, expr, out_lines):
        etype = expr["type"]

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
            inferred = expr.get("inferred_type", "")
            
            if inferred == "i32_string_array":
                # handle lowered string arrays
                self.string_array_literal_emitter.emit_string_array(expr, out_lines)
            
            elif inferred == "i32_json_array":
                # handle json array
                self.array_literal_expression_emitter.emit(expr, out_lines)

            elif inferred in ("i32_ptr",):
                self.int_array_literal_emitter.emit_int_array(expr, out_lines)

            elif inferred in ("i64_ptr",):
                self.long_array_literal_emitter.emit_long_array(expr, out_lines)

            elif inferred in ("f32_ptr",):
                self.float_array_literal_emitter.emit_float_array(expr, out_lines)

            elif inferred in ("f64_ptr",):
                self.double_array_literal_emitter.emit_double_array(expr, out_lines)

            else:
                # If we didn't catch it above, fallback
                self.array_literal_expression_emitter.emit(expr, out_lines)
        else:
            # fallback => push 0
            out_lines.append('  i32.const 0')

    # -------------------------------------------------------------------------
    #  Data Segment Helpers
    # -------------------------------------------------------------------------

    def _add_data_segment(self, text: str) -> int:
        """
        Store 'text' in self.data_segments, returning the offset in memory.
        We'll encode as UTF-8 plus a null terminator.
        This only matters if we're NOT importing memory.
        """
        data_bytes = text.encode('utf-8', errors='replace') + b'\0'
        offset = self.current_data_offset
        self.data_segments.append((offset, data_bytes))
        logger.debug(f"_add_data_segment: Stored '{text}' at offset {offset} with bytes {data_bytes}")
        self.current_data_offset += len(data_bytes)
        logger.debug(f"_add_data_segment: Updated current_data_offset to {self.current_data_offset}")
        return offset


    # -------------------------------------------------------------------------
    #  Helper to convert i32_ptr => i32, i64_ptr => i64, etc.
    # -------------------------------------------------------------------------
    def _wasm_basetype(self, t: str) -> str:
        pointer_types = {
            "i32_ptr", "i64_ptr", "f32_ptr", "f64_ptr",
            "i32_json", "i32_json_array",
            "i32_string", "i32_string_array",
            # etc.
        }
        if t in pointer_types:
            return "i32"

        basic_type_map = {
            "int": "i32",  "i32": "i32",
            "long": "i64", "i64": "i64",
            "float": "f32","f32": "f32",
            "double":"f64","f64": "f64",
        }
        return basic_type_map.get(t, "i32")  # fallback




    # -------------------------------------------------------------------------
    #  Utility
    # -------------------------------------------------------------------------
    def _normalize_local_name(self, name: str) -> str:
        """
        E.g. 'x' -> '$x'
        """
        if name.startswith('$$'):
            return '$' + name[2:]
        elif not name.startswith('$'):
            return f'${name}'
        else:
            return name

    def infer_type(self, expr_node, context_type=None):
        if "inferred_type" in expr_node:
            return expr_node["inferred_type"]

        if expr_node["type"] == "LiteralExpression":
            val_str = str(expr_node.get("value", "0"))
            if "." in val_str:
                guessed = "f32"
            else:
                try:
                    val = int(val_str)
                    guessed = "i64" if abs(val) > 2147483647 else "i32"
                except ValueError:
                    guessed = "f32"

            if context_type:
                return self._unify_types(guessed, context_type)
            else:
                return guessed

        return "i32"

    def _unify_types(self, t1, t2):
        priority = {"i32": 1, "i64": 2, "f32": 3, "f64": 4}
        p1 = priority.get(t1, 0)
        p2 = priority.get(t2, 0)
        return t1 if p1 >= p2 else t2
