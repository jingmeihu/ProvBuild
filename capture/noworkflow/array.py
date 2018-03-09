def func():
	return [[1,2],  [3,4]]

def ret():
	return 6

test = func()
for item in test:
	item[0] = ret()

test2 = [1,2]
test2[0] = ret()
print(test)