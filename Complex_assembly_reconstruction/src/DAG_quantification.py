import networkx as nx 
import random
import copy
import string
from scipy import stats
from matplotlib import pyplot as plt
import seaborn as sns
import numpy as np 

def normalize_edge(nG, edge_dict):
    new_edge_list = []
    for node in nG.nodes():
        total_weight = 0
        neighbor_ls = []
        for neighbor in nx.all_neighbors(nG, node):
            if len(neighbor) > len(node):
                neighbor_ls.append(neighbor)
                total_weight += edge_dict[(node, neighbor)]
        for neighbor in neighbor_ls:
            weight = edge_dict[(node, neighbor)]
            new_edge_list.append((node, neighbor, weight/total_weight))
    return new_edge_list   

def nearest_index(paths, sub2):
    n = 0
    m = 0
    while m<1:
        if paths[n].count(sub2)>0:
            m+=1
        n+=1
    return n-1

def calculate_pair_prob(pair, nG, edge_dict):
    sub1, sub2 = pair
    #All subcomplexes that contain both subunit1 and subunit2
    target_subcomplex = [i for i in nG.nodes() if i.count(sub1)!=0 and i.count(sub2)!=0]
    
    #Save distinct paths from subunits1 to where subunit1 and 2 coalesce
    sub1_paths_dict = {} 
    for target in target_subcomplex:
        for i in nx.all_simple_paths(nG, sub1, target):
            ls = i[:nearest_index(i, sub2)+1]
            sub1_paths_dict[str(ls)] = ls
    #Save distinct paths from subunits2 to where subunit1 and 2 coalesce
    sub2_paths_dict = {}
    for target in target_subcomplex:
        for i in nx.all_simple_paths(nG, sub2, target):
            ls = i[:nearest_index(i, sub1)+1]
            sub2_paths_dict[str(ls)] = ls

    sub1_paths = list(sub1_paths_dict.values())
    sub2_paths = list(sub2_paths_dict.values())

    #All subcomplexes that subunit1 and 2 first coalesce
    assembly_subcomplexes = list(set([i[-1] for i in sub1_paths]+[i[-1] for i in sub2_paths]))

    final_prob = 0 
    for subcomplex in assembly_subcomplexes:
        
        sub1_total = 0
        n = 0
        for path in sub1_paths:
            if path[-1] == subcomplex:
                path_p = 1
                for i in range(len(path)-1):
                    path_p *= edge_dict[(path[i], path[i+1])]
                sub1_total += path_p 
                n +=1
        if n==0:
            sub1_p = 1
        else:
            sub1_p = sub1_total/n

        sub2_total = 0
        n = 0 
        for path in sub2_paths:
            if path[-1] == subcomplex: 
                path_p = 1
                for i in range(len(path)-1):
                    path_p *= edge_dict[(path[i], path[i+1])]
                sub2_total += path_p 
                n +=1
        if n==0:
            sub2_p = 1
        else:
            sub2_p = sub2_total/n
        
        final_prob += sub1_p*sub2_p

    #return final_prob
    return final_prob/len(assembly_subcomplexes)

def calculate_distance(All_pairs, nG, edge_weight_dict):
    pairwise_distance_dict = {}
    for pair in All_pairs:
        distance = 1/calculate_pair_prob(pair, nG, edge_weight_dict)
        pairwise_distance_dict[pair] = distance
    return pairwise_distance_dict

def gen_codon_table(original):
    codon_table = {}
    new = [i for i in string.ascii_lowercase[:len(original)]]
    random.shuffle(new)
    
    for i in range(len(original)):
        codon_table[new[i]] = original[i] 
    
    return codon_table

def sort_a(s):
    return ''.join(sorted(s))
    
def convert_subunits(sub, codon_table):
    s1 = sub.replace('1', 'a')
    s2 = s1.replace('2', 'b')
    s3 = s2.replace('3', 'c')
    s4 = s3.replace('4', 'd')
    s5 = s4.replace('5', 'e')
    s6 = s5.replace('6', 'f')
    s7 = s6.replace('7', 'g')
    s8 = s7.replace('8', 'h')
    s9 = s8.replace('9', 'i')
    ls = list(codon_table.keys())
    
    for i in range(len(ls)):
        s9 = s9.replace(ls[i], codon_table[ls[i]])
        
    return sort_a(s9) 

def generate_random_ctrl_ks(All_subunits, All_pairs, new_edge_list, group1, group2):
    codon_table = gen_codon_table(All_subunits)
    
    edge_list_new_shuffle = [(convert_subunits(i[0],codon_table),convert_subunits(i[1],codon_table),i[2]) for i in new_edge_list]
    edge_weight_dict_shuffle = {(i[0], i[1]):i[2]for i in edge_list_new_shuffle} 

    nG=nx.DiGraph()
    nG.add_weighted_edges_from(edge_list_new_shuffle)

    pairwise_distance_dict_shuffle = {}
    for pair in All_pairs:
        distance = 1/calculate_pair_prob(pair, nG, edge_weight_dict_shuffle)
        pairwise_distance_dict_shuffle[pair] = distance

    group1_intra_pairs = [i for i in All_pairs if set(i).issubset(set(group1))]
    group2_intra_pairs = [i for i in All_pairs if set(i).issubset(set(group2))]
    inter_pairs = [i for i in All_pairs if set(i).intersection(set(group1)) != set() and set(i).intersection(set(group2)) != set()]

    group1_intra_distance = [pairwise_distance_dict_shuffle[i] for i in group1_intra_pairs]
    group2_intra_distance = [pairwise_distance_dict_shuffle[i] for i in group2_intra_pairs]
    inter_distance = [pairwise_distance_dict_shuffle[i] for i in inter_pairs]
    
    intra_ = group1_intra_distance + group2_intra_distance
    inter_ = inter_distance
    ks_stat, p_value = stats.ks_2samp(intra_, inter_)

    return p_value

def draw_distribution(intra_, inter_, bins_1=10, bins_2=43, complex_name='CSN'):
    plt.figure(figsize=(6, 5))
    sns.distplot(intra_,bins_1,label='intra-group distance', kde=False, hist_kws={"alpha":0.6}) #color=sns.color_palette()[4]
    sns.distplot(inter_,bins_2, label='inter-group distance', kde=False, hist_kws={"alpha":0.6}) #color='green'
    plt.title(f'Pairwise distance of subunits in {complex_name} DAG')
    plt.ylabel('Number')
    plt.xlabel('Distance')
    #plt.xlim(0, np.array(inter_).max())
    plt.legend(bbox_to_anchor=(1.1, 1))
    plt.show()

def draw_CDF(data_ls, label_ls):
    plt.figure(figsize=(6, 5))

    for i in range(2):
        data = data_ls[i]
        count, bins_count = np.histogram(data, bins=1000,density=True)
        pdf = count / sum(count)
        cdf = np.cumsum(pdf)

        plt.plot(bins_count[1:], cdf, label="CDF of intra-group distance", linewidth=4) #sns.color_palette()[4]

    data = inter_
    count, bins_count = np.histogram(data, bins=1000, density=True)
    pdf = count / sum(count)
    cdf = np.cumsum(pdf)

    plt.plot(bins_count[1:], cdf, label="CDF of inter-group distance", linewidth=4) #color=green

    plt.ylabel('Fraction')
    plt.xlabel('Distance') 
    #plt.xlim(0, 2256)
    plt.legend(bbox_to_anchor=(1.1, 1))
    plt.show()