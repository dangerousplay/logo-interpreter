
# Logo interpreter

A simple logo interpreter and parser using the Python Ply library developed for the compilers course.

## Running

The pip dependencies declared in [requirements.txt](requirements.txt) should be installed:

```shell
pip install -r requirements.txt
```

## Implementation

### Semantic Analyser

To verify the semantics of the given program, a Semantic Verifier was implemented.
Due to nested scopes being allowed in the language, a Scope Symbol Table was implemented using as reference the implementation done by [Ruslan Pivak](https://ruslanspivak.com/lsbasi-part14/).

![](https://ruslanspivak.com/lsbasi-part14/lsbasi_part14_img14.png)

Source: [Let’s Build A Simple Interpreter. Part 14: Nested Scopes and a Source-to-Source Compiler](https://ruslanspivak.com/lsbasi-part14/)

## Examples

### Parser example

There is one example in then [parser_example.py](./parser_example.py) file that parses a simple program:

```logo
TO RR :AABB
 SET B = AABB ^ 2
END

RR 1234

SET B = 13

RR B
SET X = 3
SET Y = 3

SET AB = X > 1
SET BB = X < 2 AND X * 2 + Y < 4 OR X == 1

IF NOT AB > 2 OR B < 2 THEN
   
END
```

Running the example:

```shell
python3 parser_example.py
```

Should return the following printed object tree:

```text
┐ → list[items=9]
├── 0 → DeclareFunction[items=3]
│   ├── 0: RR
│   ├── 1 → list[items=1]
│   │   └── 0: AABB
│   └── 2 → list[items=1]
│       └── 0 → Assignment[items=2]
│           ├── 0: B
│           └── 1 → BinaryOperation[items=3]
│               ├── 0: TokenType.POW
│               ├── 1 → Identifier[items=1]
│               │   └── 0: AABB
│               └── 2: 2.0
├── 1 → InvokeFunction[items=2]
│   ├── 0: RR
│   └── 1 → list[items=1]
│       └── 0: 1234.0
├── 2 → Assignment[items=2]
│   ├── 0: B
│   └── 1: 13.0
├── 3 → InvokeFunction[items=2]
│   ├── 0: RR
│   └── 1 → list[items=1]
│       └── 0 → Identifier[items=1]
│           └── 0: B
├── 4 → Assignment[items=2]
│   ├── 0: X
│   └── 1: 3.0
├── 5 → Assignment[items=2]
│   ├── 0: Y
│   └── 1: 3.0
├── 6 → Assignment[items=2]
│   ├── 0: AB
│   └── 1 → BinaryOperation[items=3]
│       ├── 0: TokenType.GREATER_THAN
│       ├── 1 → Identifier[items=1]
│       │   └── 0: X
│       └── 2: 1.0
├── 7 → Assignment[items=2]
│   ├── 0: BB
│   └── 1 → BinaryOperation[items=3]
│       ├── 0: TokenType.AND
│       ├── 1 → BinaryOperation[items=3]
│       │   ├── 0: TokenType.LESS_THAN
│       │   ├── 1 → Identifier[items=1]
│       │   │   └── 0: X
│       │   └── 2: 2.0
│       └── 2 → BinaryOperation[items=3]
│           ├── 0: TokenType.OR
│           ├── 1 → BinaryOperation[items=3]
│           │   ├── 0: TokenType.LESS_THAN
│           │   ├── 1 → BinaryOperation[items=3]
│           │   │   ├── 0: TokenType.PLUS
│           │   │   ├── 1 → BinaryOperation[items=3]
│           │   │   │   ├── 0: TokenType.TIMES
│           │   │   │   ├── 1 → Identifier[items=1]
│           │   │   │   │   └── 0: X
│           │   │   │   └── 2: 2.0
│           │   │   └── 2 → Identifier[items=1]
│           │   │       └── 0: Y
│           │   └── 2: 4.0
│           └── 2 → BinaryOperation[items=3]
│               ├── 0: TokenType.IS_EQUAL
│               ├── 1 → Identifier[items=1]
│               │   └── 0: X
│               └── 2: 1.0
└── 8 → IfStatement[items=3]
    ├── 0 → BinaryOperation[items=3]
    │   ├── 0: TokenType.OR
    │   ├── 1 → NotOperation[items=1]
    │   │   └── 0 → BinaryOperation[items=3]
    │   │       ├── 0: TokenType.GREATER_THAN
    │   │       ├── 1 → Identifier[items=1]
    │   │       │   └── 0: AB
    │   │       └── 2: 2.0
    │   └── 2 → BinaryOperation[items=3]
    │       ├── 0: TokenType.LESS_THAN
    │       ├── 1 → Identifier[items=1]
    │       │   └── 0: B
    │       └── 2: 2.0
    ├── 1: None
    └── 2: None
```

## Running the tests

There are automated tests in the [tests](./tests) directory for the major features of the language.

The tests can be run using the unittest module:

```shell
python -m unittest discover -s tests -p '*.py'
```