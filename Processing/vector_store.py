from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

VECTOR_STORE_DIR = Path("Data/vector_store/shl_faiss")
VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

EMBEDDING_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"


def get_embedding_model():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)


def save_vector_store(vector_store: FAISS):

    vector_store.save_local(VECTOR_STORE_DIR)
    print(f"Vector store saved at: {VECTOR_STORE_DIR}")


def load_vector_store() -> FAISS:
    embeddings = get_embedding_model()

    if not VECTOR_STORE_DIR.exists():
        raise FileNotFoundError(
            "FAISS index not found. Please build embeddings first."
        )

    return FAISS.load_local(
        VECTOR_STORE_DIR,
        embeddings,
        allow_dangerous_deserialization=True,
    )
