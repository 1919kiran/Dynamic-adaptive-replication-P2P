vm2 = [10,20,-5,30,10,10,200,0,30,30,116,20480,20]
vm1 = [6,9,12,15,3,27,45,8,15,19,111,46080,0]
vm1 = [6,9,12,15,12,27,54,12,-42,23,111,216,13]
print("-----")
print("VM1:")
for i in range(1,32):
    if i > len(vm1):
        print(f"R{i}=0")
    else:
        print(f"R{i}={vm1[i-1]}")
print("-----")
print("VM2:")
for i in range(1,32):
    if i > len(vm2):
        print(f"R{i}=0")
    else:
        print(f"R{i}={vm2[i-1]}")