from datetime import datetime
import json

class CacheHandler():
    def __init__(self, expire_time):
        self.last_cache = None
        self.tree = None
        self.expire_time = expire_time

    def is_cache_expired(self):
        current_time = datetime.now()
        time_difference = current_time - self.last_cache

        if time_difference < self.expire_time:
            return False
        else:
            return True

    def load_cache(self):
        with open("media.json", "r") as json_file:
            self.tree = json.load(json_file)

        return self.tree

    def set_tree(self, tree):
        self.tree = tree
        with open('media.json', 'w') as json_file:
            json.dump(self.tree, json_file)
        print(f"Saved cache at {self.last_cache}")
        self.set_time(datetime.now())

    def set_time(self, last_cache):
        self.last_cache = last_cache

