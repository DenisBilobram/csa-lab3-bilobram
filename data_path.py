from typing import List
from microcode import SignalValue
from numpy import int16


class ALU:
    first_operand: int16 = None

    second_operand: int16 = None

    result: int16 = None

    zero_flag: bool = None

    def __init__(self) -> None:
        self.first_operand = int16(0)
        self.second_operand = int16(0)
        self.result = int16(0)
        self.zero_flag = False


class Memory:
    memory: List[int16] = None

    output_value: int16 = None

    def __init__(self, data: List[int16]):
        self.memory = [int16(el) for el in data]
        self.memory.extend([int16(0)] * (1024 - len(data)))
        self.output_value = int16(0)


class DataPath:
    data_memory: Memory = None

    address_register: int16 = None

    data_register: int16 = None

    operand_register: int16 = None

    r1: int16 = None

    r2: int16 = None

    r3: int16 = None

    alu: ALU = None

    input_buffer: List[int16] = None
    output_buffer: List[int16] = None

    mux1: int16 = None

    mux2: int16 = None

    mux3: int16 = None

    operand_bus: int16 = None

    def __init__(self, data: List[int16], input_tokens: List[str]):
        self.data_memory = Memory(data)
        self.data_register = int16(0)
        self.operand_register = int16(0)
        self.address_register = int16(0)
        self.r1 = int16(0)
        self.r2 = int16(0)
        self.r3 = int16(0)
        self.alu = ALU()
        self.input_buffer = input_tokens.copy()
        self.output_buffer = []
        self.mux1 = int16(0)
        self.mux2 = int16(0)
        self.mux3 = int16(0)
        self.operand_bus = int16(0)

    def signal_sel_op_first(self, selector: int16):
        match selector:
            case SignalValue.SEL_OP_FIRST_R1.value:
                self.alu.first_operand = self.r1
            case SignalValue.SEL_OP_FIRST_R2.value:
                self.alu.first_operand = self.r2
            case SignalValue.SEL_OP_FIRST_R3.value:
                self.alu.first_operand = self.r3

    def signal_sel_op_second(self, selector: int16):
        match selector:
            case SignalValue.SEL_OP_SECOND_R1.value:
                self.alu.second_operand = self.r1
            case SignalValue.SEL_OP_SECOND_R2.value:
                self.alu.second_operand = self.r2
            case SignalValue.SEL_OP_SECOND_R3.value:
                self.alu.second_operand = self.r3
            case SignalValue.SEL_OP_SECOND_OP.value:
                self.alu.second_operand = self.operand_register

    def signal_operation(self, operation: int16):
        match operation:
            case SignalValue.OPERATION_ADD.value:
                self.alu.result = self.alu.first_operand + self.alu.second_operand
            case SignalValue.OPERATION_SUB.value:
                self.alu.result = self.alu.first_operand - self.alu.second_operand
            case SignalValue.OPERATION_IDIV.value:
                self.alu.result = self.alu.first_operand % self.alu.second_operand
            case SignalValue.OPERATION_DIV.value:
                self.alu.result = self.alu.first_operand // self.alu.second_operand
            case SignalValue.OPERATION_MUL.value:
                self.alu.result = self.alu.first_operand * self.alu.second_operand
            case SignalValue.OPERATION_INC.value:
                self.alu.result = self.alu.first_operand + 1
            case SignalValue.OPERATION_DEC.value:
                self.alu.result = self.alu.first_operand - 1

        if self.alu.result == int16(0):
            self.alu.zero_flag = True
        else:
            self.alu.zero_flag = False

    def signal_sel_r_write(self, selector: int16):
        match selector:
            case SignalValue.SEL_R_WRITE_ALU.value:
                self.mux1 = self.alu.result

            case SignalValue.SEL_R_WRITE_OR.value:
                self.mux1 = self.operand_register

            case SignalValue.SEL_R_WRITE_INP_BUFF.value:
                if len(self.input_buffer) == 0:
                    raise EOFError()
                symbol = self.input_buffer[0]
                if isinstance(symbol, str):
                    symbol = int16(ord(symbol))
                assert -128 <= symbol <= 127, "input token is out of bound: {}".format(
                    symbol
                )
                self.mux1 = symbol

            case SignalValue.SEL_R_WRITE_DR.value:
                self.mux1 = self.data_register

            case SignalValue.SEL_R_WRITE_MUX2.value:
                self.mux1 = self.mux2

    def signal_sel_r_read(self, selector: int16):
        match selector:
            case SignalValue.SEL_R_READ_R1.value:
                self.mux2 = self.r1
            case SignalValue.SEL_R_READ_R2.value:
                self.mux2 = self.r2
            case SignalValue.SEL_R_READ_R3.value:
                self.mux2 = self.r3

    def signal_sel_address(self, selector: int16):
        match selector:
            case SignalValue.SEL_ADDRESS_OPERAND.value:
                self.mux3 = self.operand_bus
            case SignalValue.SEL_ADDRESS_MUX2.value:
                self.mux3 = self.mux2

    def signal_mem_read(self):
        self.data_memory.output_value = self.data_memory.memory[self.address_register]

    def signal_mem_write(self):
        self.data_memory.memory[self.address_register] = self.mux2

    def signal_inp_buf_next(self):
        self.input_buffer.pop(0)

    def signal_out_buf_next(self):
        self.output_buffer.append(chr(self.mux2))

    def signal_latch_addr(self):
        self.address_register = self.mux3

    def signal_latch_dr(self):
        self.data_register = self.data_memory.output_value

    def signal_latch_or(self):
        self.operand_register = self.operand_bus

    def signal_latch_r1(self):
        self.r1 = self.mux1

    def signal_latch_r2(self):
        self.r2 = self.mux1

    def signal_latch_r3(self):
        self.r3 = self.mux1

    def signal_out_buf_write(self):
        pass

    def signal_inp_buf_read(self):
        pass
