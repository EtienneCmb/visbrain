import os
import logging
import fileinput
from sphinx_gallery.gen_rst import scale_image
from sphinx_gallery import sphinx_compatibility


logger = sphinx_compatibility.getLogger('sphinx')
logger.setLevel(logging.INFO)
logger.info("generating thumbnails using example images...")
# logger.warning(colorize('test', 'darkred'))

cwd = os.getcwd()
path_to_examples = os.path.join(cwd.split('docs')[0], 'examples')
image_pattern = '.. image::'
to_thmb = os.path.join(cwd, "_build/html/_images/sphx_glr_{}_thumb.png")

ex_py_files = []
for root, subdirs, files in os.walk(path_to_examples):
    for i in files:
        if os.path.splitext(i)[1] == '.py':
            image_found = False
            im_file = os.path.join(root, i)
            image_name = os.path.splitext(os.path.split(im_file)[1])[0]
            for line in fileinput.input(im_file):
                if line.find(image_pattern) + 1:
                    line_sp = line[:-1].split('.. image:: ')[1]
                    from_image = os.path.join(*(cwd, '_static', 'examples', line_sp))
                    to_image = to_thmb.format(image_name)
                    image_found = True
            if image_found:
                print('        Thumbnail created %s' % image_name)
                scale_image(from_image, to_image, 400, 280)
            else:
                logger.warning('        No image defined in %s' % im_file)
