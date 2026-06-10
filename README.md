# Flight Management Database

A Flight Management Database system built with Python and SQLite, featuring a
normalised relational schema and a command-line interface for managing flights,
pilots, aircraft, and destinations.

## Requirements

- Python 3
- SQLite

## Setup

Run these commands from the project folder, in order:

```bash
# 1. Create the database tables from the schem
sqlite3 flights.db < schema.sql

# 2. Populate the database with sample data
python seed_data.py

# 3. Run the application
python main.py
```

A pre-built `flights.db` is already included in the repository, so steps 1 and 2
can be skipped if you only want to run the application.

## Files

- `schema.sql` — database schema (table definitions, keys, constraints)
- `seed_data.py` — populates the database with sample data
- `main.py` — the command-line application
- `flights.db` — pre-built SQLite database