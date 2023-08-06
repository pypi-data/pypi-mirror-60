"""Wrappers for the IOP source

References:
    [1] IOP Journals home page https://iopscience.iop.org/journalList
    [2] IOP terms and conditions https://iopscience.iop.org/page/terms
"""

from pheed.core import source


class IOPSource(source.Source):
    def __init__(self):
        raise NotImplementedError
