BASE = 20


class Score:
    """スコアクラス

    自然言語処理を使って
    各文書・文書間のスコアを計算する


    Todo:
        * NLPの計算方法があっていないかも
        * 名前定義が少し微妙かも

    """

    @classmethod
    def calc_score_by_simple_counts(cls, body, wakati, keyword, **kwargs):
        """スコアを単純なキーワードカウントで計算する

        文書Bodyに、kwargs['keyword']が何回含まれているか？
        で判定する。
        そのため、keywords = kwags['keyword']は手動で設定する必要がある。

        Args:
            body(str): 文書
            wakati(str): 分かたれた文書
            keyword(str): キーワード
            **kwargs(dict): keywordsをキーとしてキーワードに関する配列

        Returns:
            float: スコア
        """
        score = 0
        for word in kwargs['keywords']:
            score += body.count(word)
        if len(body) != 0:
            score /= len(body)
        else:
            score = 0
        return score
