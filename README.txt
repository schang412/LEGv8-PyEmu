# LEGv8 Python Emulator
## About
This is a tool developed by Spencer Chang at University of Califronia San Diego.
It was developed for use in ECE30 in Spring 2020.

It does **NOT** contain the full LEGv8 Instruction Set, but it does include the main functions that are used in ECE30. I plan to update it if there are functions that we use that were not initially in the set. 

I cannot guarantee that successful execution on this platform equates to successful execution on the LEGGIS simulator provided in class. 

## Usage
From the command-line:
```
./assembler.py loop_demo_findmax.s -vv -o my_code.out
```
From another python file:
```
from assembler import Assembler
if __name__ == '__main__':
    prog = open('my_code.s', 'r')
    a = Assembler(prog)
    a.run()
    print(a)
```
Unit Testing from another python file:
See demo.py

## Formatting Data
The format for data is:
```
.dtype NAME [VALUE]
```
Right now, the only type supported is `.long`. `[VALUE]` is a comma separated list of values. NAME is the case insensitive label given to the address of the data. 
Example:
```
.long array 3, 4, 5
.long arraysize 3
```