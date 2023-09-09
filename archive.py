from lunarclient import API

import json
import os
import io
import colorama
import json
import argparse
import platform
from zipfile import ZipFile
from datetime import datetime

def print_(type, state, message):
		colors = {0: colorama.Back.GREEN, 1: colorama.Back.YELLOW, 2: colorama.Back.RED, 3: colorama.Back.CYAN}
		print(f'{colors[type]}{state}{colorama.Style.RESET_ALL} {message}')

print("""  ___           _     _                
 / _ \         | |   (_)               
/ /_\ \_ __ ___| |__  ___   _____ _ __ 
|  _  | '__/ __| '_ \| \ \ / / _ \ '__|
| | | | | | (__| | | | |\ V /  __/ |   
\_| |_/_|  \___|_| |_|_| \_/ \___|_|
""")


arg = argparse.ArgumentParser()

# archiver args
arg.add_argument('--save-jar', type=bool, default=True, help='save jar files')
arg.add_argument('--save-response', type=bool, default=True, help='save launch response')
arg.add_argument('--save-build-data', type=bool, default=True, help='save lunarBuildData.txt')
arg.add_argument('--folder-structure', type=str, default='out/$os/$version/$buildhash/', help='save path')
arg.add_argument('--avoid-duplicates', type=bool, default=True, help='avoid downloading duplicates')

# launch request args
arg.add_argument('--os', type=str, choices=['darwin', 'linux', 'win32'], default={'Linux': 'linux', 'Windows': 'win32', 'Darwin': 'darwin'}.get(platform.system()))
arg.add_argument('--os-version', type=str, default=platform.version())
arg.add_argument('--arch', type=str, choices=['arm', 'arm64', 'ia32', 'mips', 'mipsel', 'ppc', 'ppc64', 's390', 's390x', 'x64'], default=platform.machine().lower() if platform.machine().lower() in ['arm', 'arm64', 'ia32', 'mips', 'mipsel', 'ppc', 'ppc64', 's390', 's390x', 'x64'] else 'x64')
arg.add_argument('--version', type=str, choices=['1.7.10', '1.8.9', '1.12.2', '1.16.5', '1.17.1', '1.18.1', '1.18.2', '1.19', '1.19.2', '1.19.3', '1.19.4', '1.20', '1.20.1'], default='1.8.9')
arg.add_argument('--branch', type=str, default='master')
arg.add_argument('--type', type=str, choices=['lunar', 'forge', 'fabric'], default='lunar')

args = arg.parse_args()

launcherVersion = API.getUpdate()['version']
print_(3, 'update', f'version {launcherVersion}')

launchResponse = API.getLaunch(os=args.os, os_release=args.os_version, arch=args.arch, version=args.version, branch=args.branch, module=args.type)
print_(0, 'launch', 'sent request successfully')

artifacts = API.parseArtifacts(launchResponse)

lastLaunchResponsePath = f'out/{args.os}/{args.version}/last.json'

duplicates = [
	artifact.name
	for artifact in artifacts
	if args.avoid_duplicates
	and os.path.exists(lastLaunchResponsePath) and any(
		artifact.name == oldArtifact.name
		and artifact.sha1 == oldArtifact.sha1
		for oldArtifact in API.parseArtifacts(json.load(open(lastLaunchResponsePath, 'r')))
	)
]

print_(3, 'main', f'found {len(duplicates)} duplicate artifact{"s"[:len(duplicates)^1]}')

if len(duplicates) >= len(artifacts):
	print_(2,  'main', 'nothing to download, exiting')
	exit()

mainFile = [artifact for artifact in artifacts if artifact.name == 'lunar.jar'][0].download()
print_(3, 'download', 'downloaded artifact lunar.jar')

buildData = None

with ZipFile(io.BytesIO(mainFile)) as zf:
	try:
		buildData = zf.read('lunarBuildData.txt').decode('utf-8')
		print_(0, 'main', 'found build data')
	except:
		print_(2, 'main', 'could not find build data')

if buildData:
	buildHash = buildData.split('\n')[3].replace('fullGitHash=','')
else:
	buildHash = datetime.now().strftime('%m-%d-%Y-%H:%M')

savePath = args.folder_structure.replace('$os', args.os).replace('$version', args.version).replace('$buildhash', buildHash)

os.makedirs(savePath, exist_ok=True)
if buildData and args.save_build_data:
	open(savePath+'lunarBuildData.txt', 'w+').write(buildData)

if args.save_response:
	json.dump(launchResponse, open(savePath+'launcherRequest.json', 'w+'), indent=4)

json.dump(launchResponse, open(lastLaunchResponsePath, 'w+'), indent=4)

if args.save_jar:
	open(savePath+'lunar.jar', 'wb').write(mainFile)

for artifact in artifacts:
	if artifact.name != 'lunar.jar' and args.save_jar and artifact.name not in duplicates:
		open(savePath+artifact.name, 'wb').write(artifact.download())
		print_(3, 'download', f'downloaded artifact {artifact.name}')

print_(0, 'main', 'done')