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
        """
        self.import_memory = import_memory

        # A) We'll collect strings of WAT lines for each function
        self.functions = []
        self.function_names = []
        self.function_counter = 0

        # B) For local variables inside the *current* function
        self.new_locals = set()
        self.func_local_map = {}
        self.local_counter = 0

        # C) Data segments for strings, array data, etc.
        self.data_segments = []
        self.current_data_offset = 1024

        # D) Statement/expression emitters
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

        # Inline function aliases: e.g. sum_func -> anon_0
        self.func_alias_map = {}

    # -------------------------------------------------------------------------
    # Program-level Emission
    # -------------------------------------------------------------------------
    def emit_program(self, ast):
        if ast["type"] != "Program":
            raise ValueError("AST root must be a Program")

        # 1) Separate function defs from other top-level stmts
        top_level_stmts = []
        function_defs = []
        for node in ast["body"]:
            if node["type"] == "FunctionDefinition":
                function_defs.append(node)
            else:
                top_level_stmts.append(node)

        # 2) For each FunctionDefinition, lift inline fn from its immediate body
        for fn in function_defs:
            fn["body"] = self.rewrite_lets_in_function_body(fn["body"])

        # 3) Lift inline functions from top-level statements
        rewritten_top = self.rewrite_lets_in_function_body(top_level_stmts)

        # 4) Emit the real function definitions we found
        for fn_node in function_defs:
            self.emit_function_definition(fn_node)

        # 5) If leftover statements remain, put them in __top_level__
        if rewritten_top:
            self.emit_top_level_statements_function(rewritten_top)

        # 6) Build final WAT
        return self.build_module()

    def rewrite_lets_in_function_body(self, stmts):
        """
        Recursively scans 'stmts' for any inline function let statements:
          let foo = function(...) ...
        or any alias like:
          let foo = someExistingFunc

        Lifts them to top-level. Also recurses into IfStatement, ForStatement, etc.
        """
        out = []
        for stmt in stmts:
            stype = stmt["type"]
            logger.debug(f"rewrite_lets_in_function_body: checking statement type='{stype}'")

            if stype == "LetStatement":
                var_name = stmt["variable"]["name"]
                expr = stmt.get("expression")
                expr_type = expr.get("type") if expr else None
                logger.debug(
                    f"  Found LetStatement with var_name='{var_name}' "
                    f"and expr='{expr_type}'"
                )

                # 1) If let X = function(...), check for 'FnExpression' or 'AnonymousFunction'
                if expr and expr_type in ("FnExpression", "AnonymousFunction"):
                    new_func_name = f"anon_{self.function_counter}"
                    self.function_counter += 1

                    logger.debug(
                        f"  Lifting inline function '{var_name}' of expr_type='{expr_type}' "
                        f"-> '{new_func_name}'"
                    )

                    func_def = {
                        "type": "FunctionDefinition",
                        "name": new_func_name,
                        "params": expr.get("parameters", []),
                        "body": expr.get("body", []),
                        "return_type": expr.get("return_type", None)
                    }
                    logger.debug(
                        f"  Emitting new function definition node for '{new_func_name}'"
                    )
                    self.emit_function_definition(func_def)

                    # Record alias so calls to var_name => call $anon_N
                    self.func_alias_map[var_name] = new_func_name
                    continue

                # 2) If let X = someExistingFunc
                elif expr and expr_type == "VariableExpression":
                    aliased_name = expr["name"]
                    logger.debug(f"  Found let alias: {var_name} -> {aliased_name}")
                    self.func_alias_map[var_name] = aliased_name
                    continue

                else:
                    logger.debug(f"  Keeping normal let statement for '{var_name}'")
                    out.append(stmt)

            elif stype == "IfStatement":
                logger.debug("  Recursing into IfStatement bodies")
                if "thenBody" in stmt:
                    stmt["thenBody"] = self.rewrite_lets_in_function_body(stmt["thenBody"])
                for eclause in stmt.get("elseifClauses", []):
                    eclause["body"] = self.rewrite_lets_in_function_body(eclause["body"])
                if "elseBody" in stmt:
                    stmt["elseBody"] = self.rewrite_lets_in_function_body(stmt["elseBody"])
                out.append(stmt)

            elif stype == "ForStatement":
                logger.debug("  Recursing into ForStatement body")
                if "body" in stmt:
                    stmt["body"] = self.rewrite_lets_in_function_body(stmt["body"])
                out.append(stmt)

            elif stype == "WhileStatement":
                logger.debug("  Recursing into WhileStatement body")
                if "body" in stmt:
                    stmt["body"] = self.rewrite_lets_in_function_body(stmt["body"])
                out.append(stmt)

            elif stype == "FunctionDefinition":
                logger.debug("  Recursing into nested FunctionDefinition")
                body_stmts = stmt.get("body", [])
                stmt["body"] = self.rewrite_lets_in_function_body(body_stmts)
                out.append(stmt)

            else:
                logger.debug(f"  Keeping statement of type='{stype}' as is.")
                out.append(stmt)

        return out

    def build_function_lines(self, func_node):
        """
        Build lines for an inline-lifted function, using function_emitter.
        Return them as a list of lines, e.g. ["(func $anon_0", ...].
        """
        func_name = func_node["name"]
        self.function_names.append(func_name)

        # Normalize param shape so function_emitter won't crash
        func_node["params"] = self._normalize_params(func_node["params"])

        func_lines = []
        self.function_emitter.emit_function(func_node, func_lines)
        return func_lines

    def emit_function_definition(self, node):
        """
        For explicit function definitions that were in the AST originally, or
        "lifted" inline definitions. We unify param shape and then call our
        function emitter.
        """
        func_name = node.get("name", f"fn_{self.function_counter}")
        self.function_counter += 1
        self.function_names.append(func_name)

        # Normalize param shape so function_emitter won't crash
        node["params"] = self._normalize_params(node["params"])

        func_lines = []
        self.function_emitter.emit_function(node, func_lines)
        self.functions.append(func_lines)

    def emit_top_level_statements_function(self, statements):
        func_name = "__top_level__"
        self.function_names.append(func_name)

        # Reset local tracking
        self.new_locals = set()
        self.func_local_map = {}
        self.local_counter = 0

        func_lines = [f'(func ${func_name}']
        for stmt in statements:
            self.emit_statement(stmt, func_lines)

        # Insert local declarations
        local_decls = []
        for var_name in self.new_locals:
            if var_name not in self.func_local_map:
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
        lines = []
        lines.append('(module')

        # Imports
        lines.append('  (import "env" "print_i32" (func $print_i32 (param i32)))')
        lines.append('  (import "env" "print_i64" (func $print_i64 (param i64)))')
        lines.append('  (import "env" "print_f32" (func $print_f32 (param f32)))')
        lines.append('  (import "env" "print_f64" (func $print_f64 (param f64)))')
        lines.append('  (import "env" "print_string" (func $print_string (param i32)))')
        lines.append('  (import "env" "print_json" (func $print_json (param i32)))')
        lines.append('  (import "env" "print_string_array" (func $print_string_array (param i32)))')
        lines.append('  (import "env" "print_i32_array" (func $print_i32_array (param i32)))')
        lines.append('  (import "env" "print_i64_array" (func $print_i64_array (param i32)))')
        lines.append('  (import "env" "print_f32_array" (func $print_f32_array (param i32)))')
        lines.append('  (import "env" "print_f64_array" (func $print_f64_array (param i32)))')
        lines.append('  (import "env" "llm" (func $llm (param i32 i32) (result i32)))')

        # Memory
        if self.import_memory:
            lines.append('  (import "env" "memory" (memory 1))')
        else:
            largest_required = 0
            for (offset, data_bytes) in self.data_segments:
                end_offset = offset + len(data_bytes)
                if end_offset > largest_required:
                    largest_required = end_offset
            PAGE_SIZE = 65536
            required_pages = (largest_required + PAGE_SIZE - 1) // PAGE_SIZE
            if required_pages < 1:
                required_pages = 1

            lines.append(f'  (memory (export "memory") {required_pages})')

        # Our collected functions
        for f_lines in self.functions:
            for line in f_lines:
                lines.append(f"  {line}")

        # Export them
        for fname in self.function_names:
            lines.append(f'  (export "{fname}" (func ${fname}))')

        # Data segments
        if not self.import_memory:
            for (offset, data_bytes) in self.data_segments:
                escaped = "".join(f"\\{b:02x}" for b in data_bytes)
                lines.append(f'  (data (i32.const {offset}) "{escaped}")')

        lines.append(')')
        return "\n".join(lines) + "\n"

    # -------------------------------------------------------------------------
    # Statement & Expression Emission
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
        elif stype == "FunctionDefinition":
            # Already handled, do nothing
            pass
        else:
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
                self.string_array_literal_emitter.emit_string_array(expr, out_lines)
            elif inferred == "i32_json_array":
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
                self.array_literal_expression_emitter.emit(expr, out_lines)
        else:
            # fallback => i32.const 0
            out_lines.append('  i32.const 0')

    # -------------------------------------------------------------------------
    # Data Segment Helpers
    # -------------------------------------------------------------------------
    def _add_data_segment(self, text: str) -> int:
        data_bytes = text.encode('utf-8', errors='replace') + b'\0'
        offset = self.current_data_offset
        self.data_segments.append((offset, data_bytes))
        logger.debug(f"_add_data_segment: Stored '{text}' at offset {offset} with bytes {data_bytes}")
        self.current_data_offset += len(data_bytes)
        logger.debug(f"_add_data_segment: Updated current_data_offset to {self.current_data_offset}")
        return offset

    # -------------------------------------------------------------------------
    # Type Helpers
    # -------------------------------------------------------------------------
    def _wasm_basetype(self, t: str) -> str:
        pointer_types = {
            "i32_ptr", "i64_ptr", "f32_ptr", "f64_ptr",
            "i32_json", "i32_json_array",
            "i32_string", "i32_string_array"
        }
        if t in pointer_types:
            return "i32"

        basic_type_map = {
            "int": "i32",  "i32": "i32",
            "long": "i64", "i64": "i64",
            "float": "f32","f32": "f32",
            "double": "f64","f64": "f64",
        }
        return basic_type_map.get(t, "i32")

    # -------------------------------------------------------------------------
    # Utility
    # -------------------------------------------------------------------------
    def _normalize_local_name(self, name: str) -> str:
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
        priority = {"i32":1, "i64":2, "f32":3, "f64":4}
        p1 = priority.get(t1,0)
        p2 = priority.get(t2,0)
        return t1 if p1 >= p2 else t2

    # -------------------------------------------------------------------------
    # The function alias helper
    # -------------------------------------------------------------------------
    def get_emitted_function_name(self, raw_name: str) -> str:
        return self.func_alias_map.get(raw_name, raw_name)

    # -------------------------------------------------------------------------
    # Param Normalization
    # -------------------------------------------------------------------------
    def _normalize_params(self, params):
        """
        Convert any list of (paramName, paramType) tuples into
        a list of dicts: [{"name": pName, "type_annotation": pType}, ...].
        If they're already dicts, just return as is.
        """
        if not params:
            return []

        # If the first item is a list/tuple, assume all are
        first = params[0]
        if isinstance(first, (list, tuple)):
            new_params = []
            for (p_name, p_type) in params:
                new_params.append({
                    "name": p_name,
                    "type_annotation": p_type
                })
            return new_params

        # else assume they're already dict-based
        return params
