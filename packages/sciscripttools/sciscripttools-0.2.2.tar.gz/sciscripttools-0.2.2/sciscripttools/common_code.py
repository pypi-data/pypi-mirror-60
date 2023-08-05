# Common Plotting Code

# module of functions which are common across some or all figure scripts

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import rc
import json
import os

from matplotlib.ticker import ScalarFormatter, FormatStrFormatter

# target options:
TARGET_report = "report"
TARGET_article = "article"
TARGET_slide = "slide"

# parameters
# could have a section which acts like a params, can the scripts read in from here
TARGET_default = TARGET_report

# Script Preamble --------------------------------------------------------------

# need something like this at start of plotting script
'''
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import json
import sys

# display plot options
matplotlib.use('Agg') # to not display (when running script in terminal)
#%matplotlib inline

# include common plotting code
sys.path += ['/root/punitpatel/repositories/thesis/assets/']
import common_code

# options
target = common_code.TARGET_default

# setup standard font
# this to update the font size for plots so there is no need to run plotting stuff twice
fig, ax = plt.subplots(1,1)
common_code.standard_font(target)
plt.close()
'''

# generic start
'''
# load data
a = common_code.load_data("example_a.json") 
b = common_code.load_data("example_b.json")

# process data

# figure
fig, axf = plt.subplots(1, 1)
sf = common_code.standard_figure(fig, axf, target)
# ax1, ax2 = axf # separate axf out for multiple subplots

# plot here

# axes labels
label = "Separation" ; unit = "\\angstrom"
sf.xlabel(ax, label, unit)
label = "Energy" ; unit = "\\electronvolt"
sf.ylabel(ax, label, unit)

sf.standard_legend()
fig.savefig("example.pdf")

print("script end")
'''

# Default Font Sizes ------------------------------------------------------------

# Latex Font Sizes
# https://tex.stackexchange.com/questions/24599/what-point-pt-font-size-are-large-etc
# These are for 12pt documents i.e. \documentclass[12pt]{article}
FONT_small = 10.95
FONT_normal = 12
FONT_Huge = 24.88

FONT_slide = 30 # not a latex size, custom size


# Default Figure Measurements --------------------------------------------------

# report
# using theses margins as in a main.tex
#\documentclass[12pt,a4paper]{report}
#\usepackage[left=4.25cm, right=3.10cm, top=3.5cm, bottom=3.5cm, textwidth=5.25in]{geometry}

# measure with https://tex.stackexchange.com/questions/39383/determine-text-width
# gives a measure of \textwidth at 5.37506 inches or 13.64806 cm
# figure width of 5.315 inches, 13.5001cm, leaves 0.14796 cm or 0.74 mm on each side
# thus should never be squashed to be fitted in 

FIG_WIDTH_report = 5.315        # inches 
FIG_RATIO_report = 3.0/2.0      # default matplotlib ratio
FIG_HEIGHT_report = FIG_WIDTH_report / FIG_RATIO_report
FIG_HEIGHT_report_small_percentage = 0.75 # standard size for small plots

FIG_adjust_bottom_default = 0.15 # adjust bottom to give space for label

FIG_adjust_subplot_label = -0.225 # default of -0.225 chosen since it looks nice with above values
FIG_adjust_left = 0.15 # even up the padding to better match right side # 0.15 looks decent, tested a few
FIG_adjust_bottom = 0.2 # brings subplot label into view # 0.2 looks decent
FIG_adjust_subplot_wspace = 0.05
FIG_adjust_subplot_hspace = 0.075

FIG_schematic_adjust_bottom_no_ticks = 0.13 
# this matches the label position of plots with ticks
# so the effective plot area is bigger on these plots

FIG_adjust_subplot_label_right_x = 0.56
FIG_adjust_subplot_label_right_y = 0.5

# I/O --------------------------------------------------------------------------

# done
# this can go into the python sciscripttools, if its more than just these functions
def load_data(filename):
    """
    Load a data file
    """
    v = json.load(open(filename))['v']
    return v

def load_datas(filenames):
    """
    Load multiple data files
    """
    vs = np.zeros(len(filenames))
    for i in range(0, len(filenames)):
        vs[i] = load_data(filenames[i])

    return vs

def save_data(filename, data):

    d = {'v':  data.tolist()}
    fn = [filename, ".json"]
    fn = "".join(fn)
    with open(fn, 'w') as outfile:
        json.dump(d, outfile)

    return 0

