import argparse
import sys
from urllib import request, parse
from urllib.request import urlretrieve
import json
from types import SimpleNamespace
import os
from urllib.parse import urlparse
import socket

def MakeJSON(entity):
    return json.dumps(entity, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

def DownloadContent(download_location, xuid, token, media_type):
	if media_type.casefold() == 's':
		DownloadData('screenshots', xuid, download_location, token)
	elif media_type.casefold() == 'v':
		DownloadData('gameclips', xuid, download_location, token)
	else:
		DownloadData('screenshots', xuid, download_location, token)
		DownloadData('gameclips', xuid, download_location, token)

def GetContentEntities(xuid, endpoint, token, continuation_token = None):
	request_string = ''
	if not continuation_token:
		request_string = f'{{"max":500,"query":"OwnerXuid eq {xuid}","skip":0}}'
	else:
		request_string = f'{{"max":500,"query":"OwnerXuid eq {xuid}","skip":0, "continuationToken": "{continuation_token}"}}'

	screenshot_request = request.Request(f'https://mediahub.xboxlive.com/{endpoint}/search', data = request_string.encode("utf-8"), headers = {'Authorization': token, 'Content-Type': 'application/json'})

	response = request.urlopen(screenshot_request)

	content_entities = None

	if response.getcode() == 200:
		print ('Successfully got content collection.')
		content_entities = json.loads(response.read(), object_hook=lambda d: SimpleNamespace(**d))
	else:
		print('Could not get a successful response from the Xbox Live service.')

	return content_entities

def GetContentEntity(endpoint, xuid, local_id, token):
	request_string = f'{{"max":20,"query":"OwnerXuid eq {xuid} and localId eq \'{local_id}\'","skip":0}}'

	screenshot_request = request.Request(f'https://mediahub.xboxlive.com/{endpoint}/search', data = request_string.encode("utf-8"), headers = {'Authorization': token, 'Content-Type': 'application/json'})

	response = request.urlopen(screenshot_request)

	content_entity = None

	if response.getcode() == 200:
		print ('Successfully got content.')
		content_entity = json.loads(response.read(), object_hook=lambda d: SimpleNamespace(**d))
	else:
		print('Could not get a successful response from the Xbox Live service.')

	return content_entity


def DownloadData(endpoint, xuid, download_location, token, continuation_token = None):
	print(f'Downloading from the {endpoint} endpoint...')

	content_entities = GetContentEntities(xuid, endpoint, token, continuation_token)

	# We just want the local IDs for now to make sure that we know what needs to be
	# downloaded. The URLs here are not used for downloads.
	local_ids = [e.localId for e in content_entities.values] 
	print(f'Obtained {len(local_ids)} content IDs.')

	if not local_ids == None:
		for local_id in local_ids:
			print(f'Currently downloading content with ID: {local_id}')

			entity = GetContentEntity(endpoint, xuid, local_id, token).values[0]

			if entity:
				metadata_path = os.path.join(download_location, entity.contentId + ".json")
				with open(metadata_path, 'w') as metadata_file:
				    metadata_file.write(MakeJSON(entity))
				print(f'Metadata acquisition successful.')

				locator = next((x for x in entity.contentLocators if x.locatorType.casefold() == 'download'))
				locator_ts = next((x for x in entity.contentLocators if x.locatorType.casefold() == 'thumbnail_small'))
				locator_tl = next((x for x in entity.contentLocators if x.locatorType.casefold() == 'thumbnail_large'))

				if locator:
					print(f'Attempting to download content at {locator.uri}...')
					media_path = os.path.join(download_location, os.path.basename(urlparse(locator.uri).path))
					try:
						urlretrieve(locator.uri, media_path)
					except:
						print(f'Could not download content at {locator.uri}.')

				if locator_ts:
					print(f'Attempting to download small thumbnail at {locator_ts.uri}...')
					media_path = os.path.join(download_location, 'small_' + os.path.basename(urlparse(locator_ts.uri).path))
					try:
						urlretrieve(locator_ts.uri, media_path)
					except:
						print(f'Could not download small thumbnail at {locator_ts.uri}.')

				if locator_tl:
					print(f'Attempting to download large thumbnail at {locator_tl.uri}...')
					media_path = os.path.join(download_location, 'large_' + os.path.basename(urlparse(locator_tl.uri).path))
					try:
						urlretrieve(locator_tl.uri, media_path)
					except:
						print(f'Could not download large thumbnail at {locator_tl.uri}.')
			else:
				print (f'Could not download entity: {local_id}')
		try:
			DownloadData(endpoint, xuid, download_location, token, content_entities.continuationToken)
		except AttributeError:
			print('No more continuation tokens. Assuming media of requested class is downloaded completely.')
	else:
		print('No content entities to process.')

def SendDeleteRequest(token, xuid, endpoint, content_id):
	request_string = '{"headers": {"Accept": "application/json", "X-XBL-Contract-Version": "2"}}'

	delete_request = request.Request(f'https://mediahub.xboxlive.com/{endpoint}/{content_id}', data = request_string.encode("utf-8"), headers = {'Authorization': token, 'Content-Type': 'application/json'})
	delete_request.get_method = lambda: 'DELETE' # Yikes, but gets the job done for now.
	response = request.urlopen(delete_request)

	response_code = response.getcode()
	acceptable_codes = [200, 202]
	if response_code in acceptable_codes:
		return True
	else:
		return False

def DeleteAllMedia(token, xuid, endpoint):
	content_entities = GetContentEntities(xuid, endpoint, token)

	while len(content_entities.values) > 0:
		for entity in content_entities.values:
			success = SendDeleteRequest(token, xuid, endpoint, entity.contentId)
			if success:
				print(f'Successfully deleted {entity.contentId}')
			else:
				print(f'Could not delete {entity.contentId}')

		content_entities = GetContentEntities(xuid, endpoint, token)

socket.setdefaulttimeout(300)

media_type = 'A'

parser = argparse.ArgumentParser(description = 'Download Xbox Live screenshots and video clips.')

subparsers = parser.add_subparsers(help='', dest='command')

parser_downloader = subparsers.add_parser('download', help='Download media from the Xbox network.')

parser_downloader.add_argument('--token',
                       metavar='token',
                       type=str,
                       help='XBL 3.0 authorization token.')

parser_downloader.add_argument('--download-location',
                       metavar='dl',
                       type=str,
                       help='Folder where content needs to be downloaded.')

parser_downloader.add_argument('--xuid',
                       metavar='xuid',
                       type=str,
                       help='Xbox Live numeric user identifier.')

parser_downloader.add_argument('--media',
                       choices=['s', 'v', 'a'],
                       help='Type of media to be downloaded. Use S for screenshots, V, for video, or A for all.')

parser_cleaner = subparsers.add_parser('clean', help='Clean media from an Xbox network account.')

parser_cleaner.add_argument('--mode', choices=['all', 'select'], help='Determines the mode of cleanup to be performed.')

parser_cleaner.add_argument('--token',
                       metavar='token',
                       type=str,
                       help='XBL 3.0 authorization token.')

parser_cleaner.add_argument('--xuid',
                       metavar='xuid',
                       type=str,
                       help='Xbox Live numeric user identifier. Optional for selective cleanup.')


args = parser.parse_args()

if not args.token:
	print('You need to specify a XBL 3.0 token in order to get screenshots and video clips.')
	sys.exit()

if args.command.casefold() == 'download':
	print('User chose to download the stored Xbox Live media.')

	if not args.download_location:
		print('You need to specify a download location.')
		sys.exit()

	if not args.xuid:
		print('You need to specify a XUID in order to get screenshots and video clips.')
		sys.exit()

	if not args.media:
		print('No media parameter specified. Assumed all media needs to be downloaded.')
	else:
		media_type = args.Media

	DownloadContent(args.DownloadLocation, args.XUID, args.Token, media_type)
	print ('Download complete.')
elif args.command.casefold() == 'clean':
	print('User chose to clean the stored Xbox Live media.')

	if not args.mode:
		print('You need to specify a cleanup mode before proceeding.')
		sys.exit()

	if args.mode.casefold() == 'all':
		print('Cleanup mode: ALL')
		if not args.xuid:
			print('You need to specify a XUID in order to get screenshots and video clips.')
			sys.exit()

		DeleteAllMedia(args.token, args.xuid, 'screenshots')
		DeleteAllMedia(args.token, args.xuid, 'gameclips')
else:
	print('Unknown command.')


