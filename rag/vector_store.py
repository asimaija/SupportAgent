import pickle
from pathlib import Path, Path
from rag.embeddings import create_embeddings

vector_file = Path(__file__).parent / "vector_store.pkl"

def create_vector_store():
    chunks,embeddings = create_embeddings()
    data = {"chunks":chunks,"embeddings":embeddings}
    with open(vector_file,"wb") as file:
        pickle.dump(data,file)
    print("Vector store created successfully!")
    print("Total chunks:", len(chunks))
    print("Embedding shape:", embeddings.shape)

def load_vector_store():
    with open(vector_file,"rb") as file:
        data = pickle.load(file)
    return data["chunks"],data["embeddings"]

if __name__=="__main__":
    create_vector_store()