def find_files(prefix = "", suffix = ""):
    """
    Find files of a given prefix and/or suffix.
    ### Arguments
    `prefix=""` : start of the filename
    ### Optional Arguments
    `suffix=""` : end of the filename, eg file format
    """

    with_path = False # flag for whether prefix came with a path or not
    path = os.path.dirname(prefix)
    if path != "":
        with_path = True
    elif path == "":
        path = os.getcwd()

    prefix = os.path.basename(prefix)
    list = np.array(os.listdir(path))
    inds_b = np.array([], dtype=int)

    if prefix == "" and suffix == "":
        print("Need to provide at least a prefix or suffix")
        return -1

    for i in range(0, len(list)):
        item = list[i]

        if prefix != "" and suffix != "":
            b = item.startswith(prefix) * item.endswith(suffix)
        elif prefix != "":
            b = item.startswith(prefix)
        elif suffix != "":
            b = item.endswith(suffix)

        if b == True:
            inds_b = np.append(inds_b, i)

    filenames = list[inds_b]

    # joinpath() will actually ignore if path == "", keep if for logically reasoning and large lists
    if with_path == True:
        filenames = [(os.path.join(path, filenames[i])) for i in range(0,len(filenames))]

    return filenames

def sort_files_r(filenames, prefix, suffix):
    """
    Sort filenames with repsect to the r values in the filename
    `preffix` and `suffix` should remove the extra characters around the
    filename, and be left with an integer for the radius
    """
    l = filenames.copy()
    n = np.zeros(len(l))
    for i in range(0, len(l)):
        l[i] = l[i].split(prefix)[1]
        l[i] = l[i].split(suffix)[0]
        n[i] = int(l[i])

    inds = np.argsort(n)
    return filenames[inds]


# Process Data -----------------------------------------------------------------

def order_dict_keys(dict):
    """
    For dictionaries with numbers as keys.
    Sort them into numerical order.
    Return as a list of strings
    """

    dk = np.array(list(dict.keys()))
    dk_f = np.sort(dk.astype(np.float))
    dk_s = dk_f.astype(np.str)

    return dk_s


def relative_location_2D_indices(a, b, x, y):
    """
    Returns indices of the points (x,y), above and below 
    a line defined by a and b
    """
    is_above = lambda p,a,b: np.cross(p - a, b - a) < 0
    
    a = np.array(a)
    b = np.array(b)
    
    d = np.column_stack((x, y))
    v = is_above(d, a, b)
    
    pos = np.arange(0, len(d), 1)[v == True]
    neg = np.arange(0, len(d), 1)[v == False]
    
    return pos, neg


# Statistics -------------------------------------------------------------------

def midpoint_index(d):
    """
    Return the middle index of the array.
    Default to the lower value if array is of even length
    """
    n = len(d)
    if n % 2 != 0: # is odd
        ind = int(n/2)+1 
        parity = True

    if n % 2 == 0: # is even
        ind = int(n/2)
        parity = False
        # by default reuturns the lower index

    ind -= 1 # 0 based indices
    
    return ind, parity

def midpoint_via_index(d):
    """
    Calculate the midpoint of the array based on the index
    Return the mid value if given an odd length array.
    Compute the mid value, using the values either side, if given an even length array.
    """
    ind, parity = midpoint_index(d)
    if parity == True: # ie odd
        mp = d[ind]
    if parity == False: # ie even
        mp = 0.5*(d[ind] + d[ind+1])
    
    return mp

