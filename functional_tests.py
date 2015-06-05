import unittest
import server

class AppIntegrationTestCase(unittest.TestCase):

    def do_get(self, route, html_snippet, test_function=None):
        result = self.app.get(route)

        self.assertEqual(result.status_code, 200)
        self.assertIn('text/html', result.headers['Content-Type'])
        self.assertIn(html_snippet, result.data)

        if test_function:
            self.assertTrue(test_function(result))

    def do_post(self, route, data={}, test_function=None):
        result = self.app.post(route, data)

        self.assertEqual(result.status_code, 200)
        self.assertIn('text/html', result.headers['Content-Type'])

        if test_function:
            self.assertTrue(test_function(result))


    def setUp(self):
        self.app = server.app.test_client()

    def test_home(self):
        self.do_get('/', '<img src="/static/images/pp-logo.png" id="logo-styling">')

    def test_search(self):
        self.do_get('/search', '<form action="/preference-form">')

    def test_login(self):
        self.do_get('/login', '<label>Username:')

    def test_login_submission(self):
        self.do_post('/login-submission', data={'username': 'demoUser.com', 'password': 'demo'})





if __name__ == "__main__":
    unittest.main()
