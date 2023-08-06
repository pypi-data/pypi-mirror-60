"""Tests for Source interface"""

from pheed.core import source


class DummySource(source.Source):
    def __init__(self, name: str):
        self.name = name


class TestSource:
    def test_create_source(self):
        s = DummySource('name')