"""
`binned_sample_constant(data, bin_width, num_bin_samples)`
Bin `data` array into bins of width `bin_width`. Sample a constant `num_bin_samples` number of points from each bin.
Returns, `sample_inds`, array of indices of original `data` array.
### Arguments
- `data` : array of single numbers
- `bin_width` : bin width
- `num_bin_samples` : number of points per bin to sample
"""
def binned_sample_constant(data, bin_width, num_bin_samples):

    num_bin_samples_arg = num_bin_samples # store original number
    sample_inds = np.array([], dtype=int) # indices of a sample of the data array

    # fit histogram to data array
    h, h_edge = np.histogram(data, int((np.max(data) - np.min(data)) / bin_width))

    for i in range(2, len(h_edge)):

        inds = np.array([], dtype=int)

        # find indices of points in a particular bin in data array
        bin_inds = np.where(((data >= h_edge[i-1]) & (data < h_edge[i])) == True)[0]

        # if not enough points in bin use all points
        if len(bin_inds) <= num_bin_samples:
            num_bin_samples = len(bin_inds)
            inds = np.indices((1, num_bin_samples))[1]

        # if enough points in bin
        elif len(bin_inds) > num_bin_samples:
            # select random points in the array
            inds = np.unique(np.random.choice(np.indices((1, len(bin_inds)))[1][0], num_bin_samples))

            # len(bin_inds) roughly equal to num_bin_samples
            # so likely not enough unique random points
            if len(inds) < num_bin_samples:
                # select almost evenly distributed (along array) points in the bin
                inds = np.asarray(np.linspace(1, len(bin_inds), num_bin_samples), dtype=int) - 1
            # statement above may produce more numbers than num_bin_samples
            # so ensure correct len of num_bin_samples
            inds = inds[0:num_bin_samples]
        bin_sample = bin_inds[inds] # select sample from bin
        sample_inds = np.append(sample_inds, bin_sample) # concatenate bin samples
        num_bin_samples = num_bin_samples_arg # reset to original number of points to sample per bin

    return sample_inds

# Plot
# done
class FixedOrderFormatter(ScalarFormatter):
    """
    Formats axis ticks using scientific notation with a constant order of 
    magnitude
    
    E.g. usage:
    ax.yaxis.set_major_formatter(FixedOrderFormatter(-2)) # displays as 10^(-2)
    """
    def __init__(self, order_of_mag=0, useOffset=True, useMathText=False):
        self._order_of_mag = order_of_mag
        ScalarFormatter.__init__(self, useOffset=useOffset, 
                                 useMathText=useMathText)
    def _set_orderOfMagnitude(self, range):
        """Over-riding this to avoid having orderOfMagnitude reset elsewhere"""
        self.orderOfMagnitude = self._order_of_mag    

# Standard Plots ---------------------------------------------------------------

class standard_font:

    def __init__(self, target):

        self.font_size = None # default

        self.target = target
        if self.target == TARGET_report:
            self.font_size = FONT_small
        elif self.target == TARGET_article:
            self.font_size = FONT_normal
        elif self.target == TARGET_slide:
            self.font_size = FONT_slide
        else:
            print("Invalid target: defaulting to FONT_normal {}pt".format(FONT_normal))
            self.font_size = FONT_normal # default
        
        # standardise plots
        self.set_font()
        self.default_font()

    def set_font(self):

        rc('text', usetex=True)
        plt.rcParams['text.latex.preamble']=[r"\usepackage{amsmath} \usepackage{siunitx} \usepackage{bm}"] 
        # amsmath # maths package
        # siunitx     # si units
        # bm           # maths bold symbols

        rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
        ## for Palatino and other serif fonts use:
        #rc('font',**{'family':'serif','serif':['Palatino']})
        rc('font', family='serif')   
        return 0

    def default_font(self):

        rc('font', size=self.font_size)          # controls default text sizes
        rc('axes', titlesize=self.font_size)     # fontsize of the axes title
        rc('axes', labelsize=self.font_size)    # fontsize of the x and y labels
        rc('xtick', labelsize=self.font_size)    # fontsize of the tick labels
        rc('ytick', labelsize=self.font_size)    # fontsize of the tick labels
        rc('legend', fontsize=self.font_size)    # legend fontsize
        rc('figure', titlesize=self.font_size)  # fontsize of the figure title
        return 0

