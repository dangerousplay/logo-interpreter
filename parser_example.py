from logo.parse import parser
from logo.lexer import lexer
from printree import ptree


if __name__ == '__main__':
    s = """
    TO RR :AABB
     SET B = AABB ^ 2
    END

    RR 1234
    
    SET B = 13
    
    RR B

    SET AB = x > 1

    IF NOT AB > 2 OR B < 2 THEN
       
    END
    """

    result = parser.parse(s, lexer=lexer)
    ptree(result, annotated=True)

    print(result)