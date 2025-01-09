# file: lmn/compiler/emitter/wasm/program_emitter.py

import logging
logger = logging.getLogger(__name__)

from lmn.compiler.emitter.wasm.param_utils import normalize_params

# Import your closure emitter
from lmn.compiler.emitter.wasm.closure_function_emitter import ClosureFunctionEmitter

class ProgramEmitter:
    """
    Handles top-level 'Program' logic:
      - Splitting out function defs vs. leftover statements
      - Rewriting inline/lambda functions in let statements
      - Emitting final function definitions
      - Building a __top_level__ function if needed
    """

    def __init__(self, wasm_emitter):
        """
        :param wasm_emitter: an instance of WasmEmitter that does the
                             lower-level function/statement emission
        """
        self.wasm_emitter = wasm_emitter

        # Create a closure emitter to handle "AnonymousFunction" codegen
        self.closure_emitter = ClosureFunctionEmitter(self.wasm_emitter)

    def emit_program(self, ast):
        """
        Main entry point for converting a top-level AST into WAT (module) lines.
        1) Separate function defs from leftover statements
        2) Rewrite 'let' statements in function bodies
        3) Rewrite 'let' statements in top-level statements
        4) Emit all function definitions
        5) If leftover statements remain, build a '__top_level__' function
        6) Build final (module ...) text
        """
        if ast["type"] != "Program":
            raise ValueError("AST root must be 'Program'")

        body_nodes = ast.get("body", [])
        logger.debug(
            "ProgramEmitter.emit_program: Handling top-level AST with %d nodes",
            len(body_nodes)
        )

        # 1) Separate function defs vs. leftover statements
        function_defs, top_level_stmts = [], []
        for node in body_nodes:
            if node["type"] == "FunctionDefinition":
                function_defs.append(node)
            else:
                top_level_stmts.append(node)

        logger.debug(
            "emit_program: found %d function defs, %d top-level statements",
            len(function_defs),
            len(top_level_stmts)
        )

        # 2) Rewrite let statements inside each function body
        for fn_node in function_defs:
            fn_name = fn_node.get("name", "<unnamed>")
            fn_body = fn_node.get("body", [])
            logger.debug("emit_program: rewriting let statements in function '%s'", fn_name)
            fn_node["body"] = self.rewrite_lets_in_function_body(fn_body)

        # 3) Rewrite let statements in top-level statements
        logger.debug("emit_program: rewriting let statements in top-level statements")
        rewritten_top = self.rewrite_lets_in_function_body(top_level_stmts)

        # 4) Emit each function definition
        for fn_node in function_defs:
            self.emit_function_definition(fn_node)

        # 5) If leftover statements remain => put them in __top_level__
        if rewritten_top:
            logger.debug(
                "emit_program: leftover top-level statements => building '__top_level__'"
            )
            self.emit_top_level_statements_function(rewritten_top)
        else:
            logger.debug(
                "emit_program: no leftover statements => no '__top_level__' function needed"
            )

        # 6) Build final (module ...) WAT
        logger.debug("emit_program: building final module via wasm_emitter.build_module()")
        return self.wasm_emitter.build_module()

    def rewrite_lets_in_function_body(self, stmts):
        """
        Recursively scans 'stmts' for:
         - inline function definitions (actual lambda)
         - function calls
         - aliases
        and lifts them if needed.

        Returns a new list of statements with modifications (e.g., replaced
        inline lambdas or function aliases).
        """
        out = []
        for stmt in stmts:
            stype = stmt["type"]
            logger.debug(
                "rewrite_lets_in_function_body: stmt type='%s' => %s",
                stype, stmt
            )

            if stype == "LetStatement":
                var_name = stmt["variable"]["name"]
                expr = stmt.get("expression")
                expr_type = expr.get("type") if expr else None

                logger.debug(
                    "  LetStatement: var='%s', expr_type='%s'",
                    var_name, expr_type
                )

                if expr and expr_type in ("FnExpression", "AnonymousFunction"):
                    # Distinguish a *true* inline lambda vs. a *function call*
                    if expr_type == "AnonymousFunction" or not expr.get("name"):
                        # => Real inline lambda => produce a closure function
                        closure_id = self.wasm_emitter.function_counter
                        self.wasm_emitter.function_counter += 1
                        closure_name = f"closure_fn_{closure_id}"

                        logger.debug(
                            "  Lifting inline function '%s' => '%s' (anonymous/lambda)",
                            var_name, closure_name
                        )

                        # If you track captures, gather them here; else empty
                        environment_layout = {}

                        closure_func_name = self.closure_emitter.emit_closure_function(
                            expr,  # the closure AST node
                            closure_id,
                            environment_layout
                        )

                        # In advanced scenarios, you might store closure_func_name in a table
                        # or alias var_name => closure_func_name for direct calls.
                        self.wasm_emitter.func_alias_map[var_name] = closure_func_name

                        # Don’t append this LetStatement => it’s replaced by the alias
                        continue
                    else:
                        # => It's a normal function call => do not lift
                        # e.g. let add5 = closure_adder(5)
                        logger.debug(
                            "  FnExpression with 'name': interpret as function call => no lifting for '%s'",
                            var_name
                        )
                        out.append(stmt)
                elif expr and expr_type == "VariableExpression":
                    # let X = someFunc => direct alias
                    aliased_name = expr["name"]
                    logger.debug(
                        "  Found let alias: %s -> %s",
                        var_name, aliased_name
                    )
                    self.wasm_emitter.func_alias_map[var_name] = aliased_name
                    continue
                else:
                    # Normal let statement => keep
                    logger.debug(
                        "  Keeping normal let statement for '%s'", var_name
                    )
                    out.append(stmt)

            elif stype in ("IfStatement", "ForStatement", "WhileStatement"):
                # Recurse into sub-bodies
                logger.debug("  Handling conditional/loop statement => recursing into sub-bodies")
                if stype == "IfStatement":
                    if "thenBody" in stmt:
                        stmt["thenBody"] = self.rewrite_lets_in_function_body(stmt["thenBody"])
                    for eclause in stmt.get("elseifClauses", []):
                        eclause["body"] = self.rewrite_lets_in_function_body(eclause["body"])
                    if "elseBody" in stmt:
                        stmt["elseBody"] = self.rewrite_lets_in_function_body(stmt["elseBody"])
                elif stype == "ForStatement" and "body" in stmt:
                    stmt["body"] = self.rewrite_lets_in_function_body(stmt["body"])
                elif stype == "WhileStatement" and "body" in stmt:
                    stmt["body"] = self.rewrite_lets_in_function_body(stmt["body"])

                out.append(stmt)

            elif stype == "FunctionDefinition":
                # Nested function definition => rewrite inside
                logger.debug("  Found nested function definition => rewriting its body")
                body_stmts = stmt.get("body", [])
                stmt["body"] = self.rewrite_lets_in_function_body(body_stmts)
                out.append(stmt)
            else:
                # Keep statement as is
                logger.debug("  Keeping statement type='%s' as is", stype)
                out.append(stmt)

        return out

    def emit_function_definition(self, node):
        """
        For explicit function definitions or "lifted" inline definitions.
        """
        func_name = node.get("name", f"fn_{self.wasm_emitter.function_counter}")
        self.wasm_emitter.function_counter += 1
        self.wasm_emitter.function_names.append(func_name)

        logger.debug("emit_function_definition: function '%s'", func_name)

        # Normalize params (helps unify param shape, e.g. param name + type)
        node["params"] = normalize_params(node["params"])

        func_lines = []
        self.wasm_emitter.function_emitter.emit_function(node, func_lines)
        self.wasm_emitter.functions.append(func_lines)
        logger.debug(
            "emit_function_definition: appended function '%s' => total lines=%d",
            func_name, len(func_lines)
        )

    def emit_top_level_statements_function(self, statements):
        """
        If leftover statements remain after function defs,
        create a __top_level__ function to hold them.
        """
        func_name = "__top_level__"
        logger.debug(
            "emit_top_level_statements_function: creating '%s' with %d stmts",
            func_name, len(statements)
        )

        self.wasm_emitter.function_names.append(func_name)

        # Reset local tracking
        self.wasm_emitter.new_locals = set()
        self.wasm_emitter.func_local_map = {}
        self.wasm_emitter.local_counter = 0

        func_lines = [f'(func ${func_name}']
        for i, stmt in enumerate(statements):
            logger.debug(
                "emit_top_level_statements_function: emitting statement[%d] => %s", 
                i, stmt
            )
            self.wasm_emitter.emit_statement(stmt, func_lines)

        # Insert local declarations
        local_decls = []
        for var_name in self.wasm_emitter.new_locals:
            if var_name not in self.wasm_emitter.func_local_map:
                self.wasm_emitter.func_local_map[var_name] = {
                    "index": self.wasm_emitter.local_counter,
                    "type": "i32"
                }
                self.wasm_emitter.local_counter += 1

            local_wasm_type = self.wasm_emitter._wasm_basetype(
                self.wasm_emitter.func_local_map[var_name]["type"]
            )
            norm_name = self.wasm_emitter._normalize_local_name(var_name)
            local_decls.append(f'  (local {norm_name} {local_wasm_type})')

        if local_decls:
            logger.debug(
                "emit_top_level_statements_function: inserting %d local declarations",
                len(local_decls)
            )

        # Insert them right after the '(func $__top_level__'
        func_lines[1:1] = local_decls
        func_lines.append(')')

        self.wasm_emitter.functions.append(func_lines)
        logger.debug(
            "emit_top_level_statements_function: finished building '%s', total lines=%d",
            func_name, len(func_lines)
        )
