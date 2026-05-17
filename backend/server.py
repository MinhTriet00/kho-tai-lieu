import os
import shutil
import uuid
from pathlib import Path
import fitz  # PyMuPDF
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import SessionLocal, Document

app = FastAPI(title="Doc Vault V2")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Setup thư mục
STORAGE_DIR = Path("storage")
PDF_DIR = STORAGE_DIR / "pdfs"
THUMB_DIR = STORAGE_DIR / "thumbnails"
PDF_DIR.mkdir(parents=True, exist_ok=True)
THUMB_DIR.mkdir(parents=True, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_thumbnail(pdf_path, thumb_path):
    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(0) # Trang đầu tiên
        pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5)) # Thu nhỏ ảnh bìa
        pix.save(thumb_path)
        doc.close()
    except Exception as e:
        print("Lỗi tạo thumbnail:", e)

@app.post("/api/upload")
async def upload_document(
    title: str = Form(...),
    grade: str = Form(...),
    subject: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Chỉ hỗ trợ file PDF")
    
    unique_id = str(uuid.uuid4())[:8]
    pdf_filename = f"{unique_id}_{file.filename}"
    thumb_filename = f"{unique_id}_thumb.png"
    
    pdf_path = PDF_DIR / pdf_filename
    thumb_path = THUMB_DIR / thumb_filename

    # Lưu file PDF
    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Tạo ảnh bìa
    generate_thumbnail(pdf_path, thumb_path)

    # Lưu Database
    new_doc = Document(
        title=title, grade=grade, subject=subject, 
        description=description, pdf_filename=pdf_filename, thumb_filename=thumb_filename
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    
    return {"status": "success", "id": new_doc.id}

@app.get("/api/documents")
def get_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    return docs

@app.get("/api/documents/{doc_id}")
def get_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(404, "Không tìm thấy tài liệu")
    return doc

@app.get("/api/files/pdf/{filename}")
def get_pdf(filename: str):
    file_path = PDF_DIR / filename
    if file_path.exists():
        return FileResponse(file_path, media_type="application/pdf")
    raise HTTPException(404, "File not found")

@app.get("/api/files/thumb/{filename}")
def get_thumb(filename: str):
    file_path = THUMB_DIR / filename
    if file_path.exists():
        return FileResponse(file_path, media_type="image/png")
    # Trả về ảnh mặc định nếu lỗi (cần có sẵn, tạm bỏ qua)
    raise HTTPException(404, "Image not found")

frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="static")
