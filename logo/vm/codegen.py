


import logging
from io import StringIO
from typing import Any, List

from tabulate import tabulate

from logo.lexer import TokenType, COMPARISON_OPERATORS, ARITHMETIC_OPERATORS, BOOL_CONDITION_OPERATORS
from logo.parse import BinaryOperation, NotOperation, WhileStatement, IfStatement, Assignment, DeclareFunction, \
    InvokeFunction, Identifier
from logo.semantic import NodeVisitor, ScopedSymbolTable, VariableSymbol, FunctionSymbol, Symbol, \
    RedeclaredSymbolException, TypeMismatchException
from logo.vm.built_in import built_in_functions, BuiltInFunctions
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
        self.functions, self.variables = built_in_functions()
        self._label_counter_ = 0

        self.false_label = None
        self.true_label = None

    def _new_variable_(self, name: str, value: Any):
        variable_name = mangle_variable(self.current_scope.full_name(), name)
        self.variables[variable_name] = value

        if not self.current_scope.lookup(name):
            self.current_scope.insert(VariableSymbol(name))

        return variable_name

    def _new_label_(self, name: str, instructions: list) -> Label:
        label = Label(self._new_label_name_(name), instructions)

        self.current_scope.insert(label)

        return label

    def _new_label_name_(self, name: str) -> str:
        self._label_counter_ += 1

        return mangle_label(self.current_scope.full_name(), name) + f"_{self._label_counter_}"

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
            elif isinstance(value, str):
                value = '"' + value + '"'

            instructions.append(Push(value))

        return instructions

    def visit_BinaryOperation(self, op: BinaryOperation):
        instructions = []

        if op.op in COMPARISON_OPERATORS or op.op in BOOL_CONDITION_OPERATORS:
            instructions.extend(self._visit_bool_expression_(op))
        else:
            instructions.extend(self._push_value_(op.left))
            instructions.extend(self._push_value_(op.right))

            if op.op is TokenType.MINUS:
                instructions.append(Subtract())
            elif op.op is TokenType.PLUS:
                instructions.append(Add())
            elif op.op is TokenType.TIMES:
                instructions.append(Multiply())
            elif op.op is TokenType.DIVIDE:
                instructions.append(Divide())
            elif op.op is TokenType.POW:
                instructions.append(Pow())

        return instructions

    def _visit_bool_expression_(self, op: BinaryOperation):
        instructions = []

        original_true_label = self.true_label
        original_false_label = self.false_label

        if op.op is TokenType.AND:
            true_label = self._new_label_name_("and_true")
            self.true_label = true_label

            instructions.extend(self._push_value_(op.left))

            self.true_label = original_true_label

            true_label = Label(true_label, self._push_value_(op.right))

            instructions.extend([true_label])
        elif op.op is TokenType.OR:
            false_label = self._new_label_name_("or_false")

            self.false_label = false_label

            instructions.extend(self._push_value_(op.left))

            false_label = Label(false_label, self._push_value_(op.right))

            instructions.extend([false_label])
        elif op.op in COMPARISON_OPERATORS:
            variable = self._new_variable_("cmp", 0)

            instructions.extend(self._push_value_(op.left))
            instructions.extend(self._push_value_(op.right))

            instructions.append(Store(variable))
            instructions.append(Compare(variable))

            if op.op is TokenType.GREATER_THAN:
                instructions.extend([JumpMore(self.true_label), Jump(self.false_label)])
            elif op.op is TokenType.GREATER_EQUAL:
                instructions.extend([JumpMore(self.true_label), JumpZ(self.true_label), Jump(self.false_label)])
            elif op.op is TokenType.LESS_EQUAL:
                instructions.extend([JumpLess(self.true_label), JumpZ(self.true_label), Jump(self.false_label)])
            elif op.op is TokenType.IS_EQUAL:
                instructions.extend([JumpZ(self.true_label), Jump(self.false_label)])
            elif op.op is TokenType.NOT_EQUAL:
                instructions.extend([JumpMore(self.false_label), Jump(self.true_label)])
            elif op.op is TokenType.LESS_THAN:
                instructions.extend([JumpLess(self.true_label), Jump(self.false_label)])

        self.true_label = original_true_label
        self.false_label = original_false_label

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

        end_label = self._new_label_("end_while", [])
        body_label = self._new_label_("body_while", body_instructions)

        self.true_label = body_label.name
        self.false_label = end_label.name

        if isinstance(statement.condition, Identifier):
            condition_instructions.append(self._load_variable_(statement.condition.value))
        elif isinstance(statement.condition, tuple):
            condition_instructions.extend(self.visit(statement.condition))
        else:
            if statement.condition:
                return body_instructions
            else:
                return []

        while_label = self._new_label_("while", condition_instructions)

        return [while_label, body_label, Jump(while_label.name), end_label]

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

        body_label = self._new_label_("body", body_instructions)
        else_label = self._new_label_("else_body", else_instructions)

        self.true_label = body_label.name
        self.false_label = else_label.name

        if isinstance(statement.condition, Identifier):
            instructions.append(self._load_variable_(statement.condition.value))
            instructions.extend([Compare(1), JumpZ(body_label.name), Jump(else_label.name)])
        elif isinstance(statement.condition, tuple):
            instructions.extend(self.visit(statement.condition))
        elif isinstance(statement.condition, bool):
            if statement.condition:
                return body_instructions
            else:
                return else_instructions
        
        instructions.extend([body_label, else_label, end_label])

        return instructions

    def visit_Assignment(self, assignment: Assignment):
        self._expect_not_declared_(assignment.variable, VariableSymbol)

        self._new_variable_(assignment.variable, 0)

        store_label = self._new_label_("assign_store", [self._store_(assignment.variable)])

        true_label = self._new_label_("assign_true", [Push(1), Jump(store_label.name)])
        false_label = self._new_label_("assign_false", [Push(0), Jump(store_label.name)])

        original_labels = [self.true_label, self.false_label]

        self.true_label = true_label.name
        self.false_label = false_label.name

        instructions = []

        instructions.extend(self._push_value_(assignment.value))
        instructions.append(Jump(store_label.name))

        self.true_label, self.false_label = original_labels

        instructions.extend([true_label, false_label, store_label])

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
        function_name = function.name.upper()
        symbol: FunctionSymbol = self._expect_symbol_(function_name, FunctionSymbol)

        instructions = self.built_in_function(function)

        if instructions:
            return instructions

        instructions = []

        if len(function.args or []) != len(symbol.params or []):
            raise Exception(f"Expected {len(symbol.params)} but {len(function.args)} were informed")

        self._function_parameters_(function, instructions)

        instructions.append(Call(function.name))

        return instructions

    def _function_parameters_(self, function, instructions):
        for param in function.args or []:
            if param is Identifier:
                self._expect_symbol_(param.value, VariableSymbol)

            instructions.extend(self._push_value_(param))

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

    def built_in_function(self, function) -> List[Any]:
        instructions = []

        if function.name.upper() == BuiltInFunctions.WRITE.value:
            self._function_parameters_(function, instructions)
            instructions.extend([Push(len(function.args or [])), Call(BuiltInFunctions.WRITE.value)])

            return instructions


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