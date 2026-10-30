import tempfile
import unittest
from pathlib import Path
from server import create_app


class JournalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.config = dict(TESTING=True, SECRET_KEY='test', DATABASE=str(Path(self.temp.name) / 'journal.db'))
        self.client = create_app(self.config).test_client()
        self.client.get('/')
        with self.client.session_transaction() as session:
            self.csrf = session['csrf']

    def tearDown(self):
        self.temp.cleanup()

    def save(self, **changes):
        data = dict(csrf=self.csrf, day='2026-10-30', title='Friday', body='A peaceful walk', mood='Good')
        data.update(changes)
        return self.client.post('/save', data=data, follow_redirects=True)

    def test_lifecycle_and_persistence(self):
        self.assertIn(b'Entry saved.', self.save().data)
        self.assertIn(b'A peaceful walk', self.client.get('/?q=peaceful').data)
        self.save(body='A new reflection')
        response = self.client.get('/?day=2026-10-30')
        self.assertIn(b'A new reflection', response.data)
        self.assertNotIn(b'A peaceful walk', response.data)
        self.assertIn(b'No matching pages', self.client.get('/?q=peaceful').data)
        self.assertIn(b'A new reflection', create_app(self.config).test_client().get('/?day=2026-10-30').data)
        self.client.post('/delete', data=dict(csrf=self.csrf, day='2026-10-30'))
        self.assertIn(b'Your story starts here', self.client.get('/').data)

    def test_validation_and_csrf(self):
        for changes in [dict(body=' '), dict(day='invalid'), dict(mood='invalid'), dict(title='x' * 161)]:
            self.assertEqual(self.save(**changes).status_code, 400)
        self.assertEqual(self.client.post('/save').status_code, 400)
        self.assertEqual(self.client.post('/delete').status_code, 400)

    def test_escaping(self):
        response = self.save(body='<script>alert(1)</script>')
        self.assertNotIn(b'<script>alert(1)</script>', response.data)
        self.assertIn(b'&lt;script&gt;', response.data)
