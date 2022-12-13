import enum
from typing import Any

from logo.vm.isa import DefineFunction, Store, Call, Push, Load, Set, Unset, Flags, MoveTo, Return, \
    Subtract, Add


class GlobalVariables(enum.Enum):
    Angle = "angle"


class BuiltInVars(enum.Enum):
    HEADING = "HEADING"
    RANDOM = "RANDOM"
    XCOR = "XCOR"
    YCOR = "YCOR"


class BuiltInFunctions(enum.Enum):
    MOVE = "MOVE"
    WRITE = "WRITE"
    READ = "READ"
    FORWARD = "FORWARD"
    BACKWARD = "BACKWARD"
    RIGHT = "RIGHT"
    LEFT = "LEFT"
    PENUP = "PENUP"
    PENDOWN = "PENDOWN"
    HOME = "HOME"
    SETXY = "SETXY"
    TYPEIN = "TYPEIN"
    WIPECLEAN = "WIPECLEAN"
    CLRSCR = "CLRSCR"
    CLEARSCREEN = "CLEARSCREEN"


def built_in_functions() -> tuple[dict[str, DefineFunction], dict[str, Any]]:
    var_num = "num"
    var_angle = GlobalVariables.Angle.value

    forward = DefineFunction("FORWARD", [Store(var_num), Load(var_angle), Load(var_num), Call(BuiltInFunctions.MOVE.value), Return()])
    backward = DefineFunction("BACKWARD", [Store(var_num), Push(180), Load(var_angle), Add(), Load(var_num), Call(BuiltInFunctions.MOVE.value), Return()])

    right = DefineFunction("RIGHT", [Store(var_num), Load(var_angle), Load(var_num), Subtract(), Store(var_angle), Return()])
    left = DefineFunction("LEFT", [Load(var_angle), Add(), Store(var_angle), Return()])

    pen_up = DefineFunction("PENUP", [Unset(Flags.PEN), Return()])
    pen_down = DefineFunction("PENDOWN", [Set(Flags.PEN), Return()])

    home = DefineFunction("HOME", [Push(0), Push(0), MoveTo(), Return()])
    setxy = DefineFunction("SETXY", [MoveTo(), Return()])

    typein = DefineFunction("TYPEIN", [Call(BuiltInFunctions.READ.value), Return()])

    wipe_clean = DefineFunction("WIPECLEAN", [Call(BuiltInFunctions.CLRSCR.value), Return()])
    clear_screen = DefineFunction("CLEARSCREEN", [Call(wipe_clean.id), Call(home.id), Return()])

    variables = {
        var_num: 0,
        var_angle: 0,
    }

    functions = {
        BuiltInFunctions.FORWARD.value: forward,
        BuiltInFunctions.BACKWARD.value: backward,
        BuiltInFunctions.RIGHT.value: right,
        BuiltInFunctions.LEFT.value: left,
        BuiltInFunctions.PENUP.value: pen_up,
        BuiltInFunctions.PENDOWN.value: pen_down,
        BuiltInFunctions.WIPECLEAN.value: wipe_clean,
        BuiltInFunctions.CLEARSCREEN.value: clear_screen,
        BuiltInFunctions.SETXY.value: setxy,
        BuiltInFunctions.HOME.value: home,
        BuiltInFunctions.TYPEIN.value: typein
    }

    return functions, variables
