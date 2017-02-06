"""Add transformations of sources and atlas."""
from .AtlasTransform import AtlasTransform
from .SourcesTransform import SourcesTransform


class transformations(AtlasTransform, SourcesTransform):
    """This class initialize source's Atlas'transformations."""

    def __init__(self, **kwargs):
        """Init."""
        AtlasTransform.__init__(self, **kwargs)
        SourcesTransform.__init__(self, **kwargs)
