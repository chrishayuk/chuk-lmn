# debug_fields.py
import sys
import json
from pprint import pprint

# Colorama imports
from colorama import init as colorama_init, Fore, Style

# Initialize colorama
colorama_init(autoreset=True)

from compiler.ast import (
    # Expressions
    LiteralExpression,
    VariableExpression,
    BinaryExpression,
    UnaryExpression,
    FnExpression,
    # Statements
    CallStatement,
    ForStatement,
    FunctionDefinition,
    IfStatement,
    PrintStatement,
    ReturnStatement,
    SetStatement,
)

def highlight_type_key(json_str: str) -> str:
    """
    Parses the JSON lines and highlights the \"type\" key in a different color.
    We'll color the entire JSON green, but if a line has \"type\": we highlight it in yellow.
    """
    lines = json_str.splitlines()
    colored_lines = []
    for line in lines:
        if '"type":' in line:
            # Replace just the "type": portion with a different color
            line = line.replace(
                '"type":',
                f'{Fore.YELLOW}"type":{Fore.GREEN}'
            )
            colored_lines.append(Fore.GREEN + line + Style.RESET_ALL)
        else:
            # color the whole line green
            colored_lines.append(Fore.GREEN + line + Style.RESET_ALL)
    return "\n".join(colored_lines)

def print_colored_dictionaries(node):
    """
    Pretty-print the results of .model_dump(by_alias=True) using pprint,
    and colorize the JSON version.
    """
    # Force by_alias=True so we see fields like "thenBody" rather than "then_body"
    d = node.model_dump(by_alias=True)
    
    # 1) Python dict (uncolored, just use pprint)
    print(f"{Fore.CYAN}to_dict() => (by_alias=True){Style.RESET_ALL}")
    pprint(d, width=120, sort_dicts=False)
    print()

    # 2) JSON dump of the same dict, color the text
    print(f"{Fore.MAGENTA}model_dump() => (by_alias=True){Style.RESET_ALL}")
    json_str = json.dumps(d, indent=2, default=str)
    colored_str = highlight_type_key(json_str)
    print(colored_str)
    print()

# --- Show Currently Imported ---
print(f"{Fore.YELLOW}Currently imported modules:{Style.RESET_ALL}")
for m in sorted(sys.modules):
    if "compiler.ast" in m:
        print(m)

# -------------------------------------------------------------------
#  Debug: Expressions
# -------------------------------------------------------------------
print(f"{Fore.GREEN}==== Debugging test_literal_int ===={Style.RESET_ALL}")
lit_int = LiteralExpression(value="5")
print_colored_dictionaries(lit_int)

print(f"{Fore.GREEN}==== Debugging test_literal_float ===={Style.RESET_ALL}")
lit_float = LiteralExpression(value="3.14")
print_colored_dictionaries(lit_float)

print(f"{Fore.GREEN}==== Debugging test_literal_string ===={Style.RESET_ALL}")
lit_string = LiteralExpression(value="hello")
print_colored_dictionaries(lit_string)

print(f"{Fore.GREEN}==== Debugging test_binary_expression ===={Style.RESET_ALL}")
left = LiteralExpression(value="5")
right = LiteralExpression(value="3")
bin_expr = BinaryExpression(operator="+", left=left, right=right)
print_colored_dictionaries(bin_expr)

print(f"{Fore.GREEN}==== Debugging test_unary_expression ===={Style.RESET_ALL}")
operand = LiteralExpression(value="10")
un_expr = UnaryExpression(operator="-", operand=operand)
print_colored_dictionaries(un_expr)

print(f"{Fore.GREEN}==== Debugging test_fn_expression_single_arg ===={Style.RESET_ALL}")
name_fact = VariableExpression(name="fact")
arg_5 = LiteralExpression(value="5")
fn_expr_single = FnExpression(name=name_fact, arguments=[arg_5])
print_colored_dictionaries(fn_expr_single)

print(f"{Fore.GREEN}==== Debugging test_fn_expression_multiple_args ===={Style.RESET_ALL}")
name_sum = VariableExpression(name="sum")
arg_a = VariableExpression(name="a")
arg_b = VariableExpression(name="b")
arg_10 = LiteralExpression(value="10")
fn_expr_multiple = FnExpression(name=name_sum, arguments=[arg_a, arg_b, arg_10])
print_colored_dictionaries(fn_expr_multiple)

# -------------------------------------------------------------------
#  Debug: Statements
# -------------------------------------------------------------------
print(f"{Fore.YELLOW}Currently imported modules:{Style.RESET_ALL}")
for m in sorted(sys.modules):
    if "compiler.ast" in m:
        print(m)

print(f"{Fore.BLUE}==== Debugging CallStatement ===={Style.RESET_ALL}")
call_stmt = CallStatement(tool_name="myTool", arguments=[lit_int, lit_float])
print_colored_dictionaries(call_stmt)

print(f"{Fore.BLUE}==== Debugging ForStatement ===={Style.RESET_ALL}")
for_stmt = ForStatement(
    variable=VariableExpression(name="i"),
    start_expr=LiteralExpression(value="1"),
    end_expr=LiteralExpression(value="5"),
    step_expr=LiteralExpression(value="1"),
    body=[
        PrintStatement(expressions=[VariableExpression(name="i")]),
        CallStatement(tool_name="innerTool", arguments=[LiteralExpression(value="99")])
    ]
)
print_colored_dictionaries(for_stmt)

print(f"{Fore.BLUE}==== Debugging FunctionDefinition ===={Style.RESET_ALL}")
func_def = FunctionDefinition(
    name="doSomething",
    params=["x", "y"],
    body=[
        SetStatement(
            variable=VariableExpression(name="x"),
            expression=BinaryExpression(
                operator="+",
                left=VariableExpression(name="x"),
                right=LiteralExpression(value="1")
            )
        ),
        PrintStatement(expressions=[VariableExpression(name="x"), VariableExpression(name="y")]),
    ]
)
print_colored_dictionaries(func_def)

print(f"{Fore.BLUE}==== Debugging IfStatement ===={Style.RESET_ALL}")
if_stmt = IfStatement(
    condition=BinaryExpression(
        operator="==",
        left=VariableExpression(name="x"),
        right=LiteralExpression(value="10")
    ),
    then_body=[PrintStatement(expressions=[LiteralExpression(value="x is 10!")])],
    else_body=[PrintStatement(expressions=[LiteralExpression(value="x is not 10")])]
)
print_colored_dictionaries(if_stmt)

print(f"{Fore.BLUE}==== Debugging PrintStatement ===={Style.RESET_ALL}")
pr_stmt = PrintStatement(expressions=[lit_string, VariableExpression(name="varXYZ")])
print_colored_dictionaries(pr_stmt)

print(f"{Fore.BLUE}==== Debugging ReturnStatement ===={Style.RESET_ALL}")
ret_stmt = ReturnStatement(
    expression=BinaryExpression(
        operator="*",
        left=VariableExpression(name="n"),
        right=FnExpression(
            name=VariableExpression(name="fact"),
            arguments=[
                BinaryExpression(operator="-", left=VariableExpression(name="n"), right=LiteralExpression(value="1"))
            ]
        )
    )
)
print_colored_dictionaries(ret_stmt)

print(f"{Fore.BLUE}==== Debugging SetStatement ===={Style.RESET_ALL}")
set_stmt = SetStatement(
    variable=VariableExpression(name="total"),
    expression=BinaryExpression(
        operator="+",
        left=VariableExpression(name="total"),
        right=LiteralExpression(value="5")
    )
)
print_colored_dictionaries(set_stmt)
