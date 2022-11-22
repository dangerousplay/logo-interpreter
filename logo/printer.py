from io import StringIO
from typing import Any, List

from logo.parse import BinaryOperation, IfStatement, Assignment, WhileStatement, DeclareFunction, NotOperation, \
    InvokeFunction, Identifier


def print_binary_operation(bop: BinaryOperation, buffer: StringIO):
    def print_bop_value(value):
        if isinstance(value, BinaryOperation):
            print_binary_operation(value, buffer)
        elif isinstance(value, Identifier):
            buffer.write(f"{value.value} ")
        else:
            buffer.write(f"{value} ")

    print_bop_value(bop.left)

    buffer.write(f"{bop.op.value} ")

    print_bop_value(bop.right)


def print_not_op(op: NotOperation, buffer: StringIO):
    buffer.write(f"NOT (")
    print_bool_expression(op.expression, buffer)
    buffer.write(") ")


def print_if_statement(if_statement: IfStatement, buffer: StringIO):
    buffer.write("IF (")
    print_bool_expression(if_statement.condition, buffer)
    buffer.write(") ")
    buffer.write("THEN \n")

    for op in if_statement.body or []:
        print_statement(op, buffer)
        buffer.write("\n")

    if if_statement.else_body is not None:
        buffer.write("ELSE \n")

        for if_statement in if_statement.else_body or []:
            print_statement(if_statement, buffer)
            buffer.write("\n")

    buffer.write("END")


def print_assignment(op: Assignment, buffer: StringIO):
    buffer.write(f"SET {op.variable} = ")

    if isinstance(op.value, BinaryOperation):
        print_binary_operation(op.value, buffer)
    elif isinstance(op.value, Identifier):
        buffer.write(f"{op.value.value} ")
    elif isinstance(op.value, NotOperation):
        print_not_op(op.value, buffer)
    else:
        buffer.write(f"{op.value} ")


def print_while_statement(statement: WhileStatement, buffer: StringIO):
    buffer.write("WHILE ( ")
    print_bool_expression(statement.condition, buffer)
    buffer.write(" )")

    for op in statement.body or []:
        print_statement(op, buffer)
        buffer.write("\n")

    buffer.write("END")


def print_declare_function(func: DeclareFunction, buffer: StringIO):
    buffer.write(f"TO {func.name} ")

    for arg in func.args or []:
        buffer.write(f":{arg} ")

    buffer.write("\n")

    for op in func.body or []:
        print_statement(op, buffer)
        buffer.write("\n")

    buffer.write("END")


def print_invoke_function(func: InvokeFunction, buffer: StringIO):
    buffer.write(f"{func.name} ")

    for arg in func.args or []:
        buffer.write(f":{arg} ")

    buffer.write("\n")


def print_statement(op, buffer: StringIO):
    if isinstance(op, Assignment):
        print_assignment(op, buffer)
    elif isinstance(op, IfStatement):
        print_if_statement(op, buffer)
    elif isinstance(op, WhileStatement):
        print_while_statement(op, buffer)
    elif isinstance(op, DeclareFunction):
        print_declare_function(op, buffer)
    elif isinstance(op, InvokeFunction):
        print_invoke_function(op, buffer)


def print_bool_expression(op, buffer: StringIO):
    if isinstance(op, Identifier):
        buffer.write(f"{op.value} ")
    elif isinstance(op, NotOperation):
        print_not_op(op, buffer)
    elif isinstance(op, BinaryOperation):
        print_binary_operation(op, buffer)
    else:
        buffer.write(f"{op} ")



def print_program(ast: List[Any]) -> str:
    buffer = StringIO()

    for op in ast:
        print_statement(op, buffer)
        buffer.write("\n")

    try:
        return buffer.getvalue()
    finally:
        buffer.close()

