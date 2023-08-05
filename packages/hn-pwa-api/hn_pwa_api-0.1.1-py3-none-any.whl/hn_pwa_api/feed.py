from .entry import Entry
from typing import Optional, List


class Feed(object):
    page: int
    name: str
    entries: List['Entry']

    def __init__(self, page: int, name: str, entries: List['Entry']):
        self.page = page
        self.name = name
        self.entries = entries
