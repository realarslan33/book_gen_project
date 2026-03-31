import os
from config import Config
from logger import setup_logger
from excel_reader import read_excel_rows
from db import SupabaseDB
from ai_service import AIService
from services import BookGenerationService
from compiler import compile_txt, compile_docx, compile_pdf
from exceptions import ProjectError


def main() -> None:
    logger = setup_logger()
    logger.info("Starting automated book generation process")

    try:
        rows = read_excel_rows(Config.INPUT_EXCEL_PATH)
        db = SupabaseDB()
        ai = AIService()
        service = BookGenerationService(db, ai, logger)

        for row in rows:
            try:
                book = service.process_outline_stage(row)
                latest_book = db.get_book_by_title(book["title"]) or book
                service.process_chapters(latest_book)

                final_status = str(row.get("final_review_notes_status", "no_notes_needed")).strip().lower()
                if final_status == "no_notes_needed":
                    chapters = db.list_chapters(latest_book["id"])
                    txt_path = compile_txt(latest_book, chapters, Config.OUTPUT_DIR)
                    docx_path = compile_docx(latest_book, chapters, Config.OUTPUT_DIR)
                    pdf_path = compile_pdf(latest_book, chapters, Config.OUTPUT_DIR)
                    logger.info("Compiled output files: %s | %s | %s", txt_path, docx_path, pdf_path)
                    db.update_book(latest_book["id"], {"book_output_status": "compiled"})
                else:
                    logger.info("Final review notes still pending for '%s'", latest_book["title"])
                    db.update_book(latest_book["id"], {"book_output_status": "waiting_for_final_review"})

            except ProjectError as exc:
                logger.error("Row failed: %s", exc)
            except Exception as exc:
                logger.exception("Unexpected error while processing row: %s", exc)

    except ProjectError as exc:
        logger.error("Project failed: %s", exc)
    except Exception as exc:
        logger.exception("Unexpected project failure: %s", exc)


if __name__ == "__main__":
    main()
