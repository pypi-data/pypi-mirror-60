"""Core definition for an article source and related utilities
"""

import abc
import typing

from pheed.core.article import Article

Results = typing.List[Article]


class Source(abc.ABC):
    """Source interface definition outlines common methods that any Source must support.
    Note, this class is an abstract base class and therefore is not intended to be instantiated directly.
    """

    def search(self, **kwargs) -> Results:
        raise NotImplementedError

    def recent(self, **kwargs) -> Results:
        raise NotImplementedError
