.data
sum: 0
num: 0
digits: RESERVE 10
digits_pointer: 0

.text
LOOP:
    LOAD R1, num
    INC R1
    CMP R1, 1001
    JZ GET_DIGITS
    STORE R1, num
    MOV R2, 3
    IDIV R3, R1, R2
    JZ ADD_TO_SUM
    MOV R2, 5
    IDIV R3, R1, R2
    JZ ADD_TO_SUM
    JMP LOOP

ADD_TO_SUM:
    LOAD R1, sum
    LOAD R2, num
    ADD R3, R1, R2
    STORE R3, sum
    JMP LOOP

GET_DIGITS:
    MOV R1, digits_pointer
    DEC R1
    DEC R1
    STORE R1, digits_pointer
LOOP_DIGITS:
    MOV R2, 10
    LOAD R1, sum
    IDIV R3, R1, R2
    MOV R1, 48
    ADD R2, R3, R1
    LOAD R1, digits_pointer
    STORE R2, (R1)
    LOAD R1, sum
    MOV R2, 10
    DIV R3, R1, R2
    JZ PRINT_DIGITS
    STORE R3, sum
    LOAD R1, digits_pointer
    DEC R1
    STORE R1, digits_pointer
    JMP LOOP_DIGITS
PRINT_DIGITS:
    LOAD R1, digits_pointer
    LOAD R2, (R1)
    CMP R2, 0
    JZ END
    OUT R2, 1
    INC R1
    STORE R1, digits_pointer
    JMP PRINT_DIGITS
END:
    HALT 