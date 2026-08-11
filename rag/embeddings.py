from rag.chunker import create_chunks
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def create_embeddings():
    chunks= create_chunks()
    embeddings = model.encode(chunks,show_progress_bar=True)
    return chunks, embeddings

if __name__=="__main__":
    chunks,embeddings = create_embeddings()
    print("Embeddinggs created successfully!")
    print("Total chunks:", len(chunks))
    print("Embedding shape" ,embeddings.shape)
    print("\nFirst chunk:")
    print(chunks[0])    
    print("\nFirst embedding:")
    print(embeddings[0])