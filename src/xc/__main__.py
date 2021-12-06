import argparse
import sys
from urllib import request, parse
import json

def DownloadContent(download_location, xuid, token, media_type):
	request_string = f'{{"max":500,"query":"OwnerXuid eq {xuid}","skip":0}}'
	
	if media_type.casefold() == 's':
		DownloadScreenshots(download_location, request_string, token)
	elif media_type.casefold() == 'v':
		DownloadClips(download_location, request_string, token)
	else:
		DownloadScreenshots(download_location, request_string, token)
		DownloadClips(download_location, request_string, token)

def DownloadScreenshots(download_location, request_string, token):
	print('Downloading screenshots...')
	print(f'Query: {request_string}')
	screenshot_request = request.Request('https://mediahub.xboxlive.com/screenshots/search', data = request_string.encode("utf-8"), headers = {'Authorization': token, 'Content-Type': 'application/json'})
	response = request.urlopen(screenshot_request)

def DownloadClips(download_location, request_string, token):
	screenshot_request = request.Request('https://mediahub.xboxlive.com/gameclips/search', data = request_string.encode("utf-8"), headers = {'Authorization': token, 'Content-Type': 'application/json'})
	response = request.urlopen(screenshot_request)

media_type = 'A'

parser = argparse.ArgumentParser(description = 'Download Xbox Live screenshots and video clips.')

parser.add_argument('DownloadLocation',
                       metavar='dl',
                       type=str,
                       help='Folder where content needs to be downloaded.')

parser.add_argument('XUID',
                       metavar='xuid',
                       type=str,
                       help='Xbox Live numeric user identifier.')

parser.add_argument('Token',
                       metavar='token',
                       type=str,
                       help='XBL 3.0 authorization token.')

parser.add_argument('Media',
                       metavar='media',
                       type=str,
                       help='Type of media to be downloaded. Use S for screenshots, V, for video, or A for all.')

args = parser.parse_args()

if not args.DownloadLocation:
	print('You need to specify a download location.')
	sys.exit()

if not args.XUID:
	print('You need to specify a XUID in order to get screenshots and video clips.')
	sys.exit()

if not args.Token:
	print('You need to specify a XBL 3.0 token in order to get screenshots and video clips.')
	sys.exit()

if not args.Media:
	print('No media parameter specified. Assumed all media needs to be downloaded.')
else:
	media_type = args.Media

DownloadContent(args.DownloadLocation, args.XUID, args.Token, media_type)
print ('Download complete.')


