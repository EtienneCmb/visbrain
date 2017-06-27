from visbrain import Colorbar

cb = Colorbar(vmin=.1, under='slateblue', vmax=.8, over='olive',
              cmap='viridis', ndigits=4, cblabel='oki !', border=False,
              name='Example1')
# cb.add_colorbar('top', clim=(-22, 45), vmin=-20, vmax=22, cblabel='Cool')
cb.show()