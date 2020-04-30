////////////////////////
//                    //
//       main         //
//                    //
////////////////////////
.long array 3, 2, 5, 6
.long arraySize 4
    lda x0, array
    lda x1, arraySize
	ldur x1, [x1, #0]
    bl printList
    
    lda x0, array
    lda x1, arraySize
    ldur x1, [x1, #0]
    
	ldur x2, [x0, #0] // x2 for max element
	addi x3, xzr, #1 // x3 as iterator
loop:
	cmp x3, x1 // subs xzr, x3, x1
	b.eq loopend
	lsl x4, x3, #3 // x4 address of array[x3]; alternative: addi x8, xzr, #8  mul x4, x3, x8
	add x4, x0, x4
	ldur x5, [x4, #0] // x5 = array[x3]
	cmp x5, x2
	b.lt ifend
	mov x2, x5 // add x2, x5, xzr
ifend:
	addi x3, x3, #1
	b loop
loopend:
	putint x2
	stop
    
    
////////////////////////
//                    //
//     printList      //
//                    //
////////////////////////
printList:
    // x0: base address
    // x1: length of the array

	mov x2, xzr
	addi x5, xzr, #32
	addi x6, xzr, #10
printList_loop:
    cmp x2, x1
    b.eq printList_loopEnd
    lsl x3, x2, #3
    add x3, x3, x0
	ldur x4, [x3, #0]
    putint x4
    putchar x5
    addi x2, x2, #1
    b printList_loop
printList_loopEnd:    
    putchar x6
    br lr