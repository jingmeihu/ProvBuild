def func_1(var1, var2, var3):
	tmp = var1 + var2
	for i in range(0, var3):
		tmp += i
	tmp -= func_2(var1, var2)
	return tmp

def func_2(var1, var2): 
	return var1 - var2 

def func_3(var1): 
	return var1 

def func_4(var1, var2): 
	return var1 + var2 

def output_write(a, b, c, d, e, f, g): 
	file = open("result.txt", "w") 
	file.write(str(a)+'\n') 
	file.write(str(b)+'\n') 
	file.write(str(c)+'\n') 
	file.write(str(d)+'\n') 
	file.write(str(e)+'\n') 
	file.write(str(f)+'\n') 
	file.write(str(g)+'\n') 
	file.close() 

a = func_3(10)
f = func_3(2) 
b = func_3(20)
c = func_3(30)
d = func_3(40)
b = func_1(a, b, 5) 
e = func_2(b, c)
if f % 2 == 0: 
	g = 0 
else: 
	g = 1 
while e > 0:
	e -= 5
d = d / 2

output_write(a, b, c, d, e, f, g) 
