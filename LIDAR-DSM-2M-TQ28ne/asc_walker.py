import os
import os.path as op
import re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import scipy.ndimage as nd

# Read an asc file and record parameters

class ascRaster:
    def __init__(self, file_name):
        self.file_name = file_name

        # read six rows for header information

        header_rows = 6

        # store header information

        self.header = {}
        row_counter = 1

        with open(self.file_name, 'rt') as file_handle:
           for line in file_handle:
              if row_counter <= header_rows:
                   [dkey, dvalue] = line.split(" ", 1)
                   self.header[dkey] = float(dvalue)
              else:
                   break
              row_counter += 1
              
        # read data array

        self.data_array = np.loadtxt(file_name, skiprows=header_rows, dtype='float64')

        self.data_array = np.clip(self.data_array, 0, 200)

        # Read our header information

        self.cellsize = self.header['cellsize']

        self.ncols = self.header['ncols']
        self.nrows = self.header['nrows']

        self.left = self.header['xllcorner']
        self.bottom = self.header['yllcorner']

        # Calculate other corner

        self.right = self.left + self.ncols * self.cellsize
        self.top = self.bottom + self.nrows * self.cellsize

    def __str__(self):
        return f'({self.left}, {self.bottom})'

    def bottom_left(self):
        return self.left, self.bottom

    def top_right(self):
        return self.right, self.top

    def get_extent(self):
        return self.left, self.bottom, self.right, self.top

    def get_size(self):
        return self.data_array.shape[0], self.data_array.shape[1]

    def zoom(self, ratio):
        self.ncols *= ratio
        self.nrows *= ratio
        self.cellsize /= ratio
        self.data_array  = nd.zoom(self.data_array, ratio, order=0)

    def smooth(self, factor):
        sigma = [self.cellsize * factor, self.cellsize * factor]
        self.data_array = nd.filters.gaussian_filter(self.data_array, sigma, mode='constant')

    def is_left(self, other):
        return  self.bottom == other.bottom and self.right == other.left

    def is_below(self, other):
        return  self.top == other.bottom and self.left == other.left

    def merge_horizontal(self, other):
        self.data_array = np.concatenate((self.data_array, other.data_array), axis=1)
        self.ncols += other.ncols
        self.right = other.right

    def merge_vertical(self, other):
        self.data_array = np.concatenate((other.data_array, self.data_array), axis=0)
        self.nrows += other.nrows
        self.top = other.top

    

    
# Walk through our directory and get our asc files

mypath = os.getcwd()

only_files = [f for f in os.listdir(mypath) if op.isfile(op.join(mypath, f))]

only_asc = [op.join(mypath, f) for f in only_files if re.search('\.asc$', f)]

# Work through directory and load asc files

asc_list = []

for f in only_asc:
    asc_list.append(ascRaster(f))


for i in range(len(asc_list) - 1, -1, -1):
    index_asc = asc_list[i]
    for j in range(len(asc_list) - 1, i, -1):
        compare_asc = asc_list[j]

        if index_asc.is_left(compare_asc):
            print(f'{index_asc} is left of {compare_asc}')

            index_asc.merge_horizontal(compare_asc)

            asc_list.pop(j)

for a in asc_list:
    print(f'{a.get_extent()}')

for i in range(len(asc_list) - 1, -1, -1):
    index_asc = asc_list[i]
    for j in range(len(asc_list) - 1, i, -1):
        compare_asc = asc_list[j]

        if index_asc.is_below(compare_asc):
            print(f'{index_asc} is below {compare_asc}')

            index_asc.merge_vertical(compare_asc)

            asc_list.pop(j)

my_asc = asc_list.pop()

print(f'{my_asc.get_extent()}')

# Now let's smooth and zoom

arows, acols = my_asc.get_size()

print(f'Before... rows: {arows} and columns: {acols}')

# Smoothing our data

my_asc.smooth(10)

# We use "zoom" to reduce the resolution

#my_asc.zoom(1/100)

# Count rows and columns

srows, scols = my_asc.get_size()

print(f'After... rows: {srows} and columns: {scols}')

cellwidth = (my_asc.right - my_asc.left) / scols
cellheight = (my_asc.top - my_asc.bottom) / srows

x, y = np.mgrid[my_asc.left:my_asc.right:cellwidth, my_asc.bottom:my_asc.top:cellheight]

#fig, ax = plt.subplots(1)
#img = plt.imshow(data_array, extent=map_extent)
fig = plt.figure('3D Surface')
ax = fig.gca(projection='3d')
ax.plot_surface(x, y, my_asc.data_array, linewidth=0, cmap=cm.terrain)
#ax.plot_wireframe(x, y, smooth_array)

plt.show()


