"""Author definition and related utilities

"""


class Author:
    def __init__(self, first_name: str, last_name: str):
        self.first_name = first_name
        self.last_name = last_name

    @property
    def name(self):
        return '{}, {}'.format(self.last_name, self.first_name)
