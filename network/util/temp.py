def foo(l):
    for i in l:
        if i%2==1:
            print(i)
        else:
            break
    else:
        print(float('inf'))

foo([1])
foo([1,2])
foo([1,2,3])
foo([])