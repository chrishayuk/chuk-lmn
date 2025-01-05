# file: lmn/compiler/ast/statements/let_statement.py
from __future__ import annotations
from typing import Literal, Optional
from lmn.compiler.ast.statements.statement_base import StatementBase

class LetStatement(StatementBase):
    """
    Represents a 'set' statement, e.g.:
      let <variable> = <expression>
    But we also allow no initializer: set x
    """
    # set the type of this node to be 'LET'
    type: Literal["LetStatement"] = "LetStatement"

    # the variable should be an expression
    variable: "Expression"

    # optional expression
    expression: Optional["Expression"] = None
    inferred_type: Optional[str] = None

    def __str__(self):
        # if expression is None, just print 'set variable'
        if self.expression is None:
            # output the node as a string
            return f"let {self.variable}"
        
        # print the statement as a string
        return f"let {self.variable} = {self.expression}"
