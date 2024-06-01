from __future__ import annotations

import logging

from numpy import int16

from data_path import DataPath
from microcode import (
    ControlStore,
    Instruction,
    InstructionDecoder,
    Microcode,
    Signal,
    SignalValue,
)


class ControlUnit:
    instruction_pointer: int16 = None

    instructions_memory: list[Instruction] = None

    instruction_register: Instruction = None

    data_path: DataPath = None

    instruction_decoder: InstructionDecoder = None

    controle_store: ControlStore = None

    mc_addres: int16 = None

    current_mc: Microcode = None

    tick: int = None

    mux1: int16 = None
    mux2: int16 = None

    def __init__(self, data_path: DataPath, instructions: list[Instruction]):
        self.instruction_pointer = int16(0)
        self.instructions_memory = instructions.copy()
        self.data_path = data_path
        self.instruction_decoder = InstructionDecoder()
        self.controle_store = ControlStore()
        self.mc_addres = int16(0)
        self.current_mc = self.controle_store.mc_memory[self.mc_addres]
        self.tick = 0
        self.mux1 = int16(0)
        self.mux2 = int16(0)

    def signal_sel_mc_addr(self, signal: int16):
        match signal:
            case SignalValue.SEL_MC_ADDR_INC.value:
                self.mux1 = self.mc_addres + int16(1)
            case SignalValue.SEL_MC_ADDR_NEXT.value:
                self.mux1 = self.instruction_decoder.mc_addres
            case SignalValue.SEL_MC_ADDR_NULL.value:
                self.mux1 = int16(0)

    def signal_sel_ip(self, signal: int16):
        match signal:
            case SignalValue.SEL_IP_INC.value:
                self.mux2 = self.instruction_pointer + int16(1)
            case SignalValue.SEL_IP_OP.value:
                self.mux2 = self.instruction_decoder.operand

    def signal_start_decode(self):
        self.instruction_decoder.zero_flag = self.data_path.alu.zero_flag
        self.instruction_decoder.decode(self.instruction_register)
        self.data_path.operand_bus = self.instruction_decoder.operand

    def signal_read_mc(self):
        self.current_mc = self.controle_store.mc_memory[self.mc_addres]

    def signal_latch_ip(self):
        self.instruction_pointer = self.mux2

    def signal_latch_ir(self):
        self.instruction_register = self.instructions_memory[self.instruction_pointer]

    def signal_latch_mc_addr(self):
        self.mc_addres = self.mux1

    def send_signal(self, signal: Signal, signal_value: int16):
        match signal:
            case Signal.LATCH_IP:
                self.signal_latch_ip()
            case Signal.SEL_IP:
                self.signal_sel_ip(signal_value)
            case Signal.LATCH_IR:
                self.signal_latch_ir()
            case Signal.LATCH_MC_ADDR:
                self.signal_latch_mc_addr()
            case Signal.SEL_MC_ADDR:
                self.signal_sel_mc_addr(signal_value)
            case Signal.READ_MC:
                self.signal_read_mc()
            case Signal.LATCH_R1:
                self.data_path.signal_latch_r1()
            case Signal.LATCH_R2:
                self.data_path.signal_latch_r2()
            case Signal.LATCH_R3:
                self.data_path.signal_latch_r3()
            case Signal.SEL_OP_1:
                self.data_path.signal_sel_op_first(signal_value)
            case Signal.SEL_OP_2:
                self.data_path.signal_sel_op_second(signal_value)
            case Signal.OPERATION:
                self.data_path.signal_operation(signal_value)
            case Signal.START_DECODE:
                self.signal_start_decode()
            case Signal.SEL_ADDR:
                self.data_path.signal_sel_address(signal_value)
            case Signal.LATCH_ADDR:
                self.data_path.signal_latch_addr()
            case Signal.MEM_READ:
                self.data_path.signal_mem_read()
            case Signal.MEM_WRITE:
                self.data_path.signal_mem_write()
            case Signal.OUT_BUF_NEXT:
                self.data_path.signal_out_buf_next()
            case Signal.INP_BUF_NEXT:
                self.data_path.signal_inp_buf_next()
            case Signal.LATCH_DR:
                self.data_path.signal_latch_dr()
            case Signal.SEL_R_READ:
                self.data_path.signal_sel_r_read(signal_value)
            case Signal.SEL_R_WRITE:
                self.data_path.signal_sel_r_write(signal_value)
            case Signal.LATCH_OR:
                self.data_path.signal_latch_or()
            case Signal.INP_BUF_READ:
                self.data_path.signal_inp_buf_read()
            case Signal.OUT_BUF_WRITE:
                self.data_path.signal_out_buf_write()

    def info(self):
        action = (
            self.instruction_register["opcode"]
            + " "
            + self.instruction_decoder.first_arg_val
            + " "
            + self.instruction_decoder.second_arg_val
            if self.mc_addres not in [0, 1]
            else "INSTR FETCH"
        )
        log_message = ""
        log_message += f"TICK: {self.tick:<5} "
        log_message += f"ACTION: {action!s:<12}  "
        log_message += f"MC: {self.mc_addres:<4}  "
        log_message += f"IP: {self.instruction_pointer:<4}  "
        log_message += f"AR: {self.data_path.address_register:<4}  "
        log_message += f"R1: {self.data_path.r1:<4}  "
        log_message += f"R2: {self.data_path.r2:<4}  "
        log_message += f"R3: {self.data_path.r3:<4}  "
        log_message += f"Z: {int(self.data_path.alu.zero_flag):<2}  "
        log_message += f"DR: {self.data_path.data_register:<4}  "
        log_message += f"OR: {self.data_path.operand_register}"

        logging.debug(log_message)

    def control_logic_procced(self):
        while True:
            self.tick += 1

            for signal, value in self.current_mc.items():
                self.send_signal(signal, value)

            self.info()

            self.send_signal(Signal.LATCH_MC_ADDR, SignalValue.LATCH)
            self.send_signal(Signal.READ_MC, SignalValue.READ_MC)
