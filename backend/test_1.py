from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket
from pydantic import BaseModel
import os
import shutil
from datetime import datetime
import fitz  # PyMuPDF for PDF processing
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import codecs
from transformers import BertTokenizer, BertForQuestionAnswering
# from langchain import LangChain 
# from llama_index import Llama_index

app = FastAPI()

# CORS middleware to allow requests from React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust for your frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database model
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    upload_date = Column(DateTime, default=datetime.utcnow)

class Query(BaseModel):
    question: str
    
# Create tables
Base.metadata.create_all(bind=engine)
logger.info("Database tables created.")

# Endpoint to check data present in the database
@app.get("/documents/")
def get_documents():
    try:
        db = SessionLocal()
        documents = db.query(Document).all()
        db.close()
        return documents
    except Exception as e:
        logger.error(f"Failed to retrieve documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve documents")


current_dir = os.path.dirname(os.path.realpath(__file__))
upload_folder = os.path.join(current_dir, 'uploads')
os.makedirs(upload_folder, exist_ok=True)

extracted_text_folder = os.path.join(current_dir, 'extracted_text')
os.makedirs(extracted_text_folder, exist_ok=True)
extracted_text_file = os.path.join(extracted_text_folder, 'extracted_text.txt')


tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForQuestionAnswering.from_pretrained('bert-base-uncased')

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    try:
        with fitz.open(pdf_path) as pdf_document:
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                text += page.get_text()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text


@app.post("/upload/")
async def upload_pdf(pdfFile: UploadFile = File(...)):
    try:
        if pdfFile.content_type != 'application/pdf':
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # Save file to 'uploads' folder
        file_path = os.path.join(upload_folder, pdfFile.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(pdfFile.file, buffer)

        
        # Save metadata to the database
        db = SessionLocal()
        db_document = Document(filename=pdfFile.filename)
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        db.close()
        
        # Extract text from the uploaded PDF file
        pdf_path = os.path.join(upload_folder, pdfFile.filename)
        text = extract_text_from_pdf(pdf_path)

       # Save extracted text to a file for further processing
        with codecs.open(extracted_text_file, "w", encoding="utf-8") as text_file:
            text_file.write(text)
            
        return JSONResponse(content={"message": f"{pdfFile.filename}","check":f"PDF processed and text extracted successfully {text}"})
       
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to upload file")

@app.post("/process_pdf/")
async def process_pdf(pdfFile: UploadFile = File(...)):
    try:
        # Ensure uploaded file is a PDF
        if pdfFile.content_type != 'application/pdf':
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # Read PDF content
        pdf_data = pdfFile.file.read()
        pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
        text = ""
        for page_num in range(len(pdf_document)):
            page_text = pdf_document[page_num].get_text()
            text += page_text

        return {"text": text}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/")
async def query_pdf(query: Query):
    try:
        # Load extracted text
        with open("./backend/extracted_text/extracted_text.txt", encoding="utf-8",errors="ignore") as text_file:
            text = text_file.read()

        # Initialize LangChain and LlamaIndex with the extracted text
        # lang_chain = LangChain(text)
        # llama_index = LlamaIndex(lang_chain)
        
        

        # Process the question using the LangChain/LlamaIndex pipeline
        #answer = llama_index.query(query.question)

        return {"question": query.question, "answer": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  

    while True:
        data = await websocket.receive_text()
        await websocket.send_text(data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


