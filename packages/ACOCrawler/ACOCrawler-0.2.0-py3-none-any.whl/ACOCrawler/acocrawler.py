import time

from .crawler import Crawler

from .components.node import Node
from .components.aconeo4J import AcoNeo4j
from .components.scrape import Scrape


class AcoCrawler(Crawler):
    """Crawlerを継承したAcoクラス

    Crawlerに必要引数を渡し
    具体的実装はこのファイルで行う
    インスタンス化する

    """

    def __init__(self, keyword, num_of_cycles, num_of_ants, keywords, alpha, beta, rho, lower, upper, base_phe, init_phe, collect_norm, init_node_score):
        super().__init__(keyword)
        self.num_of_cycles = num_of_cycles
        self.num_of_ants = num_of_ants
        self.keywords = keywords
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.lower = lower
        self.upper = upper
        self.ant_paths = []
        self.base_phe = base_phe
        self.init_phe = init_phe
        self.collect_norm = collect_norm
        self.init_node_score = init_node_score

    def start(self):
        super().start()
        self.init_node = Node(url=self.keyword, domain=self.keyword, title=self.keyword, anchors=self.seed_urls,
                              body=self.keyword, wakati=self.keyword, score=self.init_node_score, is_expanded=False, visit_times=1,
                              created=self.start_time, updated=self.start_time)
        if not AcoNeo4j.is_already_node(self.keyword):
            AcoNeo4j.create_node(self.init_node)

    def solve(self):
        """Acoの実行

        cycle回だけ、
        run(各サイクルで、蟻の移動・フェロモンの更新)を行う
        """
        super().solve()
        for cycle in range(self.num_of_cycles):
            try:
                self.run(cycle)
            except Exception as e:
                print("SolveError", e)
                continue

    def run(self, cycle):
        """Acoの各サイクル

        蟻をnum_of_ants体だけ動かす。
        もし現在のノードが展開されてないなら、現ノードから出ている先のURLをスクレイピングする。
        現ノードはすでに展開されていることに注意する。

        もし展開されているなら、次のURLを一つ選び、移動する。

        移動し終わったら、パスが構築されるためフェロモン更新を行う。

        Args:
            cycle(int): 何サイクル目か？

        Returns:

        """
        super().run(cycle)

        ant_path = [[] for _ in range(self.num_of_ants)]

        for ant_k in range(self.num_of_ants):
            now_url = self.keyword
            ant_path[ant_k].append(now_url)

            for move_i in range(cycle):
                now_node = AcoNeo4j.get_node(now_url)

                if now_node is None:
                    print("NoneError", now_url)
                    continue

                if not now_node.is_expanded:
                    AcoNeo4j.set_node(now_url, 'is_expanded', True)

                    for to_url in now_node.anchors:
                        if AcoNeo4j.is_already_node(to_url):
                            to_node = AcoNeo4j.get_node(to_url)
                            AcoNeo4j.add_value_node(to_url, 'visit_times', 1)
                        else:
                            try:
                                result = Scrape.page_scrape(to_url, self.keyword, keywords=self.keywords)
                                to_node = Node(url=to_url, domain=result['domain'], title=result['title'],
                                               anchors=result['anchors'], body=result['body'], wakati=result['wakati'],
                                               score=result['score'], is_expanded=False, visit_times=1,
                                               created=time.time(),
                                               updated=time.time())
                            except Exception as e:
                                print("ScrapeError", e)
                                continue

                        if not AcoNeo4j.is_already_node(to_url) and to_node.score > self.collect_norm:
                            try:
                                AcoNeo4j.create_node(to_node)
                            except Exception as e:
                                print("CreateNodeError", e)
                                continue

                        if not AcoNeo4j.is_already_edge(now_url, to_url) and now_url != to_url and to_node.score > self.collect_norm:
                            similarity = to_node.score
                            heuristic = to_node.score
                            pheromone = to_node.score * self.base_phe + self.init_phe

                            # エッジの登録
                            AcoNeo4j.create_edge(now_url, to_url, pheromone=pheromone, heuristic=heuristic,
                                                 similarity=similarity)

                # フェロモン付きのエッジを取り出す
                anchors = AcoNeo4j.get_anchors(now_url)

                if len(anchors) == 0:
                    if len(ant_path[ant_k]) > 1:
                        ant_path[ant_k].pop()
                        now_url = ant_path[ant_k][-1]
                    continue

                next_url = AcoNeo4j.calc_next_link_aco_tabu(anchors, self.alpha, self.beta, ant_path[ant_k])
                AcoNeo4j.add_value_node(next_url, 'visit_times', 1)
                AcoNeo4j.add_value_edge(now_url, next_url, 'pass_times', 1)
                now_url = next_url
                ant_path[ant_k].append(now_url)

        # フェロモン蒸発
        AcoNeo4j.mul_all_edges_pheromone(self.rho)

        # フェロモン分泌
        for path in ant_path:
            add_pheromone = AcoNeo4j.calc_path_scores(path)
            AcoNeo4j.splay_pheromone_by_ant_k(add_pheromone, path)
        # AcoNeo4j.clamp_pheromones(self.lower, self.upper)

        # 情報の保存
        self.ant_paths.append(ant_path)
