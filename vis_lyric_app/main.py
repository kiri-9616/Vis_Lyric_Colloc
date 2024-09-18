#ユーザの入力の単語が含まれる曲名のみを抽出
import csv
from network_lib import word_extract
from network_lib import analysis
from network_lib import word_network
import os
import pandas as pd
from pyvis.network import Network
from tqdm import tqdm
from network_lib import openCSV
from network_lib import word_vectorizer
import numpy as np
import time
from network_lib import query_remake
import h5py
import numpy as np
import vector_similarity

DATA_NUM = 100000

vecs = []
lyric_names = []
lyric_texts = []

total_time = 0
start = time.time()

with h5py.File("resource/lyrics_utanet_random.h5", "r") as f:
    for idx in range(DATA_NUM):
        grp = f[str(idx)]
        name = grp.attrs["name"]
        text_words = eval(grp.attrs["text_words"])
        phrase_vecs = grp["phrase_vecs"][:] 

        lyric_names.append(name)
        lyric_texts.append(text_words)
        vecs.append(phrase_vecs)

        if idx % 10000 == 0:
            elapsed_time = time.time()-start
            total_time += elapsed_time
            print(f"{idx} data loaded")
            print(f"time: {elapsed_time} total_time: {total_time} sec")
            start = time.time()

print("Load complete\n")

def main(input1,input2,lang):

    # #言語ごとに読み込むファイルを切り替える
    # csv_path = "resource/"
    
    # #日本語の場合
    # if lang == "jp":
    #     with open(csv_path + "lyrics_utanet_random.csv","r",encoding="utf-8")as f:
    #         reader = csv.DictReader(f)
    #         lyrics = [row for row in reader]

    #     #pbar = tqdm(total=len(lyrics)-1)

    #     #lyrics = lyrics[:10000]

    # #英語の場合
    # elif lang == "eng":
    #     with open(csv_path + "lyrics_engAZ.csv","r",encoding="utf-8")as f:
    #         reader = csv.DictReader(f)
    #         lyrics = [row for row in reader]


    #     pbar = tqdm(total=len(lyrics)-1)
    #     pass

    # print(len(vecs))
    # print(len(lyrics))

    #ユーザの入力を形態素解析
    user_queries = [input1,input2]
    print(user_queries)

    result = {}

    total_time = 0
    start = time.time()
    #各クエリを用いた歌詞検索
    for query in user_queries:

        #クエリをLLMで解釈
        remake_query = query_remake.get_answer(query)

        #クエリを単語に分割
        #ストップワードの準備
        sloth_path = "resource/slothlib.csv"
        stopwords = openCSV.openCSV(sloth_path)
        stopwords.remove([])
        stopwords = [word[0] for word in stopwords]

        # 処理する語形
        word_form = ["名詞", "動詞", "形容詞", "副詞"]

        processed_query = word_extract.word_extract(remake_query,word_form,stopwords)

        #クエリのベクトルを取得
        query_vec = word_vectorizer.infer_vector(processed_query)
        query_vec = np.array(query_vec, dtype=np.float32)

        elapsed_time = time.time()-start
        print(f"query remaked time:{elapsed_time} sec")
        total_time += elapsed_time

        #歌詞をまとめるリスト
        search_result = []

        start = time.time()
        #曲ごとに処理
        for idx, each_vec in enumerate(vecs):
            max_similarity = vector_similarity.batch_max_cosine_similarity(query_vec, each_vec)

            if max_similarity > 0.8:
                search_result.append(idx)

            if idx % 10000 == 0:
                elapsed_time = time.time()-start
                total_time += elapsed_time
                print(f"{idx} data calculated")
                print(f"time: {elapsed_time} sec, total_time: {total_time} sec")
                start = time.time()

        result[query] = search_result
        total_time += time.time() - start
        print("Total time:", total_time)
        start = time.time()

    total_time += time.time() - start
    print("Complete search lyrics from each queries:", total_time)


    #結果の差分や共通部分を取得
    if input2 != "":
        q1andq2 = set(result[input1]) & set(result[input2])
        q1_q2 = set(result[input1]) - set(result[input2])
        q2_q1 = set(result[input2]) - set(result[input1])

        result[input1 + " + " + input2] = q1andq2
        result[input1 + " - " + input2] = q1_q2
        result[input2 + " - " + input1] = q2_q1


    #共起ネットワークの作成
    #保存先の用意
    result_path = "templates/result/"

    return_path = []

    nets = []

    start = time.time()
    #ユーザ入力単語ごとに作成
    for name,idxies in result.items():

        start = time.time()

        print(name)

        #保存先ディレクトリの用意
        save_path = result_path +name
        if not(os.path.isdir(save_path)):
            os.mkdir(save_path)
        save_path = save_path + "/"

        return_path.append({"word":name, "num":len(idxies)})

        #抽出した歌詞をくっつける
        text = []
        for idx in idxies:
            text.extend(lyric_texts[idx])

        #print(text)
            
        # text = ""

        # for each in lyrics:
        #     text = text + each["text"] + "\n"
        print(f"complete combine text.")


        #共起ネットワークの作成

        net,result = analysis.kyouki(text,save_path)
        elapsed_time = time.time()-start
        total_time += elapsed_time
        print(f"complete generate network. elapsed time : {elapsed_time}, total time : {total_time} sec")
        start = time.time()


        # #wordcloudの作成
        # analysis.wc(result["node_value"],save_path)

        nets.append({"net_name":name, "net":net})

    total_time += time.time() - start
    print("Complete generate network:", total_time)

    return return_path,nets


