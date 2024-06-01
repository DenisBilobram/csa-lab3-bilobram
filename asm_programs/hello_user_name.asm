.data
prompt: 'W', 'h', 'a', 't', ' ', 'i', 's', ' ', 'y', 'o', 'u', 'r', ' ', 'n', 'a', 'm', 'e', '?', '\n', 0
hello: 'H', 'e', 'l', 'l', 'o', ',', ' ', 0
exclamation: '!', 0
name: RESERVE 30

.text
START:
    MOV R1, prompt
PRINT_PROMPT:
    LOAD R2, (R1)
    CMP R2, 0
    JZ END_PRINT_PROMPT
    OUT R2, 1
    INC R1
    JMP PRINT_PROMPT

END_PRINT_PROMPT:
    MOV R1, name
READ_NAME:
    IN R2, 1
    CMP R2, '\n'
    JZ END_READ_NAME
    STORE R2, (R1)
    INC R1
    JMP READ_NAME

END_READ_NAME:
    MOV R2, 0
    INC R1
    STORE R2, (R1)

    MOV R1, hello
PRINT_HELLO:
    LOAD R2, (R1)
    CMP R2, 0
    JZ END_PRINT_HELLO
    OUT R2, 1
    INC R1
    JMP PRINT_HELLO

END_PRINT_HELLO:
    MOV R1, name
PRINT_NAME:
    LOAD R2, (R1)
    CMP R2, 0
    JZ END
    OUT R2, 1
    INC R1
    JMP PRINT_NAME
END:
    LOAD R1, exclamation
    OUT R1, 1

    HALT
