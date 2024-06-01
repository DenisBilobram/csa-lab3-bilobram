.data
hello: 'H', 'e', 'l', 'l', 'o', '\n', 0

.text
START:
    MOV R1, hello
PRINT:
    LOAD R2, (R1)
    CMP R2, 0
    JZ END
    OUT R2, port1_out
    INC R1
    JMP PRINT
END:
    HALT