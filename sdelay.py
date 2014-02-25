#!/usr/bin/env python2

"""
Generates a software delay loop for the picoblaze architecture based on a
number of parameters, such as clock speed in MHz, the number of cycles an
instruction takes to execute, and the amount of time to delay for in seconds.
"""

import math

class SoftDelay:

    def __init__(self, clk_speed, cycles_per_instr, delay_time):
        # Clock speed in MHz
        self.clk_speed = clk_speed
        # The number of clock cycles it takes to execute an instruction
        self.cycles_per_instr = 2
        self.delay_time = delay_time

    @property
    def dummy_i(self):
        """
        Returns the number of dummy instructions we need to execute
        """

        # The number of instruction in a second
        i_sec = (self.clk_speed * (10**6)) / self.cycles_per_instr

        # Multiply that by how long we need to delay for in seconds
        return i_sec * self.delay_time

    def generate(self):
        """
        We're going to generate assembly that uses nested for loops to create
        a software delay. The picoblaze registers are 8 bits, which means we
        each one can store the value 0-255 as a binary integer. The assembley
        generated looks something like this:

        LOAD S0, 0x00
        LOAD S1, 0x00

        loop:
            ADD S0, 0x01
            JUMP NZ, loop
            ADD S1, 0x01
            JUMP NZ, loop

        This is a nested for loop that loops 256^2 times
        """

        # Work out the number of registers we need. The number of dummy
        # instructions is divided by the number of registers * 2, because each
        # increment instruction is an increment followed by a jump. We use 256
        # instead of 255 because the loop stops when there is an overflow from
        # 255 to 0. 
        registers = 1
        while ((self.dummy_i / (registers * 2)) > (256**registers)):
            registers += 1

        # Work out the rough number of times we want to count to 256 and round
        # up
        count_num = int(math.ceil((self.dummy_i / (registers * 2)) / 256))

        # Create a loop to do just that. We want 256 - the number of outer
        # loops we need to do so that we overflow
        s0 = 256 - count_num

        # Generate appropriate assembly
        out = "; Initialise loop registers\n"
        out += "LOAD S0, {0}\n".format(hex(s0))
        out += "LOAD S1, {0}\n\n".format(hex(0))
        out += "; Loop for approx {0} seconds\n".format(self.delay_time)
        out += "loop:\n"
        out += "    ADD S0, 0x01\n"
        out += "    JUMP NZ, loop\n"
        out += "    ADD S1, 0x01\n"
        out += "    JUMP NZ, loop\n"

        return out

if __name__ == "__main__":
    sd = SoftDelay(10, 2, 2 * (10**-3))
    print sd.generate()
