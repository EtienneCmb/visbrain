from .AtlasTransform import AtlasTransform
from .SourcesTransform import SourcesTransform


class transformations(AtlasTransform, SourcesTransform):

    """docstring for transformations
    """

    def __init__(self, **kwargs):
        AtlasTransform.__init__(self, **kwargs)        
        SourcesTransform.__init__(self, **kwargs)
