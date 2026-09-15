from dataclasses import dataclass

from pypdf import PdfReader


@dataclass
class PageContent:

    document_id: str
    document_name: str
    page_number: int
    chunk_id: str
    text: str


class PDFService:

    @staticmethod
    def extract_text(
        file_path: str,
        document_id: str,
        document_name: str
    ):

        reader = PdfReader(
            file_path
        )

        chunks = []

        chunk_size = 1200
        chunk_overlap = 200

        for page_index, page in enumerate(
            reader.pages
        ):

            text = page.extract_text() or ""

            text = " ".join(
                text.split()
            )

            if not text:
                continue

            start = 0
            chunk_number = 0

            while start < len(text):

                end = start + chunk_size

                chunk_text = text[
                    start:end
                ]

                chunk_id = (
                    f"{document_id}"
                    f"_p{page_index + 1}"
                    f"_c{chunk_number}"
                )

                chunks.append(
                    PageContent(
                        document_id=document_id,
                        document_name=document_name,
                        page_number=page_index + 1,
                        chunk_id=chunk_id,
                        text=chunk_text
                    )
                )

                chunk_number += 1

                if end >= len(text):
                    break

                start = (
                    end - chunk_overlap
                )

        return chunks