# compiler/emitter/wasm/wasm_emitter.py

# STATEMENT EMITTERS
from compiler.emitter.wasm.statements.if_emitter import IfEmitter
from compiler.emitter.wasm.statements.set_emitter import SetEmitter
from compiler.emitter.wasm.statements.print_emitter import PrintEmitter
from compiler.emitter.wasm.statements.return_emitter import ReturnEmitter
from compiler.emitter.wasm.statements.for_emitter import ForEmitter
from compiler.emitter.wasm.statements.call_emitter import CallEmitter
from compiler.emitter.wasm.statements.function_emitter import FunctionEmitter  # NEW

# EXPRESSION EMITTERS
from compiler.emitter.wasm.expressions.binary_expression_emitter import BinaryExpressionEmitter
from compiler.emitter.wasm.expressions.fn_expression_emitter import FnExpressionEmitter
from compiler.emitter.wasm.expressions.unary_expression_emitter import UnaryExpressionEmitter
from compiler.emitter.wasm.expressions.literal_expression_emitter import LiteralExpressionEmitter
from compiler.emitter.wasm.expressions.variable_expression_emitter import VariableExpressionEmitter


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
        """
        if ast["type"] != "Program":
            raise ValueError("AST root must be a Program")

        for node in ast["body"]:
            if node["type"] == "FunctionDefinition":
                self.emit_function_definition(node)
            # If other top-level statements exist, handle them

        return self.build_module()

    def build_module(self):
        """
        Wrap the collected functions (and imports, exports) in a single WASM (module ...) string.
        """
        lines = []
        lines.append('(module')

        # Example import for printing an i32
        lines.append('  (import "env" "print_i32" (func $print_i32 (param i32)))')

        # Insert each function
        for f in self.functions:
            for line in f:
                lines.append(f"  {line}")

        # Export "main" if present
        for fname in self.function_names:
            if fname == "main":
                lines.append(f'  (export "main" (func ${fname}))')

        lines.append(')')
        return "\n".join(lines) + "\n"

    def emit_function_definition(self, node):
        """
        Delegates the function definition to FunctionEmitter.
        """
        func_lines = []
        # The function emitter handles param locals, body statements, etc.
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
            # Other statements
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
            # Replace leading '$$' with single '$'
            return '$' + name[2:]
        elif not name.startswith('$'):
            # Prepend '$'
            return f'${name}'
        else:
            # Already starts with single '$', do nothing
            return name
