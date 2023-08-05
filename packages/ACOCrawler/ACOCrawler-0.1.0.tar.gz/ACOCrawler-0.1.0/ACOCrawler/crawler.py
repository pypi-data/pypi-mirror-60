import time

from .components.google import Google


class Crawler:

    def __init__(self, keyword):
        self.keyword = keyword
        self.start_time = time.time()
        self.seed_urls = Google().Search(keyword=keyword, type='text', maximum=10)
        self.init_node = None
        self.cycle_time = 0
        pass

    def start(self):
        pass

    def solve(self):
        pass

    def run(self, cycle):
        self.cycle_time = cycle
        pass

    def finish(self):
        pass
