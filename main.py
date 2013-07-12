#######################################################
#	Steam Summer Sale Notifier
#	Ver 0.1
#	Author : Yi Yeon Jae (pusungwi@gmail.com)
#######################################################

from twitter import *

import os
import urllib.request
import io
import json
import lxml.html
import time, datetime

SEARCH_URL = 'http://store.steampowered.com'
STEAM_API_KEY = ''
TWT_CONSUMER_APP_NAME = "SSSNotifier"
TWT_CONSUMER_KEY = ''
TWT_CONSUMER_SECRET = ''
STEAM_APP_UNKNOWN_NAME = '???'

MY_TWITTER_CREDS = os.path.expanduser('~/.sss_creds')
STEAM_APP_LIST_PATH = os.path.expanduser('steamAppList')
DAILY_SALE_TXT_PATH = os.path.expanduser('dSaleList')
FLASH_SALE_TXT_PATH = os.path.expanduser('fSaleList')
VOTE_SALE_TXT_PATH = os.path.expanduser('vSaleList')

def getSteamAppNameFromID(id):
	resultDict = None
	if not os.path.exists(STEAM_APP_LIST_PATH):
		print('Steam App List Not Found. Dumping...')
		targetUrl = "http://api.steampowered.com/ISteamApps/GetAppList/v2/?key=" + STEAM_API_KEY
		targetJSON = urllib.request.urlopen(targetUrl)
		targetDecodedJSON = targetJSON.read().decode('utf-8')
		resultDict = json.loads(targetDecodedJSON)

		with open(STEAM_APP_LIST_PATH, 'w') as f:
			json.dump(resultDict, f)
	else:
		#data = open(STEAM_APP_LIST_PATH)
		#resultDict = json.load()
		with open(STEAM_APP_LIST_PATH) as f:
			resultDict = json.load(f)

	appsList = resultDict['applist']['apps']

	for appDict in appsList:
		if str(id) == str(appDict['appid']):
			return appDict['name']

	return STEAM_APP_UNKNOWN_NAME

# twitter auth
if not os.path.exists(MY_TWITTER_CREDS):
    oauth_dance(TWT_CONSUMER_APP_NAME, TWT_CONSUMER_KEY, TWT_CONSUMER_SECRET, MY_TWITTER_CREDS)

oauth_token, oauth_secret = read_token_file(MY_TWITTER_CREDS)
# auth end

twt = Twitter(auth=OAuth(oauth_token, oauth_secret, TWT_CONSUMER_KEY, TWT_CONSUMER_SECRET))

