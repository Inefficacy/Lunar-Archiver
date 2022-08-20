# Lunar Client Archiver
## An easy to use tool to archive versions of [Lunar Client](https://lunarclient.com/)
## Prerequisites

 - Python 3
## Getting Started
 - Install requirements using `python3 -m pip install -r requirements.txt`
 - Setup configuration in `config.json`
 - Run `archive.py` with Python 3
## Configuration
|Name| Type | Description |
|--|--|--|
| saveJar | boolean | save the JAR files |
| saveResponse | boolean | save the JSON response |
| saveBuildData | boolean | save lunarBuildData.txt |
| folderStrcuture | string | output path |
| verbose | bool | show whats happening |
| mainFile | JSON | main JAR file |
| launchRequest | JSON | what will be sent to the Lunar API |

## To-Do
 - [x] API
 - [ ] Get build data on MacOS
 - [ ] Multi-Threaded download
 - [ ] Check SHA1 hash when downloading an artifact