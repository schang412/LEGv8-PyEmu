
//X0 is arg1
//X1 is arg2
//return: X2 is the sum
func1:
ADD X2, X0, X1
BR LR

//X0 is arg1
//X1 is arg2 
//return: X2 is the larger + 5
func2:
SUBS XZR, X0, X1
B.LE func2_false
ADDI X2, X0, #5
BR LR
func2_false:
ADDI X2, X1, #5
BR LR