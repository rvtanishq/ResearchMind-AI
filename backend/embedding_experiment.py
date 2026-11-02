from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

texts = [
    "The system detects tumors in medical images.",
    "A neural network identifies cancer from scans.",
    "The weather will be sunny tomorrow.",
]

embeddings = model.encode(texts)

print("Embedding shape:", embeddings.shape)

similarities = model.similarity(embeddings, embeddings)

print(similarities)