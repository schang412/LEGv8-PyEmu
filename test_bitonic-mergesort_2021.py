#!/usr/bin/env python3

'''
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
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import sys

from assembler import Assembler
import random
def floor_log2(n):
        assert n > 0
        last = n
        n &= n -1
        while n:
            last = n
            n &= n - 1
        return last

def test_findm(prog_obj, v=0):
    # test parameters
    input_n = random.sample(range(1,5000), 10)
    expected_output = [floor_log2(x) for x in input_n]

    uut = 'FindM'
    test_status_summary = []
    # test loop
    print('Beginning test for {}...'.format(uut))
    for i in range(len(input_n)):
        # preload X0
        prog_obj.registers['X0'] = input_n[i]

        # run test
        prog_obj.unit_test(uut,v)

        # fetch output
        output = prog_obj.registers['X0']

        # print status
        if expected_output[i] == output:
            print('\033[92m' + 'UUT: {} | Test: {} | passed'.format(uut, i+1) + '\033[0m')
            test_status_summary.append(True)
        else:
            print('\033[91m' + 'UUT: {} | Test: {} | failed'.format(uut, i+1) + '\033[0m')
            test_status_summary.append(False)

        # restore memory for next test
        prog_obj.restore()
    return test_status_summary

def test_redloop(prog_obj, v=0):
    # test parameters
    input_arrays = [[2,4,3,1], [7,6,5,8]]
    expected_output_arrays = [[2,1,3,4], [5,6,7,8]]
    uut = 'RedLoop'

    test_status_summary = []

    #test loop
    print('Beginning test for {}...'.format(uut))
    for i in range(len(input_arrays)):
        # preload the array into memory
        cmd_input_array = '.long A {}'.format(', '.join(str(v) for v in input_arrays[i]))
        prog_obj.memory.insert(cmd_input_array)
        # pre load the array size into memory
        cmd_input_size = '.long SIZE {}'.format(len(input_arrays[i]))
        prog_obj.memory.insert(cmd_input_size)

        # preload X0, X1
        prog_obj.registers['X0'] = prog_obj.memory.labels['A']
        prog_obj.registers['X1'] = len(input_arrays[i])
        prog_obj.registers['X2'] = floor_log2(prog_obj.registers['X1'])

        # run test
        prog_obj.unit_test(uut,v)

        # compose outputs
        output_array = []
        for j in range(len(input_arrays[i])):
            output_array.append(prog_obj.memory[prog_obj.memory.labels['A'] + (j*8)])

        # print status
        if expected_output_arrays[i] == output_array:
            print('\033[92m' + 'UUT: {} | Test: {} | passed'.format(uut, i+1) + '\033[0m')
            test_status_summary.append(True)
        else:
            print('\033[91m' + 'UUT: {} | Test: {} | failed'.format(uut, i+1) + '\033[0m')
            test_status_summary.append(False)

        # restore memory for next test
        prog_obj.restore()
    return test_status_summary

def test_blueloop(prog_obj, v=0):
    # test parameters
    input_arrays = [[2,5,6,7], [2,5,6,7,1,3,4,8]]
    expected_output_arrays = [[2,5,6,7], [2,4,3,1,7,6,5,8]]
    uut = 'BLueLoop'

    test_status_summary = []

    #test loop
    print('Beginning test for {}...'.format(uut))
    for i in range(len(input_arrays)):
        # preload the array into memory
        cmd_input_array = '.long A {}'.format(', '.join(str(v) for v in input_arrays[i]))
        prog_obj.memory.insert(cmd_input_array)
        # pre load the array size into memory
        cmd_input_size = '.long SIZE {}'.format(len(input_arrays[i]))
        prog_obj.memory.insert(cmd_input_size)

        # preload X0, X1
        prog_obj.registers['X0'] = prog_obj.memory.labels['A']
        prog_obj.registers['X1'] = len(input_arrays[i])
        prog_obj.registers['X2'] = floor_log2(prog_obj.registers['X1'])

        # run test
        prog_obj.unit_test(uut,v)

        # compose outputs
        output_array = []
        for j in range(len(input_arrays[i])):
            output_array.append(prog_obj.memory[prog_obj.memory.labels['A'] + (j*8)])

        # print status
        if expected_output_arrays[i] == output_array:
            print('\033[92m' + 'UUT: {} | Test: {} | passed'.format(uut, i+1) + '\033[0m')
            test_status_summary.append(True)
        else:
            print('\033[91m' + 'UUT: {} | Test: {} | failed'.format(uut, i+1) + '\033[0m')
            test_status_summary.append(False)

        # restore memory for next test
        prog_obj.restore()
    return test_status_summary

def test_redrecurssion(prog_obj,v=0):
    # test parameters
    input_arrays = [[2,4,3,1], [7,6,5,8]]
    expected_output_arrays = [[1,2,3,4], [5,6,7,8]]
    uut = 'RedRecursion'

    test_status_summary = []

    #test loop
    print('Beginning test for {}...'.format(uut))
    for i in range(len(input_arrays)):
        # preload the array into memory
        cmd_input_array = '.long A {}'.format(', '.join(str(v) for v in input_arrays[i]))
        prog_obj.memory.insert(cmd_input_array)
        # pre load the array size into memory
        cmd_input_size = '.long SIZE {}'.format(len(input_arrays[i]))
        prog_obj.memory.insert(cmd_input_size)

        # preload X0, X1
        prog_obj.registers['X0'] = prog_obj.memory.labels['A']
        prog_obj.registers['X1'] = len(input_arrays[i])

        # run test
        prog_obj.unit_test(uut,v)

        # compose outputs
        output_array = []
        for j in range(len(input_arrays[i])):
            output_array.append(prog_obj.memory[prog_obj.memory.labels['A'] + (j*8)])

        # print status
        if expected_output_arrays[i] == output_array:
            print('\033[92m' + 'UUT: {} | Test: {} | passed'.format(uut, i+1) + '\033[0m')
            test_status_summary.append(True)
        else:
            print('\033[91m' + 'UUT: {} | Test: {} | failed'.format(uut, i+1) + '\033[0m')
            test_status_summary.append(False)

        # restore memory for next test
        prog_obj.restore()
    return test_status_summary

def test_bluerecurssion(prog_obj,v=0):
    # test parameters
    input_arrays = [[2,5,7,6], [2,5,7,6,8,1,3,4], [3,7,8,4,2,6,5,1], [3,7,4,8,6,2,1,5]]
    expected_output_arrays = [[2,5,6,7], [1,2,3,4,5,6,7,8], [1,2,3,4,5,6,7,8], [1,2,3,4,5,6,7,8]]
    uut = 'BLueRecursion'

    test_status_summary = []

    #test loop
    print('Beginning test for {}...'.format(uut))
    for i in range(len(input_arrays)):
        # preload the array into memory
        cmd_input_array = '.long A {}'.format(', '.join(str(v) for v in input_arrays[i]))
        prog_obj.memory.insert(cmd_input_array)
        # pre load the array size into memory
        cmd_input_size = '.long SIZE {}'.format(len(input_arrays[i]))
        prog_obj.memory.insert(cmd_input_size)

        # preload X0, X1
        prog_obj.registers['X0'] = prog_obj.memory.labels['A']
        prog_obj.registers['X1'] = len(input_arrays[i])

        # run test
        prog_obj.unit_test(uut,v)

        # compose outputs
        output_array = []
        for j in range(len(input_arrays[i])):
            output_array.append(prog_obj.memory[prog_obj.memory.labels['A'] + (j*8)])

        # print status
        if expected_output_arrays[i] == output_array:
            print('\033[92m' + 'UUT: {} | Test: {} | passed'.format(uut, i+1) + '\033[0m')
            test_status_summary.append(True)
        else:
            print('\033[91m' + 'UUT: {} | Test: {} | failed'.format(uut, i+1) + '\033[0m')
            test_status_summary.append(False)

        # restore memory for next test
        prog_obj.restore()
    return test_status_summary

def main():
    p = open('tiw030_anliu_2021_project.s', 'r')
    a = Assembler(p)
    v=0 # no extra info
    # v=1 (parse info, end of program memory dump)
    # v=2 (execution steps)
    # v=3 (execution step register dump)
    # v=4 (execution step parse and memory dump)

    test_summary = []
    units_under_test = []

    units_under_test.append('FindM')
    units_under_test.append('RedLoop')
    units_under_test.append('BLueLoop')
    units_under_test.append('RedRecursion')
    units_under_test.append('BLueRecursion')

    print()
    if 'FindM' in units_under_test:
        test_summary.append(test_findm(a,v))
        print()

    if 'RedLoop' in units_under_test:
        test_summary.append(test_redloop(a,v))
        print()

    if 'BLueLoop' in units_under_test:
        test_summary.append(test_blueloop(a,v))
        print()
    if 'RedRecursion' in units_under_test:
        test_summary.append(test_redrecurssion(a,v))
        print()
    if 'BLueRecursion' in units_under_test:
        test_summary.append(test_bluerecurssion(a,v))
        print()

    print('-------------------- Test Summary --------------------')
    for i in range(len(test_summary)):
        for j in range(len(test_summary[i])):
            if test_summary[i][j]:
                print('\033[92m' + 'UUT: {} | Test: {} | passed'.format(units_under_test[i], j+1) + '\033[0m')
            else:
                print('\033[91m' + 'UUT: {} | Test: {} | failed'.format(units_under_test[i], j+1) + '\033[0m')
        print()


if __name__ == '__main__':
    main()
