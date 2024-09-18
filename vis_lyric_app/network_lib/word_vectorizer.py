#形態素解析した結果をdoc2vecでベクトル化する

#自作ライブラリをインポート
import sys
import os
# print(sys.path)

#ライブラリのインポート
from gensim.models.doc2vec import Doc2Vec
import csv
from . import word_extract
#import word_extract
import time
import os
from . import openCSV
#import openCSV
import numpy as np

#モデルの読み込み
module_path = os.path.dirname(__file__)
model_path = module_path + "/jawiki.doc2vec.dbow300d/jawiki.doc2vec.dbow300d.model"
start = time.time()
model = Doc2Vec.load(model_path)
elapsed_time = time.time() - start
print ("model_load_elapsed_time:{0}".format(elapsed_time) + "[sec]")

#配列に格納された２つの文書の類似度を計算する
def calc_similarity(vec1, vec2):
    # #類似度を計算
    # start = time.time()
    # similarity = model.docvecs.similarity_unseen_docs(model, doc1, doc2,alpha=1, min_alpha=0.0001, steps=5)
    # elapsed_time = time.time() - start
    # print ("calc_similarity_elapsed_time:{0}".format(elapsed_time) + "[sec]")
    # print(similarity)

    # #doc1,doc2をベクトル化
    # vec1 = model.infer_vector(doc1)
    # vec2 = model.infer_vector(doc2)

    # print(len(vec1))

    #cos類似度を計算
    start = time.time()
    #similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    similarity = np.dot(vec1, vec2)/(np.sqrt(np.dot(vec1, vec1))*np.sqrt(np.dot(vec2, vec2)))
    elapsed_time = time.time() - start
    print ("calc_similarity_elapsed_time:{0}".format(elapsed_time) + "[sec]")
    print(similarity)




    return similarity

def infer_vector(doc):
    #docをベクトル化
    vec = model.infer_vector(doc)
    return vec


if __name__ == "__main__":
    #テスト
    
    # stopwordの準備
    sloth_path = "../resource/slothlib.csv"
    stopwords = openCSV.openCSV(sloth_path)
    stopwords.remove([])
    stopwords = [word[0] for word in stopwords]

    # 処理する語形
    word_form = ["名詞", "動詞", "形容詞", "副詞"]


    # doc1 = "女性の主人公が片想いを伝える楽曲"
    # doc2 = "例えば君の顔に昔よりシワが増えても　それでもいいんだ"\
    #     "僕がギターを思うように弾けなくなっても　心の歌は君で溢れているよ"\
    #     "高い声も出せずに思い通り歌えない"\
    #     "それでもうなずきながら一緒に歌ってくれるかな"\
    #     "割れんばかりの拍手も　響き渡る歓声もいらない"\
    #     "君だけ　分かってよ　分かってよ"\
    #     "Darlin'　夢が叶ったの"\
    #     "お似合いの言葉が見つからないよ"\
    #     "Darlin'　夢が叶ったの"\
    #     "「愛してる」"
    
    # doc1 = word_extract.word_extract(doc1,word_form,stopwords)
    # doc2 = word_extract.word_extract(doc2,word_form,stopwords)

    # vec1 = model.infer_vector(doc1)
    # vec2 = model.infer_vector(doc2)

    # print(calc_similarity(vec1, vec2))
    


    #utanetの歌詞をベクトル化し、csvファイルに保存
    #データの読み込み
    with open("../resource/lyrics_utanet_ver3.csv","r")as f:
        reader = csv.DictReader(f)
        lyrics = [row for row in reader]

    #result = []
    result = []
    count = 0
    memory = 0
    start = time.time()
    #各フレーズに対し操作
    for lyric_data in lyrics:
        # lyric_name = lyric_data["name"]
        # artist = lyric_data["artist"]

        #歌詞の各フレーズをベクトル化
        vecs = []
        for text in eval(lyric_data["text_words"]):
            vec = model.infer_vector(text)
            vecs.append(tuple(vec))
        
        # result.append({"name":lyric_name,"artist":artist,"vec":vecs})
        result.append(tuple(vecs))
        

        #print(len(vecs))

        count += 1
        if count % 1000 == 0:
            end_time = time.time()
            elapsed_time = end_time - start
            print(f"{count} data finished, {elapsed_time} second")
            start = end_time

            
            #resultのメモリサイズを求める
            # memory += sys.getsizeof(result)
            # for ly in result:
            #     memory += sys.getsizeof(ly)
            #     for ph in ly:
            #         memory += sys.getsizeof(ph)
            #         for v in ph:
            #             memory += sys.getsizeof(v)
            # print(f"result memory size : {memory}")

                

            if count == 1000:
            #     # with open("../resource/lyrics_utanet_vec.csv","w")as f:
            #     #     csv_writer = csv.DictWriter(f, ["name", "artist", "vec"])
            #     #     csv_writer.writeheader()
            #     #     csv_writer.writerows(result)

                with open("../resource/lyrics_utanet_vec_ver2.csv","w")as f:
                    csv_writer = csv.writer(f)
                    for ly in result:
                        for ph in ly:
                            csv_writer.writerow(ph)
                        #一曲が終わったことを示す区切り
                        csv_writer.writerow("1")

            else:
            #     # with open("../resource/lyrics_utanet_vec.csv","a")as f:
            #     #     csv_writer = csv.DictWriter(f, ["name", "artist", "vec"])
            #     #     csv_writer.writerows(result)

                with open("../resource/lyrics_utanet_vec_ver2.csv","a")as f:
                    csv_writer = csv.writer(f)
                    for ly in result:
                        for ph in ly:
                            csv_writer.writerow(ph)
                        #一曲が終わったことを示す区切り
                        csv_writer.writerow("1")

            result = []
            
    with open("../resource/lyrics_utanet_vec_ver2.csv","a")as f:
        csv_writer = csv.writer(f)
        for ly in result:
            for ph in ly:
                csv_writer.writerow(ph)
            #一曲が終わったことを示す区切り
            csv_writer.writerow("1")

    # start = time.time()
    # np.save("../resource/lyrics_utanet_vec.npy",np.array(result, dtype=object))
    # end = time.time()
    # print(f"{end - start} second")

    # #ベクトル化した歌詞をcsvファイルに保存
    # with open("../resource/lyrics_utanet_vec.csv","w")as f:
    #     csv_writer = csv.DictWriter(f, ["name", "artist", "vec"])
    #     csv_writer.writeheader()
    #     csv_writer.writerows(result)

        


