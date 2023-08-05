import itertools
import bisect
import random

from .neo4J import Neo4j


class AcoNeo4j(Neo4j):
    """Neo4jを継承したACOに関連するNeo4j

    Neo4jより派生したクラス
    """

    @classmethod
    def calc_next_url_aco(cls, anchors, alpha, beta):
        """次に移動するURLを確率選択して返す

        ACOの確率選択式を利用して
        確率選択して選んだ次に移動するべきURLを返す

        Args:
            anchors(list(dict)): 次に移動できるURL候補配列
            alpha(float): フェロモン
            beta(float): ヒューリスティック呈す

        Returns:
            str: 次のURL

        """
        tau_arr = []
        for anchor in anchors:
            p = anchor['pheromone']
            h = anchor['heuristic']
            tau = p ** alpha + h ** beta
            tau_arr.append(tau)
        sum_v = sum(tau_arr)
        prob_arr = list(itertools.accumulate(tau_arr))
        next_url = anchors[bisect.bisect_left(prob_arr, sum_v * random.random())]['to_url']
        return next_url

    @classmethod
    def calc_next_link_aco_tabu(cls, anchors, alpha, beta, path):
        """次に移動するURLを確率選択して返す

        ACOの確率選択式を利用して
        確率選択して選んだ次に移動するべきURLを返す
        Tabu処理をする

        Args:
            anchors(list(dict)): 次に移動できるURL候補配列
            alpha(float): フェロモン
            beta(float): ヒューリスティック呈す
            path(list): アリの通った経路

        Returns:
            str: 次のURL

        """
        tau_arr = []
        for anchor in anchors:
            p = anchor['pheromone']
            h = anchor['heuristic']
            tau = p ** alpha + h ** beta
            tau_arr.append(tau)
        sum_v = sum(tau_arr)
        prob_arr = list(itertools.accumulate(tau_arr))

        next_url = None
        for i in range(10000):
            next_url = anchors[bisect.bisect_left(prob_arr, sum_v * random.random())]['to_url']
            if next_url not in path:
                return next_url

        return next_url

    @classmethod
    def mul_all_edges_pheromone(cls, rho):
        """エッジにrhoをかけて蒸発させる

        エッジのフェロモンを蒸発させる
        ただ、残留率といったほうが正しい

        Args:
            rho(float): 蒸発率

        Returns:

        """
        cls.set_mul_all_edges('pheromone', rho)

    @classmethod
    def calc_path_scores(cls, path):
        """経路のパスのスコア（フェロモン）を計算する

        蟻のパスを引数として
        各ノードのスコアを合計しその平均(フェロモン)を返す

        Args:
            path(list(str)): アリが通ったパス

        Returns:
            float: 各エッジに加算することになるフェロモン
        """
        score = 0
        for url in path:
            node = cls.get_node(url)
            score += node.score
        if len(path) == 0:
            return 0
        return score / len(path)

    @classmethod
    def splay_pheromone_by_ant_k(cls, add_pheromone, path):
        """アリkが分泌したフェロモンをパスに添付する

        calc_path_scoresで計算したフェロモンを
        通ったpathのエッジに加算する

        Args:
            add_pheromone(float): 一つあたりのエッジに加算するフェロモン
            path: アリが通ったパス

        Returns:

        """
        with cls.DRIVER.session() as session:
            for i in range(len(path) - 1):
                query = f'MATCH (n1:Node{{url: "{path[i]}"}}) MATCH (n2:Node{{url: ' \
                        f'"{path[i + 1]}"}}) MATCH (n1)-[r:Link]->(n2) SET r.pheromone = r.pheromone + {add_pheromone}'
                session.run(query)

    @classmethod
    def clamp_pheromones(cls, lower, upper):
        """フェロモンのClamp

        Args:
            lower:
            upper:

        Returns:

        """
        cls.set_clamp_all_edges('pheromone', lower, upper)
