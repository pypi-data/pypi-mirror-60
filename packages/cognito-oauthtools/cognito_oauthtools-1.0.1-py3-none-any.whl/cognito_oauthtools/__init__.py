import requests

version = "1.0.1"

class Client:
	def __init__(self, endpoint, client_id, client_secret, host_domain, logout_path="/", redirect_path="/oauth"):
		self.endpoint = endpoint
		self.client_id = client_id
		self.client_secret = client_secret
		self.host = host_domain
		self.logout_path = logout_path
		self.redirect_path = redirect_path

	@property
	def loginUrl(self):
		return 'https://' + self.endpoint + '/login?client_id=' + self.client_id + "&redirect_uri=https://" + self.host + self.redirect_path + "&response_type=code"

	@property
	def registerUrl(self):
		return 'https://' + self.endpoint + '/signup?client_id=' + self.client_id + "&redirect_uri=https://" + self.host + self.redirect_path + "&response_type=code"

	@property
	def logoutUrl(self):
		return 'https://' + self.endpoint + '/logout?client_id=' + self.client_id + "&logout_uri=https://" + self.host + self.logout_path

	def get_token(self, code):
		r = requests.post('https://' + self.endpoint + '/oauth2/token', auth=(self.client_id, self.client_secret),
			data = {'code':code, 'grant_type':'authorization_code', 'redirect_uri': "https://" + self.host + self.redirect_path })
		return r.json()['access_token']

class User:
	def __init__(self, client, token = None):
		self.data = {}
		self.token = token
		self.client = client
		self.reload()

	def is_logged_in(self):
		self.reload()
		return 'username' in self.data

	def reload(self):
		if self.token:
			self.data = requests.post('https://' + self.client.endpoint + '/oauth2/userInfo', headers={'Authorization' :"Bearer " + self.token}).json()