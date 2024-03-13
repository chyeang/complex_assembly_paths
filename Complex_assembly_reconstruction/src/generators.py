##Import requirements
from itertools import combinations as comb 
import numpy as np 
import ast
from bisect import bisect_left
##Structure generator
def binary_decompose(sub_num):
    LS = []
    for j in range(2, sub_num+1):
        subu = j
        i = subu 
        ls = []
        while i >=subu/2+1:
            i -= 1
            j = subu - i
            ls.append([i, j])
        LS.append(ls)
    return LS

def gen_list(l, k):
    if l != k:
        ls = []
        for i in l:
            for j in k:
                s = [i, j]
                ls.append(s)
        return ls
    else:
        ls = []
        n = 0
        for i in l:
            for j in k[n:]:
                s = [i, j]
                ls.append(s)
            n +=1
        return ls

def struture_simulator(LS):
    ls = [[1]]
    for i in LS:
        if len(i) == 1:  #deal with [[1, 1]] and [[2, 1]]
            if i[0][0] == 1:
                ls.append(i) #append [[1, 1]]
            if i[0][0] == 2:
                s = [ls[1][0],i[0][1]] #s = [[1, 1], 1]
                ls.append([s])
        else:
            ls1 = []
            for j in i:
                s = gen_list(ls[j[0]-1], ls[j[1]-1])
                for k in s:
                    ls1.append(k)
            ls.append(ls1)
    return ls

def structure_generator(sub_num):
    
    LS = binary_decompose(sub_num)
    ls = struture_simulator(LS)
    
    return ls[-1] 

## Order generator
def decompose(structure, x, length, left, right):
    if structure[0] == structure[1]:
        l = list(comb(x, length))
        ls = l[:len(l)//2]
    else:
        ls = list(comb(x, length))
    output_ls = [] 
    for y in ls:
        z = tuple([i for i in x if i not in y])
        if left != () and right !=():
            output_ls.append(left+(y, z)+right) 
        elif left == () and right!=():
            output_ls.append((y, z)+right) 
        elif left != () and right==():
            output_ls.append(left+(y, z)) 
        else: 
            output_ls.append((y, z))
    return output_ls

def element_length(l):
    def func(l):
        if not isinstance(l, (list, tuple)):
            yield 1
        else:
            for i in l:
                if not isinstance(i, (list, tuple)):
                    yield 1
                else:
                    yield from func(i)
    n = 0 
    for i in func(l):
        n+=i 
    return n

def generate_sub_structure(structure):
    if isinstance(structure[0], (list, tuple)):
        yield element_length(structure[0]), structure[0]
        yield element_length(structure[1]), structure[1]
    for i in structure:
        if not isinstance(i, (list, tuple)) or element_length(i)<=3:
            pass
        else:
            yield from generate_sub_structure(i)
            
def find_all_position(input_str, target_str, origi=0):
    ind = input_str.find(target_str)
    if ind != -1:
        yield ind + origi
        origi = ind+len(target_str)
        remain = input_str[origi:]
        if len(remain)>len(target_str):
            yield from find_all_position(remain, target_str, origi)

def generate_stru_dict(structure):
    stru_dict = {} 
    for i in generate_sub_structure(structure):
        key, struc = i 
        stru_dict.setdefault(key, [])
        stru_dict[key].append(struc)

    for i in stru_dict.keys():
        if i>=4 and len(stru_dict[i])>1:
            ls = []
            for j in stru_dict[i]:
                for k in list(find_all_position(str(structure), str(j))):
                    ls.append((k, j))
            stru_dict[i] = sorted(dict(ls).items())
    return stru_dict
            
def order_generator(structure, subunit_ls, left, right, stru_dict, total_len):

    if left != () and not all([len(m)<=2 for m in left]):
        pass
    else:
        left_len, right_len = element_length(structure[0]), element_length(structure[1])
        LS = decompose(structure, subunit_ls, left_len, left, right) 

        for i in LS:
            if all([len(k)<=2 for k in i]):
                yield i
            else: 
                for j in range(len(i)):
                    length = len(i[j])
                    if length>2:
                        left = tuple(i[:i.index(i[j])])
                        right = tuple(i[i.index(i[j])+1:])
                        if len(stru_dict[length])>1 and length>=4:
                            n = 0 
                            for item in left:
                                n+=len(item)
                            ind = int(np.round(n/total_len*len(stru_dict[length])))
                            stru = stru_dict[length][ind][1]
                        else:
                            stru = stru_dict[length][0]

                        yield from order_generator(stru, i[j], left, right, stru_dict, total_len)

## Tree generator
def order_converter(ls):
    stri = '' 
    for i in ls:
        for j in i:
            stri += j 
    return stri

def assign_element(structure, converted_order):
    s1 = str(structure)
    s2 = s1.replace('1', ''''%s\'''')
    tup = tuple([i for i in converted_order])
    s3 = s2%tup
    ls = ast.literal_eval(s3)
    return ls

def tree_generator(structure, order):
    converted_order = order_converter(order)
    tree = assign_element(structure, converted_order)
    return tree, converted_order

## frequency
def gen_code_ls(module_ls): 
    All_situations = [] 
    for i in range(len(module_ls), 0, -1): 
        for j in comb(module_ls, i):
            All_situations.append(j)
    All_situations.append('None')
    
    #Convert the situation into string
    All_string = [] 
    for i in All_situations:
        string = '' 
        for j in i:
            string += j 
        All_string.append(string)
        
    #Convert the string into code
    code_ls = [] 
    for i in All_string: 
        code = ''
        for module in module_ls:
            if i.find(module) == -1:
                code+='0'
            else: 
                code+='1'
        code_ls.append(code)
        
    return code_ls 

def gen_bins(sorted_all_score, bin_num=100, linear=True):
    mi = sorted_all_score[0]
    ma = sorted_all_score[-1] 
    if linear == True:
        bins_arr = np.linspace(mi, ma, bin_num+1)[:-1]
    else:
        bins_arr = np.logspace(np.log10(mi), np.log10(ma), bin_num+1)[:-1]
    
    return bins_arr 

def return_bins_index(myList, myNumber, length):
    """
    Assumes myList is sorted. Returns the closest smaller value to myNumber.
    
    """
    pos = bisect_left(myList, myNumber)
    
    if pos==length:
        return pos - 1 
    else:
        after = myList[pos]
        if myNumber == after:
            return pos
        elif myNumber < after:
            return pos - 1