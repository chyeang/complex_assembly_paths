# Reconstruction of protein complex assembly from pairwise cooperative stabilization data


## Installation

We recommend using Python 3.7 and Jupyter Notebook to run the calculation.  Please also install the libraries listed in the requirements.txt 

- Install Python and Jupyter Notebook at Anaconda (https://www.anaconda.com/ )

- Using pip or conda to install/upgrade the required libraries

  ```bash
  $ python -m pip install --upgrade pip
  $ pip install -r requirements.txt
  ```
- Or download the following dependencies manually
	- numpy==1.19.5
	- scipy==1.4.1
	- pandas==1.2.4
	- matplotlib==3.1.0
	- networkx==2.3
	- seaborn==0.9.0

For example:

 ```bash
  $ pip install numpy==1.19.5
 ``` 

## Implementation

### Jupyter Notebook

- Once you have installed the Anaconda, you can launch the Jupyter Notebook via Anaconda-Navigator or Anaconda prompt:

  ```bash
  $ Jupyter Notebook
  ```

- Open the Main.ipynb and start to run the program.

## What's in the box?
- root
	- data 
		- LSm.csv
		- CSN.csv
	- result
		- dag_info
		- tree_info
		- tree_score
		- img
	- src
		- data_converter.py
		- generators.py
		- calculator.py
		- result_reader.py
		- network_drawer.py
		- boxplot_drawer.py
		- DAG_quantification.py
		- draggable_network.py
	- Main.py
	- requirements.txt
	- readme.md
	- DAG_drawer.py
	- Tree_drawer.py
		
> data folder contains raw data of LSm and CSN for testing in a csv file format, including stabilization values of any pairs of subunits in a corresponding complex.

> result folder all the tree scores, output images for figure, top-ranking tree information, and DAG information for drawing the final figures.

> src folder contains all the functions for simulation of all binary trees and calculation of tree scores based on pairwise cooperative stability data


## Demos

### Use jupyter notebook to open Main.ipynb

### how to use your own data
You can put your data as csv file in the data folder.
Specify:

- The name of your complex
- real names of the subunits in order 
- mono_degrad = False (True if you would like to consider monomer stability)
- cal_state = False (True if you would like to consider monomer stability)

```python
complex_name = 'LSm'
real_names = ['1', '2', '3', '6', '5', '7', '4']
sub_num = len(real_names)
mono_degrad = True
cal_state = True
subunit_ls = [i for i in string.ascii_lowercase[:sub_num]]
dict_for_convert = {subunit_ls[i]:real_names[i] for i in range(sub_num)}
dict_for_convert_re = {real_names[i]:subunit_ls[i] for i in range(sub_num)}
stablize_dict = csv_reader('data/LSm.csv', sub_num)
all_pair_dict = all_pair_generator(stablize_dict, sub_num)
subcom_dict = subcom_dict_generator(stablize_dict, sub_num)
all_structure = structure_generator(sub_num)
```
For a complex with 9 subunits, it may take ~2 mins to run the calculation (MacBook Pro 2020, M1)

```python
folder = f'result/tree_score/{complex_name}/'
files = [i for i in os.listdir(folder) if i.endswith('.txt')]
Your_favor_name = results(folder, files)
```

After the calculation, you can import and explore the result:

```python
parameters, cpu_number = parameter_assignment(all_structure, subunit_ls, all_pair_dict, 
                                            stablize_dict, subcom_dict, complex_name, mono_degrad, cal_state)
start = time.time()
try: #try using multiple CPUs to calculate
    with Pool(cpu_number) as p:
        p.starmap(calculation_func, parameters)
except:
    for para in parameters:
        calculation_func(*para)    
end = time.time()
print(f'Time for calculation: {end-start:.4f} s')
```

The result object has a built-in function for drawing the score distribution of all trees. You can set the save=True to save the figure; it will be saved as a PNG file in result/img.

```python
Your_favor_name.plot_All(save=False, complex_name=complex_name)
```
 After that, you can also draw the top-ranking trees. Adjust the 'num' to obtain a different number of top-ranking trees. In the draw_tree() function, if_save=True would save the tree information in the folder specified in the filename.

```python
num = 10
for i in LSm_cal_state.sorted_All[-num:]:
    old_string, item = i 
    ind, score = item
    structure = LSm_cal_state.structure_ls[ind]
    order = subunit_converter(old_string, dict_for_convert) 
    tree = assign_element(structure, order) 
    print(score)
    draw_tree(tree, if_save=False, filename=f'result/tree_info/LSm_top{num}.txt')
    num -= 1
```

Finally, you could draw a DAG by merging top-ranking trees to see the general features of complex assembly. You can set how many top-ranking trees and the threshold (edge frequency). Please also feed the subunit name converter, the string of the final complex, and the number of total subunits to the cutoff_gate() function. You can save the DAG information by setting the 'if_save' to True.

```python 
top_num = 100
threshold = 5
target = LSm_cal_state
convert = dict_for_convert
convert_re = dict_for_convert_re
final = '1234567'
number = sub_num 
prefix = '_lsm_'
plt.style.use(['default'])
    
edge_list = cutoff_gate(top_num, threshold, target, convert, convert_re, final, number, prefix, if_save=False)
```

Quantification of two-branched features in the complex assembly scheme.
For example, in the CSN complex, subunits 1, 3, 8, and 9 seem to be a group (assemble), and subunits 6, 7, 4, 5, and 2 seem to be another group. We quantify this feature by calculating the distance between two subunits in the DAG. 

```python 
All_subunits = [str(i) for i in range(1, 1+9)]
All_pairs = [i for i in comb(All_subunits, 2)]

nG=nx.DiGraph()
nG.add_weighted_edges_from(edge_list)
edge_dict = {(i[0], i[1]):i[2] for i in edge_list}

new_edge_list = normalize_edge(nG, edge_dict)
edge_weight_dict = {(i[0],i[1]):i[2]for i in new_edge_list} 
pairwise_distance_dict = calculate_distance(All_pairs, nG, edge_weight_dict)
```

Then, we calculate the p-value by the Kolmogorov–Smirnov test (K-S test) between inner-distance (subunits within a group) and intra-distance (subunits within different groups). 

```python 
group1 = ['6', '7', '4', '5', '2']
group2 = ['1', '3', '8', '9']

group1_intra_pairs = [i for i in All_pairs if set(i).issubset(set(group1))]
group2_intra_pairs = [i for i in All_pairs if set(i).issubset(set(group2))]
inter_pairs = [i for i in All_pairs if set(i).intersection(set(group1)) != set() and set(i).intersection(set(group2)) != set()]

group1_intra_distance = {i:pairwise_distance_dict[i] for i in group1_intra_pairs} 
group2_intra_distance = {i:pairwise_distance_dict[i] for i in group2_intra_pairs}
inter_distance = {i:pairwise_distance_dict[i] for i in inter_pairs}
intra_distance = {i:pairwise_distance_dict[i] for i in group1_intra_pairs + group2_intra_pairs} 

intra_ = list(group1_intra_distance.values()) + list(group2_intra_distance.values())
inter_ = list(inter_distance.values()) 
statistic, pvalue = stats.ks_2samp(intra_, inter_)
print(f'p-value: {pvalue}')
```

By shuffling the subunits and calculating all distances and the K-S statistics 10000 times, we can obtain a bootstrapping p-value.
The 10000 times could take ~10 minutes to run

```python
random_set_p_values = []
N = 10000
for i in range(N):
    p = generate_random_ctrl_ks(All_subunits, All_pairs, new_edge_list, group1, group2)
    random_set_p_values.append(p)

bootstrap_p = len([i for i in random_set_p_values if i <= pvalue])/N
print(f'Bootstrap p-value = {bootstrap_p}') 
```

### DAG_drawer.py

After saving the DAG information, you could use the customized module (DraggableNetwork v1.4) to draw the DAG via a GUI. We recommend using Visual Studio Code (https://code.visualstudio.com/) to edit the code.

Open the DAG_drawer.py:
You can specify the subunit order by the list 'subunits_ls' (line 114)
Read the save the DAG information by two functions: read_edge() and read_node_size(), which take a filename as an input.

```python
subunits_ls=['4', '5', '7', '6', '3', '2', '1']
real_names = ['1', '2', '3', '6', '5', '7', '4']
sub_num = len(real_names)
subunit_ls = [i for i in string.ascii_lowercase[:sub_num]]
dict_for_convert_re = {real_names[i]:subunit_ls[i] for i in range(sub_num)}
edge_list = read_edge('result/dag_info/edge_list_lsm_top100_5.txt')
node_size = read_node_size('result/dag_info/node_size_lsm_top100_5.txt')
img_folder = 'LSM/'
```
After setting these parameters, save and close the DAG_drawer.py
Use the terminal to run it.

```bash
$ python DAG_drawer.py
```
It will launch a GUI that allows you to drag the node to adjust its position, save/load the position, and save the DAG as an image. 

### Tree_drawer.py

Similarly, after saving the tree information, you could use the customized module (DraggableNetwork v1.4) to draw the tree.

Open the tree_drawer.py:
You can specify the complex_name (line 53).
Also, you could set how many top-ranking trees you would like to draw in
line 54.

```python
#Import data
complex_name = 'EMC'
for top_num in range(1, 21):
    root, edge_list = read_edge(f'result/tree_info/{complex_name}_top{top_num}.txt')
```
After setting these parameters, save and close the tree_drawer.py
Use the terminal to run it.

```bash
$ python tree_drawer.py
```
It will launch a GUI that allows you to drag the node to adjust its position, save/load the position, and save the tree as an image. 
