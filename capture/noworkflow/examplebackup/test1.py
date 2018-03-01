def func_1(var1, var2, var3):
	local_1 = var1+2
	if var3 == 1: 
		local_2 = var2+3 
	else: 
		local_2 = var2+4 
	local_1 = func_2(local_1, local_2)
	return local_1, local_2

def func_2(var1, var2): 
	return var1 + var2 

def func_3(var1): 
	return var1 + 10 

def func_4(var1, var2): 
	return var1 - var2 

def func_5(var1, var2):
	return var1 * var2

def file_write(x, y, z): 
 
	file = open("result.txt", "w") 
	file.write(str(x)+'\n') 
	file.write(str(y)+'\n') 
	file.write(str(z)+'\n') 
	file.close() 

x = func_3(20) 
y = func_3(10)
z = func_3(10) 

if z % 2 == 0: 
	z = func_2(x, y) 
elif y % 2 == 0: 
	z = func_4(x, y) 
else: 
	z = func_5(x, y) 

print(x)
print(y)
print(z)

file_write(x, y, z) 
