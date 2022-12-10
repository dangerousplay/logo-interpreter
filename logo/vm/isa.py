import enum
from collections import namedtuple

Load = namedtuple("LOAD", "id")
Push = namedtuple("PUSH", "value")
Pop = namedtuple("POP", "")
Duplicate = namedtuple("DUP", "")
Store = namedtuple("STOR", "id")

Compare = namedtuple("CMP", "value")

Label = namedtuple("Label", "name instructions")
Jump = namedtuple("JP", "label")
JumpZ = namedtuple("JZ", "label")
JumpNZ = namedtuple("JNZ", "label")
JumpMore = namedtuple("JMORE", "label")
JumpLess = namedtuple("JLESS", "label")

Add = namedtuple("ADD", "")
Subtract = namedtuple("SUB", "")
Multiply = namedtuple("MUL", "")
Pow = namedtuple("POW", "")
Divide = namedtuple("DIV", "")
IntDivide = namedtuple("IDIV", "")

Random = namedtuple("RAND", "")

Not = namedtuple("NOT", "")
And = namedtuple("AND", "")
Or = namedtuple("OR", "")
Truncate = namedtuple("TRUNC","")

Skipnz = namedtuple("SKIPNZ", "")
Skipz = namedtuple("SKIPZ", "")

Read = namedtuple("READ", "")
Write = namedtuple("WRITE", "")

MoveTo = namedtuple("MVTO", "")

Call = namedtuple("CALL", "function")

DefineFunction = namedtuple("DEF", "id instructions")

Set = namedtuple("SET", "number")
Unset = namedtuple("UNSET", "number")

Return = namedtuple("RET", "")


class Flags(enum.IntEnum):
    PEN = 1
    DRAW = 2
    ERASE = 3
    EXC = 5


