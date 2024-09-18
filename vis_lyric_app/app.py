from flask import Flask, render_template, request, redirect, url_for
import time
import csv
import main

#appの始まり            
app = Flask(__name__)

global_nets = []

#vecs = main.read_vecs()

#最初のページの内容
@app.route('/', methods=['GET', 'POST'])
def index():
    global global_nets
    #global vecs

    if request.method == 'POST':
        user_input1 = request.form['user_input1']
        user_input2 = request.form["user_input2"]
        lang = request.form["lang_option"]
        analysis_result,intersec,nets = perform_analysis(user_input1,user_input2,lang)
        global_nets = nets
        buttons = generate_buttons(analysis_result)
        checkboxes = generate_checkboxes(intersec)
        return render_template('analyzed.html', buttons=buttons,checkboxes = checkboxes, nets = nets)
    return render_template('index.html')

#分析内容
def perform_analysis(input_text1,input_text2,lang):
    #ユーザ入力から共起ネットワークを作成
    result,nets = main.main(input_text1,input_text2,lang)

    if len(nets) == 1:
        intersection = []
    #共起ネットワークの積集合を取得
    else:
        intersection = main.matched_net(nets)
    return result,intersection,nets

#分析結果よりボタンを作成
def generate_buttons(result):
    #入力単語の形態素の数だけ分析
    buttons = []

    #ボタンの内容を作成
    for each in result:
        buttons.append({"text":each["word"] + " " + str(each["num"]) + "件", "url": url_for("button_action", word = each["word"])})
    return buttons

#積集合のラベルを作成
def generate_checkboxes(intersec):
    checkboxes = []
    for word in intersec:
        checkboxes.append({'name': word, 'label': word})
    return checkboxes

#各ボタンのページの内容
@app.route('/<word>')
def button_action(word):
    return render_template("result/"+word+"/kyouki.html")


#チェックボックスの内容を受け取る部分
@app.route('/analyzed/<nets>', methods = ['GET', 'POST'])
def analyzed(nets):
    if request.method == "POST":
        global global_nets
        selected_checkboxes = request.form.getlist('options')
        result_path = main.difference_net(selected_checkboxes,global_nets)

        content = []
        count = 0
        for result in result_path: 
            count += 1         
            if result == "nothing":
                content.append("差分はありません")
            else:
                with open("templates/" + result,"r")as f:
                    html = f.read()

                if count == 2:
                    html = html.replace("mynetwork","mynetwork2")
                    html = html.replace("drawGraph","drawGraph2")
                content.append(html)

        name1 = global_nets[0]["net_name"]
        name2 = global_nets[1]["net_name"]

        return render_template("result.html", content1 = content[0], content2 = content[1], name1 = name1, name2 = name2)

if __name__ == '__main__':
    app.run(debug=True,use_reloader=False,port=5000,host="0.0.0.0")
