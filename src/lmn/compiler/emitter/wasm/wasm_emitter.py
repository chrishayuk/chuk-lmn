# file: lmn/compiler/emitter/wasm/wasm_emitter.py

from lmn.compiler.emitter.wasm.expressions.conversion_expression_emitter import ConversionExpressionEmitter
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

class WasmEmitter:
    def __init__(self):
        """
        Orchestrates the WASM (WAT) code emission from the typed AST.
        We store:
          - self.functions: list of list-of-lines (one list per function)
          - self.function_names: so we can export them
        """
        self.functions = []
        self.function_names = []
        self.function_counter = 0

        # Track new locals for the current function
        self.new_locals = set()
        self.func_local_map = {}
        self.local_counter = 0

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

    def emit_program(self, ast):
        """
        Accepts a Program node with .body => top-level statements, which might be:
          - function definitions
          - let statements
          - print statements, etc.
        We separate function definitions vs. top-level code, then emit a
        special __top_level__ function if needed.
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

    def emit_top_level_statements_function(self, statements):
        """
        Creates a function __top_level__ for statements that are not inside any user function.
        We do *not* forcibly zero them with i32.const 0 or anything, 
        but rely on let/assignment to insert correct typed zeros if needed.
        """
        func_name = "__top_level__"
        self.function_names.append(func_name)

        # Reset local-tracking for this new function
        self.new_locals = set()
        self.func_local_map = {}
        self.local_counter = 0

        func_lines = []
        func_lines.append(f'(func ${func_name}')

        # Emit each top-level statement
        for stmt in statements:
            self.emit_statement(stmt, func_lines)

        # Insert local declarations (ex: (local $myVar i64))
        local_decls = []
        for var_name in self.new_locals:
            var_type = self.func_local_map[var_name]["type"]
            local_decls.append(f'  (local {var_name} {var_type})')

        # Insert them at index 1, right after '(func $name'
        func_lines[1:1] = local_decls

        # Notice: We do NOT do anything like "i32.const 0 / local.set" for each local here.
        # That is the job of LetEmitter or AssignmentEmitter if there's no expression.

        func_lines.append(')')
        self.functions.append(func_lines)

    def build_module(self):
        """
        Builds the final WAT module with imports and function exports.
        """
        lines = []
        lines.append('(module')

        # Basic printing imports
        lines.append('  (import "env" "print_i32" (func $print_i32 (param i32)))')
        lines.append('  (import "env" "print_i64" (func $print_i64 (param i64)))')
        lines.append('  (import "env" "print_f64" (func $print_f64 (param f64)))')

        # Insert each function
        for f_lines in self.functions:
            for line in f_lines:
                lines.append(f"  {line}")

        # Export each function name
        for fname in self.function_names:
            lines.append(f'  (export "{fname}" (func ${fname}))')

        lines.append(')')
        return "\n".join(lines) + "\n"

    def emit_function_definition(self, node):
        """
        Delegates to self.function_emitter; 
        adds the function name to self.function_names for exporting.
        """
        func_name = node.get("name", f"fn_{self.function_counter}")
        self.function_counter += 1
        self.function_names.append(func_name)

        func_lines = []
        self.function_emitter.emit_function(node, func_lines)
        self.functions.append(func_lines)

    def emit_statement(self, stmt, out_lines):
        """
        Chooses the correct emitter for a statement based on its .type.
        """
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
            # fallback => do nothing or push i32.const 0
            pass

    def emit_expression(self, expr, out_lines):
        """
        Chooses the correct expression emitter (binary, unary, literal, etc.)
        """
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
        else:
            # fallback => i32.const 0 is a last-ditch approach if we can't figure out anything
            out_lines.append('  i32.const 0')

    def _normalize_local_name(self, name: str) -> str:
        """
        Ensures local variable has exactly one '$' prefix:
         - 'x' -> '$x'
         - '$$x' -> '$x'
         - '$x' stays '$x'
        """
        if name.startswith('$$'):
            return '$' + name[2:]
        elif not name.startswith('$'):
            return f'${name}'
        else:
            return name

    def infer_type(self, expr_node, context_type=None):
        """
        If we have a context_type (the local’s known type, e.g. 'i64'),
        we unify the naive guess with that context_type.
        """
        if "inferred_type" in expr_node:
            return expr_node["inferred_type"]  # trust the AST

        # Otherwise, do naive guess
        if expr_node["type"] == "LiteralExpression":
            val_str = str(expr_node.get("value", "0"))
            # naive logic...
            if "." in val_str:
                guessed = "f32"
            else:
                try:
                    val = int(val_str)
                    guessed = "i64" if abs(val) > 2147483647 else "i32"
                except ValueError:
                    guessed = "f32"
            # unify with context?
            if context_type:
                return self._unify_types(guessed, context_type)
            else:
                return guessed
        ...
        # fallback => i32
        return "i32"


    def _unify_types(self, t1, t2):
        """
        If either is 'higher' in numeric precedence, pick that. 
        i32 < i64 < f32 < f64
        """
        priority = {"i32": 1, "i64": 2, "f32": 3, "f64": 4}
        return t1 if priority[t1] >= priority[t2] else t2
