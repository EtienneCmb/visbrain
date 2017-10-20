from visbrain.objects import RoiObj


r = RoiObj('brodmann')
r.get_roi_vertices(level=4, plot=True, smooth=3, unique_color=False)
# r.get_roi_vertices(level=[4, 6, 8], plot=True, smooth=3, unique_color=True)
r.preview(axis=False)