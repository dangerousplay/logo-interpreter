import collections
import itertools

import ply.yacc as yacc

from .lexer import TokenType, lexer, tokens, ARITHMETIC_OPERATORS, BOOL_CONDITION_OPERATORS

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
    """if : IF LPAREN expression RPAREN THEN statement_list  END"""
    _assert_bool_expression_(p[3])

    p[0] = IfStatement(p[3], p[6], else_body=None)


def p_if_else(p):
    """if : IF LPAREN expression RPAREN THEN statement_list ELSE statement_list END"""
    _assert_bool_expression_(p[3])

    p[0] = IfStatement(p[3], p[6], p[8])


def p_while(p):
    """while : WHILE LPAREN expression RPAREN statement_list END"""
    _assert_bool_expression_(p[3])

    p[0] = WhileStatement(p[3], p[5])


def p_assignment(p):
    """assignment : ID EQUAL expression"""
    p[0] = Assignment(p[1], p[3])


def p_expression_and(p):
    'expression : expression AND expression'
    p[0] = BinaryOperation(TokenType.AND, p[1], p[3])


def p_bool_expression_or(p):
    'expression : expression OR expression'
    p[0] = BinaryOperation(TokenType.OR, p[1], p[3])


def p_expression_string(p):
    'expression : STRING'
    p[0] = p[1]

def p_bool_expression(p):
    'expression : expression_not'
    p[0] = p[1]


def p_bool_expression_not(p):
    'expression_not : NOT bool_expression_eq'
    p[0] = NotOperation(p[2])


def p_bool_expression_not_e(p):
    'expression_not : bool_expression_eq'
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


def p_bool_expression_m(p):
    'bool_expression_eq : math_expression'
    p[0] = p[1]


def p_bool_expression_value(p):
    """bool_expression_eq : TRUE
                          | FALSE
    """
    p[0] = to_bool(p[1])


def p_expression_p(p):
    'bool_expression_eq : LPAREN expression RPAREN'
    p[0] = p[2]


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
    """id : COLON ID"""
    p[0] = Identifier(p[2])

def p_factor_expr(p):
    'factor : LPAREN math_expression RPAREN'
    p[0] = p[2]


def _assert_bool_expression_(p):
    if isinstance(p, (Identifier, bool)):
        return
    elif isinstance(p, BinaryOperation):
        _assert_bool_condition_(p)
    elif isinstance(p, NotOperation):
        _assert_bool_condition_(p.expression)
    else:
        raise Exception(f"Unexpected token for boolean expression: {p}")


def _assert_bool_condition_(p: BinaryOperation):
    if p.op in ARITHMETIC_OPERATORS:
        raise Exception(f"Unexpected math operator in bool expression: Line {p}")

    if p.op in BOOL_CONDITION_OPERATORS:
        _assert_bool_expression_(p.left)
        _assert_bool_expression_(p.right)


def to_bool(bool_str):
    """Parse the string and return the boolean value encoded or raise an exception"""
    if isinstance(bool_str, str) and bool_str:
        if bool_str.lower() in ['true', 't', '1']:
            return True
        elif bool_str.lower() in ['false', 'f', '0']:
            return False

    # if here we couldn't parse it
    raise ValueError("%s is no recognized as a boolean value" % bool_str)


# Error rule for syntax errors
def p_error(token):
    if token:
        raise Exception(
            f"Unexpected token:{token.lineno}: {token.type}:'{token.value}'"
        )

    raise Exception("Syntax error at EOF.")


parser = yacc.yacc()
