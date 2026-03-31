from typing import Dict, List
from exceptions import ValidationError
from ai_service import AIService
from db import SupabaseDB

VALID_STATUS_VALUES = {"yes", "no", "no_notes_needed", ""}


def normalize_status(value: str) -> str:
    return (value or "").strip().lower()


class BookGenerationService:
    def __init__(self, db: SupabaseDB, ai: AIService, logger) -> None:
        self.db = db
        self.ai = ai
        self.logger = logger

    def process_outline_stage(self, row: Dict) -> Dict:
        title = str(row.get("title", "")).strip()
        notes_before = str(row.get("notes_on_outline_before", "")).strip()
        notes_after = str(row.get("notes_on_outline_after", "")).strip()
        status_outline_notes = normalize_status(str(row.get("status_outline_notes", "")))

        if not title:
            raise ValidationError("Title is required.")
        if not notes_before:
            raise ValidationError(f"notes_on_outline_before is required for title '{title}'.")
        if status_outline_notes not in VALID_STATUS_VALUES:
            raise ValidationError(f"Invalid status_outline_notes for title '{title}'.")

        existing = self.db.get_book_by_title(title)
        if existing:
            book = existing
            self.logger.info("Book already exists. Reusing record for '%s'", title)
        else:
            outline_data = self.ai.generate_outline(title=title, notes_before=notes_before)
            book = self.db.insert_book(
                {
                    "title": title,
                    "notes_on_outline_before": notes_before,
                    "outline": outline_data.get("outline_text", ""),
                    "notes_on_outline_after": notes_after,
                    "status_outline_notes": status_outline_notes or "no",
                    "book_output_status": "outline_ready",
                }
            )
            for chapter in outline_data.get("chapters", []):
                self.db.insert_chapter(
                    {
                        "book_id": book["id"],
                        "chapter_number": chapter.get("chapter_number"),
                        "chapter_title": chapter.get("chapter_title", ""),
                        "chapter_goal": chapter.get("chapter_goal", ""),
                        "chapter_notes_status": "no",
                        "chapter_notes": "",
                        "chapter_text": "",
                        "chapter_summary": "",
                    }
                )

        return book

    def process_chapters(self, book: Dict) -> None:
        status = normalize_status(book.get("status_outline_notes", ""))
        if status == "yes":
            self.logger.info("Outline notes pending for '%s'. Waiting.", book["title"])
            self.db.update_book(book["id"], {"book_output_status": "waiting_for_outline_notes"})
            return
        if status in {"", "no"}:
            self.logger.info("Outline status is empty/no for '%s'. Pausing.", book["title"])
            self.db.update_book(book["id"], {"book_output_status": "paused_outline_status"})
            return

        chapters = self.db.list_chapters(book["id"])
        previous_summaries: List[str] = []

        for chapter in chapters:
            chapter_status = normalize_status(chapter.get("chapter_notes_status", ""))
            if chapter_status == "yes":
                self.logger.info("Waiting for chapter notes on chapter %s", chapter.get("chapter_number"))
                continue
            if chapter_status in {"", "no"}:
                self.logger.info("Chapter %s paused because notes status is empty/no", chapter.get("chapter_number"))
                continue

            context_input = "\n".join(previous_summaries) if previous_summaries else "No previous chapter summaries."
            result = self.ai.generate_chapter(
                title=book["title"],
                chapter_title=chapter.get("chapter_title", ""),
                chapter_goal=chapter.get("chapter_goal", ""),
                context_input=context_input,
                chapter_notes=chapter.get("chapter_notes", ""),
            )
            chapter_text = result.get("chapter_text", "")
            chapter_summary = result.get("chapter_summary", "")
            self.db.update_chapter(
                chapter["id"],
                {
                    "chapter_text": chapter_text,
                    "chapter_summary": chapter_summary,
                },
            )
            previous_summaries.append(chapter_summary)

        self.db.update_book(book["id"], {"book_output_status": "chapters_processed"})
