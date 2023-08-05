class Node:
    """Nodeクラス

    Nodeに関する情報を入れておく
    Neo4jクラスでDBから情報を取り出すときにも受け取り皿として使う

    """

    def __init__(self, url, domain, title, anchors, body, wakati, score, is_expanded, visit_times, created, updated):
        self.url = url
        self.domain = domain
        self.title = title
        self.anchors = anchors
        self.body = body
        self.wakati = wakati
        self.score = score
        self.is_expanded = is_expanded
        self.visit_times = visit_times
        self.created = created
        self.updated = updated

    def __repr__(self):
        return f'<Node url:{self.url}, title:{self.title}, is_expanded:{self.is_expanded}>'

    @classmethod
    def get_node(cls, url, domain, title, anchors, body, wakati, score, is_expanded, visit_times, created, updated):
        return Node(url, domain, title, anchors, body, wakati, score, is_expanded, visit_times, created, updated)
