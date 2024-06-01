from isa import ArgType, Opcode

from enum import Enum, auto
from typing import Dict, List, Union
from numpy import int16


class Signal(Enum):
    LATCH_IP = auto()
    SEL_IP = auto()
    LATCH_IR = auto()
    LATCH_MC_ADDR = auto()
    SEL_MC_ADDR = auto()
    READ_MC = auto()
    LATCH_R1 = auto()
    LATCH_R2 = auto()
    LATCH_R3 = auto()
    SEL_OP_1 = auto()
    SEL_OP_2 = auto()
    OPERATION = auto()
    START_DECODE = auto()
    SEL_ADDR = auto()
    LATCH_ADDR = auto()
    MEM_READ = auto()
    MEM_WRITE = auto()
    OUT_BUF_WRITE = auto()
    OUT_BUF_NEXT = auto()
    INP_BUF_READ = auto()
    INP_BUF_NEXT = auto()
    LATCH_DR = auto()
    SEL_R_READ = auto()
    SEL_R_WRITE = auto()
    LATCH_OR = auto()


class SignalValue(Enum):
    LATCH = 1
    SEL_IP_INC = 0
    SEL_IP_OP = 1
    SEL_MC_ADDR_INC = 0
    SEL_MC_ADDR_NEXT = 1
    SEL_MC_ADDR_NULL = 2
    SEL_OP_FIRST_R1 = 0
    SEL_OP_FIRST_R2 = 1
    SEL_OP_FIRST_R3 = 2
    SEL_OP_SECOND_R1 = 0
    SEL_OP_SECOND_R2 = 1
    SEL_OP_SECOND_R3 = 2
    SEL_OP_SECOND_OP = 3
    OPERATION_ADD = 0
    OPERATION_SUB = 1
    OPERATION_IDIV = 2
    OPERATION_DIV = 3
    OPERATION_MUL = 4
    OPERATION_INC = 5
    OPERATION_DEC = 6
    READ = 1
    WRITE = 1
    SEL_ADDRESS_OPERAND = 0
    SEL_ADDRESS_MUX2 = 1
    SEL_R_READ_R1 = 0
    SEL_R_READ_R2 = 1
    SEL_R_READ_R3 = 2
    SEL_R_WRITE_ALU = 0
    SEL_R_WRITE_OR = 1
    SEL_R_WRITE_INP_BUFF = 2
    SEL_R_WRITE_DR = 3
    SEL_R_WRITE_MUX2 = 4
    START_DECODE = 1
    READ_MC = 1


Instruction = Dict[str, Union[Opcode, List[Dict[ArgType, str]]]]

Microcode = Dict[Signal, SignalValue]


