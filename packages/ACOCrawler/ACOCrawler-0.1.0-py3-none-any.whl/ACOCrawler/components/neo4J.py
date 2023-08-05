from neo4j import GraphDatabase
from string import Template

from .node import Node

NEO4J_URL = 'bolt://localhost:7687'
NEO4J_ACCOUNT = 'neo4j'
NEO4J_PASSWORD = 'neo4jj'


class Neo4j:
    DRIVER = GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_ACCOUNT, NEO4J_PASSWORD))

    @classmethod
    def is_already_node(cls, url):
        """ すでにノードがあるか？

        Args:
            url(str):

        Returns:

        """
        query = f'MATCH (n:Node{{url:"{url}"}}) return COUNT(n)'
        with cls.DRIVER.session() as session:
            for record in session.run(query):
                return record[0] > 0

    @classmethod
    def is_already_edge(cls, from_url, to_url):
        """すでにエッジがあるか？

        Args:
            from_url:
            to_url:

        Returns:

        """
        query = f'MATCH (n1:Node{{url:"{from_url}"}}), (n2:Node{{url:"{to_url}"}}), (n1)-[r:Link]->(n2) return COUNT(r);'
        with cls.DRIVER.session() as session:
            for record in session.run(query):
                return record[0] > 0

    @classmethod
    def create_node(cls, node):
        """ノードを作る

        Args:
            node(Node):

        Returns:

        """
        anchors = node.anchors
        anchors_text = ['"' + anchor + '"' for anchor in anchors]
        anchors_text = ','.join(anchors_text)

        query = f'MERGE (:Node{{' \
                f'url:"{node.url}", ' \
                f'domain:"{node.domain}", ' \
                f'title:"{node.title}", ' \
                f'anchors: [{anchors_text}], ' \
                f'body: "{node.body}", ' \
                f'wakati:"{node.wakati}", ' \
                f'score:{node.score}, ' \
                f'is_expanded:{node.is_expanded}, ' \
                f'visit_times: {node.visit_times}, ' \
                f'created: {node.created}, ' \
                f'updated: {node.updated}' \
                f'}})'
        with cls.DRIVER.session() as session:
            session.run(query)

    @classmethod
    def create_edge(cls, from_url, to_url, pheromone, heuristic, similarity):
        """エッジを作る

        Args:
            from_url(str):
            to_url(str):
            pheromone(float): フェロモン値。外側で計算しておく。
            heuristic(float): ヒューリスティック値。外側で計算しておく。
            similarity(float): fromとtoの文書間類似度。

        Returns:

        """
        template = Template(
            'MATCH (n1:Node{url:"${from_url}"}), (n2:Node{url:"${to_url}"}) CREATE (n1)-[:Link{edge_id: "${edge_id}", pheromone:${pheromone}, heuristic: ${heuristic}, similarity: ${similarity}, from_url:"${from_url}", to_url: "${to_url}", pass_times: ${pass_times}}]->(n2);')
        query = template.substitute(from_url=from_url, to_url=to_url, edge_id=from_url + to_url, pheromone=pheromone,
                                    heuristic=heuristic, similarity=similarity, pass_times=0)
        with cls.DRIVER.session() as session:
            session.run(query)

    @classmethod
    def set_node(cls, url, key, value):
        """ノードのキーにプロパティをセットする

        Args:
            url:
            key:
            value:

        Returns:

        """
        query = f'MATCH (n:Node{{url:"{url}"}}) SET n.{key} = {value}'
        with cls.DRIVER.session() as session:
            session.run(query)

    @classmethod
    def add_value_node(cls, url, key, value):
        """ノードのキーの値を加算する

        Args:
            url:
            key:
            value:

        Returns:

        """
        query = f'MATCH (n:Node{{url:"{url}"}}) SET n.{key} = n.{key} + {value}'
        with cls.DRIVER.session() as session:
            session.run(query)

    @classmethod
    def add_value_edge(cls, from_url, to_url, key, value):
        """エッジのキーの値を加算する

        Args:
            url:
            key:
            value:

        Returns:

        """
        query = f'MATCH (n1:Node{{url:"{from_url}"}}), (n2:Node{{url:"{to_url}"}}), (n1)-[r:Link]->(n2) SET r.{key} = r.{key} + {value}'
        with cls.DRIVER.session() as session:
            session.run(query)

    @classmethod
    def get_node(cls, url):
        """ノードを取り出す

        Args:
            url:

        Returns:
            Node: ノードを返す
        """
        query = f'MATCH (n:Node{{url:"{url}"}}) return n'
        with cls.DRIVER.session() as session:
            for record in session.run(query):
                node = Node(**record[0])
                return node

    @classmethod
    def get_anchors(cls, url):
        """urlの文書に含まれるアンカー配列を返す

        Args:
            url:

        Returns:
            list(str): URL配列を返す
        """
        query = f'MATCH (n:Node{{url:"{url}"}}) MATCH (n)-[r:Link]->(to:Node) return r, to'
        anchors = []
        with cls.DRIVER.session() as session:
            for record in session.run(query):
                data = {
                    'to_url': record[0].nodes[1]['url'],
                    'heuristic': record[0]['heuristic'],
                    'pheromone': record[0]['pheromone']
                }
                anchors.append(data)
        return anchors

    @classmethod
    def get_nodes_properties(cls, *args):
        """すべてのレコードで、キーで選んだプロパティを辞書配列で返す

        Args:
            *args: 取り出したいキーの文字列配列

        Returns:
            辞書配列
        """
        query = f'MATCH(n:Node) RETURN n order by n.created ASC;'
        results = []
        with cls.DRIVER.session() as session:
            for record in session.run(query):
                props = {}
                for key in args:
                    props[key] = record[0][key]
                results.append(props)
        return results

    @classmethod
    def get_records_properties(cls, *args):
        """すべてのエッジレコードで、キーで選んだプロパティを辞書配列で返す

        Args:
            *args: 取り出したいキーの文字列配列

        Returns:
            dict: 辞書配列
        """
        query = f'MATCH (n:Node) , (n)-[r:Link]->() return r;'
        results = []
        with cls.DRIVER.session() as session:
            for record in session.run(query):
                props = {}
                for key in args:
                    props[key] = record[0][key]
                results.append(props)
        return results

    @classmethod
    def count_nodes(cls):
        query = f'MATCH(n:Node) return COUNT(n);'
        with cls.DRIVER.session() as session:
            for record in session.run(query):
                return record[0]

    @classmethod
    def count_edges(cls):
        query = f'MATCH (n:Node)-[r:Link]->() return COUNT(r);'
        with cls.DRIVER.session() as session:
            for record in session.run(query):
                return record[0]

    @classmethod
    def set_mul_all_edges(cls, key, value):
        """エッジのキーにvalueをかける

        Args:
            key(str):
            value(float):

        Returns:

        """
        query = f'MATCH ()-[r:Link]->() SET r.{key} = r.{key} * {value}'
        with cls.DRIVER.session() as session:
            session.run(query)

    @classmethod
    def set_clamp_all_edges(cls, key, lower, upper):
        """エッジすべてにClampをする

        Args:
            key:
            lower:
            upper:

        Returns:

        """
        query = f'MATCH ()-[r:Link]->() SET r.{key} = CASE WHEN r.{key} < {lower} THEN {lower} WHEN r.{key} > {upper} THEN {upper}  ELSE r.{key} end'
        with cls.DRIVER.session() as session:
            session.run(query)
