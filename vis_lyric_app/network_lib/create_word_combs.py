import itertools
from . import word_extract
from tqdm import tqdm

def create_word_combs(text,word_form=[],stopwords=[]):
    """
    単語の組み合わせを作成

    :param text: string 共起行列を作成するテキスト
    :param word_form: array 取得したい語形
    :return : array[(word1,word2),....]
    """
    #テキストの分割
    #split_text = text.split("。")
    #split_text = text.split("\n")
    #split_text = text.split(" ")
    #split_text = [i for i in split_text if i != ""]

    split_text = text

    #print(split_text)


    #pbar = tqdm(total=len(split_text))

    #単語の組み合わせを作成
    word_combs = []
    for each in split_text:
        #テキストをmecabで分割（戻り値：list[word1,word2,word3...]）
        #sentence = word_extract.word_extract(each,word_form,stopwords)
        sentence = each

        #重複した語を削除
        sentence = list(set(sentence))

        comb = (list(itertools.combinations(sentence,2)))

        #単語の組み合わせをソートする。 (A,B)と(B,A)を統一
        sorted_comb = [tuple(sorted(words)) for words in comb]
        #print(sorted_comb)

        word_combs.extend(sorted_comb)

        #pbar.update(1)

    return word_combs


if __name__ == "__main__":
    
    text = "同じ行に登場する単語の組み合わせを作成する関数です"

    word_combs = create_word_combs(text,["名詞","動詞"])
    print(word_combs)