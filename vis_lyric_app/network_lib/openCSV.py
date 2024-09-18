import csv

#csvファイルを読み込み、データをリストに格納する関数
def openCSV(path):
    with open(path,"r",encoding="utf-8")as f:
        reader = csv.reader(f)
        result = [row for row in reader]

    return result

if __name__ == "__main__":
    print("csvファイルを開くための関数です。")