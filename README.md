# Automated Book Generation System

Simple Python project for the assessment.

## What it does
- Reads input from Excel
- Generates outline from title + notes
- Stores data in Supabase
- Generates chapters one by one
- Uses previous chapter summaries as context
- Compiles final output to TXT, DOCX, and PDF
- Includes basic exception handling and logging

## Files
- `main.py` - runs the flow
- `excel_reader.py` - reads Excel input
- `ai_service.py` - outline/chapter generation
- `db.py` - Supabase operations
- `services.py` - business logic
- `compiler.py` - final export
- `schema.sql` - Supabase tables

## Expected Excel columns
Minimum:
- `title`
- `notes_on_outline_before`

Optional:
- `notes_on_outline_after`
- `status_outline_notes`
- `final_review_notes_status`

## Install
```bash
pip install -r requirements.txt
```

## Setup
1. Copy `.env.example` to `.env`
2. Add Supabase and OpenAI values
3. Create tables using `schema.sql`
4. Put your Excel file path in `.env`

## Run
```bash
python main.py
```

## Status logic used
### Outline stage
- `yes` -> wait for outline notes
- `no_notes_needed` -> continue
- `no` or empty -> pause

### Final stage
- `no_notes_needed` -> compile book
- anything else -> wait

## Notes
This is kept simple on purpose so you can explain it easily in an interview.
