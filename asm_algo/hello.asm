.data
HELLO: 'H', 'e', 'l', 'l', 'o', 0

.text
START:
    MOV R1, HELLO
PRINT:
    LOAD R2, (R1)
    CMP R2, 0
    JZ END
    OUT R2, port1_out
    INC R1
    JMP PRINT
END:
    HALT