import lcapi
import json
from zipfile import ZipFile
from datetime import datetime
import os
import io

print("""  ___           _     _                
 / _ \         | |   (_)               
/ /_\ \_ __ ___| |__  ___   _____ _ __ 
|  _  | '__/ __| '_ \| \ \ / / _ \ '__|
| | | | | | (__| | | | |\ V /  __/ |   
\_| |_/_|  \___|_| |_|_| \_/ \___|_|""")

print('Loading config...')
config = json.load(open('config.json'))

lunarapi = lcapi.LcAPI(config['launcherRequest'], config['verbose'])

launchRequest = lunarapi.download()

if launchRequest == False:
	exit()

artifacts = [a['name'] for a in launchRequest.json()['launchTypeData']['artifacts']]

avoidDuplicatePath = config['avoidDuplicate']['path'].replace('$os', config['launcherRequest']['os']).replace('$version', config['launcherRequest']['version'])

duplicates = [
	newArtifact["name"]
	for newArtifact in launchRequest.json()["launchTypeData"]["artifacts"]
	if config["avoidDuplicate"]["enabled"] == True
	and os.path.exists(avoidDuplicatePath) and any(
		newArtifact["name"] == oldArtifact["name"]
		and newArtifact["sha1"] == oldArtifact["sha1"]
		for oldArtifact in json.load(open(avoidDuplicatePath))["launchTypeData"]["artifacts"]
	)
]

lunarapi.print_(3, 'main', f'found {len(duplicates)} duplicate{"s"[:len(duplicates)^1]} artifact')

mainFile = lunarapi.downloadArtifact('lunar.jar')

buildData = None

with ZipFile(io.BytesIO(mainFile)) as zf:
	try:
		buildData = zf.read('lunarBuildData.txt').decode('utf-8')
		lunarapi.print_(0, 'main', 'found build data')
	except:
		lunarapi.print_(2, 'main', 'could not find build data')

if buildData:
	buildHash = buildData.split('\n')[3].replace('fullGitHash=','')
else:
	buildHash = datetime.now().strftime('%m-%d-%Y-%H:%M')

savePath = config['folderStructure'].replace('$os', config['launcherRequest']['os']).replace('$version', config['launcherRequest']['version']).replace('$buildhash', buildHash)

os.makedirs(savePath, exist_ok=True)
if buildData and config['saveBuildData']:
	open(savePath+'lunarBuildData.txt', 'w+').write(buildData)

if config['saveResponse']:
	open(savePath+'launcherRequest.json', 'w+').write(launchRequest.text)

open(avoidDuplicatePath, 'w+').write(launchRequest.text)

if config['saveJar']:
	open(savePath+'lunar.jar', 'wb').write(mainFile)

for artifactName in artifacts:
	if artifactName != 'lunar.jar' and config['saveJar'] and artifactName not in duplicates:
		artifact = lunarapi.downloadArtifact(artifactName)
		open(savePath+artifactName, 'wb').write(artifact)

lunarapi.print_(0, 'main', 'done')