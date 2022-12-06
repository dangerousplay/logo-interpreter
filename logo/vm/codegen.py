


import logging
from io import StringIO
from typing import Any

from tabulate import tabulate

from logo.lexer import TokenType, COMPARISON_OPERATORS, ARITHMETIC_OPERATORS
from logo.parse import BinaryOperation, NotOperation, WhileStatement, IfStatement, Assignment, DeclareFunction, \
    InvokeFunction, Identifier
from logo.semantic import NodeVisitor, ScopedSymbolTable, VariableSymbol, FunctionSymbol, Symbol, \
    RedeclaredSymbolException, TypeMismatchException
from logo.vm.isa import Load, And, Or, Not, Compare, Store, Push, Label, Add, JumpZ, Jump, JumpLess, Return, Subtract, \
    Multiply, Divide, Pow, DefineFunction, JumpNZ, JumpMore, Call, Set, Truncate, Unset


def mangle_variable(scope: str, variable: str) -> str:
    return f"{scope}_var_{variable}"


def mangle_label(scope: str, name: str) -> str:
    return f"{scope}_label_{name}"


class CodeGenerator(NodeVisitor):
    def __init__(self):
        self.current_scope = ScopedSymbolTable(
            scope_name='global',
            scope_level=1,
            enclosing_scope=None,
        )
        self.variables = {}
        self.functions = {}
        self._label_counter_ = 0

    def _new_variable_(self, name: str, value: Any):
        variable_name = mangle_variable(self.current_scope.full_name(), name)
        self.variables[variable_name] = value

        if not self.current_scope.lookup(name):
            self.current_scope.insert(VariableSymbol(name))

        return variable_name

    def _new_label_(self, name: str, instructions: list) -> Label:
        self._label_counter_ += 1

        label_name = mangle_label(self.current_scope.full_name(), name) + f"_{self._label_counter_}"
        label = Label(label_name, instructions)

        self.current_scope.insert(label)

        return label

    def _load_variable_(self, name: str):
        variable_name = self._get_variable_name_(name)
        return Load(variable_name)

    def _store_(self, variable: str):
        return Store(self._get_variable_name_(variable))

    def _push_value_(self, expression):
        instructions = []

        if isinstance(expression, Identifier):
            instructions.append(self._load_variable_(expression.value))
        elif isinstance(expression, tuple):
            instructions.extend(self.visit(expression))
        else:
            value = expression

            if isinstance(value, bool):
                value = int(value)

            instructions.append(Push(value))

        return instructions

    def visit_BinaryOperation(self, op: BinaryOperation):
        instructions = []
        left_instructions = []
        right_instructions = []

        def operand(op):
            if isinstance(op, Identifier):
                return [self._load_variable_(op.value)]
            if isinstance(op, tuple):
                return self.visit(op)
            else:
                return [Push(op)]

        left_instructions.extend(self._push_value_(op.left))
        right_instructions.extend(self._push_value_(op.right))

        instructions.extend(left_instructions)
        instructions.extend(right_instructions)

        def _on_zero_increment_(amount: int):
            increment_label = self._new_label_("increment", [Push(amount), Add()])
            end_label = self._new_label_("end_increment", [])

            instructions.extend([JumpZ(increment_label.name), Jump(end_label.name), increment_label, end_label])

        if op.op is TokenType.AND:
            instructions.append(Truncate())
            instructions.append(And())
        elif op.op is TokenType.OR:
            instructions.append(Truncate())
            instructions.append(Or())
        elif op.op in COMPARISON_OPERATORS:
            variable = self._new_variable_("cmp", 0)

            instructions.append(Store(variable))
            instructions.append(Compare(variable))

            if op.op is TokenType.GREATER_THAN:
                instructions.append(Not())
            elif op.op is TokenType.GREATER_EQUAL:
                _on_zero_increment_(1)
            elif op.op is TokenType.LESS_EQUAL:
                _on_zero_increment_(1)
            elif op.op is TokenType.IS_EQUAL:
                _on_zero_increment_(1)
            elif op.op is TokenType.NOT_EQUAL:
                increment_label = self._new_label_("increment", [Push(2), Add()])
                end_label = self._new_label_("end_cmp_neq", [])

                instructions.extend([JumpLess(increment_label.name), Jump(end_label.name), increment_label, end_label])
            else:
                pass
        elif op.op is TokenType.MINUS:
            instructions.append(Subtract())
        elif op.op is TokenType.PLUS:
            instructions.append(Add())
        elif op.op is TokenType.TIMES:
            instructions.append(Multiply())
        elif op.op is TokenType.DIVIDE:
            instructions.append(Divide())
        elif op.op is TokenType.POW:
            instructions.append(Pow())
        else:
            raise Exception(f"Unknown operation: {op}")

        return instructions

    def visit_NotOperation(self, op: NotOperation):
        instructions = self.visit(op.expression)
        instructions.append(Not())
        return instructions

    def visit_WhileStatement(self, statement: WhileStatement):
        condition_instructions = []
        body_instructions = []

        if statement.body:
            for st in statement.body or []:
                body_instructions.extend(self.visit(st))

        if isinstance(statement.condition, Identifier):
            condition_instructions.append(self._load_variable_(statement.condition.value))
        elif isinstance(statement.condition, tuple):
            condition_instructions.extend(self.visit(statement.condition))
        else:
            if statement.condition:
                return body_instructions
            else:
                return []

        end_label = self._new_label_("end_while", [])
        while_label = self._new_label_("while", condition_instructions + body_instructions)

        loop_instructions = [Compare(1), JumpZ(while_label.name), Jump(end_label.name), while_label, Jump(while_label.name), end_label]

        return condition_instructions + loop_instructions

    def visit_IfStatement(self, statement: IfStatement):
        instructions = []
        body_instructions = []
        else_instructions = []
        end_label = self._new_label_("end_if", [])

        if statement.body:
            for st in statement.body or []:
                body_instructions.extend(self.visit(st))
                
            body_instructions.append(Jump(end_label.name))    
        if statement.else_body:
            for st in statement.else_body or []:
                else_instructions.extend(self.visit(st))

        if isinstance(statement.condition, Identifier):
            instructions.append(self._load_variable_(statement.condition.value))
        elif isinstance(statement.condition, tuple):
            instructions.extend(self.visit(statement.condition))
        elif isinstance(statement.condition, bool):
            if statement.condition:
                return body_instructions
            else:
                return else_instructions

        body_label = self._new_label_("body", body_instructions)
        else_label = self._new_label_("else_body", else_instructions)
        
        instructions.extend([Compare(1), JumpZ(body_label.name), Jump(end_label.name), body_label, else_label, end_label])

        return instructions

    def visit_Assignment(self, assignment: Assignment):
        self._expect_not_declared_(assignment.variable, VariableSymbol)

        self._new_variable_(assignment.variable, 0)

        instructions = []

        instructions.extend(self._push_value_(assignment.value))

        instructions.append(self._store_(assignment.variable))

        return instructions

    def _get_variable_name_(self, identifier: str):
        _, scope_name = self.current_scope.lookup(identifier)
        var_name = mangle_variable(scope_name, identifier)

        return var_name

    def visit_DeclareFunction(self, function: DeclareFunction):
        function_name = function.name.upper()

        self._expect_not_declared_(function_name)

        self.current_scope.insert(FunctionSymbol(function_name, function.args))

        instructions = []

        if function.body:
            for arg in function.args or []:
                self._new_variable_(arg, 0)
                instructions.append(self._store_(arg))

            for statement in function.body or []:
                if isinstance(statement, DeclareFunction):
                    self.visit(statement)
                else:
                    instructions.extend(self.visit(statement))

        instructions.append(Return())

        self.functions[function_name] = DefineFunction(function_name, instructions)

        return instructions

    def visit_InvokeFunction(self, function: InvokeFunction):
        symbol: FunctionSymbol = self._expect_symbol_(function.name.upper(), FunctionSymbol)

        instructions = []

        if len(function.args or []) != len(symbol.params or []):
            raise Exception(f"Expected {len(symbol.params)} but {len(function.args)} were informed")

        for param in function.args or []:
            if param is Identifier:
                self._expect_symbol_(param.value, VariableSymbol)

            if isinstance(param, str):
                param = Identifier(param)

            instructions.extend(self._push_value_(param))

        instructions.append(Call(function.name))

        return instructions

    def visit_Identifier(self, id: Identifier):
        self._expect_symbol_(id.value)

    def __enter_scope__(self, name: str):
        logging.debug(f"Entering scope '{name}'")

        scope = ScopedSymbolTable(
            scope_name=name,
            scope_level=self.current_scope.scope_level,
            enclosing_scope=self.current_scope,
        )

        self.current_scope.children_scopes.append(scope)
        self.current_scope = scope

    def _expect_not_declared_(self, name: str, type=None, current_scope_only=True):
        symbol, _ = self.current_scope.lookup(name, current_scope_only)

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

    def _expect_symbol_(self, name: str, symbol_type=None, current_scope_only=False):
        symbol, _ = self.current_scope.lookup(name, current_scope_only)

        if symbol:
            if not symbol_type:
                return symbol

            if not isinstance(symbol, symbol_type):
                raise TypeMismatchException(symbol, f"Expecting symbol {symbol_type.__name__} with name {name} found {symbol.type}")
        else:
            raise Exception(f"Not found symbol of type {symbol_type} with name {name}")

        return symbol


