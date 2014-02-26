Creates a software delay loop of a specified length for the Picoblaze Architecture

The output is something like this:

    ; The following code block is a software delay loop that delays
    ; for approximately 2 seconds on a 10MHz picoblaze, where each instruction
    ; takes 2 clock cycles. Exactly 10092701 instructions will be executed, taking
    ; 20185402 clock cycles. The exact time delay should be 2.0185402 seconds.
    LOAD S0, 0x0
    LOAD S1, 0x0
    LOAD S2, 0xb3
    
    loop:
        ADD S0, 0x01
        JUMP NZ, loop
        ADD S1, 0x01
        JUMP NZ, loop
        ADD S2, 0x01
        JUMP NZ, loop