class InstructionDecoder:
    operand: int16 = None

    mc_addres: int16 = None

    zero_flag: bool = None

    first_arg_val: str = None
    second_arg_val: str = None
    second_arg_type: ArgType = None
    first_arg_type: ArgType = None
    third_arg_val: str = None

    def __init__(self):
        self.operand = 0
        self.mc_addres = 0
        self.zero_flag = False

        self.dispatch_table = {
            Opcode.MOV: self.handle_mov,
            Opcode.LOAD: self.handle_load,
            Opcode.STORE: self.handle_store,
            Opcode.ADD: self.handle_add,
            Opcode.SUB: self.handle_sub,
            Opcode.IDIV: self.handle_idiv,
            Opcode.DIV: self.handle_div,
            Opcode.MUL: self.handle_mul,
            Opcode.INC: self.handle_inc,
            Opcode.DEC: self.handle_dec,
            Opcode.CMP: self.handle_cmp,
            Opcode.JMP: self.handle_jmp,
            Opcode.JZ: self.handle_jz,
            Opcode.JNZ: self.handle_jnz,
            Opcode.OUT: self.handle_out,
            Opcode.IN: self.handle_in,
            Opcode.HALT: self.handle_halt,
        }

        self.mc_address_mapping = {
            ("MOV", "R1", ArgType.NUMBER): 2,
            ("MOV", "R2", ArgType.NUMBER): 3,
            ("MOV", "R3", ArgType.NUMBER): 4,
            ("MOV", "R1", "R2"): 5,
            ("MOV", "R2", "R1"): 6,
            ("MOV", "R2", "R3"): 7,
            ("MOV", "R3", "R2"): 8,
            ("MOV", "R1", "R3"): 9,
            ("MOV", "R3", "R1"): 10,
            ("LOAD", "R1", ArgType.NUMBER): 11,
            ("LOAD", "R2", ArgType.NUMBER): 13,
            ("LOAD", "R3", ArgType.NUMBER): 15,
            ("LOAD", "R1", "R2"): 23,
            ("LOAD", "R1", "R3"): 26,
            ("LOAD", "R2", "R1"): 29,
            ("LOAD", "R2", "R3"): 32,
            ("LOAD", "R3", "R1"): 35,
            ("LOAD", "R3", "R2"): 38,
            ("STORE", "R1", ArgType.NUMBER): 17,
            ("STORE", "R2", ArgType.NUMBER): 19,
            ("STORE", "R3", ArgType.NUMBER): 21,
            ("STORE", "R1", "R2"): 41,
            ("STORE", "R1", "R3"): 43,
            ("STORE", "R2", "R1"): 45,
            ("STORE", "R2", "R3"): 47,
            ("STORE", "R3", "R1"): 49,
            ("STORE", "R3", "R2"): 51,
            ("ADD", "R1"): 53,
            ("ADD", "R2"): 55,
            ("ADD", "R3"): 57,
            ("SUB", "R1", "R2"): 59,
            ("SUB", "R2", "R1"): 61,
            ("SUB", "R3", "R1"): 63,
            ("SUB", "R1", "R3"): 103,
            ("SUB", "R2", "R3"): 105,
            ("SUB", "R3", "R2"): 107,
            ("IDIV", "R1", "R2"): 65,
            ("IDIV", "R2", "R1"): 67,
            ("IDIV", "R3", "R1"): 69,
            ("IDIV", "R1", "R3"): 109,
            ("IDIV", "R2", "R3"): 111,
            ("IDIV", "R3", "R2"): 113,
            ("DIV", "R1", "R2"): 71,
            ("DIV", "R2", "R1"): 73,
            ("DIV", "R3", "R1"): 75,
            ("DIV", "R1", "R3"): 97,
            ("DIV", "R2", "R3"): 99,
            ("DIV", "R3", "R2"): 101,
            ("MUL", "R1", "R2"): 115,
            ("MUL", "R2", "R1"): 117,
            ("MUL", "R3", "R1"): 119,
            ("DEC", "R1"): 121,
            ("DEC", "R2"): 123,
            ("DEC", "R3"): 125,
            ("INC", "R1"): 77,
            ("INC", "R2"): 79,
            ("INC", "R3"): 81,
            ("CMP", "R1", "R2"): 83,
            ("CMP", "R2", "R3"): 84,
            ("CMP", "R1", "R3"): 85,
            ("CMP", "R1", ArgType.NUMBER): 94,
            ("CMP", "R2", ArgType.NUMBER): 95,
            ("CMP", "R3", ArgType.NUMBER): 96,
            ("JMP",): 86,
            ("JZ", True): 86,
            ("JZ", False): 93,
            ("JNZ", True): 93,
            ("JNZ", False): 86,
            ("OUT", "R1"): 87,
            ("OUT", "R2"): 88,
            ("OUT", "R3"): 89,
            ("IN", "R1"): 90,
            ("IN", "R2"): 91,
            ("IN", "R3"): 92,
        }

    def set_mc_address(self, command, *args):
        key = (command,) + args
        self.mc_addres = self.mc_address_mapping.get(key, None)
        if self.mc_addres is None:
            raise ValueError(
                f"No microcode address found for command {command} with args {args}"
            )

    def decode(self, instruction: Instruction):
        opcode = Opcode[instruction["opcode"]]
        args = instruction["args"]
        self.first_arg_val = ""
        self.first_arg_type = None
        self.second_arg_val = ""
        self.second_arg_type = None

        if len(args) > 0:
            self.first_arg_val = list(args[0].values())[0]
            self.first_arg_type = ArgType[list(args[0].keys())[0].upper()]
            if self.first_arg_type == ArgType.NUMBER:
                self.operand = int16(int(self.first_arg_val))

        if len(args) > 1:
            self.second_arg_val = list(args[1].values())[0]
            self.second_arg_type = ArgType[list(args[1].keys())[0].upper()]
            if self.second_arg_type == ArgType.NUMBER:
                self.operand = int16(int(self.second_arg_val))

        handler = self.dispatch_table.get(opcode)
        if handler:
            handler()

    def handle_mov(self):
        if (
            self.first_arg_type == ArgType.REG
            and self.second_arg_type == ArgType.NUMBER
        ):
            self.set_mc_address("MOV", self.first_arg_val, self.second_arg_type)
        else:
            self.set_mc_address("MOV", self.first_arg_val, self.second_arg_val)

    def handle_load(self):
        if (
            self.first_arg_type == ArgType.REG
            and self.second_arg_type == ArgType.NUMBER
        ):
            self.set_mc_address("LOAD", self.first_arg_val, self.second_arg_type)
        else:
            self.set_mc_address("LOAD", self.first_arg_val, self.second_arg_val)

    def handle_store(self):
        if (
            self.first_arg_type == ArgType.REG
            and self.second_arg_type == ArgType.NUMBER
        ):
            self.set_mc_address("STORE", self.first_arg_val, self.second_arg_type)
        else:
            self.set_mc_address("STORE", self.first_arg_val, self.second_arg_val)

    def handle_add(self):
        self.set_mc_address("ADD", self.first_arg_val)

    def handle_sub(self):
        self.set_mc_address("SUB", self.first_arg_val, self.second_arg_val)

    def handle_idiv(self):
        self.set_mc_address("IDIV", self.first_arg_val, self.second_arg_val)

    def handle_div(self):
        self.set_mc_address("DIV", self.first_arg_val, self.second_arg_val)

    def handle_mul(self):
        self.set_mc_address("MUL", self.first_arg_val, self.second_arg_val)

    def handle_inc(self):
        self.set_mc_address("INC", self.first_arg_val)

    def handle_dec(self):
        self.set_mc_address("DEC", self.first_arg_val)

    def handle_cmp(self):
        if self.second_arg_type == ArgType.NUMBER:
            self.set_mc_address("CMP", self.first_arg_val, self.second_arg_type)
        else:
            self.set_mc_address("CMP", self.first_arg_val, self.second_arg_val)

    def handle_jmp(self):
        self.set_mc_address("JMP")

    def handle_jz(self):
        self.set_mc_address("JZ", self.zero_flag)

    def handle_jnz(self):
        self.set_mc_address("JNZ", not self.zero_flag)

    def handle_out(self):
        self.set_mc_address("OUT", self.first_arg_val)

    def handle_in(self):
        self.set_mc_address("IN", self.first_arg_val)

    def handle_halt(self):
        raise StopIteration()


