# RAG Chat Application with Google Gemini
## 🚀 Objective
This project is a Retrieval-Augmented Generation (RAG) chat application that integrates Google Gemini to provide intelligent responses using scraped web content as its knowledge base. Users can input URLs, scrape content, and interact with a chatbot that uses this content for generating context-aware answers.

# 📂 Project Structure
├── fastapi/                  # Backend (FastAPI) <br/>
│   ├── chroma_db/            # Vector database storage<br/>
│   ├── app_fastapi.py        # API routes and backend
logic<br>
│<br/>
├── frontend/                 # Frontend (HTML, CSS, JS)<br/>
│   ├── app.js                # Frontend logic<br/>
│   ├── index.html            # Main webpage<br/>
│   ├── style.css             # Custom styles<br/>
│<br/>
├── src/                      # Core Python logic<br/>
│   ├── chroma_db/            # Vector storage for embeddings<br/>
│   ├── app.py                # LSTM model integration<br/>
│   ├── scrapping.py          # Web scraping logic<br/>
├── .env                      # Environment variables (API keys)<br/>
├── requirements.txt          # Python dependencies<br/>

# 🛠️ Tech Stack
Frontend: HTML, CSS, JavaScript (Vanilla)
Backend: FastAPI (Python)
Scraping: Custom Python-based scraper
Vector Database: ChromaDB (or any compatible vector storage)
Embedding & RAG: Google Gemini API

# Video Sample:

https://github.com/user-attachments/assets/43d08465-b04f-4177-b14a-5dac8b4b56a7

# Some Problems that are faced during this project:
1. Developing a frontend but used HTML,CSS, JavaScript
2. Hosting - I am still looking for it.
   
