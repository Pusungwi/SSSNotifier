#######################################################
#	Steam Summer Sale Notifier
#	Ver 0.1
#	Author : Yi Yeon Jae (pusungwi@gmail.com)
#######################################################

from lxml import etree
from twitter import *

import os
import urllib.request
import io

SEARCH_URL = 'http://store.steampowered.com'
TOP_VOTED_TXT_PATH = os.path.expanduser('~/.topvoted')
TWT_CONSUMER_APP_NAME = "SSSNotifier"
TWT_CONSUMER_KEY = ':-P'
TWT_CONSUMER_SECRET = ':-P'
MY_TWITTER_CREDS = os.path.expanduser('~/.sss_creds')

# twitter auth
if not os.path.exists(MY_TWITTER_CREDS):
    oauth_dance(TWT_CONSUMER_APP_NAME, TWT_CONSUMER_KEY, TWT_CONSUMER_SECRET,
                MY_TWITTER_CREDS)

oauth_token, oauth_secret = read_token_file(MY_TWITTER_CREDS)
# auth end

twt = Twitter(auth=OAuth(
    oauth_token, oauth_secret, TWT_CONSUMER_KEY, TWT_CONSUMER_SECRET))

try:
	requestFullUrl = SEARCH_URL
	recvSearchHtml = urllib.request.urlopen(requestFullUrl)
except IOError:
	print("URL address Error")
else:
	discountTitle = ''
	discountPercent = ''
	discountWasPrice = ''
	discountNowPrice = ''
	parser = etree.HTMLParser()
	recvRawHtml = recvSearchHtml.read()
	recvRawDecodedHtml = recvRawHtml.decode('utf-8')
	recvParsedHtml = etree.parse(io.StringIO(recvRawDecodedHtml), parser) # result parsed tree
	#debug code
	#result = etree.tostring(recvParsedHtml.getroot(), pretty_print=True, method="html")
	#print(result)
	
	for htmlTree in recvParsedHtml.getiterator():
		#print("-------------------------")
		#print("head : %s", htmlTree.head)
		#print("text : %s", htmlTree.text)
		#print("-------------------------")
		for htmlValue in htmlTree.values():
			#topvoted item select if method
			if htmlValue == 'ss_topvoted':
				for tmpTopVotedItem in htmlTree.getchildren():
						tvItemValues = tmpTopVotedItem.values()
						#discount item select if method
						if (tvItemValues[0] == 'discount'):
							priceItems = tmpTopVotedItem.getchildren()[0]
							for tmpPriceItem in priceItems.getchildren():
								#was/now price select if method
								if tmpPriceItem.values() == []:
									discountNowPrice = tmpPriceItem.text.strip()
								else:
									discountWasPrice = tmpPriceItem.text.strip()
							discountPercent = tmpTopVotedItem.text.strip()[1:]	
						else:
							tmp = tmpTopVotedItem.values()
							discountTitle = tmp[1]
						#print("-------------------------")
						#tmp = tmpTopVotedItem.values()
						#print(tmp)
						#print("tag : %s", tmpTopVotedItem.tag)
						#print("text : %s", tmpTopVotedItem.text.strip())
						#print("-------------------------")

	topVotedGameStr = "[NEW] 최다 득표 할인 게임 : " + discountTitle + " -" + discountPercent + " 가격 : " + discountWasPrice + " -> " + discountNowPrice + " #bot"
	print(topVotedGameStr)
	# twitter auth
	if os.path.exists(TOP_VOTED_TXT_PATH):
		#test print
		wasTopVotedGameFile = open(TOP_VOTED_TXT_PATH, 'r+')
		wasTopVotedGameStr = wasTopVotedGameFile.read()
		if wasTopVotedGameStr != topVotedGameStr:
			wasTopVotedGameFile.write(topVotedGameStr)
			twt.statuses.update(status=topVotedGameStr)
		else:
			print("No Update")
		wasTopVotedGameFile.close()
	else:
		wasTopVotedGameFile = open(TOP_VOTED_TXT_PATH, 'w')
		wasTopVotedGameFile.write(topVotedGameStr)
		twt.statuses.update(status=topVotedGameStr)
		wasTopVotedGameFile.close()
		
