import logging

from lmn.compiler.typechecker.statements.base_statement_checker import BaseStatementChecker
from lmn.compiler.typechecker.utils import normalize_type

logger = logging.getLogger(__name__)

class FunctionDefinitionChecker(BaseStatementChecker):
    """
    A checker for FunctionDefinition nodes that allows:
      - No declared return type => infer from body
      - Declared -> T => unify with each return
      - Declared -> void => no return expressions allowed
    """

    def check(self, func_def):
        func_name = func_def.name
        logger.debug(f"=== Checking FunctionDefinition '{func_name}' ===")

        # ------------------------------------------------------------
        # 1) Gather parameters
        # ------------------------------------------------------------
        param_names = []
        param_types = []
        param_defaults = []

        for param in func_def.params:
            param_names.append(param.name)
            declared_type = getattr(param, "type_annotation", None) or "int"
            declared_type = normalize_type(declared_type)
            param_types.append(declared_type)

            has_default = hasattr(param, "default_value")
            param_defaults.append(param.default_value if has_default else None)

        logger.debug(
            f"[{func_name}] Gathered {len(param_names)} params => {list(zip(param_names, param_types))}"
        )

        # ------------------------------------------------------------
        # 2) Determine declared_return_type
        # ------------------------------------------------------------
        maybe_declared = getattr(func_def, "return_type", None)
        if maybe_declared:
            declared_return_type = normalize_type(maybe_declared)
            logger.debug(f"[{func_name}] Found declared return type => '{declared_return_type}'")
        else:
            declared_return_type = None
            logger.debug(f"[{func_name}] No declared return type => using None")

        # ------------------------------------------------------------
        # 3) Store an initial function signature in the symbol table
        # ------------------------------------------------------------
        # We'll store "void" if there's no declared type,
        # but local_scope can override with None if we’re inferring.
        initial_table_return_type = declared_return_type if declared_return_type else "void"
        self.symbol_table[func_name] = {
            "param_names": param_names[:],
            "param_types": param_types[:],
            "param_defaults": param_defaults[:],
            "return_type": initial_table_return_type
        }

        logger.debug(
            f"[{func_name}] Wrote to symbol table => return_type={initial_table_return_type}"
        )

        # ------------------------------------------------------------
        # 4) Create local scope
        # ------------------------------------------------------------
        local_scope = dict(self.symbol_table)
        local_scope["__current_function_return_type__"] = declared_return_type
        assigned_vars = local_scope.get("__assigned_vars__", set())

        for i, p_name in enumerate(param_names):
            local_scope[p_name] = param_types[i]
            assigned_vars.add(p_name)

        local_scope["__assigned_vars__"] = assigned_vars

        logger.debug(
            f"[{func_name}] local_scope['__current_function_return_type__']="
            f"{local_scope['__current_function_return_type__']}"
        )
        logger.debug(
            f"[{func_name}] local_scope param bindings => "
            f"{', '.join([f'{p}={local_scope[p]}' for p in param_names])}"
        )

        # ------------------------------------------------------------
        # 5) Type-check the function body
        # ------------------------------------------------------------
        logger.debug(f"[{func_name}] Starting to type-check the function body...")
        for stmt in func_def.body:
            self.dispatcher.check_statement(stmt, local_scope)

            # After each statement, let's see if return type changed
            current_ret = local_scope.get("__current_function_return_type__", None)
            logger.debug(
                f"[{func_name}] After checking stmt='{stmt.type}', "
                f"__current_function_return_type__={current_ret}"
            )

        # ------------------------------------------------------------
        # 6) Finalize the function's return type
        # ------------------------------------------------------------
        final_return_type = local_scope.get("__current_function_return_type__")
        if final_return_type is None:
            # Means no 'return' was ever set => void
            final_return_type = "void"

        logger.debug(
            f"[{func_name}] Finalizing return type => {final_return_type}"
        )

        # Update symbol table
        fn_info = self.symbol_table[func_name]
        fn_info["return_type"] = final_return_type
        self.symbol_table[func_name] = fn_info

        # Also update the AST node
        func_def.return_type = final_return_type

        # ------------------------------------------------------------
        # 7) Persist updated param types back into the AST
        # ------------------------------------------------------------
        for i, param in enumerate(func_def.params):
            param.type_annotation = param_types[i]

        logger.debug(
            f"=== Finished type-checking function '{func_name}' => "
            f"return_type={final_return_type}, param_types={param_types} ==="
        )
        logger.debug("")
