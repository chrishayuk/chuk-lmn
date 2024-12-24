# compiler/emitter/wasm/wasm_emitter.py

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
        
    def infer_type(self, expr_node):
        """
        A naive approach to determine if expr_node is i32, i64, f32, or f64.
        This can read from expr_node data or from a symbol table if you store that info.
        """
        # 1) If it’s a literal expression with a decimal => f32
        # 2) If the literal is large => i64
        # 3) Otherwise => i32
        # 4) Or, if expr_node is a BinaryExpression, unify left/right ...
        #    you'd need to recursively call self.infer_type(left), self.infer_type(right).
        # For now, here's a trivial example that always returns i32:
        
        if expr_node["type"] == "LiteralExpression":
            val_str = str(expr_node.get("value", "0"))
            if "." in val_str:
                return "f32"
            try:
                int_val = int(val_str)
                # If it’s bigger than 2^31-1, treat as i64
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
