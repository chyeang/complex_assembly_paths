import networkx as nx 
import src.draggable_network as draggable_network
import matplotlib.pyplot as plt
import random

def read_edge(filename):
    edge_list = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith('>'):
                root = line.strip().strip('>') 
            else:
                edge = line.strip().split(',')
                edge_list.append((edge[0], edge[1]))
    return root, edge_list

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
            nextx = xcenter -width/6- dx/1.2 
            for child in children:
                nextx += 0.72*dx
                pos = _hierarchy_pos(G,child, width = dx, vert_gap = vert_gap, 
                                    vert_loc = vert_loc-vert_gap, xcenter=nextx,
                                    pos=pos, parent = root)
        return pos

    return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)

#Import data
complex_name = 'LSm'
for top_num in range(1, 5):
    root, edge_list = read_edge(f'result/tree_info/{complex_name}_top{top_num}.txt')

    #Create a network object
    G = nx.DiGraph()
    G.add_edges_from(edge_list)
    G_for_pos = nx.Graph()
    G_for_pos.add_edges_from(edge_list)
    pos = hierarchy_pos(G_for_pos, root)

    label_pos = {}
    for key in pos.keys():
        label_pos[key] = (pos[key][0], pos[key][1]-0.1)

    #Create matplotlib object for drawing
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    labels = nx.draw_networkx_labels(G, pos=pos, font_size=45, font_color='k', font_family='arial', font_weight='bold')
    edges = nx.draw_networkx_edges(G, pos=pos, ax=ax, arrowstyle='-', width=4) #, arrowstyle='->',connectionstyle='arc3, rad=0.3'
    nodes0 = nx.draw_networkx_nodes(G, pos=pos, ax=ax, node_color='w', node_shape='o', alpha=1)
    nodes = nx.draw_networkx_nodes(G, pos=pos, node_size=3000, ax=ax, node_color='w', node_shape='o', alpha=1) #(189/255, 215/255, 238/255)

    draggable_network.DraggableNetwork(G, nodes, edges, labels, nodes0, weights=4)

