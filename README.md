# complex_assembly_paths
source codes for "Altered Assembly Paths Mitigate Interference among Paralogous Complexes"
Source codes, example data and README files for the software programs in the paper "Altered Assembly Paths Mitigate Interference among Paralogous Complexes" by Yeh et al.


## Complex assembly reconstruction

This program can reconstruct and score all possible complex assembly paths represented as binary trees based on pairwise stability examination experient of all subunits in a complex.
We also provide tools for visualizing the results and conducting statistical tests of the assembly features.

- data
        - CSN.csv
        - LSm.csv
- result
        - dag_info
        - img
        - tree_info 
        - tree_score
- src
        - box_plot_drawer.py
        - calculator.py
        - DAG_quantification.py
        - data_converter.py
        - draggable_network.py
        - generators.py
        - network_drawer.py
        - result_reader.py
- requirements.txt
- DAG_drawer.py
- Tree_drawer.py
- README.md
- MIT License.txt
- Main.ipynb

README.md provides detailed documentation of how to install and some demos by using the testing dataset in the data folder.

Main.ipynb is an interactive jupyter notebook demonstrating all the functions in this module.
 
         
## Model fitting to FACS data

This program can perform model fitting to obtain the cooperative stability between two proteins. In addition, 
data processing and data visualization are also included.

- data
        - GPS_HUS1_RAD1_for_testing.txt
        - GPS_RAD1_HUS1_for_testing.txt
- requirements.txt
- README.md
- MIT License.txt
- Main.ipynb

README.md provides detailed documentation of how to install and some demos by using the testing dataset in the data folder.

Main.ipynb is an interactive jupyter notebook demonstrating all the functions in this module.

## General information 

We recommend using Python 3.7 or later and jupyter notebook to explore the program's functions. The running time of the program using the testing data set is typically within 2 mins, at most 10 mins. 

- Testing environment:
        - Device: MacBook Pro 2020 (M1, 16GB RAM)
        - OS: macOS Big Sur, version 11.7.10
        - Software: Python 3.8
(END)
