import unittest
import server


class AppIntegrationTestCase(unittest.TestCase):

    def do_get(self, route, html_snippet):
        result = self.app.get(route)

        self.assertEqual(result.status_code, 200)
        self.assertIn('text/html', result.headers['Content-Type'])
        self.assertIn(html_snippet, result.data)

        return result.data

    def do_post(self, route, data={}):
        result = self.app.post(route, data=data)

        self.assertEqual(result.status_code, 200)
        self.assertIn('text/html', result.headers['Content-Type'])

        return result.data

    def setUp(self):
        self.app = server.app.test_client()

    def test_home(self):
        self.do_get('/', '<img src="/static/images/pp-logo.png" id="logo-styling">')

    def test_search(self):
        self.do_get('/search', '<form action="/preference-form">')

    def test_login(self):
        self.do_get('/login', '<label>Username:')

    def test_login_submission(self):
        result = self.app.post('/login-submission', data={'username': 'demoUser@gmail.com', 'password': 'demo'})

        self.assertEqual(result.status_code, 302)
        self.assertIn('text/html', result.headers['Content-Type'])





if __name__ == "__main__":
    from model import connect_to_db
    from server import app
    connect_to_db(app)
    unittest.main()
