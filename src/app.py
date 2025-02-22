from sentence_transformers import SentenceTransformer
import chromadb
import os
import google.generativeai as genai
import uuid
import logging
from typing import List, Union
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def chunk_text(text: str, max_chunk_size: int = 50, overlap: int = 10) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Input text to chunk
        max_chunk_size: Maximum number of words per chunk
        overlap: Number of overlapping words between chunks
    
    Returns:
        List of text chunks
    """
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + max_chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end >= len(words):
            break
        start = end - overlap
    return chunks

def read_documents(file_path: Union[str, Path]) -> str:
    """Read document content from file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        raise

def process_documents(file_path: str, embedder: SentenceTransformer, collection: chromadb.Collection):
    """Process documents and store in ChromaDB with embeddings."""
    try:
        # Read document content
        doc_content = read_documents(file_path)
        
        # Chunk the document
        chunks = chunk_text(doc_content)
        
        # Generate embeddings
        embeddings = embedder.encode(chunks, convert_to_numpy=True)
        
        # Generate unique IDs for each chunk
        ids = [str(uuid.uuid4()) for _ in chunks]
        
        # Add to collection
        collection.add(
            documents=chunks,
            embeddings=[emb.tolist() for emb in embeddings],
            ids=ids
        )
        logger.info(f"Successfully processed and stored {len(chunks)} chunks")
        
    except Exception as e:
        logger.error(f"Error processing documents: {str(e)}")
        raise

def setup_gemini() -> genai.GenerativeModel:
    """Configure and return Gemini model."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name="gemini-2.0-flash")

def generate_response(model: genai.GenerativeModel, context: str, query: str) -> str:
    """Generate response using Gemini model."""
    prompt = f"""Using the following context, please answer the question. If the context doesn't contain 
    relevant information, please indicate that.

    Context: {context}
    
    Question: {query}"""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        raise

def main():
    try:
        # Initialize components
        embedder = SentenceTransformer("all-MiniLM-L6-v2")
        client = chromadb.PersistentClient(path="./chroma_db")
        collection = client.get_or_create_collection(name="documents")
        
        # Process documents
        docs_path = Path('D:/Jayakrishna/src/scraping_results_20250220_233402.txt')
        process_documents(docs_path, embedder, collection)
        
        # Setup Gemini
        model = setup_gemini()
        
        while True:
            # Get query from user
            query = input("\nEnter your query (or 'quit' to exit): ")
            if query.lower() == 'quit':
                break
                
            # Generate query embedding
            query_embedding = embedder.encode(query, convert_to_numpy=True)
            
            # Retrieve similar documents
            results = collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=2
            )
            
            # Extract context
            retrieved_context = " ".join([doc for doc in results["documents"][0] if doc])
            
            print("\nRetrieved Context:")
            print(retrieved_context)
            
            # Generate and display response
            answer = generate_response(model, retrieved_context, query)
            print("\nGenerated Answer:")
            print(answer)
            
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()