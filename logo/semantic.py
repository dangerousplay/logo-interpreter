import logging
from io import StringIO
from tabulate import tabulate

from logo.parse import BinaryOperation, NotOperation, WhileStatement, IfStatement, Assignment, DeclareFunction, \
    InvokeFunction, Identifier


# Scoped symbol table implementation based on
# https://github.com/rspivak/lsbasi/blob/07e1a14516156a21ebe2d82e0bae4bba5ad73dd6/part14/spi.py
# https://ruslanspivak.com/lsbasi-part14/

class Symbol(object):
    def __init__(self, name, type=None):
        self.name = name
        self.type = type


class VariableSymbol(Symbol):
    def __init__(self, name):
        super().__init__(name)


class FunctionSymbol(Symbol):
    def __init__(self, name, params=None):
        super().__init__(name)

        self.params = params if params is not None else []


def built_in():
    forward = FunctionSymbol("FORWARD", params=["num"])
    backward = FunctionSymbol("BACKWARD", params=["num"])

    right = FunctionSymbol("RIGHT", params=["angle"])
    left = FunctionSymbol("LEFT", params=["angle"])

    pen_up = FunctionSymbol("PENUP")
    pen_down = FunctionSymbol("PENDOWN")

    wipe_clean = FunctionSymbol("WIPECLEAN")
    clear_screen = FunctionSymbol("CLEARSCREEN")

    return {
        "RANDOM": VariableSymbol("RANDOM"),
        "HEADING": VariableSymbol("HEADING"),
        "YCOR": VariableSymbol("YCOR"),
        "XCOR": VariableSymbol("XCOR"),
        "FO": forward,
        "FORWARD": forward,
        "BACKWARD": backward,
        "BK": backward,
        "RT": right,
        "RIGHT": right,
        "LEFT": left,
        "LT": left,
        "PENUP": pen_up,
        "PU": pen_up,
        "PD": pen_down,
        "PENDOWN": pen_down,
        "WIPECLEAN": wipe_clean,
        "WC": wipe_clean,
        "CLEARSCREEN": clear_screen,
        "CS": clear_screen,
        "HOME": FunctionSymbol("HOME"),
        "SETXY": FunctionSymbol("SETXY", ['x', 'y']),
        "PRINT": FunctionSymbol("PRINT", ['data']),
        "TYPEIN": VariableSymbol("TYPEIN"),
    }


class ScopedSymbolTable(object):
    def __init__(self, scope_name, scope_level, enclosing_scope=None):
        self._symbols = built_in()
        self.scope_name = scope_name
        self.scope_level = scope_level
        self.enclosing_scope = enclosing_scope

    def __str__(self):
        buffer = StringIO()

        buffer.write("Scoped Symbol Table \n")
        buffer.write(f"Scope Name: {self.scope_name}\n")
        buffer.write(f"Scope Level: {self.scope_level}\n")

        enclosing_scope_name = self.enclosing_scope.scope_name if self.enclosing_scope else None

        buffer.write(f"Enclosing scope: {enclosing_scope_name}\n")
        buffer.write("\n")
        buffer.write("Symbols: \n")

        buffer.write(tabulate(self._symbols.items(), ['Name', 'Value'], tablefmt="grid"))

        try:
            return buffer.getvalue()
        finally:
            buffer.close()

    __repr__ = __str__

    def insert(self, symbol):
        logging.debug('Inserting symbol with name: %s' % symbol.name)

        self._symbols[symbol.name] = symbol

    def lookup(self, name, current_scope_only=False):
        logging.debug('Lookup for symbol: %s. (Scope name: %s)' % (name, self.scope_name))
        symbol = self._symbols.get(name)

        if symbol is not None:
            return symbol

        if current_scope_only:
            return None

        # recursively go up the chain and lookup the name
        if self.enclosing_scope is not None:
            return self.enclosing_scope.lookup(name)


class RedeclaredSymbolException(Exception):
    symbol: Symbol

    def __init__(self, symbol: Symbol, message: str):
        super().__init__(message)
        self.symbol = symbol


