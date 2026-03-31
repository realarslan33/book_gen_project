import os
from supabase import create_client, Client


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def insert_book(title: str, notes: str):
    try:
        response = (
            supabase.table("books")
            .insert({"title": title, "notes_on_outline_before": notes})
            .execute()
        )
        return response
    except Exception as e:
        print(f"Insert failed: {e}")
        return None
