def func_1(var1, var2, var3):
	local_1 = var1+2
	if var3 == 1: 
		local_2 = var2+3 
	else: 
		local_2 = var2+4 
	local_1 = func_2(local_1, local_2)
	return local_1, local_2

def func_2(var1, var2): 
	return var1+var2 

def func_3(var1):
	return var1+10

def file_write(n, m, x, y, z):

	file = open("result.txt", "w") 
	file.write(str(n)+'\n')
	file.write(str(m)+'\n') 
	file.write(str(x)+'\n')
	file.write(str(y)+'\n') 
	file.write(str(z)+'\n') 
	file.close() 

x = func_3(10)
y = func_3(20)
n = func_3(30)
y, z = func_1(x, y, 1) 
m = func_2(y, z) 
print(n)
print(m)
print(x)
print(y)
print(z)

y = y + 10 

file_write(n, m, x, y, z)
