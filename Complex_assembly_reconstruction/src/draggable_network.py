import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import networkx as nx 
import threading
import time 
from tkinter import filedialog
'''
Author: Kuan-Lun Hsu 
Purpose: Create an interactive interface for drawing a network
_________________________________________________________________________
version 1.4, Date: 2022/07/19
Features:
1. Can save the current network as a figure
2. Labels switch 
3. Draggable switch
_________________________________________________________________________
version 1.3, Date: 2022/01/21
Features:
1. import external images to represent nodes (also draggable)
2. when loading previously saved node position, update the image position as well

Reference:https://moonbooks.org/Articles/How-to-insert-an-image-a-picture-or-a-photo-in-a-matplotlib-figure/
_________________________________________________________________________
version 1.2, Date: 2021/12/12
Features:
1. A new button to load previously saved node positions 
2. Pop up a filedialog for selecting folder and file
3. During loading process, the button shows 'Loading...'. After finished, it shows 'Load position'
_________________________________________________________________________
version 1.1, Date: 2021/12/10
Features:
1. Click a button to save the current node positions 
2. Pop up a filedialog for selecting a folder and naming the file
3. During saving process, the button shows 'Saving...'. After finished, it shows 'Save positions'

Reference1:https://matplotlib.org/stable/api/widgets_api.html#matplotlib.widgets.Button
Reference2:https://stackoverflow.com/questions/18602034/python-parallel-threads
_________________________________________________________________________
version 1.0, Date: 2021/07/27
Features:
1. Select a node and drag it to adjust its position
2. Drag the figure to explore the network
3. Scroll the mouse wheel to zoom in/out  

Reference1: https://stackoverflow.com/questions/52840767/pathcollection-not-iterable-creating-a-draggable-scatter-plot
Reference2: https://stackoverflow.com/questions/11551049/matplotlib-plot-zooming-with-scroll-wheel 
Reference3: https://matplotlib.org/stable/_modules/matplotlib/patches.html#FancyArrowPatch
Reference4: https://matplotlib.org/stable/_modules/matplotlib/collections.html#PathCollection
Reference5: https://matplotlib.org/stable/_modules/matplotlib/text.html#Text
Reference6: https://matplotlib.org/stable/users/event_handling.html
'''

