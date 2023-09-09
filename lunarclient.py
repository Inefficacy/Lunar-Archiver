import yaml
import requests
import random
import uuid

# define some constants

ELECTRON_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Electron/15.3.4 Safari/537.36' # generic user agent for electron

LUNAR_CLIENT_VERSION = '0.0.0'
LUNAR_CLIENT_USER_AGENT = f'Lunar Client Launcher v{LUNAR_CLIENT_VERSION}'

class Endpoints:
	UPDATE = 'https://launcherupdates.lunarclientcdn.com/latest.yml'
	METADATA = 'https://api.lunarclientprod.com/launcher/metadata'
	LAUNCH = 'https://api.lunarclientprod.com/launcher/launch'

# generate random (invalid) hex
randomString = lambda l: ''.join(random.choices('0123456789abcdef', k=l))

# TODO: add typings

# artifact object
class Artifact:
	def __init__(self, raw):
		self.name = raw['name']
		self.sha1 = raw['sha1']
		self.url = raw['url']
		self.differentialUrl = raw['differentialUrl']
		self.type = raw['type']

	def download(self):
		r = requests.get(self.url, headers={'User-Agent': ''})
		if r.status_code != 200:
			raise ValueError(r.text)
		return r.content

# the actual wrapper
class API:
	def getUpdate():
		global LUNAR_CLIENT_VERSION, LUNAR_CLIENT_USER_AGENT
		r = requests.get(Endpoints.UPDATE, headers={'User-Agent': ELECTRON_USER_AGENT})
		if r.status_code != 200:
			raise ValueError(r.text)
		parsed = yaml.safe_load(r.text)

		LUNAR_CLIENT_VERSION = parsed['version']
		LUNAR_CLIENT_USER_AGENT = f'Lunar Client Launcher v{LUNAR_CLIENT_VERSION}'

		return parsed

	def getMetadata(version=LUNAR_CLIENT_VERSION):
		r = requests.get(Endpoints.METADATA, params={'launcher_version': version}, headers={'User-Agent': LUNAR_CLIENT_USER_AGENT})
		if r.status_code != 200:
			raise ValueError(r.text)
		return r.json()

	def getLaunch(**kwargs):
		"""
		Send a launch request

		Args:
			hwid: hardware id
			installation_id: uuid v4 used to identify installations
			hwid_private: ?
			os (aix, darwin, freebsd, linux, openbsd, sunos, win32): from os.platform() in nodejs
			os_release: from os.release()
			arch (arm, arm64, ia32, mips, mipsel, ppc, ppc64, s390, s390x, x64): from os.arch()
			launcher_version: version of the lunar client launcher,
			version (1.7.10, 1.8.9, 1.12.2, 1.16.5, 1.17.1, 1.18.1, 1.18.2, 1.19, 1.19.2, 1.19.3, 1.19.4, 1.20, 1.20.1): minecraf version
			branch (master): branch to launch from
			launch_type (OFFLINE, ONLINE): not sure if this is even relevant
			args ([]): ?
			module (lunar, forge, fabric): formerly classifer

		Returns:
			dict: launch response

		Raises:
			ValueError: if the response status code is not ok
		"""
		json = {
			'hwid': randomString(34),
			'installation_id': str(uuid.uuid4()),
			'hwid_private': randomString(512),
			'os': 'win32',
			'os_release': '10.0.0',
			'arch': 'x64',
			'launcher_version': LUNAR_CLIENT_VERSION,
			'version': '1.8.9',
			'branch': 'master',
			'launch_type': 'OFFLINE',
			'args': [],
			'module': 'lunar'
		}
		json.update(kwargs)

		headers = {
			'User-Agent': LUNAR_CLIENT_USER_AGENT
		}
		headers.update({'x-'+k: v for k, v in json.items() if k in ('hwid', 'installation_id', 'hwid_private')})

		r = requests.post(Endpoints.LAUNCH, json=json, headers=headers)
		if r.status_code != 200:
			raise ValueError(r.text)
		j = r.json()
		if j['success'] == False:
			raise ValueError(j['error']['message'])
		return j

	def parseArtifacts(launchResponse=None):
		if launchResponse == None:
			launchResponse = API.getLaunch()
		return [Artifact(a) for a in launchResponse['launchTypeData']['artifacts']]