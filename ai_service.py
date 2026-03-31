import json
from typing import Dict, List
from openai import OpenAI
from config import Config
from exceptions import AIServiceError


class AIService:
    def __init__(self) -> None:
        if not Config.OPENAI_API_KEY:
            raise AIServiceError("OPENAI_API_KEY is missing.")
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL

    def _ask_json(self, prompt: str) -> Dict:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.3,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "Return valid JSON only."},
                    {"role": "user", "content": prompt},
                ],
            )
            content = response.choices[0].message.content
            if not content:
                raise AIServiceError("Empty response from AI.")
            return json.loads(content)
        except Exception as exc:
            raise AIServiceError(f"AI request failed: {exc}") from exc

    def generate_outline(self, title: str, notes_before: str) -> Dict:
        prompt = f"""
        Create a simple book outline.
        Book title: {title}
        Editor notes before outline: {notes_before}

        Return JSON with this structure:
        {{
          "outline_text": "full outline as text",
          "chapters": [
            {{"chapter_number": 1, "chapter_title": "...", "chapter_goal": "..."}}
          ]
        }}
        """
        return self._ask_json(prompt)

    def generate_chapter(self, title: str, chapter_title: str, chapter_goal: str, context_input: str, chapter_notes: str) -> Dict:
        prompt = f"""
        Write one chapter for a book.
        Book title: {title}
        Chapter title: {chapter_title}
        Chapter goal: {chapter_goal}
        Previous chapter summaries: {context_input}
        Editor chapter notes: {chapter_notes}

        Return JSON with this structure:
        {{
          "chapter_text": "full chapter text",
          "chapter_summary": "short summary"
        }}
        """
        return self._ask_json(prompt)