class DraggableNetwork():

    epsilon = 30 #range size for selecting node

    def __init__(self, G, nodes, edges, labels, nodes0=None, node_size=None,
                weights=None, node_size_radius=None, artist_ls=None, initial_key_ls=None, edge_list=None):
        
        self.G = G
        self.nodes = nodes
        self.nodes0 = nodes0 
        self.node_size = node_size
        self.edges = edges 
        self.labels = labels#labels
        self.weights = weights
        self.node_size_radius=node_size_radius
        self.move_from = 0
        self._ind = None
        self.ax = nodes.axes
        self.initial_labels = {x[0]:x[1] for x in labels.items()} 
        #Add external img
        self.artist_ls = artist_ls
        self.initial_key_ls = initial_key_ls
        self.edge_list = edge_list
        #Add mark
        self.mark = plt.axes([0.8, 0.98, 0.12, 0.05])
        self.mark.axis('off')
        self.mark.annotate('DraggableNetwork v1.4', (0, 0))
        #Add button
        self.axbtn1 = plt.axes([0.2, 0.025, 0.12, 0.05])
        self.axbtn2 = plt.axes([0.35, 0.025, 0.12, 0.05])
        self.axbtn3 = plt.axes([0.5, 0.025, 0.12, 0.05])
        self.axbtn4 = plt.axes([0.65, 0.025, 0.12, 0.05])
        self.axbtn5 = plt.axes([0.83, 0.9, 0.1, 0.05])
        self.label_state = 'on'
        self.drag_state = 'Draggable'
        self.btn1 = Button(ax=self.axbtn1, label='Save positions', color='powderblue', hovercolor='tomato')
        self.btn2 = Button(ax=self.axbtn2, label='Load positions', color='powderblue', hovercolor='tomato')
        self.btn3 = Button(ax=self.axbtn3, label=f'Labels ({self.label_state})', color='powderblue', hovercolor='tomato')
        self.btn4 = Button(ax=self.axbtn4, label='Save fig.', color='powderblue', hovercolor='tomato')
        self.btn5 = Button(ax=self.axbtn5, label=f'{self.drag_state}', color='powderblue', hovercolor='powderblue')
        self.canvas = self.ax.figure.canvas
        #Connect the canvas to the mouse event and run the corresponding function if happend
        self.canvas.mpl_connect('button_press_event', self.button_press_callback)
        self.canvas.mpl_connect('button_release_event', self.button_release_callback)
        self.canvas.mpl_connect('motion_notify_event', self.motion_notify_callback)
        
        self.zoom_factory(self.ax, 0.9)
        self.button_factory(self.btn1, self.btn2, self.btn3, self.btn4, self.btn5)

        plt.show()
        

    def get_ind_under_point(self, event):   
        xy = np.asarray(self.nodes.get_offsets()) #Obtain the positions of all nodes
        xyt = self.ax.transData.transform(xy)
        xt, yt = xyt[:, 0], xyt[:, 1]

        d = np.sqrt((xt - event.x)**2 + (yt - event.y)**2)  #Calculate the distance between the click site and all nodes
        ind = d.argmin()  #Select the nearest node, return its index

        if self.node_size == None:
            if d[ind] >= self.epsilon:  #If the distance is larger than the set bound
                ind = None
        else:
            if d[ind] >= self.node_size_radius[ind]:
                ind = None

        return ind

    def button_press_callback(self, event):
        if event.inaxes is None:
            return
        if event.button != 1:
            return
        if event.x < 130 or event.y < 111: #If outside the figure
            return
        self._ind = self.get_ind_under_point(event)
        if self._ind == None:
            self.move_from = (event.x, event.y)

    def button_release_callback(self, event):
        if event.button != 1:
            return
        self._ind = None
        self.move_from = 0

    def motion_notify_callback(self, event):
        if self._ind == None and self.move_from == 0:
            return
        if event.inaxes == None:
            return
        if event.button != 1:
            return
        if self.move_from != 0:
            cur_xlim = self.ax.get_xlim()
            cur_ylim = self.ax.get_ylim()
            cur_xrange = (cur_xlim[1] - cur_xlim[0])
            cur_yrange = (cur_ylim[1] - cur_ylim[0])
            xy_factor = cur_xrange/cur_yrange
            xdata = (event.x - self.move_from[0])/300*cur_xrange # get event x location
            ydata = (event.y - self.move_from[1])/300/xy_factor*cur_xrange # get event y location
       
            self.ax.set_xlim([cur_xlim[0]-xdata,
                        cur_xlim[1]-xdata])
            self.ax.set_ylim([cur_ylim[0]-ydata,
                        cur_ylim[1]-ydata])

            self.move_from = (event.x, event.y)
            plt.draw() # force re-draw

        elif self._ind != None:
            x, y = event.xdata, event.ydata
            xy = np.asarray(self.nodes.get_offsets())

            target_pos = tuple(xy[self._ind])  #Save the selected original node position
            xy[self._ind] = np.array([x, y])   #Update node position

            for edge in self.edges:            #Update edge position if it's connected to the selected node 
                posA, posB = edge._posA_posB 
                if posA == target_pos or posB == target_pos:
                    if posA == target_pos:
                        edge.set_positions((x, y), posB)
                    else:
                        edge.set_positions(posA, (x, y))

            if self.labels != None:
                for label in self.labels.values(): #Update label position  
                    position = label.get_position()
                    if position == target_pos:
                        label.set_position((x, y))

            self.nodes.set_offsets(xy)
            if self.nodes0 != None:
                self.nodes0.set_offsets(xy)
            
            #Update external images
            if self.artist_ls != None:
                for artist in self.artist_ls:
                    if artist.xybox == target_pos:
                        artist.xybox = (x, y)

            self.canvas.draw_idle()

    def zoom_factory(self, ax, base_scale):
        def zoom_fun(event):
            # get the current x and y limits
            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()
            cur_xrange = (cur_xlim[1] - cur_xlim[0])*.5
            cur_yrange = (cur_ylim[1] - cur_ylim[0])*.5
            xdata = event.xdata # get event x location
            ydata = event.ydata # get event y location
            if event.button == 'up':
                # deal with zoom in
                scale_factor = np.log(1/base_scale)
            elif event.button == 'down':
                # deal with zoom out
                scale_factor = np.log(base_scale)
            else:
                # deal with something that should never happen
                scale_factor = 1
                print(event.button)
            # set new limits
            ax.set_xlim([cur_xlim[0] - cur_xrange*scale_factor,
                        cur_xlim[1] + cur_xrange*scale_factor])
            ax.set_ylim([cur_ylim[0] - cur_yrange*scale_factor,
                        cur_ylim[1] + cur_yrange*scale_factor])
            plt.draw() # force re-draw


        # attach the call back 
        self.canvas.mpl_connect('scroll_event', zoom_fun)

        #return the function
        return zoom_fun
    
    def button_factory(self, btn1, btn2, btn3, btn4, btn5):
        def saving_thread():
            time.sleep(0.001) #timedelay for the button to show 'Saving' 
            f = filedialog.asksaveasfile(mode='w', defaultextension=".txt")
            if f!=None:
                string = '' 
                if self.labels == None:
                    label_values = self.labels_origi.values()
                else:
                    label_values = self.labels.values()
                for i in label_values:
                    key = i.get_text()
                    x, y = i.get_position()
                    string += key+':'+str(x)+','+str(y)+'\n'
                f.write(string)
                f.close()
            self.btn1.label.set_text('Save positions')
            plt.draw()

        def load_thread():
            time.sleep(0.001) #timedelay for the button to show 'loading...' 
            f = filedialog.askopenfile(mode='r', defaultextension=".txt")
            if f!=None:
                initial_position = {}
                lines = f.readlines()
                for line in lines:
                    node, xy = line.strip().split(':')
                    x, y = xy.split(',')
                    
                    #align along wiht their y axis
                    position = self.initial_labels[node].get_position()
                    #if len(node) ==1 or node=='11' or node=='12' or node=='1112356789S':
                    if len(node) ==1:                   
                        initial_position[node] = (float(position[0]), float(position[1]))
                    else:
                        initial_position[node] = (float(x), float(position[1]))

                print(initial_position)
                f.close()
                self.ax.cla() #clear the axes

                if self.labels != None:
                    self.labels = nx.draw_networkx_labels(self.G, pos=initial_position, ax=self.ax, font_size=10, font_color='k', font_family='arial', font_weight='bold')#'sans-serif'
                self.edges = nx.draw_networkx_edges(self.G, pos=initial_position, ax=self.ax, arrowstyle='-',width=self.weights) #, arrowstyle='->',connectionstyle='arc3, rad=0.3'
                if self.nodes0 != None: 
                    self.nodes0 = nx.draw_networkx_nodes(self.G, pos=initial_position, ax=self.ax, node_size=self.node_size, node_color='w', node_shape='o', alpha=1) #(189/255, 215/255, 238/255)
                self.nodes = nx.draw_networkx_nodes(self.G, pos=initial_position, ax=self.ax, node_size=self.node_size, node_color=(189/255, 215/255, 238/255), node_shape='o', alpha=1) #linewidths=2, edgecolors='k'

                if self.artist_ls != None:
                    for i in range(len(self.artist_ls)):
                        self.artist_ls[i].xybox = initial_position[self.initial_key_ls[i]]
                        self.ax.add_artist(self.artist_ls[i])
                #plt.savefig('eif3_dag.png', dpi=300) 

            self.btn2.label.set_text('Load positions')
            plt.draw()
        
        def savefig_thread():
            time.sleep(0.001) #timedelay for the button to show 'Saving' 
            filename = filedialog.asksaveasfilename(defaultextension=".png")
            if filename!=None:
                plt.savefig(filename, dpi=300, bbox_inches = "tight")
            self.btn4.label.set_text('Save fig.')
            plt.draw()   

        def save_pos_button(event): 
            t1 = threading.Thread(name='save pos',target=saving_thread) 
            t1.start() 
            self.btn1.label.set_text('Saving...')
            plt.draw()

        def load_pos_button(event): 
            t2 = threading.Thread(name='load pos',target=load_thread) 
            t2.start() 
            self.btn2.label.set_text('Loading...')
            plt.draw()        
        
        def label_switch_button(event):
            if self.labels != None:
                self.initial_position = {}
                for i in self.labels.values():
                    node = i.get_text()
                    x, y = i.get_position()
                    self.initial_position[node] = (x, y)

            if self.label_state =='on':
                self.labels_origi = self.labels
                self.labels = None
                self.label_state = 'off'
            else:
                self.labels = self.labels_origi
                self.label_state = 'on'
            self.ax.cla() #clear the axes

            if self.labels != None:
                self.labels = nx.draw_networkx_labels(self.G, pos=self.initial_position, ax=self.ax, font_size=10, font_color='k', font_family='arial', font_weight='bold')#'sans-serif'
            self.edges = nx.draw_networkx_edges(self.G, pos=self.initial_position, ax=self.ax, arrowstyle='-',width=self.weights) #, arrowstyle='->',connectionstyle='arc3, rad=0.3'
            if self.nodes0 != None: 
                self.nodes0 = nx.draw_networkx_nodes(self.G, pos=self.initial_position, ax=self.ax, node_size=self.node_size, node_color='w', node_shape='o', alpha=1) #(189/255, 215/255, 238/255)
            self.nodes = nx.draw_networkx_nodes(self.G, pos=self.initial_position, ax=self.ax, node_size=self.node_size, node_color=(189/255, 215/255, 238/255), node_shape='o', alpha=1) #linewidths=2, edgecolors='k'
            
            self.btn3.label.set_text(f'Labels ({self.label_state})')
            plt.draw()
        
        def save_fig_button(event):
            t3 = threading.Thread(name='save fig.',target=savefig_thread) 
            t3.start() 
            self.btn4.label.set_text('Saving...')
            plt.draw()

        def drag_switch_button(event):
            if self.labels != None:
                self.initial_position = {}
                for i in self.labels.values():
                    node = i.get_text()
                    x, y = i.get_position()
                    self.initial_position[node] = (x, y)
            else: 
                self.initial_position = {}
                for i in self.labels_origi.values():
                    node = i.get_text()
                    x, y = i.get_position()
                    self.initial_position[node] = (x, y)

            if self.drag_state == 'Draggable':
                self.drag_state = 'Fixed'
                self.G = nx.Graph() 
                self.G.add_weighted_edges_from(self.edge_list)
            else:
                self.drag_state = 'Draggable'
                self.G = nx.DiGraph() 
                self.G.add_weighted_edges_from(self.edge_list)
            self.weights = [(self.G[u][v]['weight'])*0.7*1.5 for u,v in self.G.edges()]
            self.ax.cla() #clear the axes
            if self.labels != None:
                self.labels = nx.draw_networkx_labels(self.G, pos=self.initial_position, ax=self.ax, font_size=10, font_color='k', font_family='arial', font_weight='bold')#'sans-serif'
            self.edges = nx.draw_networkx_edges(self.G, pos=self.initial_position, ax=self.ax, arrowstyle='-',width=self.weights) #, arrowstyle='->',connectionstyle='arc3, rad=0.3'
            if self.nodes0 != None: 
                self.nodes0 = nx.draw_networkx_nodes(self.G, pos=self.initial_position, ax=self.ax, node_size=self.node_size, node_color='w', node_shape='o', alpha=1) #(189/255, 215/255, 238/255)
            self.nodes = nx.draw_networkx_nodes(self.G, pos=self.initial_position, ax=self.ax, node_size=self.node_size, node_color=(189/255, 215/255, 238/255), node_shape='o', alpha=1) #linewidths=2, edgecolors='k'
            self.btn5.label.set_text(f'{self.drag_state}')
            plt.draw()

        btn1.on_clicked(save_pos_button)
        btn2.on_clicked(load_pos_button)
        btn3.on_clicked(label_switch_button)
        btn4.on_clicked(save_fig_button)
        btn5.on_clicked(drag_switch_button)
    
if __name__ == '__main__':
    #Demonstration
    #Set up a network
    edge_list = [(1, 2), (2, 3), (1, 3), (2, 4), (1, 4), (1, 5), (2, 5)] 
    initial_position = {1:(-1, 3),2:(1, 1),3:(2, -3), 4:(-3, -4), 5:(0, 0)}

    #Create a network object
    G = nx.DiGraph()
    G.add_edges_from(edge_list)

    #Create matplotlib object for drawing
    fig, ax = plt.subplots(1, 1)

    labels = nx.draw_networkx_labels(G, pos=initial_position, font_size=12, font_color='k', font_family='sans-serif', font_weight='normal')
    edges = nx.draw_networkx_edges(G, pos=initial_position, ax=ax, width=2) #, arrowstyle='->',connectionstyle='arc3, rad=0.3'
    nodes = nx.draw_networkx_nodes(G, pos=initial_position, ax=ax, node_size=300, node_color=[(0.4, 0.7, 0.5) for i in range(5)], node_shape='o')

    DraggableNetwork(G, nodes, edges, labels)


