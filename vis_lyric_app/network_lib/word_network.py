from pyvis.network import Network
import pandas as pd
import networkx as nx
import community
from . import generate_color

def word_network(df):

    #グラフ化した結果を保存する
        #node_value = それぞれのノードのつながりの数
        #node_cluster = それぞれのノードのクラスタNo.
    result = {"node_value":"","node_cluster":""}

    #データフレームをネットワークに整形
    G = nx.from_pandas_edgelist(df[:200],source = "first_word", target = "second_word", edge_attr = "weight")   

    #クラスタリングを行う
    cluster_G = community.best_partition(G)
    cluster_len = max(cluster_G.values())
    #print(cluster_len)
    #cluster_color = ["crimson","orange","yellow","deeppink","hotpink","greenyellow","red","tomato","orangered","gold","peachpuff","olive","khaki","lime","lightgreen","springgreen","green","cyan","salmon","lightblue","burlywood","dodgerblue","skyblue","deepskyblue","blue","navy","darkolivegreen","magenta","blueviolet","coral","purple","indigo","slategray","gray","black"]
    cluster_color = generate_color.generate_color(cluster_len+1)
    #print(cluster_color)
    #print(cluster_G)

    result["node_cluster"] = cluster_G

    #可視化する
    net = Network(height="700px", width="90%", bgcolor="#FFFFFF", font_color="black", notebook=True)

    #可視化するネットワークのモデルを指定（各ノードが重力を持ったようなモデル）
    net.force_atlas_2based()

    net.from_nx(G)
    
    #各ノードのエッジ情報を確保
    neighbor_map = net.get_adj_list()

    #ノードの大きさをつながりの多さに変更、ノードの色をクラスタの色にする
    node_values = {}
    for node in net.nodes:
        #print(node)
        node_value = len(neighbor_map[node["id"]])
        node["value"] = node_value
        node["color"] = cluster_color[cluster_G[node["id"]]]
        node_values[node["id"]] = node_value
 
    #エッジの大きさをweightに変更
    for edge in net.edges:
        #print(edge)
        edge["value"] = edge["weight"]

    #net.show_buttons(filter_=['physics'])
    
    result["node_value"] = node_values

    return net,result



if __name__ == "__main__":
    print("ネットワークを作成している関数です。主にこのプログラムでネットワークのパラメータを設定します。")