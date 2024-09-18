import pandas as pd
import collections
from . import word_network
from . import create_word_combs

#共起ネットワーク作成の関数
def kyouki(text,save_path,word_form=[],stopwords=[]):
    """
    :param text : string 共起ネットワークを作りたいテキスト
    :param save_path : string ネットワークの保存先
    :param word_form : array[string,string,...] 取得する単語の語形
    :return result : dict{"node_value":{ノード名:ノードの大きさ}, "node_cluster":{ノード名:ノードのクラスタ番号}}
    """

    #単語の組み合わせ作成
    word_combs = create_word_combs.create_word_combs(text)

    #単語の組み合わせ回数をカウント
    ct = collections.Counter(word_combs)
    
    #データフレームに整形
    df = pd.DataFrame([{"first_word" : i[0][0], "second_word": i[0][1], "weight":i[1]} for i in ct.most_common()])
    
    #ネットワーク化
    got_net,result = word_network.word_network(df)

    #ネットワークの保存
    got_net.show(save_path + "kyouki.html") 

    return got_net,result


#wordcloundの作成 
from wordcloud import WordCloud

def wc(node_value,save_path):
    """
    :param node_value : dict{ノード名：ノードの大きさ} wordcloudに使う単語と、その単語の大きさ
    :param save_path : string 結果を保存するパス
    """

    #日本語用のフォントパス
    font_path = "../font/TakaoPGothic.ttf"

    #wordcloudの設定
    wordcloud = WordCloud(font_path=font_path, width=800, height=400, background_color="white")

    #wordcloudを作成
    wordcloud.generate_from_frequencies(node_value)

    #wordcloudの保存
    wordcloud.to_file(save_path + "wordcloud.png")

    
if __name__ == "__main__":
    print("共起ネットワークとワードクラウドを生成するプログラム。具体的な操作を集約している。")