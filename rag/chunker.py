import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

from data.dataset import load_dataset


chunk_size = 1200
overlap = 150
n_clusters = 5  # tweak based on how many topics you expect in your corpus


# ---------------------------------------------------------------------------
# Sentence-aware chunking
# ---------------------------------------------------------------------------

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])")


def split_sentences(text):
    text = text.strip()
    if not text:
        return []
    sentences = _SENTENCE_SPLIT_RE.split(text)
    return [s.strip() for s in sentences if s.strip()]


def chunk_text(text):
    sentences = split_sentences(text)
    if not sentences:
        return []

    chunks = []
    current_sentences = []
    current_len = 0

    def flush():
        chunk = " ".join(current_sentences).strip()
        if chunk:
            chunks.append(chunk)

    for sentence in sentences:
        sentence_len = len(sentence) + 1

        if current_sentences and current_len + sentence_len > chunk_size:
            flush()

            overlap_sentences = []
            overlap_len = 0
            for s in reversed(current_sentences):
                s_len = len(s) + 1
                if overlap_len + s_len > overlap and overlap_sentences:
                    break
                overlap_sentences.insert(0, s)
                overlap_len += s_len

            current_sentences = overlap_sentences
            current_len = overlap_len

        current_sentences.append(sentence)
        current_len += sentence_len

    flush()

    return chunks


# ---------------------------------------------------------------------------
# Document loading helper
# ---------------------------------------------------------------------------

_PAGE_SPLIT_RE = re.compile(r"(?=^TITLE:\s)", re.MULTILINE)
_SOURCE_LINE_RE = re.compile(r"^SOURCE:\s*(\S+)", re.MULTILINE)


def _split_scraped_pages(text):
    """
    Some scrapers concatenate multiple pages into a single string, each
    formatted like:

        TITLE: <page title>
        SOURCE: <url>

        <page body>

    This splits that concatenation back into separate (doc_id, text) pages,
    using the SOURCE url (or title) as the doc_id. Returns [] if the text
    doesn't look like this format.
    """
    if not text.strip().startswith("TITLE:"):
        return []

    blocks = [b.strip() for b in _PAGE_SPLIT_RE.split(text) if b.strip()]
    if len(blocks) <= 1:
        return []

    docs = []
    for i, block in enumerate(blocks):
        match = _SOURCE_LINE_RE.search(block)
        doc_id = match.group(1) if match else f"doc_{i}"
        docs.append((doc_id, block))
    return docs


def load_documents():
    """
    Normalize load_dataset()'s output into a list of (doc_id, text) pairs.

    Handles the common shapes:
      - a single string containing multiple "TITLE:"/"SOURCE:" scraped pages
        (split into one document per page)
      - a single string (one document)
      - a list of strings
      - a dict of {doc_id: text}
      - a list of dicts with a "text" (or "content") field
    """
    raw = load_dataset()

    if isinstance(raw, str):
        pages = _split_scraped_pages(raw)
        if pages:
            return pages
        return [("doc_0", raw)]

    if isinstance(raw, dict):
        return [(str(k), v) for k, v in raw.items()]

    if isinstance(raw, list):
        docs = []
        for i, item in enumerate(raw):
            if isinstance(item, str):
                docs.append((f"doc_{i}", item))
            elif isinstance(item, dict):
                text = item.get("text") or item.get("content") or ""
                doc_id = item.get("id", f"doc_{i}")
                docs.append((str(doc_id), text))
        return docs

    raise ValueError(f"Unrecognized dataset format: {type(raw)}")


# ---------------------------------------------------------------------------
# Document clustering
# ---------------------------------------------------------------------------

def cluster_documents(docs, k=n_clusters):
    """
    Cluster documents by topical similarity using TF-IDF + KMeans.

    docs: list of (doc_id, text)
    returns: dict mapping cluster_label -> list of (doc_id, text)
    """
    texts = [text for _, text in docs]

    # Guard against having fewer documents than clusters
    k = min(k, len(texts)) or 1

    # max_df / min_df as fractions only make sense with enough documents;
    # with a tiny corpus they can contradict each other (e.g. max_df=0.95
    # excluding terms that min_df=1 requires). Fall back to no filtering
    # when there aren't enough documents for it to be meaningful.
    if len(texts) >= 5:
        vectorizer = TfidfVectorizer(
            max_df=0.95,
            min_df=1,
            stop_words="english",
        )
    else:
        vectorizer = TfidfVectorizer(stop_words="english")

    matrix = vectorizer.fit_transform(texts)

    if matrix.shape[1] == 0:
        raise ValueError(
            f"TF-IDF produced an empty vocabulary from {len(texts)} document(s). "
            "Check that load_documents() is returning real document text "
            "(not empty strings), and that documents aren't only stop words."
        )

    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(matrix)

    clusters = {}
    for (doc_id, text), label in zip(docs, labels):
        clusters.setdefault(int(label), []).append((doc_id, text))

    return clusters


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def create_chunks():
    """
    Cluster documents first, then chunk within each cluster.

    returns: list of chunk dicts:
        {"cluster": int, "doc_id": str, "chunk_index": int, "text": str}
    """
    docs = load_documents()
    clusters = cluster_documents(docs)

    all_chunks = []
    for cluster_label in sorted(clusters.keys()):
        for doc_id, text in clusters[cluster_label]:
            doc_chunks = chunk_text(text)
            for i, chunk in enumerate(doc_chunks):
                all_chunks.append(
                    {
                        "cluster": cluster_label,
                        "doc_id": doc_id,
                        "chunk_index": i,
                        "text": chunk,
                    }
                )

    return all_chunks


if __name__ == "__main__":
    chunks = create_chunks()

    doc_ids = {c["doc_id"] for c in chunks}
    cluster_labels = {c["cluster"] for c in chunks}

    print(f"Total documents: {len(doc_ids)}")
    print(f"Total clusters: {len(cluster_labels)}")
    for label in sorted(cluster_labels):
        docs_in_cluster = {c["doc_id"] for c in chunks if c["cluster"] == label}
        print(f"  Cluster {label}: {len(docs_in_cluster)} document(s)")

    print(f"\nTotal chunks created: {len(chunks)}")

    print("\nFirst chunk:")
    print(chunks[0])

    print("\n*****************")

    print("\nSecond chunk:")
    print(chunks[1])