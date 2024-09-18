import MeCab
import neologdn
import re
import nltk
from nltk.corpus import wordnet,stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import string

# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download("stopwords")

tagger = MeCab.Tagger("/opt/homebrew/lib/mecab/dic/mecab-ipadic-neologd")
stopwords = set(stopwords.words('english'))

# WordNetLemmatizerの初期化
lemmatizer = WordNetLemmatizer()

def word_extract(text,word_form=[],stopwords=[]):
    """
    特定語形単語の抽出

    :param text: string 共起行列を作成するテキスト
    :param word_form: array 取得したい語形
    :return : array 
    """

    # MeCabのインスタンスを作成

    #テキストを正規化
    text = neologdn.normalize(text)

    #ストップワードの設定
    stopwords2 = stopwords + ["\u3000"]

    # 形態素解析して単語を抽出
    node = tagger.parseToNode(text)
    words = []
    while node:
        feature = node.feature.split(",")
        #print(node.surface, feature)

        #単語以外や、非自立の単語を取り除く
        if node.surface != "" and feature[0] != "BOS/EOS" and "非" not in feature[1]:

            #word_formの指定がない場合、全ての単語を抽出
            if word_form == []:
                if len(feature) >= 7 and feature[7] not in stopwords2:
                    words.append(feature[7])
                    #print(feature[7])
                elif node.surface not in stopwords2:
                    words.append(node.surface)

            #word_formの指定がある場合、word_formで指定された語形のみを抽出
            elif feature[0] in word_form:
                if not(re.fullmatch('[a-zA-Z]+', node.surface)):
                    if len(feature) >= 7 and feature[7] not in stopwords2:
                        words.append(feature[7])
                        #print(feature[7])
                    elif node.surface not in stopwords2:
                        words.append(node.surface)

        node = node.next

    return words

def word_extract_eng(text,word_form=[],stopword_flag=True):
    # 小文字に変換
    text = text.lower()
    
    # 句読点の除去
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # 単語トークン化
    words = word_tokenize(text)

    # ストップワードを使用するかどうか
    if stopword_flag:
        #単語の原型を抽出
        lemmatized_words = [lemmatizer.lemmatize(word, get_wordnet_pos(word)) for word in words if word not in stopwords]
    else:
        lemmatized_words = [lemmatizer.lemmatize(word, get_wordnet_pos(word)) for word in words if word]
    
    return lemmatized_words


def get_wordnet_pos(word):
    # WordNetの品詞タグを取得
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}
    
    return tag_dict.get(tag, wordnet.NOUN)


if __name__ == "__main__":
    print(word_extract("この関数では、入力したテキストの単語の原型を確認できます。抽出する語形も制限可能です。"))

    input_text = "I am running in the park, and I will be swimming later. It's a beautiful day."
    lemmatized_text = word_extract_eng(input_text)
    print(lemmatized_text)