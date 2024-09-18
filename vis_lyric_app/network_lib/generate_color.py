#ランダムな色を選択された数だけ生成するプログラム
import random

def generate_color(num):
    #結果を格納するリスト
    result = []

    #指定された回数だけ色を作る
    count = 0
    while(count < num):

        #ランダムにrgbの値を生成
        color = [random.randint(0,255) for i in range(3)]

        #pyvisが読み込める形に加工
        rgb_color = "rgb("

        for each in color:
            rgb_color = rgb_color + str(each) + ","

        rgb_color = rgb_color.rstrip(",")
        rgb_color = rgb_color + ")"

        if not(rgb_color in result):
            result.append(rgb_color)
            count += 1
            #print("ok")

    
    return result
    
if __name__ == "__main__":
    print("ランダムにrgbのカラーを0~255の整数値で作成する関数です。")
    result = generate_color(3)
    print(result)