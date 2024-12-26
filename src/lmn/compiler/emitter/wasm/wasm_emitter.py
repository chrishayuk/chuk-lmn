# file: compiler/emitter/wasm/wasm_emitter.py

# STATEMENT EMITTERS
from lmn.compiler.emitter.wasm.statements.if_emitter import IfEmitter
from lmn.compiler.emitter.wasm.statements.set_emitter import SetEmitter
from lmn.compiler.emitter.wasm.statements.print_emitter import PrintEmitter
from lmn.compiler.emitter.wasm.statements.return_emitter import ReturnEmitter
from lmn.compiler.emitter.wasm.statements.for_emitter import ForEmitter
from lmn.compiler.emitter.wasm.statements.call_emitter import CallEmitter
from lmn.compiler.emitter.wasm.statements.function_emitter import FunctionEmitter  # NEW

# EXPRESSION EMITTERS
from lmn.compiler.emitter.wasm.expressions.binary_expression_emitter import BinaryExpressionEmitter
from lmn.compiler.emitter.wasm.expressions.fn_expression_emitter import FnExpressionEmitter
from lmn.compiler.emitter.wasm.expressions.unary_expression_emitter import UnaryExpressionEmitter
from lmn.compiler.emitter.wasm.expressions.literal_expression_emitter import LiteralExpressionEmitter
from lmn.compiler.emitter.wasm.expressions.variable_expression_emitter import VariableExpressionEmitter


class WasmEmitter:
    def __init__(self):
        # Collect function text lines to build the final module
        self.functions = []
        self.function_names = []
        self.function_counter = 0

        # Local variable tracking for the current function
        self.func_local_map = {}
        self.local_counter = 0

        # Statement emitters
        self.if_emitter = IfEmitter(self)
        self.set_emitter = SetEmitter(self)
        self.print_emitter = PrintEmitter(self)
        self.return_emitter = ReturnEmitter(self)
        self.for_emitter = ForEmitter(self)
        self.call_emitter = CallEmitter(self)
        self.function_emitter = FunctionEmitter(self)  # NEW

        # Expression emitters
        self.binary_expr_emitter = BinaryExpressionEmitter(self)
        self.fn_expr_emitter = FnExpressionEmitter(self)
        self.unary_expr_emitter = UnaryExpressionEmitter(self)
        self.literal_expr_emitter = LiteralExpressionEmitter(self)
        self.variable_expr_emitter = VariableExpressionEmitter(self)

    def emit_program(self, ast):
        """
        Build a complete WASM module from the top-level AST.
        Gathers any top-level statements (non-function) into a special function so they can be executed.
        """
        if ast["type"] != "Program":
            raise ValueError("AST root must be a Program")

        # Gather top-level statements
        top_level_statements = []

        for node in ast["body"]:
            if node["type"] == "FunctionDefinition":
                self.emit_function_definition(node)
            else:
                # Treat as a top-level statement
                top_level_statements.append(node)

        # If we have any top-level statements, emit them in a special function
        if top_level_statements:
            self.emit_top_level_statements_function(top_level_statements)

        return self.build_module()

    def emit_top_level_statements_function(self, statements):
        """
        Wraps top-level statements in a special function so they are valid in WASM.
        We append the name "__top_level__" to function_names so it gets exported.
        """
        func_name = "__top_level__"
        self.function_names.append(func_name)

        func_lines = []
        func_lines.append(f'(func ${func_name}')

        for stmt in statements:
            self.emit_statement(stmt, func_lines)

        func_lines.append(')')
        self.functions.append(func_lines)

    def build_module(self):
        lines = []
        lines.append('(module')

        # Import for printing 32-bit integers
        lines.append('  (import "env" "print_i32" (func $print_i32 (param i32)))')

        # Import for printing 64-bit integers
        lines.append('  (import "env" "print_i64" (func $print_i64 (param i64)))')

        # Import for printing 64-bit floats
        lines.append('  (import "env" "print_f64" (func $print_f64 (param f64)))')

        # (Optionally import a print_f32 if you handle 32-bit floats separately)
        # lines.append('  (import "env" "print_f32" (func $print_f32 (param f32)))')

        # Insert each function
        for f in self.functions:
            for line in f:
                lines.append(f"  {line}")

        # Export each named function
        for fname in self.function_names:
            lines.append(f'  (export "{fname}" (func ${fname}))')

        lines.append(')')
        return "\n".join(lines) + "\n"


    def emit_function_definition(self, node):
        """
        Delegates the function definition to FunctionEmitter.
        Also adds the function name to self.function_names so it is exported.
        """
        func_name = node.get("name", f"fn_{self.function_counter}")
        self.function_counter += 1

        self.function_names.append(func_name)

        func_lines = []
        self.function_emitter.emit_function(node, func_lines)
        self.functions.append(func_lines)

    def emit_statement(self, stmt, out_lines):
        stype = stmt["type"]
        if stype == "IfStatement":
            self.if_emitter.emit_if(stmt, out_lines)
        elif stype == "SetStatement":
            self.set_emitter.emit_set(stmt, out_lines)
        elif stype == "PrintStatement":
            self.print_emitter.emit_print(stmt, out_lines)
        elif stype == "ReturnStatement":
            self.return_emitter.emit_return(stmt, out_lines)
        elif stype == "ForStatement":
            self.for_emitter.emit_for(stmt, out_lines)
        elif stype == "CallStatement":
            self.call_emitter.emit_call(stmt, out_lines)
        else:
            # No emitter for this statement => do nothing or raise an error
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
        else:
            # Fallback or unknown expression
            out_lines.append('  i32.const 0')

    def _normalize_local_name(self, name: str) -> str:
        """
        Ensures local variable has exactly one '$' prefix:
            - 'x'    -> '$x'
            - '$$x'  -> '$x'
            - '$x'   -> '$x' (unchanged)
        """
        if name.startswith('$$'):
            return '$' + name[2:]
        elif not name.startswith('$'):
            return f'${name}'
        else:
            return name
        
    def infer_type(self, expr_node):
        """
        A naive approach to determine if expr_node is i32, i64, f32, or f64.
        """
        if expr_node["type"] == "LiteralExpression":
            val_str = str(expr_node.get("value", "0"))
            if "." in val_str:
                return "f32"
            try:
                int_val = int(val_str)
                if abs(int_val) > 2147483647:
                    return "i64"
                else:
                    return "i32"
            except ValueError:
                return "f32"
        
        elif expr_node["type"] == "BinaryExpression":
            left = expr_node["left"]
            right = expr_node["right"]
            left_t = self.infer_type(left)
            right_t = self.infer_type(right)
            return self._unify_types(left_t, right_t)
        
        # fallback
        return "i32"

    def _unify_types(self, t1, t2):
        priority = {"i32": 1, "i64": 2, "f32": 3, "f64": 4}
        return t1 if priority[t1] >= priority[t2] else t2
