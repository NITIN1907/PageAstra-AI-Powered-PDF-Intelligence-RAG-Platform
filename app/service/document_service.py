from sqlalchemy.orm import Session

from app.models.document import Document, DocumentChunk


class DocumentService:

    @staticmethod
    def create_document(
        db: Session,
        document_id: str,
        filename: str,
        stored_filename: str,
        file_path: str
    ):
        document = Document(
            id=document_id,
            filename=filename,
            stored_filename=stored_filename,
            file_path=file_path,
            status="processing"
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    @staticmethod
    def add_chunks(
        db: Session,
        document_id: str,
        chunks
    ):
        db_chunks = []

        for chunk in chunks:
            db_chunk = DocumentChunk(
                document_id=document_id,
                chunk_id=chunk.chunk_id,
                page_number=chunk.page_number,
                text=chunk.text
            )

            db.add(db_chunk)
            db_chunks.append(db_chunk)

        db.commit()

        return db_chunks

    @staticmethod
    def mark_indexed(
        db: Session,
        document_id: str
    ):
        document = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if document:
            document.status = "indexed"
            db.commit()

        return document

    @staticmethod
    def mark_failed(
        db: Session,
        document_id: str
    ):
        document = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if document:
            document.status = "failed"
            db.commit()

        return document

    @staticmethod
    def get_documents(db: Session):
        return (
            db.query(Document)
            .order_by(Document.id.desc())
            .all()
        )

    @staticmethod
    def get_indexed_chunks(db: Session):
        return (
            db.query(DocumentChunk)
            .join(Document)
            .filter(Document.status == "indexed")
            .order_by(DocumentChunk.id.asc())
            .all()
        )

    @staticmethod
    def get_document(
        db: Session,
        document_id: str
    ):
        return (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

    @staticmethod
    def delete_document(
        db: Session,
        document_id: str
    ):
        document = (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

        if not document:
            return None

        file_path = document.file_path

        db.delete(document)
        db.commit()

        return file_path