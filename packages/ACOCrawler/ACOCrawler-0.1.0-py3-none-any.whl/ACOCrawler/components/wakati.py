import MeCab

select_conditions = ["動詞", "形容詞", "名詞"]

tagger = MeCab.Tagger('')
tagger.parse('')


class Wakati:
    """分かちクラス

    文書を分かちてうれしい
    """

    @classmethod
    def wakati_text(cls, text):
        """textを分かちた結果を返す

        文書を受け取り、Mecabで形態素解析する。
        その後、品詞が有望なものだけ配列に入れて
        最後に半角スペース空けにして一行の文字列で返す

        Args:
            text(str): 文書body

        Returns:
            str: 分かたれた文書wakati
        """

        node = tagger.parseToNode(text)
        terms = []

        while node:

            term = node.surface

            pos = node.feature.split(',')[0]

            if pos in select_conditions:
                terms.append(term)

            node = node.next

        result = ' '.join(terms)
        return result
