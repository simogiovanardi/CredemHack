import vertexai
from vertexai.language_models import TextEmbeddingModel

PROJECT_ID = credemhack-iam
REGION = us
MODEL_ID = MODEL_ID


vertexai.init(project=PROJECT_ID, location=REGION)

model = TextEmbeddingModel.from_pretrained(MODEL_ID)
embeddings = model.get_embeddings(...)