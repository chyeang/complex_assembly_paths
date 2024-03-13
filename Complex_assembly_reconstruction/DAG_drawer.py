import networkx as nx 
import src.draggable_network as draggable_network
import matplotlib.pyplot as plt
import numpy as np
from src.data_converter import subunit_converter
import string

from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
import os

def gen_artist(filename, xy):
    img = mpimg.imread(filename)
    imagebox = OffsetImage(img, zoom=0.05) #0.27
    annotation = AnnotationBbox(imagebox, xy, frameon=False)
    return annotation

def read_edge(filename):
    edge_list = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        for line in lines:
            edge = line.strip().split(',')
            edge_list.append((edge[0], edge[1], float(edge[2])))
    return edge_list

def read_node_size(filename):
    node_size = {}
    with open(filename, 'r') as f:
        lines = f.readlines()
        for line in lines:
            n_s = line.strip().split(',')
            node, size = n_s[0], float(n_s[1])
            node_size[node] = size 
    return node_size

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

def convert_null(string):
    return string

def directed_acyclic_graph_by_klhsu(G, convert_re, subunits_ls, width=1.0, vertical_gap=0.5, vertical_location =100, xcenter = 0):
    position = {}
    
    nodes_group_by_number = {}
    nodes_length_ls = []
    for node in list(G.nodes):
        #converted_node = convert_re(node) #for PCI complexes
        converted_node = ''.join(subunit_converter(node, convert_re))
        length = len(converted_node)
        nodes_group_by_number.setdefault(length, [])
        nodes_group_by_number[length].append(node)
        nodes_length_ls.append(length)    
    
    distinct_length_ls = sorted(list(set(nodes_length_ls)))
    number = len(distinct_length_ls)
    

    for number_group in nodes_group_by_number.items():
        y = vertical_location - (number - distinct_length_ls.index(number_group[0])+1)*vertical_gap
        if len(number_group[1])==1:
            position[number_group[1][0]]=(xcenter, y)
  
        else:
            nodes_number = len(number_group[1])
            half_width = (number - number_group[0])*width
            unit_width = 2*half_width/(nodes_number-1)
            
            if number_group[0] == 1:
                nodes_number = len(number_group[1])
                half_width = (number - number_group[0])*width
                unit_width = 2*half_width/(nodes_number-1)
                for i in range(nodes_number):
                    position[subunits_ls[i]] = (-half_width+i*unit_width, y) 

            else:
                for i in range(nodes_number):
                    position[number_group[1][i]] = (-half_width+i*unit_width, y)
        
    return position


#presentation
#subunits_ls=['6', '7', '4', '5', '2', '9', '8', '3', '1']
#subunits_ls=['8', '9', '5', '11', '6', 'S', '12', '3', '7']
#subunits_ls=['6', '7', '5', '9', '8', '11', '3', 'S', '12']
#subunits_ls=['G', 'I', 'B', 'A', 'J', 'C', 'D', 'E', 'K', 'L', 'F', 'M', 'H']
#comparison 
#subunits_ls=['5', '6', '7', '4', '2', '1', '3', '8', '9']
#subunits_ls=['11', '8', '9', '5', '6', '7', '3', 'S', '12']

subunits_ls=['4', '5', '7', '6', '3', '2', '1']
real_names = ['1', '2', '3', '6', '5', '7', '4']
sub_num = len(real_names)
subunit_ls = [i for i in string.ascii_lowercase[:sub_num]]
dict_for_convert_re = {real_names[i]:subunit_ls[i] for i in range(sub_num)}
edge_list = read_edge('result/dag_info/edge_list_lsm_top100_5.txt')
node_size = read_node_size('result/dag_info/node_size_lsm_top100_5.txt')
img_folder = 'LSM/'

'''
subunits_ls=['1', '7', '01', '5', '6', '4', '3', '2', '8']
sub_num = len(subunits_ls)
real_names = ['1', '2', '3', '4', '5', '6', '7', '8', '10']
subunit_ls = [i for i in string.ascii_lowercase[:sub_num]]
dict_for_convert_re = {real_names[i]:subunit_ls[i] for i in range(sub_num)}
edge_list = read_edge('result/dag_info/edge_list_emc_top2000_45.txt')
node_size = read_node_size('result/dag_info/node_size_emc_top2000_45.txt')
img_folder = 'EMC/'
'''
#Create a network object
G = nx.DiGraph()
G.add_weighted_edges_from(edge_list)
pos = directed_acyclic_graph_by_klhsu(G, dict_for_convert_re, subunits_ls)

