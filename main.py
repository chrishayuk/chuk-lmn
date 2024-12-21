# #from lexer.tokenizer import Tokenizer, TokenizationError

# # def read_basic_file(file_path):
# #     with open(file_path, 'r') as file:
# #         return file.read()

# # # Example usage
# # #file_path = 'samples/test1.bas'
# # file_path = 'samples/aceyducey.bas'
# # #file_path = 'samples/dartmouth_first.bas'
# # file_path = 'samples/complex.bas'

# # try:
# #     input_code = read_basic_file(file_path)
# #     tokenizer = Tokenizer(input_code)
# #     tokens = tokenizer.tokenize()
# #     for token in tokens:
# #         print(token)
# # except FileNotFoundError:
# #     print(f"File not found: {file_path}")
# # except TokenizationError as e:
# #     print(f"Tokenization error: {str(e)}")


# from compiler.parser.ast import PrintStatement, LetStatement, Literal, Program, Variable, BinaryExpression
# from compiler.lexer.tokenizer import Tokenizer, TokenizationError
# from compiler.parser.parser import Parser

# Sample BASIC-like program
# program = '''
# 10 LET X = 5
# 20 LET Y = 10
# 30 PRINT "The result is:"
# 40 PRINT X + Y
# 50 END
# '''

# print(program)

# # Tokenize the program
# tokenizer = Tokenizer(program)
# tokens = tokenizer.tokenize()

# print(tokens)

# # Parse the tokens into an AST
# parser = Parser(tokens)
# ast = parser.parse()

# print(ast)

# # Print the AST
# def print_ast(node, indent=''):
#     if isinstance(node, Program):
#         print(indent + 'Program')
#         for statement in node.statements:
#             print_ast(statement, indent + '  ')
#     elif isinstance(node, LetStatement):
#         print(indent + 'LetStatement')
#         print(indent + '  Variable:', node.variable.name)
#         print_ast(node.expression, indent + '  ')
#     elif isinstance(node, PrintStatement):
#         print(indent + 'PrintStatement')
#         print_ast(node.expression, indent + '  ')
#     # elif isinstance(node, IfStatement):
#     #     print(indent + 'IfStatement')
#     #     print_ast(node.condition, indent + '  ')
#     #     print(indent + '  Then:')
#     #     print_ast(node.then_block, indent + '    ')
#     # elif isinstance(node, ForStatement):
#     #     print(indent + 'ForStatement')
#     #     print(indent + '  Variable:', node.variable.name)
#     #     print(indent + '  Start:', node.start.value)
#     #     print(indent + '  End:', node.end.value)
#     #     print(indent + '  Step:', node.step.value if node.step else '1')
#     #     print(indent + '  Body:')
#     #     for statement in node.body:
#     #         print_ast(statement, indent + '    ')
#     # elif isinstance(node, NextStatement):
#     #     print(indent + 'NextStatement')
#     #     print(indent + '  Variable:', node.variable.name)
#     elif isinstance(node, BinaryExpression):
#         print(indent + 'BinaryExpression')
#         print(indent + '  Operator:', node.operator.value)
#         print_ast(node.left, indent + '  ')
#         print_ast(node.right, indent + '  ')
#     elif isinstance(node, Literal):
#         print(indent + 'Literal')
#         print(indent + '  Value:', node.value)
#     elif isinstance(node, Variable):
#         print(indent + 'Variable')
#         print(indent + '  Name:', node.name)

# print_ast(ast)

# Sample BASIC-like program
program = '''
10 LET X = 5
20 LET Y = 10
30 PRINT "The result is:"
40 PRINT X + Y
50 IF X < Y THEN PRINT "X is less than Y"
60 FOR I = 1 TO 5
70   PRINT I
80 NEXT I
'''

# Assuming you have a `parse` method in your `Parser` class that returns a `Program` instance
from compiler.lexer.tokenizer import Tokenizer
from compiler.ast.parser import Parser

input_string = program#'10 PRINT "Hello World"'
tokenizer = Tokenizer(input_string)
tokens = tokenizer.tokenize()
parser = Parser(tokens)
program = parser.parse()

# Get the JSON representation of the AST
ast_json = program.to_json()

# Print or save the JSON
print(ast_json)