import os
import secrets
import sqlite3
from datetime import date
from pathlib import Path
from flask import Flask, abort, redirect, render_template, request, session, url_for


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(SECRET_KEY=os.environ.get('SECRET_KEY') or secrets.token_hex(32),
                      DATABASE=str(Path(app.instance_path) / 'journal.sqlite3'),
                      MAX_CONTENT_LENGTH=1024 * 1024, SESSION_COOKIE_SAMESITE='Lax')
    app.config.update(config or {})
    Path(app.config['DATABASE']).parent.mkdir(parents=True, exist_ok=True)

    def database():
        db = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
        return db

    with database() as db:
        db.execute('CREATE TABLE IF NOT EXISTS entries (day TEXT PRIMARY KEY, title TEXT NOT NULL, body TEXT NOT NULL, mood TEXT NOT NULL)')

    @app.before_request
    def csrf():
        session.setdefault('csrf', secrets.token_hex(32))
        if request.method == 'POST' and not secrets.compare_digest(session['csrf'], request.form.get('csrf', '')):
            abort(400, 'Reload the page and try again.')

    @app.get('/')
    def home():
        day = request.args.get('day', date.today().isoformat())
        try:
            selected = date.fromisoformat(day)
        except ValueError:
            abort(400, 'Choose a valid date.')
        query = request.args.get('q', '').strip()
        with database() as db:
            entry = db.execute('SELECT * FROM entries WHERE day=?', (day,)).fetchone()
            entries = db.execute('SELECT * FROM entries WHERE instr(lower(title || char(10) || body), lower(?)) > 0 ORDER BY day DESC', (query,)).fetchall()
            count = db.execute('SELECT count(*) FROM entries').fetchone()[0]
        return render_template('index.html', entry=entry, entries=entries, day=day,
                               selected=selected, today=date.today().isoformat(), query=query, count=count,
                               moods=['Great', 'Good', 'Okay', 'Low', 'Difficult'])

    @app.post('/save')
    def save():
        day = request.form.get('day', '')
        try:
            date.fromisoformat(day)
        except ValueError:
            abort(400, 'Choose a valid date.')
        title = request.form.get('title', '').strip()
        body = request.form.get('body', '').strip()
        mood = request.form.get('mood', '')
        if not body or len(body) > 100000 or len(title) > 160:
            abort(400, 'Write an entry up to 100,000 characters and a title up to 160 characters.')
        if mood not in ['', 'Great', 'Good', 'Okay', 'Low', 'Difficult']:
            abort(400, 'Choose a valid mood.')
        with database() as db:
            db.execute('INSERT INTO entries VALUES (?, ?, ?, ?) ON CONFLICT(day) DO UPDATE SET title=excluded.title, body=excluded.body, mood=excluded.mood', (day, title or 'A moment from my day', body, mood))
        return redirect(url_for('home', day=day, saved='1'))

    @app.post('/delete')
    def delete():
        with database() as db:
            db.execute('DELETE FROM entries WHERE day=?', (request.form.get('day', ''),))
        return redirect(url_for('home'))

    return app


app = create_app()
if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG') == '1')
