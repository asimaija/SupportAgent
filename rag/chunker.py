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

    text = load_dataset()

    chunks = chunk_text(text)

    return chunks


if __name__ == "__main__":

    chunks = create_chunks()

    print(f"Total chunks created: {len(chunks)}")

    print("\nFirst chunk:")
    print(chunks[0])

    print("\n*****************")

    print("\nSecond chunk:")
    print(chunks[1])