class standard_figure:

    def __init__(self, fig, axes, target):

        self.fig = fig
        self.axes = axes
        self.target = target

        # if its only one axis, put into array
        try:
            len(axes)
        except:
            self.axes = [axes]
        
        self.standard_size()
        self.standard_axes_ticks()
        
    def standard_size(self):

        if self.target == TARGET_report:
            self.fig.set_size_inches([FIG_WIDTH_report, FIG_HEIGHT_report])

            # even up the padding to better match right side
            self.fig.subplots_adjust(left=FIG_adjust_left, 
                                                    bottom = FIG_adjust_bottom_default) 
        #if target == TARGET_article :  
        #if target == TARGET_slide:
        return 0

    def standard_axes_ticks(self):
        "Standardise axis ticks"
        for i in range(0, len(self.axes)):
            ax = self.axes[i]
            ax.minorticks_on()
            ax.tick_params(direction = 'in', which = 'both', 
                                        bottom = True, top = True, left = True, right = True)
        return

    def argument_axes(self, axes):

        # default for other functions should be 'axes = None'
        # default to all axes if none
        if axes == None:
            axes = self.axes
        # if only one given, put it into an array
        else:
            try: 
                len(axes)
            except:
                axes = [axes]
        
        return axes

    def standard_legend(self, axes = None, title=None, loc = 1, ncol = 1,
                                            columnspacing = None):

        axes = self.argument_axes(axes)
        for ax in axes:
            ax.legend(title=title, loc = loc, ncol = ncol, handlelength=1,
                                columnspacing = columnspacing)
        return 0

    def add_subplot_labels(self, axes = None, adjust=FIG_adjust_subplot_label, 
                                                fig_adjust_bottom = FIG_adjust_bottom):

        axes = self.argument_axes(axes)

        # defaults chosen as it works well with default values
        alphabet = ["a", "b", "c", "d", "e", "f"]
        for i in range(0, len(axes)):
            ax = axes[i]
            letter = alphabet[i]
            x_label_px, _ = ax.xaxis.get_label().get_position()
            ax.text(x_label_px, adjust,'({})'.format(letter), 
                            horizontalalignment='center',
                            verticalalignment='center',
                            transform = ax.transAxes)

        # adjust figure to make visual the subcaptions
        self.fig.subplots_adjust(bottom=fig_adjust_bottom)

        return 0

    def add_subplot_labels_right(self, adjust_x=FIG_adjust_subplot_label_right_x, 
                                                adjust_y = FIG_adjust_bottom):
        # defaults chosen as it works well with default values
        alphabet = ["a", "b", "c", "d", "e", "f"]
        for i in range(0, len(self.axes )):
            ax = self.axes[i]
            x_label_px, x_label_py  = ax.xaxis.get_label().get_position()
            ax.text(x_label_px + adjust_x, 
                        x_label_py + FIG_adjust_subplot_label_right_y, 
                        '({})'.format(alphabet[i]), 
                        horizontalalignment='center',
                        verticalalignment='center',
                        transform = ax.transAxes)

        return 0

    def reduce_axes_clutter(self, axes=None, axis_xy =  ["x", "y"], nticks = False, order = False):

        axes = self.argument_axes(axes)

        if axis_xy == "x":
            axis_xy = ["x"]
        elif axis_xy == "y":
            axis_xy = ["y"]

        for ax in axes:
            for xy in axis_xy:
                if nticks != False:
                    ax.locator_params(axis=xy, nbins=nticks)

                if order != False:
                    print("Warning: changing the scale order found to not work in scripts, check plot. Does work in a notebook!")
                    print("Using function reduce_axes_clutter() with order argument")
                    if xy == "x":
                        ax.xaxis.set_major_formatter(FixedOrderFormatter(order))
                    if xy == "y": 
                        ax.yaxis.set_major_formatter(FixedOrderFormatter(order))

        return 0        

    def standard_size_adjust(self, height_percentage = 1.0,
                                                    fig_adjust_bottom = FIG_adjust_bottom):

        if self.target == TARGET_report:
            w, h = self.fig.get_size_inches()
            self.fig.set_size_inches([w, h * height_percentage])

        self.fig.subplots_adjust(left=FIG_adjust_left) 
        self.fig.subplots_adjust(bottom=fig_adjust_bottom)        

        return

    # x and y labels -------------------
    def latex_unit(self, unit):
        
        # if no unit given, return empty string
        if unit == None:
            return ""
        # otherwise return unit string
        return "$\\left[ \\si{" + unit + "} \\right]$"

    def xlabel(self, ax, xlabel, xunit = None):
        ax.set_xlabel("{} {}".format(xlabel, self.latex_unit(xunit)))
        return 0

    def ylabel(self, ax, ylabel, yunit = None):
        ax.set_ylabel("{} {}".format(ylabel, self.latex_unit(yunit)))
        return 0

    def xylabel(self, ax, xlabel, xunit, ylabel, yunit):
        self.xlabel(self, ax, xlabel, xunit)
        self.ylabel(self, ax, ylabel, yunit)
        return 0

    # could use self.axes here to run over multiple axes
    def remove_ticks(self, ax):
        """
        removing the axis ticks
        """
        ax.set_xticks([]) # labels
        ax.set_yticks([])
        ax.xaxis.set_ticks_position('none') # tick markers
        ax.yaxis.set_ticks_position('none')
        return 0
        
    # could use self here to run over multiple axes
    def remove_axes(self, ax):
        """
        removing the default axis on all sides
        """
        for side in ['bottom','right','top','left']:
            ax.spines[side].set_visible(False)

        return 0

    # could use self.axes here to run over multiple axes
    def schematic_arrow_axis(self, ax, xaxis = True, yaxis = True,
                                                        xwidth = 0.001, ywidth = 0.001,
                                                        remove_defaults = True,
                                                        set_yaxis_zero = None):
    
        # width default from matplotlib is 0.001
        # https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.arrow.html

        # set_yaxis_zero: moves the x axis

        if remove_defaults == True:
            self.remove_ticks(ax)
            self.remove_axes(ax)

        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()

        # get width and height of axes object to compute
        # matching arrowhead length and width
        dps = self.fig.dpi_scale_trans.inverted()
        bbox = ax.get_window_extent().transformed(dps)
        width, height = bbox.width, bbox.height

        # manual arrowhead width and length
        hw = 1./70.*(ymax-ymin)
        hl = 1./140.*(xmax-xmin)
        lw = 0.5 # axis line width

        # compute matching arrowhead length and width
        yhw = hw/(ymax-ymin)*(xmax-xmin)* height/width
        yhl = hl/(xmax-xmin)*(ymax-ymin)* width/height

        # draw x and y axis
        if xaxis == True:

            if set_yaxis_zero == None:
                yzero = ymin
            else:
                yzero = set_yaxis_zero

            ax.arrow(xmin, yzero, xmax-xmin, 0.0, fc='k', ec='k', lw = lw,
                    head_width=hw, head_length=hl, width = xwidth,
                    length_includes_head= True, clip_on = False)

        if yaxis == True:
            ax.arrow(xmin, ymin, 0., ymax-ymin, fc='k', ec='k', lw = lw,
                    head_width=yhw, head_length=yhl, width = ywidth,
                    length_includes_head= True, clip_on = False)
        
        return 0

    # single text in the sense that only ticks or only x label
    def schematic_subplots_adjust_single_text(self, 
                                                bottom = FIG_schematic_adjust_bottom_no_ticks):
            self.fig.subplots_adjust(bottom = bottom)
            return 0 


    def schematic_log_arrow_axis(self, ax, xaxis = True, yaxis = True,
                                            xwidth = 0.001, ywidth = 0.001,
                                            remove_defaults = True,
                                            set_yaxis_zero = None):
        """
        Draw schematic arrow axes for log plots
        """
        # width default from matplotlib is 0.001
        # https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.arrow.html

        # set_yaxis_zero: moves the x axis

        if remove_defaults == True:
            self.remove_ticks(ax)
            self.remove_axes(ax)

        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()

        # functions fx and fy take log-scale coordinates to 'axes' coordinates
        def fx(x):
            return (np.log(x) - np.log(xmin))/(np.log(xmax) - np.log(xmin))
        def fy(y):
            return (np.log(y) - np.log(ymin))/(np.log(ymax) - np.log(ymin))
        
        lw = 0.5 # axis line width

        # draw x and y axis
        if xaxis == True:

            if set_yaxis_zero == None:
                yzero = ymin
            else:
                yzero = set_yaxis_zero

            x0 = fx(xmin)
            y0 = fy(ymin)
            x1 = fx(xmax) - fx(xmin)
            y1 = fy(ymin) - fy(ymin)
            
            head_width = 0.015
            head_length = 0.006
            
            ax.arrow(x0, y0, x1, y1, # input transformed arrow coordinates 
                        transform = ax.transAxes, # tell matplotlib to use axes coordinates   
                        facecolor = 'black', ec='k', lw = lw,
                        head_width=head_width, head_length=head_length, width = xwidth,
                        length_includes_head= True, clip_on = False)
                
        if yaxis == True:
            x0 = fx(xmin)
            y0 = fy(ymin)
            x1 = fx(xmax) - fx(xmax)
            y1 = fy(ymax) - fy(ymin)
            
            head_width = 0.0060 
            head_length = 0.015
            
            ax.arrow(x0, y0, x1, y1, # input transformed arrow coordinates 
                        transform = ax.transAxes, # tell matplotlib to use axes coordinates   
                        facecolor = 'black', ec='k', lw = lw,
                        head_width=head_width, head_length=head_length, width = ywidth,
                        length_includes_head= True, clip_on = False
                        )

        return 0



    # this uses very similar code to schematic arrows
    # could reduce this to reuse overlapping code
    def vector_arrows_2D(self, ax, xaxis = True, yaxis = True,
                        length = 5.0, x_offset = 0.0, y_offset = 0.0,
                        xlabel = "", ylabel = "",
                        xlabel_x_offset = 0.0, xlabel_y_offset = 0.0,
                        ylabel_x_offset = 0.0, ylabel_y_offset = 0.0):
        """
        Plot small vector arrows to help define 2D directions
        """
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()

        # location of end of arrows
        xmax = xmin + length
        ymax = ymin + length

        # get width and height of axes object to compute
        # matching arrowhead length and width
        dps = self.fig.dpi_scale_trans.inverted()
        bbox = ax.get_window_extent().transformed(dps)
        width, height = bbox.width, bbox.height

        width = 1 ; height = 1

        # manual arrowhead width and length
        hw = 1.0/10.0*(ymax-ymin)
        hl = 1.0/10.0*(xmax-xmin)
        lw = 0.5 # axis line width

        # compute matching arrowhead length and width
        yhw = hw/(ymax-ymin)*(xmax-xmin)* height/width
        yhl = hl/(xmax-xmin)*(ymax-ymin)* width/height

        # draw x and y axis
        xbase = xmin + x_offset
        ybase = ymin + y_offset

        xwidth = 0.001; ywidth = 0.001
        if xaxis == True:
            ax.arrow(xbase, ybase, xmax-xmin, 0.0, fc='k', ec='k', lw = lw,
                    head_width=hw, head_length=hl, width = xwidth,
                    length_includes_head= True, clip_on = False)

            ax.annotate(ylabel, xy = (xmin, ymin), 
                        xytext = (xbase + length + xlabel_x_offset, ybase + xlabel_y_offset))
            
        if yaxis == True:
            ax.arrow(xbase, ybase, 0., ymax-ymin, fc='k', ec='k', lw = lw,
                    head_width=yhw, head_length=yhl, width = ywidth,
                    length_includes_head= True, clip_on = False)
        
            ax.annotate(xlabel, xy = (xmin, ymin), 
                        xytext = (xbase + ylabel_x_offset , ybase + length + ylabel_y_offset))
        
        # for ax.annotate
        # xy = (xmin, ymin), as point has to remain in plot
        # so only move text
        # if point not in plot, text will not appear
        
        return 0


