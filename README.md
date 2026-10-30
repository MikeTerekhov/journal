# Daybook

A local daily journal using Flask and SQLite. Write one entry per date, choose a mood, search past entries, and edit or delete them.

## Run

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python server.py
```

Open http://127.0.0.1:5000. Entries are stored in `instance/journal.sqlite3`. Back up this file to preserve your writing. The sidebar opens saved entries. Saving for a date replaces that date's entry.

This version is for personal use on your computer. It has no accounts or encryption. Keep it on localhost; shared hosting needs authentication. Debug mode is off by default; set `FLASK_DEBUG=1` for development. Optionally set `SECRET_KEY` to preserve form sessions across restarts.

## Test

```sh
venv/bin/python -m unittest discover -s tests
```
