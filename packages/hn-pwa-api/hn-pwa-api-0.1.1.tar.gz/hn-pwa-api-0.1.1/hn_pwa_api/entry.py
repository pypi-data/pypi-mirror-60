from enum import Enum
from typing import Optional


class TypeEnum(Enum):
    JOB = "job"
    LINK = "link"
    ASK = "ask"


class Entry:
    comments_count: int
    domain: Optional[str]
    id: int
    index: Optional[int]
    points: Optional[int]
    time: int
    time_ago: str
    title: str
    type: TypeEnum
    url: str
    user: Optional[str]

    def __init__(self, comments_count: int, id: int, points: Optional[int], time: int, time_ago: str, title: str, index: Optional[int], type: TypeEnum, url: str, user: Optional[str], domain: str = None) -> None:
        self.comments_count = comments_count
        self.domain = domain
        self.id = id
        self.points = points
        self.time = time
        self.time_ago = time_ago
        self.title = title
        self.type = type
        self.url = url
        self.user = user
        self.index = index

    def __repr__(self):
        values = "\n".join([f"\t'{k}': {repr(v)}" for k,v in self.__dict__.items()])
        return f"{self.__class__} ({{\n{values}\n}})"