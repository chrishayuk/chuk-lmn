# compiler/ast/expressions/binry_operator.py
from enum import Enum

class BinaryOperator(str, Enum):
    PLUS = "+"
    MINUS = "-"
    MUL = "*"
    DIV = "/"
    EQ = "=="
    NEQ = "!="