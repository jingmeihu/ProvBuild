import csv
import sys

def comp(var1, var2, var3):
    local_1 = var1 + 1
    if var3 % 2 == 0: 
        local_2 = var2 + 1
    else: 
        local_2 = var2
    local_1 = minus(local_1, local_2)
    return local_1, local_2

def minus(var1, var2): 
    return var1 - var2 

def extract_column(data, column):
    col_data = []
    for row in data:
        col_data.append(float(row[column]))
    return col_data

def add(a, b):
    res = a + b
    return res

def csv_read(f):
    reader = csv.reader(open(f, "rU"), delimiter=":")
    data = []
    for row in reader:
        data.append(row)
    return data

def output_write(data1, data2, data3):
    t = extract_column(data1, 0)
    p = extract_column(data2, 1)
    file = open("result.txt", "w")
    file.write(str(t)+'\n')
    file.write(str(p)+'\n')
    file.write(str(data3)+'\n')
    file.close() 
    return

def run_simulation(a, b):
    data1 = add(a, b)
    data2 = double(a)
    return data1, data2

def double(a):
    res = a + a
    return res

def previous(a):
    res = a - 1
    return res

def file_write(x, y, z): 
    file = open("result.txt", "w") 
    file.write(str(x)+'\n') 
    file.write(str(y)+'\n') 
    file.write(str(z)+'\n') 
    file.close() 
    return

# Main Program
data_input_a = "data1.dat"
x = double(37) 
data_input_b = "data2.dat"

data_a = csv_read(data_input_a)
y = previous(18)
data_b = csv_read(data_input_b)

data_add, data_double = run_simulation(data_a, data_b)

z = previous(29) 
for i in range(1,5):
    y += i
res = comp(x, y, z)
output_write(data_add, data_double, res)
