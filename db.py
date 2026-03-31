from typing import Any, Dict, List, Optional
from supabase import create_client, Client
from config import Config
from exceptions import DatabaseError


class SupabaseDB:
    def __init__(self) -> None:
        if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
            raise DatabaseError("SUPABASE_URL or SUPABASE_KEY is missing.")
        try:
            self.client: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        except Exception as exc:
            raise DatabaseError(f"Failed to connect to Supabase: {exc}") from exc

    def insert_book(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = self.client.table("books").insert(payload).execute()
            if not response.data:
                raise DatabaseError("Book insert returned no data.")
            return response.data[0]
        except Exception as exc:
            raise DatabaseError(f"Failed to insert book: {exc}") from exc

    def update_book(self, book_id: Any, payload: Dict[str, Any]) -> None:
        try:
            self.client.table("books").update(payload).eq("id", book_id).execute()
        except Exception as exc:
            raise DatabaseError(f"Failed to update book {book_id}: {exc}") from exc

    def get_book_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.client.table("books").select("*").eq("title", title).limit(1).execute()
            return response.data[0] if response.data else None
        except Exception as exc:
            raise DatabaseError(f"Failed to fetch book by title '{title}': {exc}") from exc

    def insert_chapter(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = self.client.table("chapters").insert(payload).execute()
            if not response.data:
                raise DatabaseError("Chapter insert returned no data.")
            return response.data[0]
        except Exception as exc:
            raise DatabaseError(f"Failed to insert chapter: {exc}") from exc

    def update_chapter(self, chapter_id: Any, payload: Dict[str, Any]) -> None:
        try:
            self.client.table("chapters").update(payload).eq("id", chapter_id).execute()
        except Exception as exc:
            raise DatabaseError(f"Failed to update chapter {chapter_id}: {exc}") from exc

    def list_chapters(self, book_id: Any) -> List[Dict[str, Any]]:
        try:
            response = (
                self.client.table("chapters")
                .select("*")
                .eq("book_id", book_id)
                .order("chapter_number")
                .execute()
            )
            return response.data or []
        except Exception as exc:
            raise DatabaseError(f"Failed to list chapters for book {book_id}: {exc}") from exc
