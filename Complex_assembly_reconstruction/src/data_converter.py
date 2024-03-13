import xlwings as xw
import string
import time
from itertools import combinations as comb 
from itertools import permutations as perm 
import copy
import pandas as pd 

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        value = func(*args, **kwargs)
        end = time.time()
        print(f'run time: {end-start} s')
        return value
    return wrapper

@timer
def excel_reader(filename, sht_name, num, ini_row, ini_col):
    wb = xw.Book(filename)
    sht = wb.sheets[sht_name]
    subunit_ls = [i for i in string.ascii_lowercase[:num]]
    stablize_dict = {} 
    for i in range(num):
        for j in range(num):
            key = subunit_ls[i] + subunit_ls[j]
            value = sht.cells(ini_row+i, ini_col+j).value
            stablize_dict[key] = value
    print('Successfully read the raw data!')
    return stablize_dict

def csv_reader(filename, num):
    df = pd.read_csv(filename)
    subunit_ls = [i for i in string.ascii_lowercase[:num]]
    stablize_dict = {} 
    for i in range(num):
        for j in range(num):
            key = subunit_ls[i] + subunit_ls[j]
            value = df.iloc[i][j]
            stablize_dict[key] = value
    return stablize_dict

def combination_prob(c1, c2, pair_dict): 
    length = 0 
    p = 1 
    for i in c1:
        for j in c2:
            p *= pair_dict[i+j]
            p *= pair_dict[j+i]
            length +=2      
    return p**(1/length)

def decompose_last(num_sub):
    LS11 = []
    for j in range(2, num_sub+1):
        subu = j
        i = subu 
        ls = []
        while i >=subu/2+1:
            i -= 1
            j = subu - i
            ls.append([i, j])
        LS11.append(ls)
    return LS11

def flat_ls(ls):
    s = '' 
    for i in ls:
        s+=i
    return s

def remove_com1(ls, component1):
    L = copy.copy(ls)
    for i in component1:
        L.remove(i)
    return L

def sort_a(s):
    return ''.join(sorted(s))

@timer
def all_pair_generator(pair_dict, num):
    LS = [i for i in string.ascii_lowercase[:num]]
    num_sub = num 
    ls = decompose_last(num_sub)
    All_pair_dict = {}

    n = 0
    for i in ls:
        for j in i:
            c1 = j[0]
            c2 = j[1]
            total = c1 + c2
            if c1==c2:
                for selec in comb(LS, total):
                    new_ls = list(selec)
                    for com1 in comb(new_ls, c1):
                        component1 = flat_ls(com1)
                        component2 = flat_ls(remove_com1(new_ls, component1))   

                        key = sort_a(component1) + ',' + sort_a(component2)
                        value = combination_prob(component1, component2, pair_dict)
                        All_pair_dict[key] = value

                        n += 1

            else:
                for selec in comb(LS, total):
                    new_ls = copy.copy(list(selec))
                    for com1 in comb(new_ls, c1):
                        component1 = flat_ls(com1)
                        component2 = flat_ls(remove_com1(new_ls, component1))    

                        key1 = sort_a(component1) + ',' + sort_a(component2)
                        key2 = sort_a(component2) + ',' + sort_a(component1)
                        value = combination_prob(component1, component2, pair_dict)
                        All_pair_dict[key1] = value
                        All_pair_dict[key2] = value

                        n += 2  
    print('Successfully convert the data to all_pairs_dictionary!')
    print(f'Number of total pairs: {n}')
    return All_pair_dict

def subcom_dict_generator(stablize_dict, sub_num): 
    subcom_dict = {} 
    num = sub_num
    LS = [i for i in string.ascii_lowercase[:num]]

    for i in range(2, num):
        for combinations in comb(LS, i):
            strin = ''.join(combinations)
            subcomplex = sort_a(strin)
            s = 1 
            n = 0 
            for permutations in perm(subcomplex, 2):
                key = ''.join(permutations)
                s*= stablize_dict[key]
                n+=1
            subcom_dict[subcomplex] = s**(1/n) 
    return subcom_dict

def save_dict(dictionary, filename):
    f = open(filename, 'w')
    string = '' 
    for i in dictionary.keys():
        string += i +':'+str(dictionary[i]) + '\n'
    f.write(string)
    f.close()
    print('Successfully saved!')

def convert_psmd(string):
    s1 = string.replace('a', '3')
    s2 = s1.replace('b', '5')
    s3 = s2.replace('c', '6')
    s4 = s3.replace('d', '7')
    s5 = s4.replace('e', '8')
    s6 = s5.replace('f', '9')
    s7 = s6.replace('g', '11')
    s8 = s7.replace('h', '12')
    s9 = s8.replace('i', 'S')
    return s9

def convert_psmd_re(string):
    s1 = string.replace('3', 'a')
    s2 = s1.replace('5', 'b')
    s3 = s2.replace('6', 'c')
    s4 = s3.replace('7', 'd')
    s5 = s4.replace('8', 'e')
    s6 = s5.replace('9', 'f')
    s7 = s6.replace('11', 'g')
    s8 = s7.replace('12', 'h')
    s9 = s8.replace('S', 'i')
    return s9

def convert_csn(string):
    s1 = string.replace('a', '1')
    s2 = s1.replace('b', '2')
    s3 = s2.replace('c', '3')
    s4 = s3.replace('d', '4')
    s5 = s4.replace('e', '5')
    s6 = s5.replace('f', '6')
    s7 = s6.replace('g', '7')
    s8 = s7.replace('h', '8')
    s9 = s8.replace('i', '9')
    return s9

def convert_csn_re(string):
    s1 = string.replace('1', 'a')
    s2 = s1.replace('2', 'b')
    s3 = s2.replace('3', 'c')
    s4 = s3.replace('4', 'd')
    s5 = s4.replace('5', 'e')
    s6 = s5.replace('6', 'f')
    s7 = s6.replace('7', 'g')
    s8 = s7.replace('8', 'h')
    s9 = s8.replace('9', 'i')
    return s9

def null_convert(string):
    return string 

def subunit_converter(old_strin, dictionary):
    new_strin = []

    if all([len(i)==1 for i in dictionary.keys()]):
        for i in old_strin:
            new_strin.append(dictionary[i])
    else:
        for i in sorted(dictionary.keys(), key=lambda x:len(x), reverse=True):
            if len(i) >1:
                node = sort_a(i)
            else:
                node = i
            ind = old_strin.find(node)
            if ind != -1:
                new_strin.append(dictionary[i])
                old_strin = old_strin[:ind] + old_strin[ind+len(node):]
    return new_strin