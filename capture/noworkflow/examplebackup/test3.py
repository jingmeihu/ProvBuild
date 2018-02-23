import csv
import sys

data_input_a = "data1.dat"
data_input_b = "data2.dat"

def add(a, b):
    res = a + b
    return res

def get_data(data):
    datares = []
    for row in data:
        datares.append(float(row))
    return datares

def extract_cols(data1, data2): 
    t = extract_col(data1, 0)
    p = extract_col(data2, 1)
    return (t, p)

def write_output_0(data1):
    res = get_data(data1)
    file = open("result.txt", "a")
    file.write(str(res)+'\n')

def csv_read(f):
    reader = csv.reader(open(f, "rU"), delimiter=":")
    data_1 = []
    data_2 = []
    for row in reader:
        data_1.append(row[0])
        data_2.append(row[1])
    return data_1, data_2

def write_result(data1):
    res = get_data(data1)
    file = open("result.txt", "w")
    file.write(str(res)+'\n')

def double2(a):
    res = a + a
    return res

def double(a, b):
    doublea = double2(a)
    doubleb = double2(b)
    return doublea, doubleb

def write_output_1(data1):
    res = get_data(data1)
    res += res
    file = open("result.txt", "a")
    file.write(str(res)+'\n')

def write(data_add, data_doublea, data_doubleb): 
    write_result(data_add)
    write_output_0(data_doublea)
    write_output_1(data_doubleb)

data_a1, data_a2 = csv_read(data_input_a)
data_b1, data_b2 = csv_read(data_input_b)
data_add = add(data_a1, data_b1)
data_doublea, data_doubleb = double(data_a2, data_b2)
write(data_add, data_doublea, data_doubleb)
