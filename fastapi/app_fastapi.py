from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # newly added
from pydantic import BaseModel
import uvicorn
import os
import uuid
import logging
from pathlib import Path
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import chromadb
import google.generativeai as genai
import requests  # newly added for scraping

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust to specific origins if necessary
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global components
@app.on_event("startup")
def startup_event():
    global embedder, client, collection, model
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(name="documents")
    model = setup_gemini()
    logger.info("Startup complete: Components initialized.")

# Reused function: Setup Gemini model
def setup_gemini() -> genai.GenerativeModel:
    # ...existing code...
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name="gemini-2.0-flash")

# Reused function: Chunk text into overlapping chunks
def chunk_text(text: str, max_chunk_size: int = 50, overlap: int = 10):
    # ...existing code...
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

# Pydantic model for scraping request
class ScrapeRequest(BaseModel):
    url: str

# Pydantic model for query request
class QueryRequest(BaseModel):
    query: str

@app.post("/process")
def process_document(request: ScrapeRequest):
    try:
        # Fetch content from the custom URL
        response = requests.get(request.url)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch URL")
        doc_content = response.text

        # Process the document: chunk, embed, and store
        chunks = chunk_text(doc_content)
        embeddings = embedder.encode(chunks, convert_to_numpy=True)
        ids = [str(uuid.uuid4()) for _ in chunks]
        collection.add(
            documents=chunks,
            embeddings=[emb.tolist() for emb in embeddings],
            ids=ids
        )
        return {"message": f"Processed {len(chunks)} chunks successfully from {request.url}"}
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
def query_document(request: QueryRequest):
    try:
        query = request.query
        query_embedding = embedder.encode(query, convert_to_numpy=True)
        results = collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=2
        )
        retrieved_context = " ".join([doc for doc in results["documents"][0] if doc])
        
        prompt = f"""Using the following context, please answer the question. If the context doesn't contain 
relevant information, please indicate that.

Context: {retrieved_context}

Question: {query}"""
        response = model.generate_content(prompt)
        return {"answer": response.text, "context": retrieved_context}
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ...existing code...
if __name__ == "__main__":
    uvicorn.run("app_fastapi:app", host="0.0.0.0", port=8000, reload=True)
