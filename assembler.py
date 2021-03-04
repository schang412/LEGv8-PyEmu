#!/usr/bin/env python3

'''
Based on https://github.com/joeylmaalouf/asm-simulator
Copyright (c) 2020 Spencer Chang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIM:21ITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import argparse
import sys
import re

class Assembler(object):
    def __init__(self, program):
        # program should be the name of a file or just plain text
        try:
            text = program.read()
        except AttributeError:
            text = program
        # save the program
        self.text = text
        # setup the registers
        self.registers = Registers()

        # cleanup the code
        lines = self.text.split('\n')
        lines = self.clean(lines)

        # split the code into data and program sections
        asm_lines, data_lines = self.split_sections(lines)

        # put the data into memory
        self.memory = Memory()
        for d in data_lines:
            self.memory.insert(d)
        # process the assembly commands
        asm_lines = self.preprocess(asm_lines)
        self.labels = self.line_labels(asm_lines)
        self.instrs = [Instruction(asm_line) for asm_line in asm_lines]
        self.flags = Flags()
        self.console_buffer = ''
    def unit_test(self, uut, v=0):
        procs = ['BL {}'.format(uut.upper().strip()), 'STOP']
        for proc in procs:
            self.instrs.append(Instruction(proc))

        self.run(verbose=v, pc=(len(self.instrs) - 2))

    def restore(self):
        self.__init__(self.text)

    def run(self, verbose=0, bp=[], pc=0):
        # bp is a list of breakpoints
        # setup the flags
        program_counter = pc
        # run while program_counter hasn't reached the end
        instr_exec_history = 'Instruction Execution History: \n'
        if verbose:
            print('*** Program Execution Begin ***')
        try:
            while program_counter < len(self.instrs):
                instr = self.instrs[program_counter]

                if program_counter in self.labels.values():
                    program_counter += 1
                    continue

                op = instr.operation

                # all commands that set the flags ends in S
                set_flags = False
                if op[-1] == 'S':
                    set_flags = True
                    op = op[:-1]

                instr_exec_history += '{:10d}: {}\n'.format(program_counter, instr)
                if program_counter in bp:
                    print('{} BREAKPOINT: {} {}'.format(terminal_fonts.BOLD, instr, terminal_fonts.END))
                    print(self.registers)
                    print(self.memory)
                    input("Press any key to continue")

                # run through all the commands
                if op == 'ADD':
                    self.registers[instr.operand0] = self.registers[instr.operand1] + self.registers[instr.operand2]
                elif op == 'ADDI':
                    self.registers[instr.operand0] = self.registers[instr.operand1] + self.immediate(instr.operand2)
                elif op == 'AND':
                    self.registers[instr.operand0] = self.registers[instr.operand1] & self.registers[instr.operand2]
                elif op == 'ANDI':
                    self.registers[instr.operand0] = self.registers[instr.operand1] & self.immediate(instr.operand2)
                elif op == "B":
                    program_counter = self.labels[instr.operand0]
                elif op == "BL":
                    self.registers['LR'] = program_counter + 1
                    program_counter = self.labels[instr.operand0]
                elif op == "BR":
                    program_counter = self.registers[instr.operand0] - 1
                elif op == "CBNZ":
                    if self.registers[instr.operand0] != 0:
                        program_counter = self.labels[instr.operand1]
                elif op == "CBZ":
                    if self.registers[instr.operand0] == 0:
                        program_counter = self.labels[instr.operand1]
                elif op[0] == 'B':
                    cond = op.split('.')[1]
                    cond_pass = False

                    if cond == 'EQ':
                        cond_pass = bool(self.flags.Z)
                    elif cond == 'NE':
                        cond_pass = not bool(self.flags.Z)
                    elif cond == 'LT':
                        cond_pass = (bool(self.flags.N) != bool(self.flags.V))
                    elif cond == 'GE':
                        cond_pass = (bool(self.flags.N) == bool (self.flags.V))
                    elif cond == 'LE':
                        cond_pass = (bool(self.flags.N) != bool(self.flags.V)) or bool(self.flags.Z)
                    elif cond == 'MI':
                        cond_pass = (bool(self.flags.N))
                    elif cond == 'PL':
                        cond_pass = not (bool(self.flags.N))
                    elif cond == 'VS':
                        cond_pass = bool(self.flags.V)
                    elif cond == 'VC':
                        cond_pass = not bool(self.flags.V)
                    elif cond == 'LO':
                        cond_pass = not bool(self.flags.C)
                    elif cond == 'HS':
                        cond_pass = bool(self.flags.C)
                    elif cond == 'LS':
                        cond_pass = not bool(self.flags.C) or bool(self.flags.Z)
                    elif cond == 'HI':
                        cond_pass = bool(self.flags.C) and not bool(self.flags.Z)
                    else:
                        print('Operation not defined: {}'.format(op))
                        return self
                    if cond_pass:
                        program_counter = self.labels[instr.operand0]
                elif op == 'EOR':
                    self.registers[instr.operand0] = self.registers[instr.operand1] ^ self.registers[instr.operand2]
                elif op == 'EORI':
                    self.registers[instr.operand0] = self.registers[instr.operand1] ^ self.immediate(instr.operand2)
                elif op == 'LDUR':
                    self.registers[instr.operand0] = self.memory[self.address_composer(instr.operand1, instr.operand2)]
                elif op == 'LDA':
                    self.registers[instr.operand0] = self.memory.labels[instr.operand1]
                elif op == 'LSL':
                    self.registers[instr.operand0] = self.registers[instr.operand1] << self.immediate(instr.operand2)
                elif op == 'LSR':
                    self.registers[instr.operand0] = self.registers[instr.operand1] >> self.immediate(instr.operand2)
                elif op == 'ORR':
                    self.registers[instr.operand0] = self.registers[instr.operand1] | self.registers[instr.operand2]
                elif op == 'ORRI':
                    self.registers[instr.operand0] = self.registers[instr.operand1] | self.immediate(instr.operand2)
                elif op == 'STUR':
                    self.memory[self.address_composer(instr.operand1, instr.operand2)] = self.registers[instr.operand0]
                elif op == 'STOP':
                    break
                elif op == 'PUTINT':
                    self.console_buffer += str(self.registers[instr.operand0])
                elif op == 'PUTCHAR':
                    self.console_buffer += chr(self.registers[instr.operand0])
                elif op == 'SUB':
                    self.registers[instr.operand0] = self.registers[instr.operand1] - self.registers[instr.operand2]
                elif op == 'SUBI':
                    self.registers[instr.operand0] = self.registers[instr.operand1] - self.immediate(instr.operand2)
                elif op == 'MUL':
                    self.registers[instr.operand0] = self.registers[instr.operand1] * self.registers[instr.operand2]
                elif op == 'UDIV':
                    self.registers[instr.operand0] = self.registers[instr.operand1] // self.registers[instr.operand2]
                else:
                    print('Operation not defined: {}'.format(op))
                    return self

                # actually set the flags
                if set_flags:
                    N = int(self.registers[instr.operand0] < 0)
                    Z = int(self.registers[instr.operand0] == 0)
                    C = int(2**64-1 < self.registers[instr.operand0])
                    V = int(2**63-1 < self.registers[instr.operand0] < 2**64-1)
                    self.flags.update(N=N, Z=Z, C=C, V=V)

                self.check_overflow()

                # XZR should always be 0
                self.registers['XZR'] = 0

                # verbose level
                if verbose >= 3:
                    print(self.registers)
                    if verbose >= 4:
                        print('Operation: [{}], Operand0: [{}], Operand1: [{}], Operand2: [{}]'.format(op, instr.operand0, instr.operand1, instr.operand2))
                        print(self.memory)

                program_counter += 1
        except:
            raise SyntaxError(terminal_fonts.to_error('Last run command: {} at PC={}'.format(self.instrs[program_counter], program_counter))) from None
        if verbose:
            print('*** Program Execution Finish ***')
            print(self)
        if verbose >= 2:
            print(instr_exec_history)
        return self
    def check_overflow(self):
        for i in range(32):
            if not (-2**64 <= self.registers[i] <= 2**64-1):
                self.registers[i] = (self.registers[i] + (2**64)) % (2*(2**64))


    def clean(self, lines):
        # removes extra lines and comments
        cleaned = []
        for line in lines:
            # only append stuff before comments
            l = line.strip().split('//')[0].strip()
            # this is to deal with labels on same line as code
            if len(l.split(':')) > 1:
                l1 = l.split(':')[0].strip() + ':'
                l2 = l.split(':')[1].strip()
                if l1: cleaned.append(l1)
                if l2: cleaned.append(l2)
            # only put it into lines if its not blank
            elif l: cleaned.append(l)
        return cleaned
    def split_sections(self, lines):
        instr = []
        data = []
        for line in lines:
            if line[0] == '.':
                data.append(line)
            else:
                instr.append(line)
        return instr, data
    def preprocess(self, lines):
        processed = []
        for line in lines:
            instr = Instruction(line)
            # handles any equivalent instructions
            if instr.operation == 'CMP':
                instr.update('SUBS', 'XZR', instr.operand0, instr.operand1)
            elif instr.operation == 'CMPI':
                instr.update('SUBIS', 'XZR', instr.operand0, instr.operand1)
            elif instr.operation == 'MOV':
                instr.update('ADD', instr.operand0, 'XZR', instr.operand1)
            processed.append(str(instr))
        return processed
    def line_labels(self, lines):
        label_lines = {}
        current_line = 0
        for line in lines:
            word = line.split(" ")[0]
            if (word[-1] == ':'):
                if word[:-1] in label_lines:
                    raise ValueError(terminal_fonts.to_error("Line label '{}' occurs more than once".format(word[:-1])))
                label_lines[word[:-1]] = current_line
            current_line += 1
        return label_lines
    def immediate(self, operand):
        if operand[0] == '#':
            q = int(operand[1:])
            if q > (2**8):
                print(terminal_fonts.to_warning('Warning immediate value (#{}) is not able to be processed bare metal'.format(q)))
            return q
        else:
            raise SyntaxError(terminal_fonts.to_error('Unknown immediate value: {}'.format(operand)))
    def address_composer(self, operand1, operand2):
        if not (operand1[0] == '[' and operand2[-1] == ']'):
            raise SyntaxError(terminal_fonts.to_error('Unknown address: {}, {}'.format(operand1, operand2)))
        if not (operand2[0] == '#'):
            raise SyntaxError(terminal_fonts.to_error('Unknown immediate value: {}'.format(operand2)))
        return self.registers[operand1[1:]] + int(operand2[1:-1])

    def __str__(self):
        ret = ''
        ret += 'Labels: \n'
        for label in self.labels:
            ret += '\t{}: {}\n'.format(label,self.labels[label])
        ret += '\n\n Instructions: \n'
        i = 0
        for instr in self.instrs:
            ret += '{:10}: {}\n'.format(i, instr)
            i += 1
        ret += str(self.memory)
        ret += str(self.registers)
        ret += '\nOutput Buffer:\n{}'.format(self.console_buffer)
        self.console_buffer = ''
        return ret

class terminal_fonts:
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    OK = '\033[92m'
    BOLD = '\033[1m'
    END = '\033[0m'
    def to_error(msg):
        return terminal_fonts.FAIL + str(msg) + terminal_fonts.END
    def to_warning(msg):
        return terminal_fonts.WARNING + str(msg) + terminal_fonts.END
    def to_ok(msg):
        return terminal_fonts.OK + str(msg) + terminal_fonts.END
class Instruction(object):
    def __init__(self, line, strict=True):
        self.raw = line
        line = line.upper()

        if strict:
            q=re.match(r"((?:B.)?\w+:?)(?:\s+(\w+))?(?:\s+)?(?:,(?:\s+)?((?:\[(?:\s+)?)?\w+))?(?:\s+)?(?:,(?:\s+)?(\#?-?\w+(?:\])?))?", line)
            self.operation = q.groups()[0]
            self.operand0 = q.groups()[1]
            self.operand1 = q.groups()[2]
            self.operand2 = q.groups()[3]
        else:
            words = line.upper().replace(",", " ").split()
            self.operation = words[0]
            self.operand0 = words[1] if len(words) > 1 else None
            self.operand1 = words[2] if len(words) > 2 else None
            self.operand2 = words[3] if len(words) > 3 else None

    def __str__(self):
        return "{} {}".format(self.operation, ", ".join([v for v in [self.operand0, self.operand1, self.operand2] if v is not None]))
    def update(self, operation, operand0, operand1, operand2):
        self.operation = operation
        self.operand0 = operand0
        self.operand1 = operand1
        self.operand2 = operand2
        pass
class Memory(object):
    def __init__(self, offset=0x1000, print_type='DEC'):
        self.data = {}
        self.labels = {}
        self.print_type = print_type
        self.offset = offset
        self.default_offset = offset
    def __str__(self):
        str_return = '\nMemories: (HEX: {})\n'.format(self.print_type)
        for i in list(self.data.keys())[::8]:
            if self.print_type == 'DEC':
                str_return += '0x{:016X}: {:19d}\n'.format(i, self[i])
            elif self.print_type == 'HEX':
                str_return += '0x{:016X}: {:16X}\n'.format(i, self[i])
            elif self.print_type == 'BIN':
                str_return += '0x{:016X}: {:064b}\n'.format(i, self[i])
        return str_return
    def __setitem__(self, key, value):
        # memory is stored in 8 bytes
        # so split it into 8 bytes, and store each byte into the key
        # we don't have to do this, but it will help catch code that
        # slips in memory
        self.data[key] = value & 0xFF
        self.data[key+1] = (value >> 8) & 0xFF
        self.data[key+2] = (value >> 16) & 0xFF
        self.data[key+3] = (value >> 24) & 0xFF
        self.data[key+4] = (value >> 32) & 0xFF
        self.data[key+5] = (value >> 40) & 0xFF
        self.data[key+6] = (value >> 48) & 0xFF
        self.data[key+7] = (value >> 56) & 0xFF
    def __getitem__(self, key):
        return_val = 0
        try:
            # memory is stored in 8 bytes
            # so reconstruct from the 8 bytes stored
            return_val |= self.data[key]
            return_val |= self.data[key+1] << 8
            return_val |= self.data[key+2] << 16
            return_val |= self.data[key+3] << 24
            return_val |= self.data[key+4] << 32
            return_val |= self.data[key+5] << 40
            return_val |= self.data[key+6] << 48
            return_val |= self.data[key+7] << 56
        except KeyError:
            # if the memory hasnt been initialized, it will throw a KeyError
            # but we want unitialized memory to just be 0
            # since return_val |= 0 << x is just return val
            # we don't have to do anything
            pass
        return return_val if not (return_val & (1 << 63)) else (return_val - (1<<64))
    def insert(self, line):
        # this is to take the data lines and store it with a specific label
        # the format is .dtype NAME CSV
        dtype, name, values = line.split(None, 2)
        dtype, name, values = dtype[1:].lower(), name.upper(), [v.strip() for v in values.split(",")]
        if dtype not in ['long']:
            raise ValueError(terminal_fonts.to_error('Invalid data type: {}'.format(dtype)))
        self.labels[name] = self.offset
        for value in values:
            self[self.offset] = int(value)
            self.offset += 8
    def reset(self):
        self.__init__()

class Flags(object):
    def __init__(self, N=0, C=0, Z=0, V=0):
        self.N = N
        self.C = C
        self.Z = Z
        self.V = V
    def update(self, N=None, C=None, Z=None, V=None):
        if N is not None:
            self.N = N
        if C is not None:
            self.C = C
        if Z is not None:
            self.Z = Z
        if V is not None:
            self.V = V
    def __str__(self):
        return 'Flags: N={}, C={}, V={}, Z={}'.format(self.N, self.C, self.V, self.Z)
class Registers(object):
    def __init__(self, SP_val=0x007FFFFFFFFC, FP_val=0x007FFFFFFFFC, print_type='DEC'):
        # we can refer to the same register using multiple names
        # so we make a dict that points to each register
        self.conversion_dict = {'X0': 0, 'X1': 1,
                                'X2': 2, 'X3': 3,
                                'X4': 4, 'X5': 5,
                                'X6': 6, 'X7': 7,
                                'X8': 8, 'X9': 9,
                                'X10': 10, 'X11': 11,
                                'X12': 12, 'X13': 13,
                                'X14': 14, 'X15': 15,
                                'X16': 16, 'X17': 17,
                                'X18': 18, 'X19': 19,
                                'X20': 20, 'X21': 21,
                                'X22': 22, 'X23': 23,
                                'X24': 24, 'X25': 25,
                                'X26': 26, 'X27': 27,
                                'X28': 28, 'X29': 29,
                                'X30': 30, 'X31': 31,
                                'XZR': 31, 'LR': 30,
                                'FP': 29, 'SP': 28 }
        self.data = [0] * (max(self.conversion_dict.values())+1)
        self['SP'] = SP_val
        self['FP'] = FP_val
        self.print_type = print_type
    def __str__(self):
        if self.print_type == 'DEC':
            str_return = '\nRegisters: (DEC)\n| ====================================================|\n| '
            for i in range(32):
                p = 'X{}'.format(i)
                if i < 10:
                    p = ' ' + p
                str_return += '{}: {:19} | '.format(p, self.data[i])
                if(((i+1)%2) == 0):
                    str_return += '\n| '
            str_return += '====================================================|\n'
        elif self.print_type == 'HEX':
            str_return = '\nRegisters: (HEX)\n| ==============================================|\n| '
            for i in range(32):
                p = 'X{}'.format(i)
                if i < 10:
                    p = ' ' + p
                str_return += '{}: {:16x} | '.format(p, self.data[i] if self.data[i] >= 0 else (1<<64) + self.data[i])
                if(((i+1)%2) == 0):
                    str_return += '\n| '
            str_return += '==============================================|\n'
        elif self.print_type == 'BIN':
            str_return = '\nRegisters: (BIN)\n| ======================================================================|\n| '
            for i in range(32):
                p = 'X{}'.format(i)
                if i < 10:
                    p = ' ' + p
                str_return += '{}: {:064b} | \n| '.format(p, self.data[i] if self.data[i] >= 0 else (1<<64) + self.data[i])
            str_return += '======================================================================|\n'
        return str_return
    def __getitem__(self, key):
        try:
            if isinstance(key, int):
                return self.data[key]
            elif isinstance(key, str):
                return self.data[self.conversion_dict[key.upper()]]
            else:
                raise ValueError(terminal_fonts.to_error("Register must be accessed at an integer or a keyword string. Invalid key: {0}".format(key)))
        except KeyError:
            raise ValueError(terminal_fonts.to_error("Register must be accessed at an integer or a keyword string. Invalid key: {0}".format(key))) from None
    def __setitem__(self, key, value):
        try:
            if isinstance(key, int):
                self.data[key] = value
            elif isinstance(key, str):
                self.data[self.conversion_dict[key.upper()]] = value
            else:
                raise ValueError(terminal_fonts.to_error("Register must be accessed at an integer or a keyword string. Invalid key: {0}".format(key)))
        except KeyError:
            raise ValueError(terminal_fonts.to_error("Register must be accessed at an integer or a keyword string. Invalid key: {0}".format(key))) from None
    def reset(self):
        self.__init__()

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="name of the LEGv8 program file")
    parser.add_argument("-v", "--verbose", help="prints status of registers and memory", action='count', default=0)
    parser.add_argument("-o", "--output", help="saves output to file instead of console")
    parser.add_argument("-bp", help="adds a breakpoint at the line specified", action='append')
    args = parser.parse_args(argv)
    p = open(args.input_file, 'r')
    a = Assembler(p)
    if args.bp is None:
        args.bp = []
    if args.output:
        sys.stdout = open(args.output, 'w')
    a.run(verbose=args.verbose, bp=args.bp)
    print(a)

if __name__ == '__main__':
    #main('bitonic-mergesort.s -o test-print.txt'.split())
    main(sys.argv[1:])