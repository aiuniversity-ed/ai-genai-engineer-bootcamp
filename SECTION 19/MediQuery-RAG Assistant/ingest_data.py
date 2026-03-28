"""
ingest.py — Load medical PDFs, chunk them, and store embeddings in ChromaDB.
 
Usage:
    python ingest.py --docs_dir ./data
"""
 
import os
import argparse
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter  
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
 
CHROMA_DIR = "./chroma_db"
EMBED_MODEL = "nomic-embed-text"  # pull with: ollama pull nomic-embed-text
 
 
def load_documents(docs_dir: str):
    """Load all PDFs from the given directory."""
    print(f"[+] Loading PDFs from: {docs_dir}")
    loader = DirectoryLoader(
        docs_dir,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader,
        show_progress=True,
    )
    docs = loader.load()
    print(f"    Loaded {len(docs)} pages from {len(set(d.metadata['source'] for d in docs))} file(s).")
    return docs
 
 
def chunk_documents(docs):
    """Split documents into overlapping chunks for better retrieval."""
    print("[+] Chunking documents...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,       # ~500 chars per chunk — works well for medical text
        chunk_overlap=100,    # overlap keeps context across chunk boundaries
        separators=["\n\n", "\n", ".", " "],
    )
    chunks = splitter.split_documents(docs)
    print(f"    Created {len(chunks)} chunks.")
    return chunks
 
 
def embed_and_store(chunks):
    """Embed chunks using Ollama and persist to ChromaDB."""
    print(f"[+] Embedding with Ollama model: {EMBED_MODEL}")
    print("    (Make sure you've run: ollama pull nomic-embed-text)")
 
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)
 
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR,
        collection_name="medical_docs",
    )
    print(f"    Stored {len(chunks)} chunks in ChromaDB at: {CHROMA_DIR}")
    return vectorstore
 
 
def run_ingestion(docs_dir: str):
    if not os.path.exists(docs_dir):
        raise FileNotFoundError(f"Documents directory not found: {docs_dir}")
 
    docs = load_documents(docs_dir)
    if not docs:
        raise ValueError("No PDF files found. Add PDFs to the docs directory.")
 
    chunks = chunk_documents(docs)
    vectorstore = embed_and_store(chunks)
    print("\n[✓] Ingestion complete! You can now run the app with: streamlit run app.py")
    return vectorstore
 
 
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest medical PDFs into ChromaDB.")
    parser.add_argument("--docs_dir", type=str, default="./data", help="Path to folder containing PDFs")
    args = parser.parse_args()
    run_ingestion(args.docs_dir)