# Plotting ---------------------------------------------------------------------

def loglog_guide_manual(ax, x, p0, p1, colour="grey", label="", linestyle=":",
                                                linewidth=1.5, logtype = None):
    """
    Manual log line of form p0 * ( x^(p1) )
    """

    if logtype == None:
            logtype = "loglog"

    if label == "":
        label_v = '{' + str(p1) + '}'
        label = r'$r^{}$'.format(label_v)

    if logtype == "loglog":
        ax.loglog(x, p0*(np.power(x, p1)),
                        linestyle=linestyle, color=colour, 
                        label = label, linewidth = linewidth)

    if logtype == "semilogy":
        ax.semilogy(x, p0*(np.power(x, p1)),
                                linestyle=linestyle, color=colour, 
                                label = label, linewidth = linewidth)


    return 0

def loglog_guide(x, y, indices=None):
    """
    automatic rough fit of guide lines for a loglog x and y
    uses the first and last point of x and y

    :param x: x array (does not need to be log values)
    :param y: y array (does not need to be log values)
    :param indices=None: indices of x and y to fit, default will leave x and y unchanged
    :returns y_g: y values of guide of form y_g = rf_p[0] * ( x^(rf_p[1]) )
    :returns rf_p: rough fit parameters of log guide of form rf_p[0] * ( x^(rf_p[1]) )
    """

    if indices is None:
        indices = np.arange(0,len(x), 1)

    x = np.array(x)[indices]
    y = np.array(y)[indices]

    # remove 0.0 values and negatives
    x = np.abs(x)[x != 0.0]
    y = np.abs(y)[y != 0.0]

    def rough_fit(x, y):
        x_log = np.log(x)
        y_log = np.log(y)
        a_0 = y[0]/( np.power( x[0], ((y_log[0] - y_log[len(y)-1]) / (x_log[0] - x_log[len(x)-1])) ) )
        g = (y_log[0] - y_log[len(y)-1]) / (x_log[0] - x_log[len(x)-1])
        p_g = [a_0, round(g,2)]
        return p_g

    def model(x, p):
        return p[0]*(np.power(x, p[1]))

    rf_p = rough_fit(x, y) # rough fit parameters
    y_g = model(x, rf_p) # log line of y values using rough fit

    return y_g, rf_p

