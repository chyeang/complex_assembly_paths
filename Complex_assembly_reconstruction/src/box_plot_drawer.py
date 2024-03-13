import numpy as np 
from matplotlib import pyplot as plt
from bisect import bisect_left

class color_codes:
    lst1 = [(1, 0.6, 0.6), (237/255, 125/255, 49/255), (255/255, 192/255, 0/255), (146/255, 208/255, 80/255), (68/255, 114/255, 196/255)]
    lst1.reverse()
    lst2 = ['#9CBAD7', '#F7C29A', '#A8CE9E', '#E29C98', '#C6B4DB']
    lst3 = ['#9CBAD7', '#A8CE9E', '#FFF3A6', '#F7C29A', (1, 0.5, 0.5)]

def return_bins_index(myList, myNumber):
    """
    Assumes myList is sorted. Returns the closest smaller value to myNumber.
    
    """
    pos = bisect_left(myList, myNumber)
    length = len(myList)
    
    if pos==length:
        return pos - 1 
    else:
        after = myList[pos]
        if myNumber == after:
            return pos
        elif myNumber < after:
            return pos - 1

def cal_cumulative(ls):
    cumulative = [] 
    m = 0 
    for i in ls:
        m+=i
        cumulative.append(m)
    return cumulative

def cal_stats(ls, bins, log=True):
    
    cumulative = cal_cumulative(ls)
    total = cumulative[-1]
    
    if log == True:
        median = np.log(bins[return_bins_index(cumulative, total/2)+1]) 
        Q1 = np.log(bins[return_bins_index(cumulative, total/4)+1])
        Q3 = np.log(bins[return_bins_index(cumulative, total/4*3)+1]) 
        IQR = Q3 - Q1 
        lower_bound = Q1 - 1.5*IQR
        upper_bound = Q3 + 1.5*IQR
        lower_bound_ind = return_bins_index(bins, np.e**(lower_bound)) -1 
        upper_bound_ind = return_bins_index(bins, np.e**(upper_bound)) -1 
        n = 0
        while n == 0:
            n = ls[lower_bound_ind-1]
            lower_bound_ind += 1 
        n = 0
        while n == 0:
            n = ls[upper_bound_ind-1]
            upper_bound_ind -= 1             
            
        lower_whisker_ind = lower_bound_ind + 1
        upper_whisker_ind = upper_bound_ind + 1
        
        lower_whisker = np.log(bins[lower_whisker_ind])
        upper_whisker = np.log(bins[upper_whisker_ind]) 
        
        lower_outlier = [] 
        for i in range(len(bins[:lower_whisker_ind])):
            if ls[i]>=total*0.0000002:#0.000000229
                lower_outlier.append(bins[i]) 
        upper_outlier = []
        for i in range(len(bins[upper_whisker_ind+1:])): 
            if ls[upper_whisker_ind+i]>=total*0.0000002: #0.000000404
                upper_outlier.append(bins[upper_whisker_ind+i])
        outlier = lower_outlier + upper_outlier 
    else:
        median = bins[return_bins_index(cumulative, total/2)+1]
        Q1 = bins[return_bins_index(cumulative, total/4)+1]
        Q3 = bins[return_bins_index(cumulative, total/4*3)+1]
        IQR = Q3 - Q1 
        lower_bound = Q1 - 1.5*IQR
        upper_bound = Q3 + 1.5*IQR
        lower_bound_ind = return_bins_index(bins, lower_bound) -1 
        upper_bound_ind = return_bins_index(bins, upper_bound) -1 
        n = 0
        while n == 0:
            n = ls[lower_bound_ind-1]
            lower_bound_ind += 1 
        n = 0
        while n == 0:
            n = ls[upper_bound_ind-1]
            upper_bound_ind -= 1             
            
        lower_whisker_ind = lower_bound_ind + 1
        upper_whisker_ind = upper_bound_ind + 1
        
        lower_whisker = bins[lower_whisker_ind]
        upper_whisker = bins[upper_whisker_ind]
    return median, Q1, Q3, lower_whisker, upper_whisker, outlier

def draw_boxplot(data_ls, bins, xticklabels, save=False):
    lw = 3
    plt.style.use(['default'])

    data_stats_ls = [np.e**np.array(cal_stats(i, bins)[:-1]) for i in data_ls]
    outlier_ls = [np.array(cal_stats(i, bins)[-1]) for i in data_ls]
    data_title_ls = ['None', 'One', 'Two', 'Three', 'All']

    all_stats_ls = []
    for i in range(len(data_ls)):
        stats = [{
            "label": data_title_ls[i],  # not required
            "med": data_stats_ls[i][0],
            "q1": data_stats_ls[i][1],
            "q3": data_stats_ls[i][2],
            # "cilo": 5.3 # not required
            # "cihi": 5.7 # not required
            "whislo": data_stats_ls[i][3],  # required
            "whishi": data_stats_ls[i][4],  # required
            "fliers": outlier_ls[i]  # required if showfliers=True
            }]
        all_stats_ls.append(stats)

    fs = 13  # fontsize
    positions = [[0.5], [1], [1.5], [2], [2.5]]

    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(10, 6), sharey=True)

    for i in range(len(data_ls)):
        axes.bxp(all_stats_ls[i], positions=positions[i], widths=0.25,
                vert=True, patch_artist=True,
                boxprops=dict(facecolor=color_codes.lst1[i], linewidth=lw), #sns.color_palette()[i]
                medianprops=dict(color='Black', linewidth=lw, solid_capstyle="butt"),
                flierprops=dict(marker='o', markersize=6, markeredgewidth=0.7),
                whiskerprops=dict(linewidth=lw, linestyle='-'),
                capprops=dict(linewidth=lw))

    for axis in ['top','bottom','left','right']:
        axes.spines[axis].set_linewidth(3)    

    axes.tick_params(axis='both', which='major', width=5)
    axes.tick_params(axis='both', which='minor', width=3.3)
    axes.tick_params(axis='y', which='major', length=13)
    axes.tick_params(axis='x', which='major', length=13)
    axes.tick_params(axis='both', which='minor', length=10)
    axes.set_xticklabels(xticklabels, fontsize=25)

    #axes.set_title('The score distribution of \nassembly trees containing different number of modules', fontsize=fs)
    axes.set_yticklabels(axes.get_yticklabels(), fontsize=25)
    axes.set_yscale('log')
    axes.set_ylabel('Score', fontsize=25)
    plt.xlim(0.25, 2.75)
    if save == True:
        plt.savefig('result/img/boxplot.png', dpi=300)
    plt.show()

