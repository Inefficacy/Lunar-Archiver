import requests
import colorama

class LcAPI:
	def print_(self, type, state, message):
		if self.verbose == True:
			typed = {0: colorama.Back.GREEN, 1: colorama.Back.YELLOW, 2: colorama.Back.RED, 3: colorama.Back.CYAN}
			rst = colorama.Style.RESET_ALL
			print(f'{typed[type]}{state}{rst} {message}')
	def __init__(self, json, verbose=True):
		colorama.init(autoreset=True)
		self.json = json
		self.verbose = verbose
	def download(self):
		self.print_(3, 'download', 'starting')
		try:
			r = requests.post('https://api.lunarclientprod.com/launcher/launch', json=self.json)
		except requests.exceptions.RequestException as e:
			self.print_(2, 'download', e)
			return False
		if r.status_code == 200 and r.json() != None:
			self.print_(1, 'download', 'finished downloading')
		else:
			self.print_(2, 'download', f'status code {r.status_code}')
			return False
		self.rjson = r.json()
		return r.content
	def downloadArtifact(self, name, checkSHA1=False):
		self.print_(3, 'download-artifact', name)
		for artifact in self.rjson['launchTypeData']['artifacts']:
			if artifact['name'] == name:
				self.print_(0, 'download-artifact', f'found artifact {name}')
				try:
					r = requests.get()
				except requests.exceptions.RequestException as e:
					self.print_(2, 'download-artifact', f'{e} on {name}')
					return False
				if r.status_code == 200 and r.content != None:
					self.print_(1, 'download-artifact', f'finished downloading {name}')
				else:
					self.print_(2, 'download-artifact', f'status code {r.status_code} on {name}')
					return False
				return r.content