#クエリの単語を含む歌詞名を持つ歌詞集合を取得
#def search_lyrics_word(query,lyrics):
    result = {}
    for each_word in query:
        #print(each_word)
        
        #ユーザ入力単語ごとに操作
        tmp_list = []
        for lyric_data in lyrics:
            
            if each_word in eval(lyric_data["name_words"]):
                tmp_list.append(lyric_data)
                #print(lyric_data["name_words"])

        result[each_word] = tmp_list

    return result

#def search_lyrics_similarity(query,lyrics,vectors):
    sloth_path = "resource/slothlib.csv"
    stopwords = openCSV.openCSV(sloth_path)
    stopwords.remove([])
    stopwords = [word[0] for word in stopwords]

    # 処理する語形
    word_form = ["名詞", "動詞", "形容詞", "副詞"]
    
    #クエリをリメイク
    remake_query = query_remake.get_answer(query)

    #クエリの形態素解析
    processed_query = word_extract.word_extract(remake_query,word_form,stopwords)

    #クエリのベクトルを取得
    query_vec = word_vectorizer.infer_vector(processed_query)

    #歌詞をまとめるリスト
    result = []

    #歌詞ごとの処理
    start = time.time()
    for lyric_idx,lyric_data in enumerate(lyrics[:DATA_NUM]):
        #print(lyric_idx)

        #10000件の歌詞を処理するごとに、処理時間を表示
        if lyric_idx % 10000 == 0:
            end = time.time()
            print(f"{lyric_idx} data finished")
            print(f"elapsed time : {end - start}")
            start = end

        #最大類似度を保存
        max_similarity = 0

        #フレーズごとの処理
        for phrase_vec in vectors[lyric_idx]:
            similarity = np.dot(query_vec, phrase_vec)/(np.sqrt(np.dot(query_vec, query_vec))*np.sqrt(np.dot(phrase_vec, phrase_vec)))
            if similarity > max_similarity:
                max_similarity = similarity

        #類似度が閾値以上のものがあれば保存
        if max_similarity > 0.75:
            result.append(lyric_data)

    return result

#クエリ単語に類似する歌詞を持つ歌詞集合を取得
#def search_lyrics_similarity(querys,lyrics,vectors):
    # stopwordの準備
    sloth_path = "resource/slothlib.csv"
    stopwords = openCSV.openCSV(sloth_path)
    stopwords.remove([])
    stopwords = [word[0] for word in stopwords]

    # 処理する語形
    word_form = ["名詞", "動詞", "形容詞", "副詞"]
    result = {}
    #クエリを形態素解析
    #remake_querys = [query_remake.get_answer(query) for query in querys]
    #クエリをリメイクする場合
    # remake_querys = ["輝く、恋、きゅんきゅん、花びら、羽","冷たい、愛し方なら、見事なさ、遠くへ行って、そよ風"]
    # print(remake_querys)
    # processed_querys = [word_extract.word_extract(query,word_form,stopwords) for query in remake_querys]
    
    #クエリをリメイクしない場合
    processed_querys = [word_extract.word_extract(query,word_form,stopwords) for query in querys]


    #各クエリごとに類似する歌詞を取得
    for idx,each_query in enumerate(processed_querys):
        #print(each_query)
        

        #クエリのベクトルを取得
        query_vec = word_vectorizer.infer_vector(each_query)

        #歌詞をまとめるリスト
        tmp_list = []

        #歌詞ごとの処理
        start = time.time()
        for lyric_idx,lyric_data in enumerate(lyrics[:DATA_NUM]):
            #print(lyric_idx)

            #10000件の歌詞を処理するごとに、処理時間を表示
            if lyric_idx % 10000 == 0:
                end = time.time()
                print(f"{lyric_idx} data finished")
                print(f"elapsed time : {end - start}")
                start = end
                

            #最大類似度を保存
            max_similarity = 0

            #フレーズごとの処理
            for phrase_vec in vectors[lyric_idx]:
                similarity = np.dot(query_vec, phrase_vec)/(np.sqrt(np.dot(query_vec, query_vec))*np.sqrt(np.dot(phrase_vec, phrase_vec)))
                if similarity > max_similarity:
                    max_similarity = similarity



            #類似度が閾値以上のものがあれば保存
            if max_similarity > 0.75:
                tmp_list.append(lyric_data)
                

        result[querys[idx]] = tmp_list
    return result            


