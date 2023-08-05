import json
import copy
from enum import Enum
from typing import Optional, List


class TypeEnum(Enum):
    COMMENT = "comment"


class Comment:
    id: int
    user: Optional[str]
    time: int
    time_ago: str
    type: TypeEnum
    content: str
    comments: List['Comment']
    comments_count: int
    level: int
    url: str
    # deleted: Optional[bool]
    # dead: Optional[bool]

    def __init__(self, id: int, time: int, time_ago: str, type: TypeEnum, content: str, comments: List['Comment'], comments_count: int, level: int, url: str, user: Optional[str] = None, deleted: Optional[bool] = None, dead: Optional[bool] = None) -> None:
        self.id = id
        self.user = user
        self.time = time
        self.time_ago = time_ago
        self.type = type
        self.content = content
        self.comments = [Comment(**c) for c in comments]
        self.comments_count = comments_count
        self.level = level
        self.url = url

    def __repr__(self):
        self_dict = copy.copy(self.__dict__)
        self_dict.update({'comments': [str(c.__class__) for c in self_dict.get('comments')]})
        values = json.dumps(self_dict, indent=4)
        return f"{self.__class__} ({values})"


class Post:
    id: int
    title: str
    points: int
    user: Optional[str]
    domain: Optional[str]
    time: int
    time_ago: str
    type: str
    content: str
    comments: List[Comment]
    comments_count: int
    url: str

    def __init__(self, id: int, title: str, points: int, user: Optional[str], time: int, time_ago: str, type: str, content: str, comments: List[Comment], comments_count: int, url: str, domain: Optional[str] = None) -> None:
        self.id = id
        self.title = title
        self.points = points
        self.user = user
        self.time = time
        self.time_ago = time_ago
        self.type = type
        self.content = content
        self.domain = domain
        self.comments = [Comment(**c) for c in comments]
        self.comments_count = comments_count
        self.url = url

    def __repr__(self):
        self_dict = copy.copy(self.__dict__)
        self_dict.update({'comments': [str(c.__class__) for c in self_dict.get('comments')]})
        values = json.dumps(self_dict, indent=4)
        return f"{self.__class__} ({values})"