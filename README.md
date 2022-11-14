
# Logo interpreter

A simple logo interpreter and parser using the Python Ply library developed for the compilers course.

## Running

The pip dependencies declared in [requirements.txt](requirements.txt) should be installed:

```shell
pip install -r requirements.txt
```

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

SET AB = x > 1

IF NOT AB > 2 OR B < 2 THEN
   
END
```

Running the example:

```shell
python3 parser_example.py
```

Should return the following printed object tree:

```text
┐ -> list[items=6]
├── 0 -> DeclareFunction[items=3]
│   ├── 0: RR
│   ├── 1 -> list[items=1]
│   │   └── 0: AABB
│   └── 2 -> list[items=1]
│       └── 0 -> Assignment[items=2]
│           ├── 0: B
│           └── 1 -> BinaryOperation[items=3]
│               ├── 0: TokenType.POW
│               ├── 1 -> Identifier[items=1]
│               │   └── 0: AABB
│               └── 2: 2.0
├── 1 -> InvokeFunction[items=2]
│   ├── 0: RR
│   └── 1 -> list[items=1]
│       └── 0: 1234.0
├── 2 -> Assignment[items=2]
│   ├── 0: B
│   └── 1: 13.0
├── 3 -> InvokeFunction[items=2]
│   ├── 0: RR
│   └── 1 -> list[items=1]
│       └── 0 -> Identifier[items=1]
│           └── 0: B
├── 4 -> Assignment[items=2]
│   ├── 0: AB
│   └── 1 -> BinaryOperation[items=3]
│       ├── 0: TokenType.GREATER_THAN
│       ├── 1 -> Identifier[items=1]
│       │   └── 0: x
│       └── 2: 1.0
└── 5 -> IfStatement[items=3]
    ├── 0 -> BinaryOperation[items=3]
    │   ├── 0: TokenType.OR
    │   ├── 1 -> NotOperation[items=1]
    │   │   └── 0 -> BinaryOperation[items=3]
    │   │       ├── 0: TokenType.GREATER_THAN
    │   │       ├── 1 -> Identifier[items=1]
    │   │       │   └── 0: AB
    │   │       └── 2: 2.0
    │   └── 2 -> BinaryOperation[items=3]
    │       ├── 0: TokenType.LESS_THAN
    │       ├── 1 -> Identifier[items=1]
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