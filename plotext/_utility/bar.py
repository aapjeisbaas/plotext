from plotext._utility.plot import get_labels
from plotext._utility.data import linspace

##############################################
############   Bar Functions    ##############
##############################################

def update_bars(x, bars, offset): # it updates the bar coordinates using the past bar dictionary of bar name and coordinates; an offset is added to the coordinates if needed
    labelled = any([type(el) == str for el in x])
    if not labelled: # all x are numbers
        xlabels = get_labels(x, "linear")
    else:# if the bars are labelled (i.e. are strings), the coordinate of the bars are calculated taking into account the coordinates of the previous bars; if a new bar is found it is added
        xlabels = list(map(str, x)) 
        xn = [] 
        for el in xlabels:
            if el in bars:
                xn.append(bars[el])
            else:
                i = len(bars) + 1
                xn.append(i)
                bars.update({el: i})
            x = xn
    return x, xlabels, labelled, bars

def update_bar_xlim(y): # it updates the bar limits along their heights (y if orientation is vertical otherwise x)
    y = [el for el in y if el is not None]
    bar_lim = [min(y, default = None), max(y, default = None)]
    return bar_lim

def update_bar_ylim(y): # it updates the bar limits along their base dimension  (x if orientation is vertical otherwise y)
    bar_lim = update_bar_xlim(y)
    if None not in bar_lim:
        delta = (bar_lim[1] - bar_lim[0]) / 20
        bar_lim[0] = bar_lim[0] - delta if bar_lim[0] - delta > 0 else bar_lim[0]
    return bar_lim

def bars(x, y, width, minimum): # given the bars center coordinates and height, it returns the full bar coordinates
    if x == []:
        return [], []
    bins = len(x)
    bin_size_half = (max(x) - min(x)) / (bins - 1) * width / 2
    xbar, ybar = [], []
    for i in range(bins):
        xbar.append([x[i] - bin_size_half, x[i] - bin_size_half,
                     x[i] + bin_size_half, x[i] + bin_size_half,
                     x[i] - bin_size_half])
        ybar.append([minimum, y[i], y[i], minimum, minimum])
    return xbar, ybar

##############################################
###########   Hist Functions    ##############
##############################################

def hist_data(data, bins = 10): # it returns data in histogram form 
    #data = [round(el, 15) for el in data]
    if data == []:
        return [], []
    m, M = min(data), max(data)
    data = [(el - m) / (M - m) * bins if el != M else bins - 1 for el in data]
    data = [int(el) for el in data]
    histx = linspace(m, M, bins)
    histy = [0] * bins
    for el in data:
        histy[el] += 1
    return histx, histy
