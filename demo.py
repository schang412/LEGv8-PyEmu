#!/usr/bin/env python3

from assembler import Assembler 
import random

def test_func1(a):
    result = []
    uut = 'func1'
    print('Commencing test on function: {}'.format(uut))
    print('Generating random values')
    for i in range(100):
        # generate random numbers between 0 to 2^11
        b = random.randint(0, 2**11)
        c = random.randint(0, 2**11)
        # fill the register
        a.registers['X0'] = b
        a.registers['X1'] = c
        # run the assmbly
        a.unit_test(uut, v=0)
        # pull the number out
        d = a.registers['X2']
        # verification
        assert(int(d) == int(b)+int(c))
        result.append([b,c,d])
    print('All tests passed for {}'.format(uut))
    return result
def test_func2(a):
    result = []
    uut = 'func2'
    print('Commencing test on function: {}'.format(uut))
    print('Generating random values')
    for i in range(100):
        # generate random numbers between 0 to 2^11
        b = random.randint(0, 2**11)
        c = random.randint(0, 2**11)
        # fill the register
        a.registers['X0'] = b
        a.registers['X1'] = c
        # run the assmbly
        a.unit_test(uut, v=0)
        # pull the number out
        d = a.registers['X2']
        # verification
        e = b if b > c else c
        e += 5
        assert(int(d) == int(e))
        result.append([b,c,d])
    print('All tests passed for {}'.format(uut))
    return result

def main():
    p = open('demo.s', 'r')
    a = Assembler(p)
    print('')
    test_func1(a)
    print('')
    test_func2(a)
    print('')


if __name__ == '__main__':
    main()