import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import scipy.ndimage as nd


# read header

file_name = 'tq2989_DSM_2M.asc'

# six rows for header information

header_rows = 6

# store header information including ncols, nrows, xllcorner, yllcorner, cellsize, NODATA_value

header = {}
row_counter = 1
with open(file_name, 'rt') as file_h:
     for line in file_h:
        if row_counter <= header_rows:
             [dkey, dvalue] = line.split(" ", 1)
             header[dkey] = float(dvalue)
        else:
             break
        row_counter += 1
        
# read data array

data_array = np.loadtxt(file_name, skiprows=header_rows, dtype='float64')

# Read our header informatiom

cellsize = header['cellsize']

ncols = header['ncols']
nrows = header['nrows']

left = header['xllcorner']
right = left + ncols * cellsize
bottom = header['yllcorner']
top = bottom + nrows * cellsize

map_extent = (left, right, bottom, top)

# Count rows and columns

arows = data_array.shape[0]
acols = data_array.shape[1]

print(f'Before... rows: {arows} and columns: {acols}')

# Smoothing our data

smoothing = 10


sigma = [cellsize * smoothing, cellsize * smoothing]
smooth_array = nd.filters.gaussian_filter(data_array, sigma, mode='constant')
#smooth_array = data_array

# We use "zoom" to reduce the resolution

zoom = 1

smooth_array = nd.zoom(smooth_array, zoom, order=0)

# Count rows and columns

srows = smooth_array.shape[0]
scols = smooth_array.shape[1]

print(f'After... rows: {srows} and columns: {scols}')

cellwidth = (right - left) / scols
cellheight = (top - bottom) / srows

x, y = np.mgrid[left:right:cellwidth, bottom:top:cellheight]

#fig, ax = plt.subplots(1)
#img = plt.imshow(data_array, extent=map_extent)
fig = plt.figure('3D Surface')
ax = fig.gca(projection='3d')
ax.plot_surface(x, y, smooth_array, linewidth=0, cmap=cm.terrain)
#ax.plot_wireframe(x, y, smooth_array)

plt.show()
