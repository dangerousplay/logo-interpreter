import io
import os
import unittest
from itertools import combinations
from json import JSONEncoder

from ddt import ddt, data, unpack
from ply import yacc

from logo.parse import IfStatement, parser, BinaryOperation, WhileStatement, DeclareFunction, Assignment, \
    InvokeFunction, NotOperation, Identifier
from logo.lexer import lexer, TokenType, COMPARISON_OPERATORS, BOOL_CONDITION_OPERATORS
from logo.printer import print_program


def load_test_file(path: str):
    with io.open(path) as f:
        f.read()


def generate_statements():
    return [
        Assignment('AB', 1.0),
        Assignment('AB', Identifier('B')),
        IfStatement(BinaryOperation(TokenType.GREATER_THAN, Identifier('A'), Identifier('C')), None, None),
        WhileStatement(BinaryOperation(TokenType.GREATER_THAN, Identifier('B'), 2.0), None),
        DeclareFunction('FUNC', ['D', 'E'], None),
        InvokeFunction('FUNC', [Identifier('D'), Identifier('E')])
    ]


def generate_math_expressions():
    operators = [
        TokenType.MINUS,
        TokenType.PLUS,
        TokenType.TIMES,
        TokenType.DIVIDE,
        TokenType.POW,
    ]

    operands = [
        Identifier('X'),
        5.0,
        Identifier('Y'),
        2.0
    ]

    possibilities = []

    simple_operations = []

    for operator in operators:
        for left, right in list(combinations(operands, 2)):
            simple_operations.append(BinaryOperation(operator, left, right))

    possibilities.extend(simple_operations)

    return possibilities


def generate_bool_expressions():
    comparison_operands = [
        Identifier('X'),
        2.0,
        Identifier('Y'),
        1.0
    ]

    operands_pair = list(combinations(comparison_operands, 2))

    possibilities = []

    simple_comparisons = []

    for operator in COMPARISON_OPERATORS:
        for left, right in operands_pair:
            simple_comparisons.append(BinaryOperation(operator, left, right))

    possibilities.extend(simple_comparisons)

    combine_pairs = list(combinations(simple_comparisons, 2))

    boolean_values = list(combinations(
        [True, False, True],
        2
    ))

    for operator in BOOL_CONDITION_OPERATORS:
        for left, right in boolean_values:
            possibilities.append(BinaryOperation(operator, left, right))

        for left, right in combine_pairs:
            possibilities.append(BinaryOperation(operator, left, right))

    return possibilities


def generate_invalid_conditions():
    operands = [
        2.0,
        Identifier('x'),
        3.0
    ]

    possibilities = []

    operands_pair = list(combinations(operands, 2))

    for operator in BOOL_CONDITION_OPERATORS:
        for left, right in operands_pair:
            possibilities.append(BinaryOperation(operator, left, right))

    possibilities.extend([
        NotOperation(2.0),
        NotOperation(Identifier('X')),
        BinaryOperation(
            TokenType.AND,
            Identifier('X'),
            BinaryOperation(
                TokenType.AND,
                Identifier('Y'),
                BinaryOperation(
                    TokenType.AND, Identifier('Z'), 2.0
                )
            )
        )
    ])

    return possibilities


