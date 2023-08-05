import requests

from .entry import Entry
from .post import Post
from .feed import Feed


class HNApi(object):
    def __init__(self, *args, **kwargs):
        self.s = requests.Session()
        self.feed_limits = {
            "news": 10,
            "newest": 12,
            "ask": 2,
            "show": 2,
            "jobs": 1
        }

    def feed(self, feed_type, pagination=1):
        if pagination < self.feed_limits[feed_type]:
            feed_entries = self.s.get(f'https://api.hnpwa.com/v0/{feed_type}/{pagination}.json').json()
        else:
            feed_entries = self.s.get(f'https://api.hnpwa.com/v0/{feed_type}/{self.feed_limits[feed_type]}.json').json()
        entries = [Entry(**feed_entry, **{'index': ((pagination - 1) * 30) + i}) for i, feed_entry in enumerate(feed_entries, start=1)]
        return Feed(pagination, feed_type, entries)


    def post_item(self, post_id):
        post = self.s.get(f'https://api.hnpwa.com/v0/item/{post_id}.json').json()
        return Post(**post)