class TypeMismatchException(Exception):
    symbol: Symbol

    def __init__(self, symbol: Symbol, message: str):
        super().__init__(message)
        self.symbol = symbol


class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)

        logging.debug(f"Visiting method '{method_name}'")

        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


class SemanticAnalyzer(NodeVisitor):
    def __init__(self):
        self.current_scope = ScopedSymbolTable(
            scope_name='global',
            scope_level=1,
            enclosing_scope=None,
        )

    def visit_BinaryOperation(self, op: BinaryOperation):
        if isinstance(op.left, tuple):
            self.visit(op.left)

        if isinstance(op.right, tuple):
            self.visit(op.right)

    def visit_NotOperation(self, op: NotOperation):
        self.visit(op.expression)

    def visit_WhileStatement(self, statement: WhileStatement):
        self.visit(statement.condition)

        self.__enter_scope__("WHILE")

        if statement.body:
            for st in statement.body or []:
                self.visit(st)

        self.__exit_scope__()

    def visit_IfStatement(self, statement: IfStatement):
        self.visit(statement.condition)

        self.__enter_scope__("IF")

        if statement.body:
            for st in statement.body or []:
                self.visit(st)

        self.__exit_scope__()

        self.__enter_scope__("IF")

        if statement.else_body:
            for st in statement.else_body or []:
                self.visit(st)

        self.__exit_scope__()

    def visit_Assignment(self, assignment: Assignment):
        self._expect_not_declared_(assignment.variable, VariableSymbol)

        if isinstance(assignment.value, tuple):
            self.visit(assignment.value)

        self.current_scope.insert(VariableSymbol(assignment.variable))

    def visit_DeclareFunction(self, function: DeclareFunction):
        self._expect_not_declared_(function.name)

        self.current_scope.insert(FunctionSymbol(function.name, function.args))

        self.__enter_scope__(function.name)

        if function.body:
            for arg in function.args or []:
                self.current_scope.insert(VariableSymbol(arg))

            for statement in function.body or []:
                self.visit(statement)

        self.__exit_scope__()

    def __enter_scope__(self, name: str):
        logging.debug(f"Entering scope '{name}'")

        self.current_scope = ScopedSymbolTable(
            scope_name=name,
            scope_level=self.current_scope.scope_level,
            enclosing_scope=self.current_scope,
        )

    def _expect_not_declared_(self, name: str, type=None, current_scope_only=True):
        symbol: Symbol = self.current_scope.lookup(name, current_scope_only)

        def throw():
            raise RedeclaredSymbolException(
                symbol,
                f"Can't declare {type.__name__} with name {symbol.name} because a {symbol.type} exists with the same name"
            )

        if not type and symbol:
            throw()
        elif symbol and type and not isinstance(symbol, type):
            throw()

    def __exit_scope__(self):
        logging.debug(f"Exiting scope '{self.current_scope.scope_name}'")

        self.current_scope = self.current_scope.enclosing_scope

    def visit_InvokeFunction(self, function: InvokeFunction):
        symbol: FunctionSymbol = self._expect_symbol_(function.name, FunctionSymbol)

        if len(function.args or []) != len(symbol.params or []):
            raise Exception(f"Expected {len(symbol.params)} but {len(function.args)} were informed")

        for param in function.args or []:
            if param is str:
                self._expect_symbol_(param, VariableSymbol)

    def _expect_symbol_(self, name: str, symbol_type=None, current_scope_only=False):
        symbol = self.current_scope.lookup(name, current_scope_only)

        if symbol:
            if not symbol_type:
                return symbol

            if not isinstance(symbol, symbol_type):
                raise TypeMismatchException(symbol, f"Expecting symbol {symbol_type.__name__} with name {name} found {symbol.type}")
        else:
            raise Exception(f"Not found symbol of type {symbol_type} with name {name}")

        return symbol

    def visit_Identifier(self, id: Identifier):
        self._expect_symbol_(id.value)
