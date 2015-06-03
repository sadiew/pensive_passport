import unittest
import server

class AppIntegrationTestCase(unittest.TestCase):

    def valid_route(self, route, html_snippet, data={}):
    	result = self.app.get(route)

    	self.assertEqual(result.status_code, 200)
        self.assertIn('text/html', result.headers['Content-Type'])
        self.assertIn(html_snippet, result.data)


    def setUp(self):
        self.app = server.app.test_client()

    def test_home(self):
    	self.valid_route('/', '<img src="/static/images/pp-logo.png" id="logo-styling">')

    def test_search(self):
    	self.valid_route('/search', '<form action="/preference-form">')

    def test_login(self):
    	self.valid_route('/login', '<label>Username:')

    def test_preference_form(self):
    	self.valid_route('/preference-form', '<form id="preference-form">')




if __name__ == "__main__":
	unittest.main()