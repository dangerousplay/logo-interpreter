import unittest

from ddt import ddt, data, unpack

from logo.parse import IfStatement, BinaryOperation, WhileStatement, DeclareFunction, Assignment, \
    InvokeFunction, Identifier
from logo.lexer import TokenType
from logo.semantic import SemanticAnalyzer


@ddt
class SemanticTestSpec(unittest.TestCase):

    @unpack
    @data(
        {'expression': [Assignment('x', 1.0), IfStatement(Identifier('x'), None, None)]},
        {'expression': [
            Assignment('y', 1.0),
            Assignment('x', 1.0),
            IfStatement(BinaryOperation(TokenType.AND, Identifier('y'), Identifier('x')), None, None)
        ]},
        {'expression': [
            Assignment('x', 1.0),
            IfStatement(Identifier('x'), [
                Assignment('y', 2.0),
                WhileStatement(Identifier('y'), None),
                WhileStatement(Identifier('x'), None),
            ], None)
        ]},
        {'expression': [
            Assignment('x', 1.0),
            IfStatement(Identifier('x'), None, [
                Assignment('y', 2.0),
                WhileStatement(Identifier('y'), None),
                WhileStatement(Identifier('x'), None),
            ])
        ]},
    )
    def test_if_scope(self, expression):
        expression = DeclareFunction('main', None, expression)

        analyzer = SemanticAnalyzer()
        analyzer.visit(expression)

    @unpack
    @data(
        {'expression': [Assignment('y', 1.0), IfStatement(Identifier('x'), None, None)]},
        {'expression': [IfStatement(Identifier('x'), None, None)]},
        {'expression': [
            Assignment('x', 1.0),
            IfStatement(Identifier('x'), [Assignment('y', 2.0)], [WhileStatement('y', None)])
        ]},
        {'expression': [
            Assignment('x', 1.0),
            IfStatement(Identifier('x'), [WhileStatement('y', None)], [Assignment('y', 2.0)])
        ]},
    )
    def test_if_scope_invalid(self, expression):
        expression = DeclareFunction('main', None, expression)

        analyzer = SemanticAnalyzer()

        with self.assertRaises(Exception):
            analyzer.visit(expression)

    @unpack
    @data(
        {'expression': [Assignment('x', 1.0), WhileStatement(Identifier('x'), None)]},
        {'expression': [
            Assignment('y', 1.0),
            Assignment('x', 1.0),
            WhileStatement(BinaryOperation(TokenType.AND, Identifier('y'), Identifier('x')), None)
        ]},
        {'expression': [
            Assignment('x', 1.0),
            WhileStatement(Identifier('x'), [
                Assignment('y', 2.0),
                WhileStatement(Identifier('y'), None),
                WhileStatement(Identifier('x'), None),
            ])
        ]},
    )
    def test_while_scope(self, expression):
        expression = DeclareFunction('main', None, expression)

        analyzer = SemanticAnalyzer()
        analyzer.visit(expression)

    @unpack
    @data(
        {'expression': [Assignment('y', 1.0), WhileStatement(Identifier('x'), None)]},
        {'expression': [WhileStatement(Identifier('x'), None)]},
        {'expression': [
            Assignment('x', 1.0),
            WhileStatement(Identifier('x'), [WhileStatement('y', None)])
        ]},
    )
    def test_while_scope_invalid(self, expression):
        expression = DeclareFunction('main', None, expression)

        analyzer = SemanticAnalyzer()

        with self.assertRaises(Exception):
            analyzer.visit(expression)

    @unpack
    @data(
        {'expression': [
            Assignment('y', 1.0),
            DeclareFunction('ff', ['x'], [
                WhileStatement(Identifier('x'), None),
                WhileStatement(Identifier('y'), None)
            ])
        ]},
        {'expression': [
            Assignment('y', 1.0),
            DeclareFunction('ff', None, [
                WhileStatement(Identifier('y'), None)
            ])
        ]},
        {'expression': [
            DeclareFunction('ff', ['y'], [
                WhileStatement(Identifier('y'), None)
            ]),
            Assignment('y', 1.0),
            InvokeFunction('ff', ['y'])
        ]},
    )
    def test_function_scope(self, expression):
        expression = DeclareFunction('main', None, expression)

        analyzer = SemanticAnalyzer()
        analyzer.visit(expression)

    @unpack
    @data(
        {'expression': [
            DeclareFunction('ff', ['x'], [
                WhileStatement(Identifier('y'), None)
            ])
        ]},
        {'expression': [
            DeclareFunction('ff', None, [
                WhileStatement(Identifier('y'), None)
            ])
        ]},
        {'expression': [
            Assignment('x', 1.0),
            DeclareFunction('ff', None, [
                WhileStatement(Identifier('y'), None)
            ])
        ]},
        {'expression': [
            Assignment('x', 1.0),
            DeclareFunction('ff', ['x'], [
                WhileStatement(Identifier('x'), None)
            ]),
            InvokeFunction('ff', [])
        ]},
    )
    def test_function_scope_invalid(self, expression):
        expression = DeclareFunction('main', None, expression)

        analyzer = SemanticAnalyzer()

        with self.assertRaises(Exception):
            analyzer.visit(expression)

    @unpack
    @data(
        {'expression': [
            Assignment('y', Identifier('RANDOM')),
            Assignment('x', Identifier('HEADING')),
            Assignment('z', Identifier('YCOR')),
            Assignment('w', Identifier('XCOR')),
        ]},
        {'expression': [
            InvokeFunction('LT', [10]),
            InvokeFunction('LEFT', [10]),
            InvokeFunction('RT', [10]),
            InvokeFunction('RIGHT', [10]),
            InvokeFunction('HOME', None),
            InvokeFunction('WIPECLEAN', None),
            InvokeFunction('WC', None),
            InvokeFunction('CLEARSCREEN', None),
            InvokeFunction('CS', None),
        ]},
    )
    def test_built_in(self, expression):
        expression = DeclareFunction('main', None, expression)

        analyzer = SemanticAnalyzer()
        analyzer.visit(expression)

    @unpack
    @data(
        {'expression': [InvokeFunction('LT', None)]},
        {'expression': [InvokeFunction('RT', None)]},
        {'expression': [InvokeFunction('RTS', None)]},
        {'expression': [InvokeFunction('HOME', ['x'])]},
    )
    def test_invalid_invoke(self, expression):
        expression = DeclareFunction('main', None, expression)

        analyzer = SemanticAnalyzer()

        with self.assertRaises(Exception):
            analyzer.visit(expression)


if __name__ == '__main__':
    unittest.main()
