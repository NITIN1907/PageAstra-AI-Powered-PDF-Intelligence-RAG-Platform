import os
import uuid

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.service.Pdf_service import PDFService
from app.service.search_service import search_service
from app.service.document_service import DocumentService

from app.models.document import Document


router = APIRouter()

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


# =========================================================
# UPLOAD PDF
# =========================================================

@router.post("/pdf/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required"
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    document_id = str(uuid.uuid4())

    stored_filename = f"{document_id}.pdf"

    file_path = os.path.join(
        UPLOAD_DIR,
        stored_filename
    )

    try:

        # -------------------------------------------------
        # 1. Save physical PDF
        # -------------------------------------------------

        contents = await file.read()

        with open(file_path, "wb") as buffer:
            buffer.write(contents)

        # -------------------------------------------------
        # 2. Create PostgreSQL document
        # -------------------------------------------------

        document = DocumentService.create_document(
            db=db,
            document_id=document_id,
            filename=file.filename,
            stored_filename=stored_filename,
            file_path=file_path
        )

        # -------------------------------------------------
        # 3. Extract PDF
        # -------------------------------------------------

        chunks = PDFService.extract_text(
            file_path,
            document_id,
            file.filename
        )

        if not chunks:
            DocumentService.mark_failed(
                db,
                document_id
            )

            if os.path.exists(file_path):
                os.remove(file_path)

            raise HTTPException(
                status_code=400,
                detail="No readable text found in PDF"
            )

        # -------------------------------------------------
        # 4. Store chunks in PostgreSQL
        # -------------------------------------------------

        DocumentService.add_chunks(
            db=db,
            document_id=document_id,
            chunks=chunks
        )

        # -------------------------------------------------
        # 5. Add chunks to FAISS
        # -------------------------------------------------

        search_service.add_document(chunks)

        # -------------------------------------------------
        # 6. Mark document indexed
        # -------------------------------------------------

        DocumentService.mark_indexed(
            db,
            document_id
        )

        return {
    "success": True,
    "message": "PDF uploaded successfully",
    "document_id": document_id,
    "filename": file.filename,
    "chunks": len(chunks),
    "status": "indexed"
}

    except HTTPException:
        raise

    except Exception as e:

        db.rollback()

        # Remove physical PDF
        if os.path.exists(file_path):
            os.remove(file_path)

        # Try to mark document failed
        try:
            DocumentService.mark_failed(
                db,
                document_id
            )
        except Exception:
            pass

        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )


# =========================================================
# GET DOCUMENTS
# =========================================================

@router.get("/pdf/documents")
def get_documents(
    db: Session = Depends(get_db)
):

    documents = DocumentService.get_documents(db)

    result = []

    for document in documents:

        result.append({
            "id": document.id,
            "filename": document.filename,
            "stored_filename": document.stored_filename,
            "status": document.status,
            "chunks": len(document.chunks),
            "created_at": (
                document.created_at.isoformat()
                if hasattr(document, "created_at")
                and document.created_at
                else None
            )
        })

    return {
        "documents": result
    }


# =========================================================
# DELETE DOCUMENT
# =========================================================

@router.delete("/pdf/{document_id}")
def delete_document(
    document_id: str,
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # 1. Find document
    # -----------------------------------------------------

    document = DocumentService.get_document(
        db,
        document_id
    )

    if not document:

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    file_path = document.file_path

    try:

        # -------------------------------------------------
        # 2. Delete PostgreSQL document
        #
        # Because of:
        # cascade="all, delete-orphan"
        #
        # chunks will also be deleted.
        # -------------------------------------------------

        DocumentService.delete_document(
            db,
            document_id
        )

        # -------------------------------------------------
        # 3. Delete physical PDF
        # -------------------------------------------------

        if file_path and os.path.exists(file_path):
            os.remove(file_path)

        # -------------------------------------------------
        # 4. Get remaining indexed chunks
        # -------------------------------------------------

        remaining_chunks = (
            DocumentService.get_indexed_chunks(db)
        )

        # -------------------------------------------------
        # 5. Rebuild FAISS
        # -------------------------------------------------

        search_service.rebuild_from_database(
            remaining_chunks
        )

        return {
            "success": True,
            "message": "Document deleted successfully",
            "document_id": document_id
        }

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Delete failed: {str(e)}"
        )