# file: lmn/compiler/emitter/wasm/expressions/expression_evaluator.py
import logging

logger = logging.getLogger(__name__)

class ExpressionEvaluator:
    """
    A utility class to evaluate expressions for array literals.
    Supports:
      - LiteralExpression: returns the literal value.
      - UnaryExpression: supports unary '+' and '-'.
      - More expression types can be added as needed.
    """

    @staticmethod
    def evaluate_expression(expr, expected_type='i32'):
        """
        Evaluates an expression node and returns its value.

        :param expr: The expression node (dict).
        :param expected_type: One of ('i32', 'i64', 'f32', 'f64') or the older
                              ('int', 'long', 'float', 'double').
        :return: Evaluated value (int or float).
        """

        # Map any old type names to the new ones
        mapped_type = ExpressionEvaluator._map_expected_type(expected_type)

        node_type = expr.get("type")

        if node_type == "LiteralExpression":
            raw_val = expr.get("value", 0)

            if mapped_type in ('i32', 'i64'):
                # Expect an integer
                if not isinstance(raw_val, int):
                    logger.warning(
                        f"LiteralExpression with non-integer value {raw_val}; defaulting to 0."
                    )
                    return 0
                return raw_val

            elif mapped_type in ('f32', 'f64'):
                # Expect a float/double
                if not isinstance(raw_val, (int, float)):
                    logger.warning(
                        f"LiteralExpression with non-float value {raw_val}; defaulting to 0.0."
                    )
                    return 0.0
                return float(raw_val)

        elif node_type == "UnaryExpression":
            op = expr.get("operator")
            operand = expr.get("operand")
            operand_val = ExpressionEvaluator.evaluate_expression(operand, mapped_type)

            if op == "-":
                return -operand_val
            elif op == "+":
                return operand_val
            else:
                logger.warning(f"Unsupported unary operator '{op}'; defaulting to 0.")
                return 0 if mapped_type in ('i32', 'i64') else 0.0

        else:
            logger.warning(f"Unhandled expression type '{node_type}'; defaulting to 0.")
            return 0 if mapped_type in ('i32', 'i64') else 0.0

    @staticmethod
    def clamp_value(val, expected_type):
        """
        Clamps the value based on the expected type's range (for i32 or i64).
        Float types typically do not require clamping, but can be extended if needed.

        :param val: The value to clamp.
        :param expected_type: One of ('i32', 'i64') or older ('int', 'long').
        :return: Clamped value.
        """
        mapped_type = ExpressionEvaluator._map_expected_type(expected_type)

        if mapped_type == 'i32':
            if not (-2**31 <= val <= 2**31 - 1):
                logger.warning(f"Value {val} out of 32-bit (i32) range; clamping.")
                return max(min(val, 2**31 - 1), -2**31)
        elif mapped_type == 'i64':
            if not (-2**63 <= val <= 2**63 - 1):
                logger.warning(f"Value {val} out of 64-bit (i64) range; clamping.")
                return max(min(val, 2**63 - 1), -2**63)

        # For f32/f64 (and older 'float'/'double'), we don't forcibly clamp here
        return val

    @staticmethod
    def _map_expected_type(expected_type: str) -> str:
        """
        Internal helper to convert older type names ('int', 'long', 'float', 'double')
        to the new lowered types ('i32', 'i64', 'f32', 'f64').
        """
        mapping = {
            'int': 'i32',
            'long': 'i64',
            'float': 'f32',
            'double': 'f64',
        }
        # If already a new name, returns it as-is; otherwise maps to new name or defaults to 'i32'.
        return mapping.get(expected_type, expected_type if expected_type in ('i32','i64','f32','f64') else 'i32')
