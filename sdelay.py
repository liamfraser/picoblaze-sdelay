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

    @property
    def register_count(self):
        """
        Work out the number of registers needed. The picoblaze registers are 8
        bits, which means we each one can store the value 0-255 as a binary
        integer.

        Each increment instruction takes 2 instructions, an ADD and a JUMP. The
        outer loop is negligible because, at most, it will only add 512
        instructions to the total, so we won't really take that into acccount.
        Hence, the division of the number of dummy instructions by
        2^(registers-1) in the loop below.
        """

        registers = 1
        while ((self.dummy_i / (2**(registers-1))) > (256**registers)):
            registers += 1

        return registers

    @property
    def outer_loops(self):
        """
        Work out the number of times the outer loop needs to loop to get the
        rough number of increments we want. Sadly we have no control over the
        inner loops so can't be too specific.
        """

        count = (self.dummy_i / (2**(self.register_count-1))) / 256
        
        # Round the number up
        count = int(math.ceil(count))

        return count

    @property
    def register_array(self):
        """
        Create an array for the number of registers we need, with the outer
        loop register as the last one in the array.
        """
        
        registers = []
        for i in range(0, self.register_count):
            registers.append(0)

        # Set the appropriate number of outer loops
        registers[-1] = 256 - self.outer_loops

        return registers

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

        # Generate appropriate assembly
        out = "; Initialise loop registers\n"

        # Initialise the registers
        for i in range(0, len(self.register_array)):
            out += "LOAD S{0:x}, {1:#x}\n".format(i, self.register_array[i])

        out += "\n"
        out += "; Loop for approx {0} seconds\n".format(self.delay_time)
        out += "loop:\n"

        # Do the increments

        for i in range(0, len(self.register_array)):
            out += "ADD S{0:x}, 0x01\n".format(i, self.register_array[i])
            out += "    JUMP NZ, loop\n"

        return out

if __name__ == "__main__":
    # 2ms
    sd = SoftDelay(10, 2, 2 * (10**-3))
    print sd.register_count
    print sd.outer_loops
    # 1s
    #sd = SoftDelay(10, 2, 1)
    print sd.generate()
