from data.dataset import load_dataset

chunk_size = 500
overlap = 50


def chunk_text(text):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk)

        start = start + chunk_size - overlap

    return chunks


def create_chunks():
    df = load_dataset()
    documents = []

    for _, row in df.iterrows():
        chunks = chunk_text(row["content"])

        for chunk in chunks:
            documents.append(chunk)

    return documents


if __name__ == "__main__":
    chunks = create_chunks()

    print(f"Total chunks created: {len(chunks)}")

    print("\nFirst  chunk:")
    print(chunks[1])
    print("*****************")
    print("\nSecond chunk:")
    print(chunks[2])