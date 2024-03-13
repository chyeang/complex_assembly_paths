from itertools import combinations as comb 
from .generators import generate_stru_dict, order_generator, tree_generator
from multiprocessing import cpu_count
import os 
import copy
import time

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        value = func(*args, **kwargs)
        end = time.time()
        print(f'run time: {end-start} s')
        return value
    return wrapper

# Decompose and calculate the score 
def decompose(binary_tree):
    yield binary_tree
    for component in binary_tree:
        if isinstance(component, (list, tuple)): 
            yield from decompose(component) 
        else:
            pass
        
def flatten(component):
    if isinstance(component, (list, tuple)): 
        for i in component:
            yield from flatten(i) 
    else:
        yield component
        
def flatten_event(event):
    flat_event = []
    for c in event:
        component = ''
        for i in flatten(c):
            component += i 
        flat_event.append(component) 
    return flat_event

##generate assembly history and states from a tree 
def gen_assembly_events(assign_tree):
    assembly_events = []
    for i in decompose(assign_tree):
        event = flatten_event(i)
        assembly_events.append(event)
    assembly_events_order = sorted(assembly_events, key=lambda d: len(str(d)), reverse=False)
    
    return assembly_events_order

def update_state(event, state_0):
    new_state = copy.copy(state_0)
    for i in event:
        new_state.remove(i)
    new_state.insert(0, event[0]+event[1])
    
    return new_state
    
def gen_state_history(assembly_events_order, state_0):
    state_history = [] 
    for i in range(len(assembly_events_order)):
        state_history.append(state_0)
        event = assembly_events_order[i]
        state_0 = update_state(event, state_0)
    
    return state_history

def sort_a(s):
    return ''.join(sorted(s))
'''
def alpha_pq(c1, c2, state_0, all_pair_dict, stablize_dict, mono_degrad):
    key = sort_a(c1) + ',' + sort_a(c2) 
    p = 1
    p *= all_pair_dict[key]

    if mono_degrad == True:
        mono_ls = [i+i for i in state_0 if len(i)==1 and i!=c1 and i!=c2]
        if len(mono_ls)>0:
            for key in mono_ls:
                p*=stablize_dict[key]

    return p

def Prob_h1h0(event, state_0, all_pair_dict, stablize_dict, mono_degrad):
    c1 = event[0]
    c2 = event[1]

    alpha_pq_ = alpha_pq(c1, c2, state_0, all_pair_dict, stablize_dict, mono_degrad)
    
    sum_alpha_pq_ = 0
    for i in comb(state_0, 2):
        c1 = i[0]
        c2 = i[1]
        sum_alpha_pq_ += alpha_pq(c1, c2, state_0, all_pair_dict, stablize_dict, mono_degrad)
    
    return alpha_pq_/sum_alpha_pq_

##Calculate the score of the tree 
def calculate_score(tree, subunit_ls, all_pair_dict, stablize_dict, prob_dict, mono_degrad=False): 
    assembly_events_order = gen_assembly_events(tree)
    state_history = gen_state_history(assembly_events_order, subunit_ls) 
    
    score = 1 
    
    for i in range(len(state_history)-1):
        event = assembly_events_order[i] 
        state = state_history[i]
        key = str(event) + str(state)
        
        try:
            s = prob_dict[key] #Judge if it was calculated and saved previously
        except:
            s = Prob_h1h0(event, state, all_pair_dict, stablize_dict, mono_degrad)
            prob_dict[key] = s
        score *= s
    
    return score, prob_dict
'''

##modification
def alpha_pq(c1, c2, state_0, all_pair_dict, stablize_dict, subcom_dict, mono_degrad, cal_state):
    if cal_state == True: 
        state_1 = [c1+c2] + [i for i in state_0 if len(i)>1 and i!=c1 and i!=c2]
        p = 1
        for subcom in state_1:
            p *= subcom_dict[sort_a(subcom)]
        
    else:
        key = sort_a(c1) + ',' + sort_a(c2) 
        p = 1
        p *= all_pair_dict[key]
        
    if mono_degrad == True:
        mono_ls = [i+i for i in state_0 if len(i)==1 and i!=c1 and i!=c2]
        if len(mono_ls)>0:
            for key in mono_ls:
                p*=stablize_dict[key]
 
    return p

def Prob_h1h0(event, state_0, all_pair_dict, stablize_dict, subcom_dict, mono_degrad, cal_state):
    c1 = event[0]
    c2 = event[1]

    alpha_pq_ = alpha_pq(c1, c2, state_0, all_pair_dict, stablize_dict, subcom_dict, mono_degrad, cal_state)
    
    sum_alpha_pq_ = 0
    for i in comb(state_0, 2):
        c1 = i[0]
        c2 = i[1]
        sum_alpha_pq_ += alpha_pq(c1, c2, state_0, all_pair_dict, stablize_dict, subcom_dict, mono_degrad, cal_state)
    
    return alpha_pq_/sum_alpha_pq_

def calculate_score(tree, subunit_ls, all_pair_dict, stablize_dict, subcom_dict, prob_dict, mono_degrad=False, cal_state=False): 
    assembly_events_order = gen_assembly_events(tree)
    state_history = gen_state_history(assembly_events_order, subunit_ls) 
    
    score = 1 
    
    for i in range(len(state_history)-1):
        event = assembly_events_order[i] 
        state = state_history[i]
        key = str(event) + str(state)
        
        try:
            s = prob_dict[key] #Judge if it was calculated and saved previously
        except:
            s = Prob_h1h0(event, state, all_pair_dict, stablize_dict, subcom_dict, mono_degrad, cal_state)
            prob_dict[key] = s
        score *= s
    
    return score, prob_dict

def save_result(folder, filename, structure, result_dict):
    try: 
        os.listdir(folder)
    except:
        os.mkdir(folder)
    strin = '' 
    with open(folder+filename, 'w') as f:
        strin += str(structure) + '\n'
        for i in result_dict.items():
            order, score = i 
            strin += order +','+str(score)+'\n'
        f.write(strin) 

def parameter_assignment(all_structure, subunit_ls, all_pair_dict, stablize_dict, subcom_dict, complex_name, mono_degrad, cal_state):
    cpu_num = cpu_count()-1 
    common_ls = [subunit_ls, all_pair_dict, stablize_dict, subcom_dict, complex_name, mono_degrad, cal_state]
    parameter_ls = [] 
    total_num = len(all_structure)
    n = 0 
    for i in range(cpu_num):
        l = all_structure[n:n+total_num//cpu_num]
        n += total_num//cpu_num
        parameter_ls.append([l, i, common_ls])    
    remain = all_structure[n:]
    for i in range(len(remain)):
        ls = parameter_ls[i][0]
        ls.append(remain[i])
    return parameter_ls, cpu_num

def calculation_func(structure_ls, cpu_ind, arg_ls):
    subunit_ls, all_pair_dict, stablize_dict, subcom_dict, complex_name, mono_degrad, cal_state = arg_ls
    sub_num = len(subunit_ls)
    n = 0
    for structure in structure_ls:
        stru_dict = generate_stru_dict(structure)
        prob_dict = {}
        result_dict = {}
        for order in order_generator(structure, subunit_ls, (), (), stru_dict, sub_num):
            tree, converted_order = tree_generator(structure, order)
            score, prob_dict = calculate_score(tree, subunit_ls, all_pair_dict, stablize_dict, subcom_dict, prob_dict, mono_degrad, cal_state)
            result_dict[converted_order] = score
        save_result(f'result/tree_score/{complex_name}/', str(cpu_ind)+'_'+str(n)+'.txt', structure, result_dict) 
        n+=1