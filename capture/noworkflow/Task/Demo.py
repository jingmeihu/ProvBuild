# original script
def foo(var): 
	return var
def bar(var1, var2):
	return var1 + var2
def output_write(a, b):
	file = open("result.txt", "w") 
	file.write(str(a)+'\n')
	file.write(str(b)) 
	file.close() 
x = foo(10)
y = foo(20)
z = bar(x, y)
z = z + y
n = y * 10
output_write(z, n)