def print_program(code: CodeGenerator, start: str) -> str:
    buffer = StringIO()

    buffer.write(f".START {start} \n\n")

    print_variables(code.variables, buffer)

    buffer.write(".CODE \n\n")

    for function in code.functions.values():
        print_function(function, buffer)

    return buffer.getvalue()


def print_variables(variables: dict, buffer: StringIO):
    buffer.write(".DATA \n")

    for name, value in variables.items():
        buffer.write(f"  {name} {value} \n")

    buffer.write("\n\n")


def print_function(func: DefineFunction, buffer: StringIO):
    buffer.write(f"DEF {func.id}: \n")

    for instruction in func.instructions:
        buffer.write("  ")
        print_instruction(instruction, buffer)

    buffer.write("\n\n")


def print_instruction(ins: Any, buffer: StringIO):
    instruction_name = type(ins).__name__

    if isinstance(ins, Load):
        buffer.write(f"{instruction_name} {ins.id}")
    elif isinstance(ins, Push):
        buffer.write(f"{instruction_name} {ins.value}")
    elif isinstance(ins, Store):
        buffer.write(f"{instruction_name} {ins.id}")
    elif isinstance(ins, Compare):
        buffer.write(f"{instruction_name} {ins.value}")
    elif type(ins) in [Jump, JumpZ, JumpLess, JumpMore, JumpNZ]:
        buffer.write(f"{instruction_name} :{ins.label}")
    elif isinstance(ins, Call):
        buffer.write(f"{instruction_name} {ins.function}")
    elif type(ins) in [Set, Unset]:
        buffer.write(f"{instruction_name} {ins.number}")
    elif isinstance(ins, Label):
        buffer.write(f"\n:{ins.name}\n")

        for instruction in ins.instructions:
            buffer.write("  ")
            print_instruction(instruction, buffer)
    else:
        buffer.write(f"{instruction_name}")

    buffer.write("\n")