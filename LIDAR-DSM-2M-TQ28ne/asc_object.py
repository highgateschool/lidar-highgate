import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import scipy.ndimage as nd

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

      # Read our header information
      
      self.cellsize = self.header['cellsize']

      self.ncols = self.header['ncols']
      self.nrows = self.header['nrows']

      self.left = self.header['xllcorner']
      self.bottom = self.header['yllcorner']

      # Calculate other corner

      self.right = self.left + self.ncols * self.cellsize
      self.top = self.bottom + self.nrows * self.cellsize

   def bottom_left(self):
      return self.left, self.bottom

   def top_right(self):
      return self.right, self.top

   def get_extent(self):
      return self.left, self.bottom, self.top, self.right

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

# Open our file

my_asc = ascRaster('tq2989_DSM_2M.asc')

arows, acols = my_asc.get_size()

print(f'Before... rows: {arows} and columns: {acols}')

# Smoothing our data

my_asc.smooth(1)

# We use "zoom" to reduce the resolution

my_asc.zoom(1/25)

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
