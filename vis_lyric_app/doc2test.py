from gensim.models import Doc2Vec

model = Doc2Vec.load("network_lib/jawiki.doc2vec.dbow300d/jawiki.doc2vec.dbow300d.model")

print(dir(model))
print("neg_labels" in dir(model))
#print(model.infer_vector("こんにちは"))