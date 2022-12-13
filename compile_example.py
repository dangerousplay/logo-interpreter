from logo.parse import parser, DeclareFunction
from logo.lexer import lexer

from logo.vm.codegen import CodeGenerator, print_program


if __name__ == '__main__':
    s = """
    TO RR :AABB
     B = :AABB ^ 2
    END

    RR 1234

    B = 13
    C = true and false

    RR :B
    X = 3
    Y = 3

    Z = 'ABC'

    AB = :X > 1
    BB = :X < 2 AND :X * 2 + :Y < 4 OR :X == 1

    IF ( NOT :AB > 2 OR :B < 2 ) THEN

    END

    WHILE (TRUE OR :AB < 2)
    END
    """

    result = parser.parse(s, lexer=lexer)

    main = DeclareFunction('MAIN', None, result)

    code_gen = CodeGenerator()
    code_gen.visit(main)

    program = code_gen.functions[main.name]

    print("The compiled program: \n")

    print(print_program(code_gen, main.name))
