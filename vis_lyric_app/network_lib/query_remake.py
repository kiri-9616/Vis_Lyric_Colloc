from llama_cpp import Llama
import os
import time

module_path = os.path.dirname(__file__)

llm = Llama(
        model_path=module_path + "/../resource/ELYZA-japanese-Llama-2-7b-fast-instruct-q4_0.gguf",
        # n_gpu_layers=-1, # Uncomment to use GPU acceleration
        # seed=1337, # Uncomment to set a specific seed
        # n_ctx=2048, # Uncomment to increase the context window
    )

def get_answer(query):

    start = time.time()

    sys_msg = "あなたは作詞者です。次の入力文章を歌詞にする際に想起される単語を５つ挙げてください。\n\
    以下のルールに従うこと。従わない場合、ペナルティが与えられる。\n\
    ・単語の区切りには空白を使用すること。\n\
    ・出力は文章ではないこと。\n\
    ・単語のみを出力すること。\n\
    ・出力は5つの異なる単語であること。\n"

    prompt = "###指示:" +  sys_msg + "\n\n" + "###入力:" + query + "\n\n" + "###出力:"

    print(prompt)

    output = llm(
        prompt,  # Prompt
        max_tokens=16,  # Generate up to 32 tokens, set to None to generate up to the end of the context window
        stop=["###指示:","\n\n###入力"],  # Stop generating just before the model would generate a new question
        echo=True  # Echo the prompt back in the output
    )  # Generate a completion, can also call create_completion
    try:
        result = output["choices"][0]["text"].split("###出力:")[1]
    except:
        result = output["choices"][0]["text"]
    
    print(result)
    print("time:", time.time()-start)
    return result

if __name__ == "__main__":
    while True:
        query = input("質問を入力してください:")

        #０を入力すると終了
        if query == "0":
            break

        print(get_answer(query))