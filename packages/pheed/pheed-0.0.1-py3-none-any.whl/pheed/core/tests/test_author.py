"""Tests for Author interface"""

from pheed.core import author


class TestAuthor:
    def test_create_author(self):
        a = author.Author(first_name='first', last_name='last')

    def test_formatted_name(self):
        a = author.Author(first_name='first', last_name='last')
        assert a.name == 'last, first'
