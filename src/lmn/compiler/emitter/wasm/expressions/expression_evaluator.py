# file: lmn/compiler/emitter/wasm/expressions/expression_evaluator.py
import logging

logger = logging.getLogger(__name__)

class ExpressionEvaluator:
    """
    A utility class to evaluate expressions for array literals.
    Supports:
      - LiteralExpression: returns the literal value.
      - UnaryExpression: supports unary '+' and '-'.
      - Can be extended to handle more expression types as needed.
    """

    @staticmethod
    def evaluate_expression(expr, expected_type='int'):
        """
        Evaluates an expression node and returns its value.

        :param expr: The expression node (dict).
        :param expected_type: 'int', 'long', 'float', or 'double' to determine type-specific checks.
        :return: Evaluated value (int or float).
        """
        node_type = expr.get("type")

        if node_type == "LiteralExpression":
            raw_val = expr.get("value", 0)
            if expected_type in ['int', 'long']:
                if not isinstance(raw_val, int):
                    logger.warning(
                        f"LiteralExpression with non-int value {raw_val}; defaulting to 0."
                    )
                    return 0
                return raw_val
            elif expected_type in ['float', 'double']:
                if not isinstance(raw_val, (int, float)):
                    logger.warning(
                        f"LiteralExpression with non-float value {raw_val}; defaulting to 0.0."
                    )
                    return 0.0
                return float(raw_val)

        elif node_type == "UnaryExpression":
            op = expr.get("operator")
            operand = expr.get("operand")
            operand_val = ExpressionEvaluator.evaluate_expression(operand, expected_type)

            if op == "-":
                return -operand_val
            elif op == "+":
                return operand_val
            else:
                logger.warning(f"Unsupported unary operator '{op}'; defaulting to 0.")
                return 0 if expected_type in ['int', 'long'] else 0.0

        else:
            logger.warning(f"Unhandled expression type '{node_type}'; defaulting to 0.")
            return 0 if expected_type in ['int', 'long'] else 0.0

    @staticmethod
    def clamp_value(val, expected_type):
        """
        Clamps the value based on the expected type's range.

        :param val: The value to clamp.
        :param expected_type: 'int', 'long', 'float', or 'double'.
        :return: Clamped value.
        """
        if expected_type == 'int':
            if not (-2**31 <= val <= 2**31 - 1):
                logger.warning(f"Value {val} out of 32-bit range; clamping.")
                return max(min(val, 2**31 - 1), -2**31)
        elif expected_type == 'long':
            if not (-2**63 <= val <= 2**63 - 1):
                logger.warning(f"Value {val} out of 64-bit range; clamping.")
                return max(min(val, 2**63 - 1), -2**63)
        # For floats and doubles, clamping is typically not required, but you can handle special cases if needed
        return val
