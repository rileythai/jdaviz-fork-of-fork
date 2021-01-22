from astrowidgets.core import ImageWidget
from jdaviz.core.registries import viewer_registry

__all__ = ['ImvizImageView']


@viewer_registry("imviz-image-viewer", label="Image 2D (Imviz)")
class ImvizImageView(ImageWidget):
    default_class = None
