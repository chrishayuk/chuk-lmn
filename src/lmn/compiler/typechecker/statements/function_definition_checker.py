# file: lmn/compiler/typechecker/statements/function_definition_checker.py
import logging

# lmn imports
from lmn.compiler.typechecker.statements.base_statement_checker import BaseStatementChecker
from lmn.compiler.typechecker.utils import normalize_type

# logger
logger = logging.getLogger(__name__)

class FunctionDefinitionChecker(BaseStatementChecker):
    """
    A checker for FunctionDefinition nodes.
    """

    def check(self, func_def):
        """
        1. Gather param metadata (names, declared types, defaults).
        2. Store them (and a preliminary return_type) in symbol_table[func_name].
        3. Create a local scope, type-check function body => unify final return type.
        4. Update symbol_table & the AST node with final return type & param types.
        """
        func_name = func_def.name

        # --------------------------------------------------------------------
        # 1) Gather parameters
        # --------------------------------------------------------------------
        param_names = []
        param_types = []
        param_defaults = []

        for param in func_def.params:
            param_names.append(param.name)

            declared_type = getattr(param, "type_annotation", None) or "int"
            declared_type = normalize_type(declared_type)
            param_types.append(declared_type)

            if hasattr(param, "default_value"):
                param_defaults.append(param.default_value)
            else:
                param_defaults.append(None)

        # 2) Preliminary return type (could be overridden by final unification)
        declared_return_type = getattr(func_def, "return_type", None) or "void"
        declared_return_type = normalize_type(declared_return_type)

        # --------------------------------------------------------------------
        # 3) Store an initial function signature in the symbol table
        # --------------------------------------------------------------------
        self.symbol_table[func_name] = {
            "param_names":    param_names,
            "param_types":    param_types[:],   # make a copy if you like
            "param_defaults": param_defaults,
            "return_type":    declared_return_type
        }

        # --------------------------------------------------------------------
        # 4) Create a local scope and add parameters
        # --------------------------------------------------------------------
        local_scope = dict(self.symbol_table)
        local_scope["__current_function_return_type__"] = declared_return_type

        for i, p_name in enumerate(param_names):
            # Add parameters to the local scope
            local_scope[p_name] = param_types[i]

        # --------------------------------------------------------------------
        # 5) Type-check the function body. ReturnStatements unify the final return type.
        # --------------------------------------------------------------------
        for stmt in func_def.body:
            self.dispatcher.check_statement(stmt, local_scope)

        # --------------------------------------------------------------------
        # 6) Finalize the function's return type
        # --------------------------------------------------------------------
        final_return_type = local_scope.get("__current_function_return_type__", "void")

        # Store the unified return type back into the symbol table
        fn_info = self.symbol_table[func_name]
        fn_info["return_type"] = final_return_type
        self.symbol_table[func_name] = fn_info

        # Also update the function-def node
        func_def.return_type = final_return_type

        # --------------------------------------------------------------------
        # 7) Persist any updated param types back into the AST
        # --------------------------------------------------------------------
        for i, param in enumerate(func_def.params):
            param.type_annotation = param_types[i]

        logger.debug(
            f"Finished type-checking function '{func_name}' -> "
            f"return_type={final_return_type}, param_types={param_types}"
        )
