from time import sleep
import chromadb
from chromadb import Settings, Client
import os
from chromadb.utils import embedding_functions
from langchain.embeddings import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader, Docx2txtLoader
import tempfile
from dotenv import load_dotenv

load_dotenv()

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_type="azure",
    model_name="text-embedding-ada-002",
    api_version="2023-05-15"
)

def get_chroma_client():
    """Get or create a ChromaDB client"""
    if not os.path.exists("./chroma_db"):
        os.makedirs("./chroma_db")
    return chromadb.PersistentClient(path="./chroma_db")

class ChromaSearchTool:
    """Custom tool for semantic search in ChromaDB."""
    def __init__(self, embeddings):
        self.embeddings = embeddings
        self.client = get_chroma_client()
             
    def search(self, query: str, k: int = 5) -> str:
        """
        Search the ChromaDB and return formatted results
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=k
        )
        
        documents = []
        for i, (doc, metadata, score) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        )):
            documents.append(f"Document {i+1} (Relevance: {1-score:.2f}):\n{doc}\n")
        
        return "\n".join(documents)
    
    def multiple_collection_search(self, query: str, k: int = 5) -> str:
        collections_name = self.client.list_collections()
        all_results = []

        for collection_name in collections_name:

            collection = self.client.get_collection(
                name=collection_name,
                embedding_function=openai_ef
                )

            results = collection.query(
                query_texts=[query],
                n_results=k
            )

            for distance, metadata, document in zip(results['distances'][0], results['metadatas'][0], results['documents'][0]):
                all_results.append((distance, metadata, document))

        all_results.sort(key=lambda x: x[0])

        top_5_results = all_results[:k]
        documents = []

        for i, (distance, metadata, document) in enumerate(top_5_results, start=1):
            formatted_result = (
                f"Document {i} (Relevance: {distance:.2f}):\n"
                f"{document.strip()}\n"
            )
            documents.append(formatted_result)
        return "\n\n".join(documents)
    
class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1800,
            chunk_overlap=200,
            length_function=len,
        )
        self.embeddings = openai_ef
        self.client = get_chroma_client()

    def process_file(self, file):
        base_filename = os.path.splitext(file.name)[0]
        collection_name_pf = f"{base_filename}"

        existing_collections = self.client.list_collections()

        if collection_name_pf in existing_collections:
            return {"status": "exists", "collection_name": collection_name_pf}
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(file.getvalue())
            tmp_file_path = tmp_file.name

        try:
            if file.name.endswith('.pdf'):
                loader = PyMuPDFLoader(tmp_file_path)
            elif file.name.endswith('.docx'):
                loader = Docx2txtLoader(tmp_file_path)
            elif file.name.endswith('.txt'):
                loader = TextLoader(tmp_file_path)
            else:
                raise ValueError("Unsupported file type")

            documents = loader.load()
            chunks = self.text_splitter.split_documents(documents)
            
            texts = [doc.page_content for doc in chunks]

            embeddings = self.embeddings(texts)
            
            collection = self.client.create_collection(name=collection_name_pf)
            
            collection.add(
                embeddings=embeddings,
                documents=texts,
                ids=[f"doc_{i}" for i in range(len(texts))]
            )
            
            return {"status": "success", "collection_name": collection_name_pf}
            
        finally:
            os.unlink(tmp_file_path)
