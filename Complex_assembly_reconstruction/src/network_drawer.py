import matplotlib.pyplot as plt
import networkx as nx
import random
from .generators import assign_element
from .calculator import sort_a
from .data_converter import subunit_converter
import ast

#Decompose a list representation of binary tree
def flatten(l):

    def flat(l):
        for element in l:
            if not isinstance(element, (list, tuple)):
                yield element
            else:
                yield from flat(element)

    s =''.join(flat(l))

    return s

def all_nodes(l):

    def generate_nodes(l):
        for k in l:
            if not isinstance(k, (list, tuple)):
                yield k
            else:
                yield flatten(k)
                yield from generate_nodes(k)
    
    node_ls = [flatten(l)]
    for i in generate_nodes(l):
        node_ls.append(i)

    return node_ls

def all_edges(node_ls):
    edge_ls = []
    for node in node_ls:
        if len(node)>1:
            for i in node_ls:
                for j in node_ls:
                    combine_node = i + j
                    if combine_node == node:
                        edge_ls.append((i, node))
                        edge_ls.append((j, node))
    return edge_ls    

#Layout of nodes in binary tree for networkx drawing
def hierarchy_pos(G, root=None, width=1., vert_gap = 0.5, vert_loc = 0, xcenter = 0.5):

    if not nx.is_tree(G):
        raise TypeError('cannot use hierarchy_pos on a graph that is not a tree')

    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(iter(nx.topological_sort(G)))  #allows back compatibility with nx version 1.11
        else:
            root = random.choice(list(G.nodes))

    def _hierarchy_pos(G, root, width=1, vert_gap = 10, vert_loc = 100, xcenter = 100, pos = None, parent = None):

        if pos is None:
            pos = {root:(xcenter,vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        children = list(G.neighbors(root))
        if not isinstance(G, nx.DiGraph) and parent is not None:
            children.remove(parent)  
        if len(children)!=0:
            #dx = width/len(children)**0.8
            dx = width/len(children)**0.5
            nextx = xcenter -width/6.5- dx/1.3 
            for child in children:
                nextx += 0.7*dx
                pos = _hierarchy_pos(G,child, width = dx, vert_gap = vert_gap, 
                                    vert_loc = vert_loc-vert_gap, xcenter=nextx,
                                    pos=pos, parent = root)
        return pos


    return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)

#Draw the tree from str tree
def save_tree_data(root, edge_ls, filename): 
    with open(filename, 'w') as f: 
        string = '' 
        string += '>' + root + '\n'
        for i in edge_ls:
            string += i[0] + ',' + i[1] + '\n'
        f.write(string)

def draw_tree(tree, if_save=False, filename=None):
    node_ls = all_nodes(tree)
    edge_ls = all_edges(node_ls) 
    root = node_ls[0]
    
    G=nx.Graph()
    G.add_edges_from(edge_ls)
    pos = hierarchy_pos(G, root)    

    nx.draw_networkx_labels(G, pos, font_size=15, font_color='k', font_family='sans-serif', font_weight='normal')
    nx.draw(G, pos=pos, with_labels=False, node_size=0, node_color='b', alpha=0.5, node_shape='o')
    if if_save == True:
        save_tree_data(root, edge_ls, filename)
    plt.show()
    
    return root, edge_ls

def check_top_ranking_trees(target, edge_list, top_num, if_save=False, file_prefix=''):
    dag_edge_list = [(i[0], i[1]) for i in edge_list]
    
    m = 1
    n = 1
    while m < top_num+1:
        i = target.sorted_All[-n] 
        tree = ast.literal_eval(i[0])
        node_list = all_nodes(tree)
        tree_edge_list_unsort = all_edges(node_list)
        tree_edge_list = [(sort_a(i[0]), sort_a(i[1])) for i in tree_edge_list_unsort]
        not_in_dag = [i for i in tree_edge_list if i not in dag_edge_list]
        
        if len(not_in_dag) == 0:
            root, edge_ls = draw_tree(tree)
            if if_save==True:
                save_tree_data(root, edge_ls, file_prefix+'_'+str(m)+'.txt')

            m += 1
        else:
            draw_tree(tree)
        print(n, not_in_dag, i[1])
        n+=1 

#DAG drawer 
def generate_feature_frequency_dict(target, top_number, convert, sorting=True):
    feature_dict = {}
    m = len(target.sorted_All) - top_number
    
    if sorting == True:
        for i in target.sorted_All[m:]:
            old_string, item = i 
            ind, score = item
            structure = target.structure_ls[ind]
            order = subunit_converter(old_string, convert) 
            tree = assign_element(structure, order) 
            
            for feature in all_nodes(tree):
                new_feature = sort_a(feature)
                feature_dict.setdefault(new_feature, 0)
                feature_dict[new_feature] += 1
                
    else:
        for i in target.sorted_All[m:]:
            old_string, item = i 
            ind, score = item
            structure = target.structure_ls[ind]
            order = subunit_converter(old_string, convert) 
            tree = assign_element(structure, order) 

            for feature in all_nodes(tree):
                feature_dict.setdefault(feature, 0)
                feature_dict[feature] += 1        
            
    return feature_dict

def decompose_top_ranking_tree(target, top_number, convert):
    
    top_ranking_tree_ls = [] 
    for i in target.sorted_All[-top_number:]:
        old_string, item = i 
        ind, score = item
        structure = target.structure_ls[ind]
        order = subunit_converter(old_string, convert) 
        tree = assign_element(structure, order) 
        
        node_list = all_nodes(tree)
        edge_list = all_edges(node_list)
        top_ranking_tree_ls.append((node_list, edge_list))
    
    return top_ranking_tree_ls

def generate_edge_lst(top_ranking_tree_ls, threshold=1):
    edge_pool = []
    for tree in top_ranking_tree_ls:
        edge_ls = tree[1]
        for edge in edge_ls:
            edge_pool.append((sort_a(edge[0]),sort_a(edge[1])))
            
    distinct_edge_ls = list(set(edge_pool))
    
    distinct_edge_ls_plot = [] 
    for edge in distinct_edge_ls:
        weight = edge_pool.count(edge)
        
        if weight>=threshold:
            distinct_edge_ls_plot.append((edge[0], edge[1], weight))

    return distinct_edge_ls_plot

def if_conect_to_final_initial(G, node, final, convert, convert_re): #final='1112356789S',
    try:
        d = nx.shortest_path_length(G,node,final) 
        converted_node = ''.join(subunit_converter(node, convert_re))
        converted_final = ''.join(subunit_converter(final, convert_re))
        
        length = len(converted_node)
        try:
            for i in converted_node:
                mono = sort_a(''.join(subunit_converter(i, convert)))
                q = nx.shortest_path_length(G, mono, node)
            if d <= len(converted_final) - length:
                return True
        except:
            return False
    except:
        return False
    
def generate_new_edge_ls(edge_list, weight, final, convert, convert_re):
    #Create a graph
    G=nx.DiGraph()
    G.add_weighted_edges_from(edge_list)
    
    new_edge_list = []
    for edge in G.edges():
        if if_conect_to_final_initial(G, edge[0], final, convert, convert_re) and if_conect_to_final_initial(G, edge[1], final, convert, convert_re):
            w = G[edge[0]][edge[1]]['weight']*weight
            new_edge_list.append((edge[0], edge[1], w))
    
    return new_edge_list

def directed_acyclic_graph_by_klhsu(G, number, convert_re, width=1.0, vertical_gap=0.5, vertical_location =100, xcenter = 0):
    position = {}
    
    nodes_group_by_number = {}
    for node in list(G.nodes):
        converted_node = ''.join(subunit_converter(node, convert_re))
        length = len(converted_node) #convert_csn_re
        nodes_group_by_number.setdefault(length, [])
        nodes_group_by_number[length].append(node)
    
    for number_group in nodes_group_by_number.items():
        y = vertical_location - (number - number_group[0])*vertical_gap
        if len(number_group[1])==1:
            position[number_group[1][0]]=(xcenter, y)
        else:
            nodes_number = len(number_group[1])
            half_width = (number - number_group[0])*width
            unit_width = 2*half_width/(nodes_number-1)
            
            for i in range(nodes_number):
                position[number_group[1][i]] = (-half_width+i*unit_width, y)

    return position

def draw_dag(new_edge_list, feature_dict_top_sorted, number, convert_re, weight=1, size=1):
    
    nG=nx.DiGraph()
    nG.add_weighted_edges_from(new_edge_list)    

    edges = nG.edges()
    pos = directed_acyclic_graph_by_klhsu(nG, number, convert_re)
    weights = [weight*0.5*(nG[u][v]['weight']) for u,v in edges]
    node_size = [feature_dict_top_sorted[x]*120*size for x in nG.nodes()]
    node_size_dict = {x:feature_dict_top_sorted[x]*120*size for x in nG.nodes()}

    plt.figure(figsize=(12, 12))
    nx.draw_networkx_labels(nG, pos, font_size=12, font_color='k', font_family='sans-serif', font_weight='normal')
    nx.draw_networkx_edges(nG, pos=pos, width=weights, arrowstyle='-')
    nx.draw_networkx_nodes(nG, pos=pos, node_size=node_size, node_color='w', alpha=1, node_shape='o')
    nx.draw_networkx_nodes(nG, pos=pos, node_size=node_size, node_color='b', alpha=0.3, node_shape='o')
    plt.show()
    
    return node_size_dict, nG

def save_dag(new_edge_list, node_size_dict, prefix, filename):
    string = ''
    for i in new_edge_list:
        for j in i:
            string+=str(j)+','
        string+='\n'

    with open('result/dag_info/edge_list' + prefix + filename + '.txt', 'w') as f:
        f.write(string)

    string = '' 
    for i in node_size_dict.items():
        for j in i:
            string+=str(j)+','
        string+='\n'

    with open('result/dag_info/node_size' + prefix + filename + '.txt', 'w') as f:
        f.write(string)

def cutoff_gate(top_num, threshold, target, convert, convert_re,
                 final, number, prefix, if_save=False, if_show=True):

    top_ranking_tree_ls = decompose_top_ranking_tree(target, top_num, convert)
    feature_dict_top_sorted = generate_feature_frequency_dict(target, top_num, convert)
    distinct_edge_ls_plot = generate_edge_lst(top_ranking_tree_ls, threshold=threshold)

    new_edge_list = generate_new_edge_ls(distinct_edge_ls_plot, 
                                         weight=1/top_num*10*0.8, 
                                         final=final, convert=convert, convert_re=convert_re)
    if if_show == True:
        node_size_dict, G = draw_dag(new_edge_list, feature_dict_top_sorted, number=number, 
                                     convert_re=convert_re, weight=2, size=1.2/top_num*10)
    if if_save==True:
        save_dag(new_edge_list, node_size_dict, prefix,'top'+str(top_num)+'_'+str(threshold))
    
    print(len(G.edges))
    print(len(G.nodes))
    
    return new_edge_list


#For PCI complexes 
def generate_feature_frequency_dict_PCI(target, top_number, sorting=True):
    feature_dict = {}
    m = len(target) - top_number
    
    if sorting == True:
        for i in target[m:]:
            tree = i[0]
            l = ast.literal_eval(tree)
            for feature in all_nodes(l):
                new_feature = sort_a(feature)
                feature_dict.setdefault(new_feature, 0)
                feature_dict[new_feature] += 1
                
    else:
        for i in target[m:]:
            tree = i[0]
            l = ast.literal_eval(tree)
            for feature in all_nodes(l):
                feature_dict.setdefault(feature, 0)
                feature_dict[feature] += 1        
            
    return feature_dict

def decompose_top_ranking_tree_PCI(target, top_number=20):
    
    top_ranking_tree_ls = [] 
    for i in target.sorted_All[-top_number:]:
        tree = ast.literal_eval(i[0])
        node_list = all_nodes(tree)
        edge_list = all_edges(node_list)
        top_ranking_tree_ls.append((node_list, edge_list))
    
    return top_ranking_tree_ls

def if_conect_to_final_initial_PCI(G, node, final, convert, convert_re): #final='1112356789S',
    try:
        d = nx.shortest_path_length(G,node,final) 
        length = len(convert_re(node))
        try:
            for i in convert_re(node):
                mono = convert(i)
                q = nx.shortest_path_length(G, mono, node)
            if d <= len(convert_re(final)) - length:
                return True
        except:
            return False
    except:
        return False
    
def generate_new_edge_ls_PCI(edge_list, weight, final, convert, convert_re):
    #Create a graph
    G=nx.DiGraph()
    G.add_weighted_edges_from(edge_list)
    
    new_edge_list = []
    for edge in G.edges():
        if if_conect_to_final_initial_PCI(G, edge[0], final, convert, convert_re) and if_conect_to_final_initial_PCI(G, edge[1], final, convert, convert_re):
            w = G[edge[0]][edge[1]]['weight']*weight
            new_edge_list.append((edge[0], edge[1], w))
    
    return new_edge_list

def directed_acyclic_graph_by_klhsu_PCI(G, number, convert_re, width=1.0, vertical_gap=0.5, vertical_location =100, xcenter = 0):
    position = {}
    
    nodes_group_by_number = {}
    for node in list(G.nodes):
        length = len(convert_re(node)) #convert_csn_re
        nodes_group_by_number.setdefault(length, [])
        nodes_group_by_number[length].append(node)
    
    for number_group in nodes_group_by_number.items():
        y = vertical_location - (number - number_group[0])*vertical_gap
        if len(number_group[1])==1:
            position[number_group[1][0]]=(xcenter, y)
        else:
            nodes_number = len(number_group[1])
            half_width = (number - number_group[0])*width
            unit_width = 2*half_width/(nodes_number-1)
            
            for i in range(nodes_number):
                position[number_group[1][i]] = (-half_width+i*unit_width, y)

    return position

def draw_dag_PCI(new_edge_list, feature_dict_top_sorted, number, convert_re, weight=1, size=1):
    
    nG=nx.DiGraph()
    nG.add_weighted_edges_from(new_edge_list)    

    edges = nG.edges()
    pos = directed_acyclic_graph_by_klhsu_PCI(nG, number, convert_re)
    weights = [weight*0.5*(nG[u][v]['weight']) for u,v in edges]
    node_size = [feature_dict_top_sorted[x]*120*size for x in nG.nodes()]
    node_size_dict = {x:feature_dict_top_sorted[x]*120*size for x in nG.nodes()}

    plt.figure(figsize=(12, 12))
    nx.draw_networkx_labels(nG, pos, font_size=12, font_color='k', font_family='sans-serif', font_weight='normal')
    nx.draw_networkx_edges(nG, pos=pos, width=weights, arrowstyle='-')
    nx.draw_networkx_nodes(nG, pos=pos, node_size=node_size, node_color='w', alpha=1, node_shape='o')
    nx.draw_networkx_nodes(nG, pos=pos, node_size=node_size, node_color='b', alpha=0.3, node_shape='o')
    plt.show()
    
    return node_size_dict, nG

def cutoff_gate_PCI(top_num, threshold, target, convert, convert_re,
                 final, number, prefix, if_save=False):

    top_ranking_tree_ls = decompose_top_ranking_tree_PCI(target, top_num)
    feature_dict_top_sorted = generate_feature_frequency_dict_PCI(target.sorted_All, top_num)
    distinct_edge_ls_plot = generate_edge_lst(top_ranking_tree_ls, threshold=threshold)

    new_edge_list = generate_new_edge_ls_PCI(distinct_edge_ls_plot, 
                                            weight=1/top_num*10*0.8, 
                                            final=final, convert=convert, convert_re=convert_re)

    node_size_dict, G = draw_dag_PCI(new_edge_list, feature_dict_top_sorted, number=number, 
                                 convert_re=convert_re, weight=2, size=1.2/top_num*10)
    if if_save==True:
        save_dag(new_edge_list, node_size_dict, prefix,'top'+str(top_num)+'_'+str(threshold))
    
    print(len(G.edges))
    print(len(G.nodes))
    #node_size_dict['57']
    
    return new_edge_list