#積集合を取る
def matched_net(nets):
    #idから全体で一致するものを抽出
    #グラフのノードの名前を全て取得
    mylist = []
    for net in nets:
        mylist.append([node["id"] for node in net["net"].nodes])

    #共通するノードのみを取得
    result = list(set(mylist[0]) & (set(mylist[1])))

    # print(mylist)
    # print(result)

    return result

#チェックボックスの内容から、差集合をとる
def difference_net(checkbox,nets):
    #差集合の保存先
    differ1_result = []
    differ2_result = []
    #print(checkbox)

    #print(nets)
    
    #checkboxで指定された単語を取得
    for check in checkbox:

        #各ネットワークの中からチェックボックスで選択された単語を含むエッジを取得
        result = []
        for net in nets:
            tmp = [(edge["from"],edge["to"]) for edge in net["net"].edges if edge["from"] == check or edge["to"]==check]
            result.append(tmp)

        #print(result)

        #取得したエッジを昇順に並び替え
        sort1 = [tuple(sorted(words)) for words in result[0]]
        sort2 = [tuple(sorted(words)) for words in result[1]]

        #それぞれの集合特有のエッジ集合を取得
        differ1 = list(set(sort1).difference(set(sort2)))
        differ2 = list(set(sort2).difference(set(sort1)))

        differ1_result.extend(differ1)
        differ2_result.extend(differ2)

        #print(result)

    # print(differ1_result)
    # print(differ2_result)

    #差集合を元にネットワーク図を構築し直す
    #エッジのweightを取り出す
    #differ1から
    df1 = []
    for diff1 in differ1_result:
        for edge in nets[0]["net"].edges:
            word_from = edge["from"]
            word_to = edge["to"]
            if (word_from == diff1[0] and word_to == diff1[1]) or (word_from == diff1[1] and word_to == diff1[0]):
                df1.append({"first_word" : diff1[0], "second_word": diff1[1], "weight":edge["weight"]})
    
    #print(df1)

    #differ2
    df2 = []
    for diff2 in differ2_result:
        for edge in nets[1]["net"].edges:
            word_from = edge["from"]
            word_to = edge["to"]
            if (word_from == diff2[0] and word_to == diff2[1]) or (word_from == diff2[1] and word_to == diff2[0]):
                df2.append({"first_word" : diff2[0], "second_word": diff2[1], "weight":edge["weight"]})
    
    # print(df2)

    #ネットワーク図の保存先を用意
    result_path = "templates/result/"
    name1 = nets[0]["net_name"]
    name2 = nets[1]["net_name"]

    save_name1 = result_path + name1 + "/" + name1 + " - " + name2
    save_name2 = result_path + name2 + "/" + name2 + " - " + name1

    for check in checkbox:
        save_name1 += "_" + check
        save_name2 += "_" + check

    #差集合が存在すれば
    if df1 == [] and df2 == []:
        return ["nothing","nothing"]
    
    elif df1 != [] and df2 != []:
        #共起ネットワークを作成
        df1 = pd.DataFrame(df1)
        df2 = pd.DataFrame(df2)

        net1,result1 = word_network.word_network(df1)
        net2,result2 = word_network.word_network(df2)

        net1.show(save_name1 + "kyouki.html") 
        net2.show(save_name2 + "kyouki.html")

        save_name1 = save_name1.lstrip("templates/")
        save_name2 = save_name2.lstrip("templates/")

        return [save_name1 + "kyouki.html",save_name2 + "kyouki.html"]
    
    elif df1 != [] and df2 == []:
        df1 = pd.DataFrame(df1)
        net1,result1 = word_network.word_network(df1)
        net1.show(save_name1 + "kyouki.html") 
        save_name1 = save_name1.lstrip("templates/")
        return [save_name1 + "kyouki.html","nothing"]
    
    elif df1 == [] and df2 != []:
        df2 = pd.DataFrame(df2)
        net2,result2 = word_network.word_network(df2)
        net2.show(save_name2 + "kyouki.html") 
        save_name2 = save_name2.lstrip("templates/")
        return ["nothing",save_name2 + "kyouki.html"]



if __name__ == "__main__":
    print("please write some words")
    user_input1 = input()
    user_input2 = input()
    path,nets = main(user_input1,user_input2)
    print(nets)
    intersec = matched_net(nets)
    difference_net(intersec[0:3],nets)
 