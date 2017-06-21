from visbrain import Colorbar

cb = Colorbar(vmin=.1, under='slateblue', vmax=.8, over='olive',
              cmap='viridis', ndigits=4, cblabel='oki !').show()