def plot_set_xlabels(ax, x):
    """
    need for nice x axis, mainly for loglog plots
    """
    x_labels = np.asarray(x, dtype=str)
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels)
    return 0

def loglog_plot_remove_labels_xaxis(ax):
    """
    remove the other 10^x labels
    """
    formatter = matplotlib.ticker.LogFormatter(labelOnlyBase=True, minor_thresholds=(1,2))
    ax.get_xaxis().set_minor_formatter(formatter)
    return 0


def loglog_ticks_manual(ax, axis_xy =  ["x", "y"]):
    """
    Force the loglog ticks back on
    """

    if axis_xy == "x":
        axis_xy = ["x"]
    elif axis_xy == "y":
        axis_xy = ["y"]

    locmin = matplotlib.ticker.LogLocator(base=10.0,subs=(0.2,0.4,0.6,0.8),numticks=10)
    for xy in axis_xy:
        if xy == "x":
            ax.xaxis.set_minor_locator(locmin)
            ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        if xy == "y": 
            ax.yaxis.set_minor_locator(locmin)
            ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())

    return 0

def zoom_around_point_2D(ax, point, width, height = None, maintain_aspect_ratio = True):
    
    # default to a box around the point
    if height == None:
        height = width

    px = point[0]
    py = point[1]
    wh = 0.5*width # width half
    hh = 0.5*height # height half
    
    if maintain_aspect_ratio == True:
        
        # calculate current axis limit aspect ratio
        xl1, xl2 = ax.get_xlim()
        yl1, yl2 = ax.get_ylim()
        axis_ratio = (np.abs(xl2 - xl1))/(np.abs(yl2 - yl1))
        
        # adjust height to match aspect ratio
        hh = 0.5*(height/axis_ratio)
    
    ax.set_xlim([px - wh, px + wh])
    ax.set_ylim([py - hh, py + hh])
    
    xl1, xl2 = ax.get_xlim()
    yl1, yl2 = ax.get_ylim()
    axis_ratio = (np.abs(xl2 - xl1))/(np.abs(yl2 - yl1))
    
    return 0

