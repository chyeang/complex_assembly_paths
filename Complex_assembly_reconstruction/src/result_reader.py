import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import ast

def read_result(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        dictionary = {}
        structure = ast.literal_eval(lines[0])
        dictionary['structure'] = structure
        for line in lines[1:]:
            order, score = line.split(',')
            dictionary[order] = float(score)    
    return dictionary

def sort_a(string):
    return ''.join(sorted(string)) 

#Convert the code and subunit symbol back and forth  
class results():
    
    def __init__(self, folder, files):
        
        #Read the data into dictionary and put it into a list
        grouped_by_structure = []
        for file in files:
            dictionary = read_result(folder+file)
            grouped_by_structure.append(dictionary)
        
        structure_ls = [] 
        #sort by score per structure 
        ind = 0
        for i in range(len(grouped_by_structure)):
            structure = grouped_by_structure[i]['structure']
            structure_ls.append(structure)
            grouped_by_structure[i].pop('structure')
            for key in grouped_by_structure[i].keys():
                score = grouped_by_structure[i][key]
                grouped_by_structure[i][key] = (ind, score)
            grouped_by_structure[i] = list(sorted(grouped_by_structure[i].items(), key=lambda d: d[1][1]))
            ind +=1 
        
        #Collect the highest score per structure    
        best_per_structure = []
        for i in grouped_by_structure:
            best_per_structure.append([i[-1][1][1], i[-1][1][0], i[-1][0]])
        sorted_best_per_structure = sorted(best_per_structure)
        
        #All trees 
        All = []
        for i in grouped_by_structure:
            for j in i:
                All.append(j)
        sorted_All = list(sorted(All , key=lambda d: d[1][1]))
        
        self.grouped_by_structure = grouped_by_structure
        self.sorted_best_per_structure = sorted_best_per_structure
        self.sorted_All = sorted_All
        self.structure_ls = structure_ls
    
    def plot_highest_per_structure(self, log=True):
        Highest_score_list = [i[-1][1][1] for i in self.grouped_by_structure]
        sorted_Highest_score_list = list(sorted(Highest_score_list))
        
        plt.plot(sorted_Highest_score_list, '.')
        plt.xlabel('Structures')
        plt.ylabel('Scores')
        if log == True:
            plt.yscale('log')
        plt.show()
        
    def plot_All(self, save=False, complex_name='default', tick_spacing=None):
        all_score_ls = [i[1][1] for i in self.sorted_All]

        fig, axes = plt.subplots(figsize=(6, 4))    

        for axis in ['top','bottom','left','right']:
            axes.spines[axis].set_linewidth(3)    

        axes.tick_params(axis='both', which='major', width=3)
        axes.tick_params(axis='both', which='minor', width=2)
        axes.tick_params(axis='y', which='major', length=8)
        axes.tick_params(axis='x', which='major', length=8)
        axes.tick_params(axis='both', which='minor', length=6)

        axes.set_ylabel('Score', fontsize=25)

        plt.title(complex_name)
        plt.ylabel("Score")
        plt.xlabel("Ranked Tree")
        axes.plot(range(1, len(all_score_ls)+1),all_score_ls, '.', color=(0.2, 0.5, 0.9),markersize=10) #'#1f77b4' (0.2, 0.5, 0.9)
        axes.set_yticklabels(axes.get_yticklabels(), fontsize=20)
        #axes.set_xticklabels(axes.get_xticklabels(), fontsize=25)
        #plt.plot(csn_liter_index, csn_liter_score, '.', color=(1, 0, 0), markersize=15)
        plt.yscale('log')
        if tick_spacing != None:
            axes.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

        if save==True:
            plt.savefig(f'result/img/{complex_name}_score_distribution.png', dpi=300, bbox_inches = "tight")
        plt.show()

##For PCI complex
def read_data(filename):
    
    with open(filename, 'r') as f:
        lines = f.readlines()
        dictionary = {}
        for line in lines:
            tree, score = line.split(':')
            dictionary[tree] = float(score)
    
    return dictionary

class results_PCI():
    
    def __init__(self, folder, files, convert):
        
        #Read the data into dictionary and put it into a list
        grouped_by_structure = []
        for file in files:
            dictionary = read_data(folder+file)
            grouped_by_structure.append(dictionary)
        
        #sort by score per structure 
        for i in range(len(grouped_by_structure)):
            grouped_by_structure[i] = list(sorted(grouped_by_structure[i].items(), key=lambda d: d[1]))
        
        #Convert the code into subunits
        for i in range(len(grouped_by_structure)):
            grouped_by_structure[i] = [(convert(x[0]), x[1]) for x in grouped_by_structure[i]]
        
        #Collect the highest score per structure    
        best_per_structure = []
        for i in grouped_by_structure:
            best_per_structure.append([i[-1][1], i[-1][0]])
        sorted_best_per_structure = sorted(best_per_structure)
        
        #All trees 
        All = []
        for i in grouped_by_structure:
            for j in i:
                All.append(j)
        sorted_All = list(sorted(All , key=lambda d: d[1]))
        
        self.grouped_by_structure = grouped_by_structure
        self.sorted_best_per_structure = sorted_best_per_structure
        self.sorted_All = sorted_All
    
    def plot_highest_per_structure(self, log=True):
        Highest_score_dist = [i[-1][1] for i in self.grouped_by_structure]
        sorted_Highest_score_dist = list(sorted(Highest_score_dist))
        
        plt.plot(sorted_Highest_score_dist, '.')
        plt.xlabel('Structures')
        plt.ylabel('Scores')
        if log == True:
            plt.yscale('log')
        plt.show()
        
    def plot_All(self, save=False, complex_name='default', tick_spacing=None):
        all_score_ls = [i[1] for i in self.sorted_All]
        fig, axes = plt.subplots(figsize=(6, 4))    

        for axis in ['top','bottom','left','right']:
            axes.spines[axis].set_linewidth(3)    

        axes.tick_params(axis='both', which='major', width=3)
        axes.tick_params(axis='both', which='minor', width=2)
        axes.tick_params(axis='y', which='major', length=8)
        axes.tick_params(axis='x', which='major', length=8)
        axes.tick_params(axis='both', which='minor', length=6)

        axes.set_ylabel('Score', fontsize=25)

        plt.title(complex_name)
        plt.ylabel("Score")
        plt.xlabel("Ranked Tree")
        axes.plot(range(1, len(all_score_ls)+1),all_score_ls, '.', color=(0.2, 0.5, 0.9),markersize=10) #'#1f77b4' (0.2, 0.5, 0.9)
        axes.set_yticklabels(axes.get_yticklabels(), fontsize=20)
        #axes.set_xticklabels(axes.get_xticklabels(), fontsize=25)
        #plt.plot(csn_liter_index, csn_liter_score, '.', color=(1, 0, 0), markersize=15)
        plt.yscale('log')
        if tick_spacing != None:
            axes.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

        if save==True:
            plt.savefig(f'result/img/{complex_name}_score_distribution.png', dpi=300, bbox_inches = "tight")
        plt.show()

def plot_All(all_score_ls, save=False, complex_name='default', tick_spacing=None):
    fig, axes = plt.subplots(figsize=(6, 4))    

    for axis in ['top','bottom','left','right']:
        axes.spines[axis].set_linewidth(3)    

    axes.tick_params(axis='both', which='major', width=3)
    axes.tick_params(axis='both', which='minor', width=2)
    axes.tick_params(axis='y', which='major', length=8)
    axes.tick_params(axis='x', which='major', length=8)
    axes.tick_params(axis='both', which='minor', length=6)

    axes.set_ylabel('Score', fontsize=25)

    plt.title(complex_name)
    plt.ylabel("Score")
    plt.xlabel("Ranked Tree")
    axes.plot(range(1, len(all_score_ls)+1),all_score_ls, '.', color=(0.2, 0.5, 0.9),markersize=10) #'#1f77b4' (0.2, 0.5, 0.9)
    axes.set_yticklabels(axes.get_yticklabels(), fontsize=20)
    #axes.set_xticklabels(axes.get_xticklabels(), fontsize=25)
    #plt.plot(csn_liter_index, csn_liter_score, '.', color=(1, 0, 0), markersize=15)
    plt.yscale('log')
    if tick_spacing != None:
        axes.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))

    if save==True:
        plt.savefig(f'result/img/{complex_name}_score_distribution.png', dpi=300, bbox_inches = "tight")
    plt.show()

def read_data_freq(freq_dict_ls, code_ls, files, path="result/tree_score/EIF3_enumeration/"):

    for i in range(len(files)):
        filename = files[i]
        file = path + filename

        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('>'):
                    index = int(line.strip()[4:])
                    target_dict = freq_dict_ls[index]
                    n = 0
                else:
                    target_dict[code_ls[n]] += int(line.strip())
                    n += 1
    return freq_dict_ls