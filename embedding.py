import vertexai
from vertexai.language_models import TextEmbeddingModel
import os
from sklearn.cluster import KMeans

PROJECT_ID = "credemhack-iam"
REGION = "us-central1"


vertexai.init(project=PROJECT_ID, location=REGION)

ocr_folder = "ocr_output"
texts = []
file_names = []

for fname in os.listdir(ocr_folder):
    if fname.endswith(".txt"):
        with open(os.path.join(ocr_folder, fname), "r", encoding="utf-8") as f:
            texts.append(f.read())
            file_names.append(fname)

            model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")

# You can batch them to avoid timeouts — e.g., 5 at a time
embeddings = []
batch_size = 5

for i in range(0, len(texts), batch_size):
    batch = texts[i:i + batch_size]
    response = model.get_embeddings(batch)
    for r in response:
        embeddings.append(r.values)  # r.values is a list of floats


kmeans = KMeans(n_clusters=10, random_state=42)
labels = kmeans.fit_predict(embeddings)

for fname, label in zip(file_names, labels):
    print(f"{fname} => Cluster {label}")
