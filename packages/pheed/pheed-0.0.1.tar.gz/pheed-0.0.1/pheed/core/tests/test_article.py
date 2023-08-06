"""Tests for Article interface"""

from pheed.core import article, author


class TestArticle:
    def test_create_article(self):
        author1 = author.Author('first1', 'last1')
        a = article.Article(title='title', authors=(author1,), url='url')
