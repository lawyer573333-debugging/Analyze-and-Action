import fitz  # PyMuPDF
import urllib.request
from bs4 import BeautifulSoup
import os

async def extract_text_from_document(document_id: str, file_path: str, source_type: str) -> str:
    """
    Ingests a document (PDF, URL, or plain text) and normalizes it into text.
    """
    text = ""
    
    try:
        if source_type == "pdf":
            # Assuming file_path is local path to the uploaded PDF
            if os.path.exists(file_path):
                doc = fitz.open(file_path)
                for page in doc:
                    text += page.get_text() + "\n"
                doc.close()
            else:
                raise FileNotFoundError(f"PDF not found at {file_path}")
                
        elif source_type == "url":
            # Basic URL scraping
            req = urllib.request.Request(file_path, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                html = response.read()
                soup = BeautifulSoup(html, 'html.parser')
                text = soup.get_text(separator=' ', strip=True)
                
        else:
            # Fallback for plain text
            text = file_path
            
        # Basic validation
        if len(text.strip()) < 50:
            raise ValueError("Extracted text is too short. Document may be empty or malformed.")
            
        return text.strip()
        
    except Exception as e:
        import logging
        logging.error(f"Ingestion failed for {document_id}: {e}")
        raise e
