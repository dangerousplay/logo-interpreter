from logo.parse import parser, DeclareFunction
from logo.lexer import lexer
from printree import ptree

from logo.semantic import SemanticAnalyzer

if __name__ == '__main__':
    s = """
    TO RR :AABB
     SET B = AABB ^ 2
    END

    RR 1234
    
    SET B = 13
    SET C = true and false
    
    RR B
    SET X = 3
    SET Y = 3

    SET AB = X > 1
    SET BB = X < 2 AND X * 2 + Y < 4 OR X == 1

    IF ( NOT AB > 2 OR B < 2 ) THEN
       
    END
    
    WHILE (TRUE OR AB < 2)
    END
    """

    result = parser.parse(s, lexer=lexer)

    analyzer = SemanticAnalyzer()
    analyzer.visit(DeclareFunction('main', None, result))

    ptree(result, annotated=True)

    print(result)