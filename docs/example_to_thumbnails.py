import logging
import os
from pathlib import Path
import fileinput

from sphinx_gallery.gen_rst import scale_image

try:
    from sphinx_gallery import sphinx_compatibility
except ImportError:  # sphinx-gallery 0.15 removed the helper module
    sphinx_compatibility = None  # type: ignore[assignment]


if sphinx_compatibility is not None:
    logger = sphinx_compatibility.getLogger('sphinx')
else:
    logger = logging.getLogger('sphinx-gallery')
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(handler)

logger.setLevel(logging.INFO)
logger.info("generating thumbnails using example images...")

DOCS_DIR = Path(__file__).resolve().parent
EXAMPLES_DIR = DOCS_DIR.parent / "examples"
THUMB_DIR = DOCS_DIR / "_build" / "html" / "_images"
THUMB_DIR.mkdir(parents=True, exist_ok=True)

to_thmb = str(THUMB_DIR / "sphx_glr_{}_thumb.png")

ex_py_files = []
for root, subdirs, files in os.walk(EXAMPLES_DIR):
    for i in files:
        if os.path.splitext(i)[1] == '.py':
            image_found = False
            im_file = os.path.join(root, i)
            image_name = os.path.splitext(os.path.split(im_file)[1])[0]
            for line in fileinput.input(im_file):
                if line.find('.. image::') + 1:
                    line_sp = line[:-1].split('.. image:: ')[1]
                    from_image = DOCS_DIR / '_static' / 'examples' / line_sp
                    to_image = to_thmb.format(image_name)
                    image_found = True
            if image_found:
                print('        Thumbnail created %s' % image_name)
                scale_image(str(from_image), to_image, 400, 280)
            else:
                logger.warning('        No image defined in %s' % im_file)