def plot_line_2D(ax, a, b, linewidth = 1, colour="grey", 
                                linestyle = ":", label = None):

    """
    Plot line between point a and b
    """
    
    # y = mx + c
    Dy = b[1] - a[1]
    Dx = b[0] - a[0]
        
    m = Dy/Dx
    c = b[1] - (m*b[0])
    
    x = np.linspace(a[0],b[0],10)
    y = (m*x) + c
    
    lines = ax.plot(x, y, linestyle=linestyle, color=colour, label = label, linewidth = linewidth)
    # plot can handle multip dimensional x and y, so returns an array of lines
    # this funciton only handles one line
    # change function to handle more and this the return as an array, so script code is aware of array
    return lines


# Plot Atoms

def plot_bonds_2D(ax, positions, bonds, linewidth = 1, colour="grey", 
                                        linestyle = ":", label = None):
    
    for i in range(0,len(bonds)):
    
        b = bonds[i]
    
        pa = positions[b[0]]
        pb = positions[b[1]]
    
        plot_line_2D(ax, pa, pb, linewidth = linewidth, colour=colour)
        
        if i == len(bonds)-1:
            plot_line_2D(ax, pa, pb, linewidth = linewidth, colour=colour, 
                                        linestyle = linestyle, label = label)
    
    return 0

def plot_atoms_2D(ax, pos, scale = 10, colour="grey", 
                                alpha = 1.0, label = None):
    
    x = pos[:,0]
    y = pos[:,1]
    ax.scatter(x, y, s = scale, color = colour, alpha = alpha, label = label)
    
    return 0

def split_regions_indices(pos, radius, center_point):
    """
    Return indices of regions defined by a radius
    where inner are the indices within the radius
    and outer are the indices beyond the raidus
    """
    inds = np.arange(0, len(pos))
    r_d = np.linalg.norm(pos - center_point, axis=1)

    inner = inds[r_d <= radius]
    outer = inds[r_d > radius]
    
    return inner, outer