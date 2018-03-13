import csv
import sys

def comp(var1, var2, var3):
    for i in range(0, var3):
        if var1 >= var2:
            var2 += minus(var3, var1)
        else:
            var1 += add(var3, var2)

    return var1, var2, var3

def get_data(data):
    datares = []
    for row in data:
        datares.append(float(row))
    return datares

def minus(var1, var2): 
    return var1 - var2 

def add(var1, var2):
    return var1 + var2

def file_read(f):
    read_file = open(f, "r")
    data1 = []
    data2 = []
    for line in read_file:
        item = line.split(":")
        data1.append(item[0])
        data2.append(item[1])
    return data1, data2

def output_write(data1, data2, data3):
    file = open("result.txt", "w")
    file.write(str(data1)+'\n')
    file.write(str(data2)+'\n')
    file.write(str(data3)+'\n')
    file.close() 
    return

def double(a):
    res = a + a
    return res

def reduce(a):
    res = a / 2
    return res

def addone(a):
    return a + 1
    
# Main Program
data_input_a = "data1.dat"
x = reduce(108) 
data_input_b = "data2.dat"

data_a1, data_a2 = file_read(data_input_a)
y = addone(18)
data_b1, data_b2 = file_read(data_input_b)

data_add = add(data_a1, data_b1)
data_double = double(data_a2) + double(data_b2)

z = addone(29) 
res = comp(x, y, z)

t = get_data(data_add)
p = get_data(data_double)

output_write(t, p, res)
