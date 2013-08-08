#######################################################
#	Steam Summer Sale Notifier
#	Ver 0.2
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
CARD_SALE_TXT_PATH = os.path.expanduser('cSaleList')

def realCheckAndPostSaleStatus(filePath, targetList, format):
	isAlreadyPosted = False
	if os.path.exists(filePath):
		with open(filePath) as f:
			resultDict = json.load(f)
		
		savedFSaleList = resultDict['data']
		for savedFSaleItem in savedFSaleList:
			if targetList[0]['id'] == savedFSaleItem['id']:
				print('already posted.')
				isAlreadyPosted = True

	if isAlreadyPosted == False:
		if os.path.exists(filePath):
			os.remove(filePath)

		saleDict = {'data':targetList, 'version':0.2}
		with open(filePath, 'w') as f:
			json.dump(saleDict, f)

		for saleItem in targetList:
			tmpStr = format % (saleItem['url'], saleItem['name'], saleItem['originalPrice'],
			 saleItem['discountedPrice'], saleItem['salePercentage'])

			try:
				dSearchDict = twt.search.tweets(q=tmpStr)
				if len(dSearchDict['statuses']) != 0:
					for dTweet in dSearchDict['statuses']:
						if dTweet['source'].count(TWT_CONSUMER_APP_NAME) == 1:
							print('removing duplicate tweet...')
							twt.statuses.destroy(id=dTweet['id'])
							break

				twt.statuses.update(status=tmpStr)
			except TwitterHTTPError as err:
				print('status error - {0}'.format(err))
			else:
				print(tmpStr)


def parsingSaleItemToDict(htmlTree):
	tmpItemDict = {}
	itemUrl = htmlTree.attrib['href'] # get sale target url
	tmpItemDict['url'] = itemUrl

	itemID = itemUrl.split('/')[4] #get sale item id and name
	tmpItemDict['id'] = itemID
	tmpItemDict['name'] = getSteamAppNameFromID(itemID)

	oPriceTree = htmlTree.cssselect('div.discount_original_price')
	if len(oPriceTree) == 0:
		print('original price not found')
		return None
	else:
		originalPrice = htmlTree.cssselect('div.discount_original_price')[0].text #get sale percentage
		tmpItemDict['originalPrice'] = originalPrice

	dPriceTree = htmlTree.cssselect('div.discount_final_price')
	if len(dPriceTree) == 0:
		print('discount price not found')
		return None
	else:
		discountedPrice = htmlTree.cssselect('div.discount_final_price')[0].text #get sale percentage
		tmpItemDict['discountedPrice'] = discountedPrice

	sPctTree = htmlTree.cssselect('div.discount_pct')
	if len(sPctTree) == 0:
		print('sale percentage not found')
		return None
	else:
		salePercentage = htmlTree.cssselect('div.discount_pct')[0].text #get sale percentage
		tmpItemDict['salePercentage'] = salePercentage

	return tmpItemDict

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

		tCardSaleDict = {}
		for tmpHtmlTree in recvParsedHtml.cssselect('div.tradingcard_spotlight a'):
			itemDict = parsingSaleItemToDict(tmpHtmlTree)
			if itemDict != None:
				tCardSaleDict = itemDict

		voteSaleDict = {}
		for tmpHtmlTree in recvParsedHtml.cssselect('div.vote_previouswinner a'):
			#print all html for debug
			#print(lxml.html.tostring(tmpHtmlTree))
			itemDict = parsingSaleItemToDict(tmpHtmlTree)
			if itemDict != None:
				voteSaleDict = itemDict

		dailySaleList = []
		for tmpHtmlTree in recvParsedHtml.cssselect('div.summersale_dailydeals a'):
			#print all html for debug
			#print(lxml.html.tostring(tmpHtmlTree))
			itemDict = parsingSaleItemToDict(tmpHtmlTree)
			if itemDict != None:
				dailySaleList.append(itemDict)

		flashSaleList = []
		for tmpHtmlTree in recvParsedHtml.cssselect('div.flashdeals_row a'):
			#print all html for debug
			#print(lxml.html.tostring(tmpHtmlTree))
			itemDict = parsingSaleItemToDict(tmpHtmlTree)
			if itemDict != None:
				flashSaleList.append(itemDict)

		print('check&posting vote sale...')
		if voteSaleDict == {}:
			print('skipping... (maybe region lock)')
		else:
			realCheckAndPostSaleStatus(VOTE_SALE_TXT_PATH, [voteSaleDict], '%s [NEW] 스팀 커뮤니티의 선택 : %s (%s->%s, %s)')

		print('check&posting card spotlight sale...')
		if tCardSaleDict == {}:
			print('skipping... (trading card region lock)')
		else:
			realCheckAndPostSaleStatus(CARD_SALE_TXT_PATH, [tCardSaleDict], '%s [NEW] 스팀 일일 세일 : %s (%s->%s, %s)')

		print('check&posting daily sale...')
		realCheckAndPostSaleStatus(DAILY_SALE_TXT_PATH, dailySaleList, '%s [NEW] 스팀 일일 세일 : %s (%s->%s, %s)')
		
		print('check&posting flash sale...')
		realCheckAndPostSaleStatus(FLASH_SALE_TXT_PATH, flashSaleList, '%s [NEW] 스팀 반짝 세일 : %s (%s->%s, %s)')

if __name__ == "__main__":
	while True:
		checkAndPostSaleStatus()
		time.sleep(60*5)
