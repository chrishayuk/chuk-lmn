# file: lmn/compiler/emitter/wasm/expressions/variable_expression_emitter.py

class VariableExpressionEmitter:
    def __init__(self, controller):
        """
        The 'controller' is a reference to your main WasmEmitter or similar.
        We'll typically do something like 'local.get $var_name' or
        'global.get $var_name' depending on how variables are stored.
        """
        self.controller = controller

    def emit(self, node, out_lines):
        """
        Example node structure:
          {
            "type": "VariableExpression",
            "name": "x"
          }

        We assume 'x' is a local variable for now, so we'll do 'local.get $x'.
        If it were a global, you'd use 'global.get $x' or something similar.

        We also normalize names so that:
          - "x"      => "$x"
          - "$$thing" => "$thing"
          - "$already" => "$already"
          - anything else is handled accordingly
        """
        raw_name = node["name"]
        normalized_name = self._normalize_local_name(raw_name)

        # Emit a local.get with the normalized name.
        out_lines.append(f'  local.get {normalized_name}')

    def _normalize_local_name(self, var_name: str) -> str:
        """
        Conforms to the test's expected rules:
         - If var_name starts with '$$', convert to a single '$'.
         - If var_name starts with a single '$', leave it as-is.
         - Otherwise, prepend a single '$'.
        """
        if var_name.startswith('$$'):
            # e.g. "$$thing" => "$thing"
            return f'${var_name[2:]}'
        elif var_name.startswith('$'):
            # e.g. "$already" => "$already"
            return var_name
        else:
            # e.g. "x" => "$x"
            return f'${var_name}'
