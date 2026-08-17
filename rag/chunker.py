import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

from data.dataset import load_dataset


CHUNK_SIZE = 500
OVERLAP = 50
N_CLUSTERS = 5


def split_sentences(text):
    return re.split(r'(?<=[.!?])\s+', text.strip())


def chunk_text(text):

    sentences = split_sentences(text)

    chunks = []
    current = ""

    for sentence in sentences:

        if len(current) + len(sentence) <= CHUNK_SIZE:
            current += sentence + " "

        else:
            chunks.append(current.strip())

            # Keep last 50 characters as overlap
            overlap = current[-OVERLAP:]

            current = overlap + " " + sentence

    if current.strip():
        chunks.append(current.strip())

    return chunks


def cluster_chunks(chunks):

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    vectors = vectorizer.fit_transform(chunks)

    k = min(N_CLUSTERS, len(chunks))

    model = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10
    )

    labels = model.fit_predict(vectors)

    return labels


def create_chunks():

    text = load_dataset()

    chunks = chunk_text(text)

    labels = cluster_chunks(chunks)

    result = []

    for i, chunk in enumerate(chunks):

        result.append({
            "chunk_id": i,
            "cluster": int(labels[i]),
            "text": chunk
        })

    return result


if __name__ == "__main__":

    chunks = create_chunks()

    print("Total chunks:", len(chunks))

    for cluster in sorted(set(c["cluster"] for c in chunks)):

        count = sum(
            1 for c in chunks
            if c["cluster"] == cluster
        )

        print(f"Cluster {cluster}: {count} chunks")

    print("\nFirst chunk:")
    print(chunks[0]["text"])

    print("\nCluster:", chunks[0]["cluster"])