from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

from langchain_text_splitters import RecursiveCharacterTextSplitter

from data.dataset import load_dataset


CHUNK_SIZE = 500
OVERLAP = 50
N_CLUSTERS = 5



_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=OVERLAP,
    separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
)


def chunk_text(text):
    return _splitter.split_text(text.strip())


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