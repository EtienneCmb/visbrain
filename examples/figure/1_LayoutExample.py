"""This script generate some figures using the Brain module. Those exported
pictures are going to be set in a layout in the 1_Example.py script.
"""
from visbrain import Figure

# Files to load :
files = ['default.png', 'inside.png', 'count.png', 'density.png',
         'repartition.jpg', 'roi.jpg']

# Titles :
titles = ['Default view', 'Select sources inside', 'Connectivity',
          'Connectivity', 'Cortical repartition', 'Cortical projection']

# X-labels / Y-labels :
xlabels = [None, None, 'Looks nice', 'Looks good', 'Repartition', 'ROI']
ylabels = ['Dirty', 'Better', None, None, None, 'Brodmann area 4 and 6']

# Background color of each axis :
ax_bgcolor = ['slateblue', 'olive', 'black', 'darkgray', None, None]


f = Figure(files, titles=titles, xlabels=xlabels, ylabels=ylabels,
           figtitle='The Brain module', grid=(3, 2), ax_bgcolor=ax_bgcolor,
           y=1., fig_bgcolor='white', figsize=(8, 12),
           text_color='black', subspace={'wspace': 0.1, 'left': 0.})

# Colorbar to the first connectivity plot :
f.colorbar_to_axis(2, (1, 5), 'viridis', title='Color by count',
                   ticks='minmax', fz_ticks=12)

# Colorbar to the second connectivity plot :
f.colorbar_to_axis(3, (0., 35.), 'magma', title='Color by density',
                   ticks='complete', vmax=30, over='darkred', fz_ticks=12,
                   vmin=10., under='gray')

# Colorbar to the first projection plot :
f.colorbar_to_axis(4, (1, 6), 'viridis', title='Nb of contributing\nsources',
                   ticks=1., fz_ticks=10, orientation='horizontal',
                   vmin=2, under='gray', vmax=4, over='#ab4642')

# Colorbar to the second projection plot :
f.colorbar_to_axis(5, (.1, .5), 'inferno', title='ROI projection',
                   ticks=[.2, .3], fz_ticks=10, orientation='horizontal')


# Finally, save the picture :
f.save('LayoutExample.png', dpi=600)

f.show()