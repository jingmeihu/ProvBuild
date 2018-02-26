import csv
import sys

def extract_column(data, column):
    col_data = []
    for row in data:
        col_data.append(float(row[column]))
    return col_data

def simulation_add(a, b):
    res = a + b
    return res

def csv_read(f):
    reader = csv.reader(open(f, "rU"), delimiter=":")
    data = []
    for row in reader:
        data.append(row)
    return data

def write_result(data1, data2):
    t = extract_column(data1, 0)
    p = extract_column(data2, 1)
    file = open("result.txt", "w")
    file.write(str(t)+'\n')
    file.write(str(p)+'\n')
    file.close() 

def run_simulation(a, b):
    data1 = simulation_add(a, b)
    data2 = simulation_double(a)
    return data1, data2

def write_output_0(data1):
    res = extract_column(data1, 0)
    file = open("result.txt", "a")
    file.write(str(res)+'\n')
    return

def simulation_double(a):
    res = a + a
    return res

def file_write(n, m, x, y, z):
    file = open("result.txt", "w") 
    file.write(str(n)+'\n')
    file.write(str(m)+'\n') 
    file.write(str(x)+'\n')
    file.write(str(y)+'\n') 
    file.write(str(z)+'\n') 
    file.close() 

def write_output_1(data1):
    res = extract_column(data1, 1)
    file = open("result.txt", "a")
    file.write(str(res)+'\n')
    return

# Main Program
data_input_a = "data1.dat"
data_input_b = "data2.dat"
data_a = csv_read(data_input_a)
data_b = csv_read(data_input_b)
data_add, data_double = run_simulation(data_a, data_b)

write_result(data_add, data_double)
# write_output_0(data_add)
# write_output_1(data_double)
