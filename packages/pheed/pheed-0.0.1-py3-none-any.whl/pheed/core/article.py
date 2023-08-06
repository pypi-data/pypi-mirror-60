"""Article definition and related utilities

"""

import typing

from pheed.core.author import Author


class Article:
    def __init__(self, title: str, authors: typing.Tuple[Author, ...], url: str):
        self.title = title
        self.authors = authors
        self.url = url
