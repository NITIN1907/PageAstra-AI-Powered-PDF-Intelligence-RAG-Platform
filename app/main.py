from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.database import (
    Base,
    engine,
    SessionLocal
)

from app.models.document import Document, DocumentChunk

from app.routes.chat import router as chat_router
from app.routes.pdf import router as pdf_router
from app.routes.search import router as search_router

from app.service.search_service import search_service
from app.service.document_service import DocumentService


app = FastAPI()


# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://page-astra-ai-powered-pdf-intellige-beta.vercel.app"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ==========================================
# STARTUP
# ==========================================

@app.on_event("startup")
def initialize_search():

    # --------------------------------------
    # Create database tables
    # --------------------------------------

    Base.metadata.create_all(
        bind=engine
    )

    db = SessionLocal()

    try:

        # ----------------------------------
        # Get indexed chunks from PostgreSQL
        # ----------------------------------

        chunks = (
            DocumentService
            .get_indexed_chunks(db)
        )

        print(
            f"Found {len(chunks)} indexed chunks "
            "in PostgreSQL"
        )

        # ----------------------------------
        # Try loading existing FAISS index
        # ----------------------------------

        loaded = search_service.load(
            chunks
        )

        # ----------------------------------
        # FAISS is valid
        # ----------------------------------

        if loaded:

            print(
                "FAISS persistence validated successfully"
            )

        # ----------------------------------
        # FAISS missing/inconsistent
        # ----------------------------------

        else:

            print(
                "FAISS index missing or inconsistent."
            )

            print(
                "Rebuilding FAISS from PostgreSQL..."
            )

            search_service.rebuild_from_database(
                chunks
            )

            print(
                "FAISS rebuild completed successfully"
            )

    except Exception as e:

        print(
            f"Search initialization failed: {e}"
        )

        raise

    finally:

        db.close()


# ==========================================
# ROUTES
# ==========================================

app.include_router(
    chat_router
)

app.include_router(
    pdf_router
)

app.include_router(
    search_router
)


# ==========================================
# ROOT
# ==========================================

@app.get("/")
def root():

    return {
        "status": "running",
        "welcome": "to my server"
    }