@ddt
class ParserTestSpec(unittest.TestCase):

    @unpack
    @data(
        {'expression': 'IF ( :X > 2 ) THEN \n END',
         'expected': [IfStatement(BinaryOperation(TokenType.GREATER_THAN, Identifier('X'), 2.0), None, None)]},
        {'expression': 'IF ( :X ) THEN \n END',
         'expected': [IfStatement(Identifier('X'), None, None)]},
        {'expression': 'IF ( :X AND :Y ) THEN \n END',
         'expected': [IfStatement(BinaryOperation(TokenType.AND, Identifier('X'), Identifier('Y')), None, None)]},
        {'expression': 'IF ( :X OR :Y ) THEN \n END',
         'expected': [IfStatement(BinaryOperation(TokenType.OR, Identifier('X'), Identifier('Y')), None, None)]},
        {'expression': 'IF ( 1 > 2 ) THEN \n END',
         'expected': [IfStatement(BinaryOperation(TokenType.GREATER_THAN, 1.0, 2.0), None, None)]},
        {'expression': 'IF ( :X > :Y ) THEN \n END',
         'expected': [IfStatement(BinaryOperation(TokenType.GREATER_THAN, Identifier('X'), Identifier('Y')), None, None)]},
        {'expression': 'IF ( :X > :Y ) THEN \n IF ( :X > 2 ) THEN \n END END',
         'expected': [
             IfStatement(
                 BinaryOperation(TokenType.GREATER_THAN, Identifier('X'), Identifier('Y')),
                 [IfStatement(BinaryOperation(TokenType.GREATER_THAN, Identifier('X'), 2.0), None, None)],
                 None
             )
         ]},

    )
    def test_if(self, expression, expected):
        actual = parser.parse(expression, lexer=lexer)

        self.assertEqual(actual, expected)

    def test_if_condition(self):
        bool_expressions = generate_bool_expressions()

        for bool_expression in bool_expressions:
            if_statement = [IfStatement(bool_expression, None, None)]

            program = print_program(if_statement)

            actual = parser.parse(program, lexer=lexer)

            self.assertEqual(if_statement, actual)

    @unpack
    @data(
        {'expression': [Assignment('X', NotOperation(op)) for op in generate_bool_expressions()]},
    )
    def test_not_operator(self, expression):
        program = print_program(expression)

        actual = parser.parse(program, lexer=lexer)

        self.assertEqual(expression, actual)

    @unpack
    @data(
        {'expression': [IfStatement(BinaryOperation(TokenType.GREATER_THAN, Identifier('X'), 2.0), generate_statements(), None)]},
        {'expression': [IfStatement(BinaryOperation(TokenType.LESS_THAN, Identifier('X'), 2.0), generate_statements(), generate_statements())]},
    )
    def test_if_body(self, expression):
        program = print_program(expression)

        actual = parser.parse(program, lexer=lexer)

        self.assertEqual(expression, actual)

    @unpack
    @data(
        *[{'expression': [IfStatement(cond, None, None)]} for cond in generate_invalid_conditions()]
    )
    def test_if_invalid_condition(self, expression):
        program = print_program(expression)

        with self.assertRaises(Exception):
            parser.parse(program, lexer=lexer)

    @unpack
    @data(
        {'expression': 'WHILE ( :X > 2 ) \n END',
         'expected': [WhileStatement(BinaryOperation(TokenType.GREATER_THAN, Identifier('X'), 2.0), None)]},
        {'expression': 'WHILE ( :X >= :Y ) \n END',
         'expected': [WhileStatement(BinaryOperation(TokenType.GREATER_EQUAL, Identifier('X'), Identifier('Y')), None)]},
        {'expression': 'WHILE ( :X >= :Y ) WHILE ( :X < 5 ) END \n END',
         'expected': [
             WhileStatement(
                 BinaryOperation(TokenType.GREATER_EQUAL, Identifier('X'), Identifier('Y')),
                 [WhileStatement(BinaryOperation(TokenType.LESS_THAN, Identifier('X'), 5.0), None)]
             )
         ]},
    )
    def test_while(self, expression, expected):
        actual = parser.parse(expression, lexer=lexer)

        self.assertEqual(actual, expected)

    @unpack
    @data(
        {'expression': [WhileStatement(BinaryOperation(TokenType.LESS_THAN, Identifier('X'), 2.0), generate_statements())]}
    )
    def test_while_body(self, expression):
        program = print_program(expression)

        actual = parser.parse(program, lexer=lexer)

        self.assertEqual(actual, expression)

    def test_while_condition(self):
        bool_expressions = generate_bool_expressions()

        for bool_expression in bool_expressions:
            while_statement = [WhileStatement(bool_expression, None)]

            program = print_program(while_statement)

            actual = parser.parse(program, lexer=lexer)

            self.assertEqual(while_statement, actual)

    @unpack
    @data(
        *[{'expression': [WhileStatement(cond, None)]} for cond in generate_invalid_conditions()]
    )
    def test_while_invalid_condition(self, expression):
        program = print_program(expression)

        with self.assertRaises(Exception):
            parser.parse(program, lexer=lexer)

    @unpack
    @data(
        {'expression': 'TO FUNC :a END',
         'expected': [DeclareFunction('FUNC', ['a'], None)]},
        {'expression': 'TO FUNC END',
         'expected': [DeclareFunction('FUNC', None, None)]},
        {'expression': 'TO FUNC :b \n a = 1234 \n c = :b > :a \n END',
         'expected': [
             DeclareFunction(
                'FUNC', ['b'],
                [
                    Assignment('a', 1234.0),
                    Assignment('c', BinaryOperation(TokenType.GREATER_THAN, Identifier('b'), Identifier('a')))
                ]
             )
         ]},
    )
    def test_declare_function(self, expression, expected):
        actual = parser.parse(expression, lexer=lexer)

        self.assertEqual(actual, expected)

    @unpack
    @data(
        {'expression': [DeclareFunction('FUNC', ['a'], generate_statements())]},
        {'expression': [DeclareFunction('FUNC', None, generate_statements())]},
    )
    def test_declare_function_body(self, expression):
        program = print_program(expression)

        actual = parser.parse(program, lexer=lexer)

        self.assertEqual(actual, expression)

    @unpack
    @data(
        {'expression': [Assignment('AB', 1234.0)]},
        {'expression': [Assignment('ABC', Identifier('AB'))]},
        {'expression': [Assignment('ABC', op) for op in generate_bool_expressions()]},
        {'expression': [Assignment('ABC', op) for op in generate_math_expressions()]},
    )
    def test_assignment(self, expression):
        program = print_program(expression)

        actual = parser.parse(program, lexer=lexer)

        self.assertEqual(actual, expression)


if __name__ == '__main__':
    unittest.main()
