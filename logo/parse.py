import collections
import itertools

import ply.yacc as yacc

from .lexer import TokenType, lexer, tokens


BinaryOperation = collections.namedtuple('BinaryOperation', 'op left right')

NotOperation = collections.namedtuple('NotOperation', 'expression')

WhileStatement = collections.namedtuple('WhileStatement', 'condition body')
IfStatement = collections.namedtuple('IfStatement', 'condition body else_body')

Assignment = collections.namedtuple('Assignment', 'variable value')

DeclareFunction = collections.namedtuple('DeclareFunction', 'name args body')
InvokeFunction = collections.namedtuple('InvokeFunction', 'name args')

Identifier = collections.namedtuple('Identifier', 'value')

Node = collections.namedtuple('Node', 'children')
Leaf = collections.namedtuple('Leaf', 'value')


def flatten(iterable):
    return list(itertools.chain(*iterable))


def filter_none(elements):
    return list(filter(lambda x: x is not None, elements))


def to_list(p):
    if len(p) > 2:
        if p[2] is None:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]]
            p[0].extend(p[2])


def p_program(p):
    """program : statement_list"""
    p[0] = p[1]


def p_statement_list(p):
    """statement_list : statement statement_list
                      |
    """
    to_list(p)


def p_statement(p):
    """statement : invoke_function
                 | assignment
                 | declare_func
                 | if
                 | while
    """
    p[0] = p[1]


def p_invoke_function(p):
    """invoke_function : ID function_args"""
    p[0] = InvokeFunction(p[1], args=p[2])


def p_function_args(p):
    """function_args : function_arg function_args
                     |
    """
    to_list(p)


def p_function_arg(p):
    """function_arg : COLON ID
                    | expression
    """
    if len(p) > 2:
        p[0] = p[2]
    else:
        p[0] = p[1]


def p_declare_func(p):
    'declare_func : TO ID declare_func_args statement_list END'
    p[0] = DeclareFunction(p[2], p[3], p[4])


def p_declare_func_args(p):
    """declare_func_args : declare_func_arg declare_func_args
                         |
    """
    to_list(p)


def p_declare_func_arg(p):
    'declare_func_arg : COLON ID'
    p[0] = p[2]


def p_if(p):
    """if : IF bool_expression THEN statement_list END"""
    p[0] = IfStatement(p[2], p[4], else_body=None)


def p_if_else(p):
    """if : IF bool_expression THEN statement_list ELSE statement_list END"""
    p[0] = IfStatement(p[2], p[4], p[6])


def p_while(p):
    """while : WHILE bool_expression statement_list END"""
    p[0] = WhileStatement(p[2], p[3])


def p_assignment(p):
    """assignment : SET ID EQUAL expression"""
    p[0] = Assignment(p[2], p[4])


def p_expression(p):
    '''expression : bool_expression
                  | math_expression
    '''
    p[0] = p[1]


def p_bool_expression_and(p):
    'bool_expression : bool_expression AND bool_expression'
    p[0] = BinaryOperation(TokenType.AND, p[1], p[3])


def p_bool_expression_or(p):
    'bool_expression : bool_expression OR bool_expression'
    p[0] = BinaryOperation(TokenType.OR, p[1], p[3])


def p_bool_expression(p):
    'bool_expression : bool_expression_not'
    p[0] = p[1]


def p_bool_expression_p(p):
    'bool_expression_eq : LPAREN bool_expression RPAREN'
    p[0] = p[2]


def p_bool_expression_not(p):
    'bool_expression_not : NOT bool_expression_eq'
    p[0] = NotOperation(p[2])


def p_bool_expression_not_e(p):
    'bool_expression_not : bool_expression_eq'
    p[0] = p[1]


def p_bool_expression_gt(p):
    'bool_expression_eq : math_expression GREATER_THAN math_expression'
    p[0] = BinaryOperation(TokenType.GREATER_THAN, p[1], p[3])


def p_bool_expression_gte(p):
    'bool_expression_eq : math_expression GREATER_EQUAL math_expression'
    p[0] = BinaryOperation(TokenType.GREATER_EQUAL, p[1], p[3])


def p_bool_expression_lt(p):
    'bool_expression_eq : math_expression LESS_THAN math_expression'
    p[0] = BinaryOperation(TokenType.LESS_THAN, p[1], p[3])


def p_bool_expression_lte(p):
    'bool_expression_eq : math_expression LESS_EQUAL math_expression'
    p[0] = BinaryOperation(TokenType.LESS_EQUAL, p[1], p[3])


def p_bool_expression_eq(p):
    'bool_expression_eq : math_expression IS_EQUAL math_expression'
    p[0] = BinaryOperation(TokenType.IS_EQUAL, p[1], p[3])


def p_bool_expression_neq(p):
    'bool_expression_eq : math_expression NOT_EQUAL math_expression'
    p[0] = BinaryOperation(TokenType.NOT_EQUAL, p[1], p[3])


def p_math_expression_plus(p):
    'math_expression : math_expression PLUS term'
    p[0] = BinaryOperation(TokenType.PLUS, p[1], p[3])


def p_math_expression_minus(p):
    'math_expression : math_expression MINUS term'
    p[0] = BinaryOperation(TokenType.MINUS, p[1], p[3])


def p_math_expression_term(p):
    'math_expression : term'
    p[0] = p[1]


def p_term_times(p):
    'term : term TIMES pow'
    p[0] = BinaryOperation(TokenType.TIMES, p[1], p[3])


def p_term_div(p):
    'term : term DIVIDE pow'
    p[0] = BinaryOperation(TokenType.DIVIDE, p[1], p[3])


def p_term_factor(p):
    'term : pow'
    p[0] = p[1]


def p_pow(p):
    'pow : factor POW factor'
    p[0] = BinaryOperation(TokenType.POW, p[1], p[3])


def p_pow_factor(p):
    'pow : factor'
    p[0] = p[1]


def p_factor_num(p):
    'factor : NUMBER'
    p[0] = p[1]


def p_factor_id(p):
    'factor : id'
    p[0] = p[1]


def p_id(p):
    'id : ID'
    p[0] = Identifier(p[1])


def p_factor_expr(p):
    'factor : LPAREN math_expression RPAREN'
    p[0] = p[2]


# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")


parser = yacc.yacc()

