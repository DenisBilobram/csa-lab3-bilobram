.text
START:
    IN R1, 1
    CMP R1, 0
    JZ END
    OUT R1, 1
    JMP START
END:
    HALT