class ControlStore:
    mc_memory: List[Microcode] = None

    def __init__(self) -> None:
        self.mc_memory = []

        # 0-1: INSTR FETCH
        self.mc_memory.append(
            {
                Signal.LATCH_IP: SignalValue.LATCH.value,
                Signal.SEL_IP: SignalValue.SEL_IP_INC.value,
                Signal.LATCH_IR: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.START_DECODE: SignalValue.START_DECODE.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NEXT.value,
            }
        )

        # 2: MOV r1, <number>
        self.mc_memory.append(
            {
                Signal.LATCH_OR: SignalValue.LATCH.value,
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_OR.value,
                Signal.LATCH_R1: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 3: MOV r2, <number>
        self.mc_memory.append(
            {
                Signal.LATCH_OR: SignalValue.LATCH.value,
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_OR.value,
                Signal.LATCH_R2: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 4: MOV r3, <number>
        self.mc_memory.append(
            {
                Signal.LATCH_OR: SignalValue.LATCH.value,
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_OR.value,
                Signal.LATCH_R3: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 5: MOV r1, r2
        self.mc_memory.append(
            {
                Signal.SEL_R_READ: SignalValue.SEL_R_READ_R2.value,
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_MUX2.value,
                Signal.LATCH_R1: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 6: MOV r2, r1
        self.mc_memory.append(
            {
                Signal.SEL_R_READ: SignalValue.SEL_R_READ_R1.value,
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_MUX2.value,
                Signal.LATCH_R2: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 7: MOV r2, r3
        self.mc_memory.append(
            {
                Signal.SEL_R_READ: SignalValue.SEL_R_READ_R3.value,
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_MUX2.value,
                Signal.LATCH_R2: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 8: MOV r3, r2
        self.mc_memory.append(
            {
                Signal.SEL_R_READ: SignalValue.SEL_R_READ_R2.value,
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_MUX2.value,
                Signal.LATCH_R3: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 9: MOV r1, r3
        self.mc_memory.append(
            {
                Signal.SEL_R_READ: SignalValue.SEL_R_READ_R3.value,
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_MUX2.value,
                Signal.LATCH_R1: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 10: MOV r3, r1
        self.mc_memory.append(
            {
                Signal.SEL_R_READ: SignalValue.SEL_R_READ_R1.value,
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_MUX2.value,
                Signal.LATCH_R3: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 11-12: LOAD r1, <direct_address>
        self.mc_memory.append(
            {
                Signal.SEL_ADDR: SignalValue.SEL_ADDRESS_OPERAND.value,
                Signal.LATCH_ADDR: SignalValue.LATCH.value,
                Signal.MEM_READ: SignalValue.READ.value,
                Signal.LATCH_DR: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_DR.value,
                Signal.LATCH_R1: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 13-14: LOAD r2, <direct_address>
        self.mc_memory.append(
            {
                Signal.SEL_ADDR: SignalValue.SEL_ADDRESS_OPERAND.value,
                Signal.LATCH_ADDR: SignalValue.LATCH.value,
                Signal.MEM_READ: SignalValue.READ.value,
                Signal.LATCH_DR: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_DR.value,
                Signal.LATCH_R2: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 15-16: LOAD r3, <direct_address>
        self.mc_memory.append(
            {
                Signal.SEL_ADDR: SignalValue.SEL_ADDRESS_OPERAND.value,
                Signal.LATCH_ADDR: SignalValue.LATCH.value,
                Signal.MEM_READ: SignalValue.READ.value,
                Signal.LATCH_DR: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_DR.value,
                Signal.LATCH_R3: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 17-18: STORE r1, <direct_address>
        self.mc_memory.append(
            {
                Signal.SEL_ADDR: SignalValue.SEL_ADDRESS_OPERAND.value,
                Signal.LATCH_ADDR: SignalValue.LATCH.value,
                Signal.SEL_R_READ: SignalValue.SEL_R_READ_R1.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )

        self.mc_memory.append(
            {
                Signal.MEM_WRITE: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 19-20: STORE r2, <direct_address>
        self.mc_memory.append(
            {
                Signal.SEL_ADDR: SignalValue.SEL_ADDRESS_OPERAND.value,
                Signal.LATCH_ADDR: SignalValue.LATCH.value,
                Signal.SEL_R_READ: SignalValue.SEL_R_READ_R2.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )

        self.mc_memory.append(
            {
                Signal.MEM_WRITE: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 21-22: STORE r3, <direct_address>
        self.mc_memory.append(
            {
                Signal.SEL_ADDR: SignalValue.SEL_ADDRESS_OPERAND.value,
                Signal.LATCH_ADDR: SignalValue.LATCH.value,
                Signal.SEL_R_READ: SignalValue.SEL_R_READ_R3.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )

        self.mc_memory.append(
            {
                Signal.MEM_WRITE: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 23-25: LOAD r1, (r2)
        self.mc_memory.append(
            {
                Signal.SEL_R_READ: SignalValue.SEL_R_READ_R2.value,
                Signal.SEL_ADDR: SignalValue.SEL_ADDRESS_MUX2.value,
                Signal.LATCH_ADDR: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )

        self.mc_memory.append(
            {
                Signal.MEM_READ: SignalValue.READ.value,
                Signal.LATCH_DR: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )

        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_DR.value,
                Signal.LATCH_R1: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 26-28: LOAD r1, (r3)
        self.mc_memory.append(
            {
                Signal.SEL_R_READ: SignalValue.SEL_R_READ_R3.value,
                Signal.SEL_ADDR: SignalValue.SEL_ADDRESS_MUX2.value,
                Signal.LATCH_ADDR: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )

        self.mc_memory.append(
            {
                Signal.MEM_READ: SignalValue.READ.value,
                Signal.LATCH_DR: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )

        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_DR.value,
                Signal.LATCH_R1: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 29-31: LOAD r2, (r1)
        self.mc_memory.append(
            {
                Signal.SEL_R_READ: SignalValue.SEL_R_READ_R1.value,
                Signal.SEL_ADDR: SignalValue.SEL_ADDRESS_MUX2.value,
                Signal.LATCH_ADDR: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )

        self.mc_memory.append(
            {
                Signal.MEM_READ: SignalValue.READ.value,
                Signal.LATCH_DR: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )

        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_DR.value,
                Signal.LATCH_R2: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 32-34: LOAD r2, (r3)
        self.mc_memory.append(
            {
                Signal.SEL_R_READ: SignalValue.SEL_R_READ_R3.value,
                Signal.SEL_ADDR: SignalValue.SEL_ADDRESS_MUX2.value,
                Signal.LATCH_ADDR: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )

        self.mc_memory.append(
            {
                Signal.MEM_READ: SignalValue.READ.value,
                Signal.LATCH_DR: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )

        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_DR.value,
                Signal.LATCH_R2: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 35-37: LOAD r3, (r1)
        self.mc_memory.append(
            {
                Signal.SEL_R_READ: SignalValue.SEL_R_READ_R1.value,
                Signal.SEL_ADDR: SignalValue.SEL_ADDRESS_MUX2.value,
                Signal.LATCH_ADDR: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )

        self.mc_memory.append(
            {
                Signal.MEM_READ: SignalValue.READ.value,
                Signal.LATCH_DR: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )

        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_DR.value,
                Signal.LATCH_R3: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 38-40: LOAD r3, (r2)
        self.mc_memory.append(
            {
                Signal.SEL_R_READ: SignalValue.SEL_R_READ_R2.value,
                Signal.SEL_ADDR: SignalValue.SEL_ADDRESS_MUX2.value,
                Signal.LATCH_ADDR: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )

        self.mc_memory.append(
            {
                Signal.MEM_READ: SignalValue.READ.value,
                Signal.LATCH_DR: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )

        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_DR.value,
                Signal.LATCH_R3: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 41-42: STORE r1, (r2)
        self.mc_memory.append(
            {
                Signal.SEL_R_READ: SignalValue.SEL_R_READ_R2.value,
                Signal.SEL_ADDR: SignalValue.SEL_ADDRESS_MUX2.value,
                Signal.LATCH_ADDR: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )

        self.mc_memory.append(
            {
                Signal.SEL_R_READ: SignalValue.SEL_R_READ_R1.value,
                Signal.MEM_WRITE: SignalValue.WRITE.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 43-44: STORE r1, (r3)
        self.mc_memory.append(
            {
                Signal.SEL_R_READ: SignalValue.SEL_R_READ_R3.value,
                Signal.SEL_ADDR: SignalValue.SEL_ADDRESS_MUX2.value,
                Signal.LATCH_ADDR: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )

        self.mc_memory.append(
            {
                Signal.SEL_R_READ: SignalValue.SEL_R_READ_R1.value,
                Signal.MEM_WRITE: SignalValue.WRITE.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 45-46: STORE r2, (r1)
        self.mc_memory.append(
            {
                Signal.SEL_R_READ: SignalValue.SEL_R_READ_R1.value,
                Signal.SEL_ADDR: SignalValue.SEL_ADDRESS_MUX2.value,
                Signal.LATCH_ADDR: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )

        self.mc_memory.append(
            {
                Signal.SEL_R_READ: SignalValue.SEL_R_READ_R2.value,
                Signal.MEM_WRITE: SignalValue.WRITE.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 47-48: STORE r2, (r3)
        self.mc_memory.append(
            {
                Signal.SEL_R_READ: SignalValue.SEL_R_READ_R3.value,
                Signal.SEL_ADDR: SignalValue.SEL_ADDRESS_MUX2.value,
                Signal.LATCH_ADDR: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )

        self.mc_memory.append(
            {
                Signal.SEL_R_READ: SignalValue.SEL_R_READ_R2.value,
                Signal.MEM_WRITE: SignalValue.WRITE.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 49-50: STORE r3, (r1)
        self.mc_memory.append(
            {
                Signal.SEL_R_READ: SignalValue.SEL_R_READ_R1.value,
                Signal.SEL_ADDR: SignalValue.SEL_ADDRESS_MUX2.value,
                Signal.LATCH_ADDR: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )

        self.mc_memory.append(
            {
                Signal.SEL_R_READ: SignalValue.SEL_R_READ_R3.value,
                Signal.MEM_WRITE: SignalValue.WRITE.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 51-52: STORE r3, (r2)
        self.mc_memory.append(
            {
                Signal.SEL_R_READ: SignalValue.SEL_R_READ_R2.value,
                Signal.SEL_ADDR: SignalValue.SEL_ADDRESS_MUX2.value,
                Signal.LATCH_ADDR: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )

        self.mc_memory.append(
            {
                Signal.SEL_R_READ: SignalValue.SEL_R_READ_R3.value,
                Signal.MEM_WRITE: SignalValue.WRITE.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 53-54: ADD r1, r2, r3
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R2.value,
                Signal.SEL_OP_2: SignalValue.SEL_OP_SECOND_R3.value,
                Signal.OPERATION: SignalValue.OPERATION_ADD.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_ALU.value,
                Signal.LATCH_R1: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 55-56: ADD r2, r1, r3
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R1.value,
                Signal.SEL_OP_2: SignalValue.SEL_OP_SECOND_R3.value,
                Signal.OPERATION: SignalValue.OPERATION_ADD.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_ALU.value,
                Signal.LATCH_R2: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 57-58: ADD r3, r1, r2
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R1.value,
                Signal.SEL_OP_2: SignalValue.SEL_OP_SECOND_R2.value,
                Signal.OPERATION: SignalValue.OPERATION_ADD.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_ALU.value,
                Signal.LATCH_R3: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 59-60: SUB r1, r2, r3
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R2.value,
                Signal.SEL_OP_2: SignalValue.SEL_OP_SECOND_R3.value,
                Signal.OPERATION: SignalValue.OPERATION_SUB.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_ALU.value,
                Signal.LATCH_R1: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 61-62: SUB r2, r1, r3
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R1.value,
                Signal.SEL_OP_2: SignalValue.SEL_OP_SECOND_R3.value,
                Signal.OPERATION: SignalValue.OPERATION_SUB.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_ALU.value,
                Signal.LATCH_R2: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 63-64: SUB r3, r1, r2
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R1.value,
                Signal.SEL_OP_2: SignalValue.SEL_OP_SECOND_R2.value,
                Signal.OPERATION: SignalValue.OPERATION_SUB.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_ALU.value,
                Signal.LATCH_R3: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 65-66: IDIV r1, r2, r3
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R2.value,
                Signal.SEL_OP_2: SignalValue.SEL_OP_SECOND_R3.value,
                Signal.OPERATION: SignalValue.OPERATION_IDIV.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_ALU.value,
                Signal.LATCH_R1: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 67-68: IDIV r2, r1, r3
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R1.value,
                Signal.SEL_OP_2: SignalValue.SEL_OP_SECOND_R3.value,
                Signal.OPERATION: SignalValue.OPERATION_IDIV.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_ALU.value,
                Signal.LATCH_R2: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 69-70: IDIV r3, r1, r2
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R1.value,
                Signal.SEL_OP_2: SignalValue.SEL_OP_SECOND_R2.value,
                Signal.OPERATION: SignalValue.OPERATION_IDIV.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_ALU.value,
                Signal.LATCH_R3: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 71-72: DIV r1, r2, r3
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R2.value,
                Signal.SEL_OP_2: SignalValue.SEL_OP_SECOND_R3.value,
                Signal.OPERATION: SignalValue.OPERATION_DIV.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_ALU.value,
                Signal.LATCH_R1: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 73-74: DIV r2, r1, r3
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R1.value,
                Signal.SEL_OP_2: SignalValue.SEL_OP_SECOND_R3.value,
                Signal.OPERATION: SignalValue.OPERATION_DIV.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_ALU.value,
                Signal.LATCH_R2: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 75-76: DIV r3, r1, r2
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R1.value,
                Signal.SEL_OP_2: SignalValue.SEL_OP_SECOND_R2.value,
                Signal.OPERATION: SignalValue.OPERATION_DIV.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_ALU.value,
                Signal.LATCH_R3: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 77-78: INC r1
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R1.value,
                Signal.OPERATION: SignalValue.OPERATION_INC.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_ALU.value,
                Signal.LATCH_R1: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 79-80: INC r2
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R2.value,
                Signal.OPERATION: SignalValue.OPERATION_INC.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_ALU.value,
                Signal.LATCH_R2: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 81-82: INC r3
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R3.value,
                Signal.OPERATION: SignalValue.OPERATION_INC.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_ALU.value,
                Signal.LATCH_R3: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 83: CMP r1, r2
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R1.value,
                Signal.SEL_OP_2: SignalValue.SEL_OP_SECOND_R2.value,
                Signal.OPERATION: SignalValue.OPERATION_SUB.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 84: CMP r2, r3
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R2.value,
                Signal.SEL_OP_2: SignalValue.SEL_OP_SECOND_R3.value,
                Signal.OPERATION: SignalValue.OPERATION_SUB.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 85: CMP r1, r3
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R1.value,
                Signal.SEL_OP_2: SignalValue.SEL_OP_SECOND_R3.value,
                Signal.OPERATION: SignalValue.OPERATION_SUB.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 86: JMP <direct_address> (and JNZ when z_flag = 0 and JZ when z_flag = 1)
        self.mc_memory.append(
            {
                Signal.SEL_IP: SignalValue.SEL_IP_OP.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 87: OUT r1, 1
        self.mc_memory.append(
            {
                Signal.SEL_R_READ: SignalValue.SEL_R_READ_R1.value,
                Signal.OUT_BUF_NEXT: SignalValue.LATCH.value,
                Signal.LATCH_OR: SignalValue.LATCH,
                Signal.OUT_BUF_WRITE: SignalValue.WRITE.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 88: OUT r2, 1
        self.mc_memory.append(
            {
                Signal.SEL_R_READ: SignalValue.SEL_R_READ_R2.value,
                Signal.OUT_BUF_NEXT: SignalValue.LATCH.value,
                Signal.LATCH_OR: SignalValue.LATCH,
                Signal.OUT_BUF_WRITE: SignalValue.WRITE.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 89: OUT r3, 1
        self.mc_memory.append(
            {
                Signal.SEL_R_READ: SignalValue.SEL_R_READ_R3.value,
                Signal.OUT_BUF_NEXT: SignalValue.LATCH.value,
                Signal.OUT_BUF_WRITE: SignalValue.WRITE.value,
                Signal.LATCH_OR: SignalValue.LATCH,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 90: IN r1, <port>
        self.mc_memory.append(
            {
                Signal.LATCH_OR: SignalValue.LATCH,
                Signal.INP_BUF_READ: SignalValue.READ.value,
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_INP_BUFF.value,
                Signal.LATCH_R1: SignalValue.LATCH.value,
                Signal.INP_BUF_NEXT: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 91: IN r2, 1
        self.mc_memory.append(
            {
                Signal.LATCH_OR: SignalValue.LATCH,
                Signal.INP_BUF_READ: SignalValue.READ.value,
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_INP_BUFF.value,
                Signal.LATCH_R2: SignalValue.LATCH.value,
                Signal.INP_BUF_NEXT: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 92: IN r3, 1
        self.mc_memory.append(
            {
                Signal.LATCH_OR: SignalValue.LATCH,
                Signal.INP_BUF_READ: SignalValue.READ.value,
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_INP_BUFF.value,
                Signal.LATCH_R3: SignalValue.LATCH.value,
                Signal.INP_BUF_NEXT: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 93: JMP <direct_address> (and JNZ when z_flag = 1 and JNZ when z_flag = 0)
        self.mc_memory.append(
            {
                Signal.SEL_IP: SignalValue.SEL_IP_INC.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 94: CMP r1, <number>
        self.mc_memory.append(
            {
                Signal.LATCH_OR: SignalValue.LATCH.value,
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_OR.value,
                Signal.SEL_OP_2: SignalValue.SEL_OP_SECOND_OP.value,
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R1.value,
                Signal.OPERATION: SignalValue.OPERATION_SUB.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 95: CMP r2, <number>
        self.mc_memory.append(
            {
                Signal.LATCH_OR: SignalValue.LATCH.value,
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_OR.value,
                Signal.SEL_OP_2: SignalValue.SEL_OP_SECOND_OP.value,
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R2.value,
                Signal.OPERATION: SignalValue.OPERATION_SUB.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 96: CMP r3, <number>
        self.mc_memory.append(
            {
                Signal.LATCH_OR: SignalValue.LATCH.value,
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_OR.value,
                Signal.SEL_OP_2: SignalValue.SEL_OP_SECOND_OP.value,
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R3.value,
                Signal.OPERATION: SignalValue.OPERATION_SUB.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 97-98: DIV r1, r3, r2
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R3.value,
                Signal.SEL_OP_2: SignalValue.SEL_OP_SECOND_R2.value,
                Signal.OPERATION: SignalValue.OPERATION_DIV.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_ALU.value,
                Signal.LATCH_R1: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 99-100: DIV r2, r3, r1
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R3.value,
                Signal.SEL_OP_2: SignalValue.SEL_OP_SECOND_R1.value,
                Signal.OPERATION: SignalValue.OPERATION_DIV.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_ALU.value,
                Signal.LATCH_R2: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 101-102: DIV r3, r2, r1
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R2.value,
                Signal.SEL_OP_2: SignalValue.SEL_OP_SECOND_R1.value,
                Signal.OPERATION: SignalValue.OPERATION_DIV.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_ALU.value,
                Signal.LATCH_R3: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 103-104: SUB r1, r3, r2
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R3.value,
                Signal.SEL_OP_2: SignalValue.SEL_OP_SECOND_R2.value,
                Signal.OPERATION: SignalValue.OPERATION_SUB.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_ALU.value,
                Signal.LATCH_R1: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 105-106: SUB r2, r3, r1
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R3.value,
                Signal.SEL_OP_2: SignalValue.SEL_OP_SECOND_R1.value,
                Signal.OPERATION: SignalValue.OPERATION_SUB.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_ALU.value,
                Signal.LATCH_R2: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 107-108: SUB r3, r2, r1
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R2.value,
                Signal.SEL_OP_2: SignalValue.SEL_OP_SECOND_R1.value,
                Signal.OPERATION: SignalValue.OPERATION_SUB.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_ALU.value,
                Signal.LATCH_R3: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 109-110: IDIV r1, r3, r2
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R3.value,
                Signal.SEL_OP_2: SignalValue.SEL_OP_SECOND_R2.value,
                Signal.OPERATION: SignalValue.OPERATION_IDIV.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_ALU.value,
                Signal.LATCH_R1: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 111-112: IDIV r2, r3, r1
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R3.value,
                Signal.SEL_OP_2: SignalValue.SEL_OP_SECOND_R1.value,
                Signal.OPERATION: SignalValue.OPERATION_IDIV.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_ALU.value,
                Signal.LATCH_R2: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 113-114: IDIV r3, r2, r1
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R2.value,
                Signal.SEL_OP_2: SignalValue.SEL_OP_SECOND_R1.value,
                Signal.OPERATION: SignalValue.OPERATION_IDIV.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_ALU.value,
                Signal.LATCH_R3: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 115-116: MUL r1, r2, r3
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R2.value,
                Signal.SEL_OP_2: SignalValue.SEL_OP_SECOND_R3.value,
                Signal.OPERATION: SignalValue.OPERATION_MUL.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_ALU.value,
                Signal.LATCH_R1: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 117-118: MUL r2, r1, r3
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R1.value,
                Signal.SEL_OP_2: SignalValue.SEL_OP_SECOND_R3.value,
                Signal.OPERATION: SignalValue.OPERATION_MUL.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_ALU.value,
                Signal.LATCH_R2: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 119-120: MUL r3, r1, r2
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R1.value,
                Signal.SEL_OP_2: SignalValue.SEL_OP_SECOND_R2.value,
                Signal.OPERATION: SignalValue.OPERATION_MUL.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_ALU.value,
                Signal.LATCH_R3: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 121-122: DEC r1
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R1.value,
                Signal.OPERATION: SignalValue.OPERATION_DEC.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_ALU.value,
                Signal.LATCH_R1: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 123-124: DEC r2
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R2.value,
                Signal.OPERATION: SignalValue.OPERATION_DEC.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_ALU.value,
                Signal.LATCH_R2: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )

        # 125-126: DEC r3
        self.mc_memory.append(
            {
                Signal.SEL_OP_1: SignalValue.SEL_OP_FIRST_R3.value,
                Signal.OPERATION: SignalValue.OPERATION_DEC.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_INC.value,
            }
        )
        self.mc_memory.append(
            {
                Signal.SEL_R_WRITE: SignalValue.SEL_R_WRITE_ALU.value,
                Signal.LATCH_R3: SignalValue.LATCH.value,
                Signal.SEL_MC_ADDR: SignalValue.SEL_MC_ADDR_NULL.value,
            }
        )