def checkAndPostSaleStatus():
	print('running... (%s)' % datetime.datetime.now())
	try:
		requestFullUrl = SEARCH_URL
		recvSearchHtml = urllib.request.urlopen(requestFullUrl)
	except IOError:
		print("URL address Error")
	else:
		recvRawHtml = recvSearchHtml.read()
		recvRawDecodedHtml = recvRawHtml.decode('utf-8')
		recvParsedHtml = lxml.html.fromstring(recvRawDecodedHtml)#etree.parse(io.StringIO(recvRawDecodedHtml), parser) # result parsed tree
		#debug code
		#result = etree.tostring(recvParsedHtml.getroot(), pretty_print=True, method="html")
		#print(recvParsedHtml)

		voteSaleDict = {}
		for tmpHtmlTree in recvParsedHtml.cssselect('div.vote_previouswinner a'):
			itemUrl = tmpHtmlTree.attrib['href'] # get sale target url
			voteSaleDict['url'] = itemUrl

			itemID = itemUrl.split('/')[4] #get sale item id and name
			voteSaleDict['id'] = itemID
			voteSaleDict['name'] = getSteamAppNameFromID(itemID)

			originalPrice = tmpHtmlTree.cssselect('div.discount_original_price')[0].text #get sale percentage
			voteSaleDict['originalPrice'] = originalPrice

			discountedPrice = tmpHtmlTree.cssselect('div.discount_final_price')[0].text #get sale percentage
			voteSaleDict['discountedPrice'] = discountedPrice

			salePercentage = tmpHtmlTree.cssselect('div.discount_pct')[0].text #get sale percentage
			voteSaleDict['salePercentage'] = salePercentage

		dailySaleList = []
		for tmpHtmlTree in recvParsedHtml.cssselect('div.summersale_dailydeals a'):
			#print all html for debug
			#print(lxml.html.tostring(tmpHtmlTree))

			tmpItemDict = {}
			itemUrl = tmpHtmlTree.attrib['href'] # get sale target url
			tmpItemDict['url'] = itemUrl

			itemID = itemUrl.split('/')[4] #get sale item id and name
			tmpItemDict['id'] = itemID
			tmpItemDict['name'] = getSteamAppNameFromID(itemID)
		
			originalPrice = tmpHtmlTree.cssselect('div.discount_original_price')[0].text #get sale percentage
			tmpItemDict['originalPrice'] = originalPrice

			discountedPrice = tmpHtmlTree.cssselect('div.discount_final_price')[0].text #get sale percentage
			tmpItemDict['discountedPrice'] = discountedPrice

			salePercentage = tmpHtmlTree.cssselect('div.discount_pct')[0].text #get sale percentage
			tmpItemDict['salePercentage'] = salePercentage

			dailySaleList.append(tmpItemDict)

		flashSaleList = []
		for tmpHtmlTree in recvParsedHtml.cssselect('div.flashdeals_row a'):
			#print all html for debug
			#print(lxml.html.tostring(tmpHtmlTree))
			tmpItemDict = {}
			itemUrl = tmpHtmlTree.attrib['href'] # get sale target url
			tmpItemDict['url'] = itemUrl

			itemID = itemUrl.split('/')[4] #get sale item id and name
			tmpItemDict['id'] = itemID
			tmpItemDict['name'] = getSteamAppNameFromID(itemID)
		
			originalPrice = tmpHtmlTree.cssselect('div.discount_original_price')[0].text #get sale percentage
			tmpItemDict['originalPrice'] = originalPrice

			discountedPrice = tmpHtmlTree.cssselect('div.discount_final_price')[0].text #get sale percentage
			tmpItemDict['discountedPrice'] = discountedPrice

			salePercentage = tmpHtmlTree.cssselect('div.discount_pct')[0].text #get sale percentage
			tmpItemDict['salePercentage'] = salePercentage

			flashSaleList.append(tmpItemDict)

		#read and write community Sale
		isVSAlreadyPosted = False 
		if os.path.exists(VOTE_SALE_TXT_PATH):
			with open(VOTE_SALE_TXT_PATH) as f:
				resultDict = json.load(f)

			if voteSaleDict['id'] == resultDict['id']:
				print('already posted. (Vote Sale)')
				isVSAlreadyPosted = True

		if isVSAlreadyPosted == False:
			print('post & saving... (Vote Sale)')
			if os.path.exists(VOTE_SALE_TXT_PATH):
				os.remove(VOTE_SALE_TXT_PATH)

			with open(VOTE_SALE_TXT_PATH, 'w') as f:
				json.dump(voteSaleDict, f)

			tmpStr = '%s [NEW] 스팀 커뮤니티의 선택 : %s (%s->%s, %s 할인)' % (voteSaleDict['url'], voteSaleDict['name'], voteSaleDict['originalPrice'],
			 voteSaleDict['discountedPrice'], voteSaleDict['salePercentage'])
			print(tmpStr)
			twt.statuses.update(status=tmpStr)

		#read and write daily sale
		isDSAlreadyPosted = False
		if os.path.exists(DAILY_SALE_TXT_PATH):
			with open(DAILY_SALE_TXT_PATH) as f:
				resultDict = json.load(f)
		
			savedDSaleList = resultDict['data']
			for savedDSaleItem in savedDSaleList:
				if dailySaleList[0]['id'] == savedDSaleItem['id']:
					print('already posted. (Daily Sale)')
					isDSAlreadyPosted = True

		if isDSAlreadyPosted == False:
			print('post & saving... (Daily Sale)')
			if os.path.exists(DAILY_SALE_TXT_PATH):
				os.remove(DAILY_SALE_TXT_PATH)

			dailySaleDict = {'data':dailySaleList, 'version':0.1}
			with open(DAILY_SALE_TXT_PATH, 'w') as f:
				json.dump(dailySaleDict, f)

			for dailySaleItem in dailySaleList:
				tmpStr = '%s [NEW] 스팀 일일 세일 : %s (%s->%s, %s 할인)' % (dailySaleItem['url'], dailySaleItem['name'], dailySaleItem['originalPrice'],
				 dailySaleItem['discountedPrice'], dailySaleItem['salePercentage'])
				print(tmpStr)
				twt.statuses.update(status=tmpStr)

		#read and write flash sale
		isFSAlreadyPosted = False
		if os.path.exists(FLASH_SALE_TXT_PATH):
			with open(FLASH_SALE_TXT_PATH) as f:
				resultDict = json.load(f)
		
			savedFSaleList = resultDict['data']
			for savedFSaleItem in savedFSaleList:
				if flashSaleList[0]['id'] == savedFSaleItem['id']:
					print('already posted. (Flash Sale)')
					isFSAlreadyPosted = True

		if isFSAlreadyPosted == False:
			print('post & saving... (Flash Sale)')
			if os.path.exists(FLASH_SALE_TXT_PATH):
				os.remove(FLASH_SALE_TXT_PATH)

			flashSaleDict = {'data':flashSaleList, 'version':0.1}
			with open(FLASH_SALE_TXT_PATH, 'w') as f:
				json.dump(flashSaleDict, f)

			for flashSaleItem in flashSaleList:
				tmpStr = '%s [NEW] 스팀 반짝 세일 : %s (%s->%s, %s 할인)' % (flashSaleItem['url'], flashSaleItem['name'], flashSaleItem['originalPrice'],
				 flashSaleItem['discountedPrice'], flashSaleItem['salePercentage'])
				print(tmpStr)
				twt.statuses.update(status=tmpStr)


if __name__ == "__main__":
	while True:
		checkAndPostSaleStatus()
		time.sleep(60*10)