'''
subunits_ls=['6', '7', '4', '5', '2', '9', '8', '3', '1']
#Import data
edge_list = read_edge('result/dag_info/edge_list_csn_top2000_45.txt')
node_size = read_node_size('result/dag_info/node_size_csn_top2000_45.txt')
img_folder = 'CSN/'
#Create a network object
G = nx.Graph()
G.add_weighted_edges_from(edge_list)
pos = directed_acyclic_graph_by_klhsu(G, convert_csn_re, subunits_ls)
'''
'''
#subunits_ls=['8', '11', '9', '5', '12', 'S', '3', '6', '7']
subunits_ls=['8', '11', '9', '5', '12', '6', '7', 'S', '3']
#subunits_ls=['8', '11', '9', '5', '6', '7', 'S', '3', '12']
#Import data
edge_list = read_edge('result/dag_info/edge_list_psmd_top2000_45.txt')
node_size = read_node_size('result/dag_info/node_size_psmd_top2000_45.txt')
img_folder = 'PSMD/'
#Create a network object
G = nx.Graph()
G.add_weighted_edges_from(edge_list)
pos = directed_acyclic_graph_by_klhsu(G, convert_psmd_re, subunits_ls)
'''
'''
subunits_ls=['M', 'F', 'H', 'G', 'I', 'B', 'J', 'A', 'C', 'E', 'D', 'K', 'L']
#subunits_ls=['F', 'M', 'H', 'A', 'C', 'J', 'G', 'I', 'B', 'K', 'L', 'E', 'D']
#Import data
edge_list = read_edge('result/dag_info/edge_list_eif3_top1000_30.txt')
node_size = read_node_size('result/dag_info/node_size_eif3_top1000_30.txt')
img_folder = 'EIF3/'
#Create a network object
G = nx.Graph()
G.add_weighted_edges_from(edge_list)
pos = directed_acyclic_graph_by_klhsu(G, convert_null, subunits_ls)
'''


#node_size_ls = [1.3*node_size[x]*0.8 for x in G.nodes()]  #1.2*11/9
node_size_ls = [2*node_size[x]*0.8 for x in G.nodes()]  
weights = [(G[u][v]['weight'])*0.7*1.5 for u,v in G.edges()] #1.3

node_size_radius = [x**0.5 for x in node_size_ls]
#Create matplotlib object for drawing
fig, ax = plt.subplots(1, 1, figsize=(10, 10))

labels = nx.draw_networkx_labels(G, pos=pos, font_size=10, font_color='k', font_family='sans-serif', font_weight='bold')
#labels = None
edges = nx.draw_networkx_edges(G, pos=pos, ax=ax, arrowstyle='-', width=weights) #, arrowstyle='->',connectionstyle='arc3, rad=0.3'
nodes0 = nx.draw_networkx_nodes(G, pos=pos, ax=ax, node_size=node_size_ls, node_color='w', node_shape='o', alpha=1)
nodes = nx.draw_networkx_nodes(G, pos=pos, ax=ax, node_size=node_size_ls, node_color=(189/255, 215/255, 238/255), node_shape='o', alpha=1)

#Add external images
#filename_ls = [x for x in os.listdir('node_img/'+img_folder) if x.strip('.png') in pos.keys()]
#initial_key_ls = [x.strip('.png') for x in filename_ls]
#position_ls = [pos[x.strip('.png')] for x in filename_ls]
artist_ls = []

#for i in range(len(filename_ls)):
#    artist = gen_artist('node_img/'+img_folder+filename_ls[i], position_ls[i])
#    ax.add_artist(artist)
#    artist_ls.append(artist)
if len(artist_ls) == 0:
    artist_ls = None

#artist_ls = None
#draggable_network.DraggableNetwork(G, nodes, edges, labels, nodes0, node_size_ls, weights, node_size_radius, artist_ls, initial_key_ls)
draggable_network.DraggableNetwork(G, nodes, edges, labels, nodes0, node_size_ls, weights, node_size_radius, artist_ls, edge_list=edge_list)

