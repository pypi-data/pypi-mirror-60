"""Wrappers for the arxiv source

References:
    [1] Arxiv home page https://arxiv.org/
    [2] Arxiv terms and conditions https://arxiv.org/robots.txt
"""

from pheed.core import source


class ArxivSource(source.Source):
    def __init__(self):
        raise NotImplementedError
