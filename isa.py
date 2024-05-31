from enum import Enum


class Opcode(Enum):
    MOV = "MOV"
    LOAD = "LOAD"
    STORE = "STORE"
    ADD = "ADD"
    SUB = "SUB"
    IDIV = "IDIV"
    DIV = "DIV"
    MUL = "MUL"
    INC = "INC"
    DEC = "DEC"
    CMP = "CMP"
    JMP = "JMP"
    JZ = "JZ"
    JNZ = "JNZ"
    HALT = "HALT"
    OUT = "OUT"
    IN = "IN"


class ArgType(Enum):
    REG = "reg"
    NUMBER = "number"
    INDIRECT_ADDRESS = "indirect_address"
