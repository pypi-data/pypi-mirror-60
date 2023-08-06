"""Wrappers for the APS source

References:
    [1] APS Journals home page https://journals.aps.org/about
    [2] APS terms and conditions https://journals.aps.org/info/terms.html
"""

from pheed.core import source


class APSSource(source.Source):
    def __init__(self):
        raise NotImplementedError