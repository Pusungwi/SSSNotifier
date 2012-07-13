from lxml import etree
from twitter import *

import os
import urllib.request
import io

SEARCH_URL = 'http://store.steampowered.com'
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
			if htmlValue == 'ss_topvoted':
				for tmpTopVotedItem in htmlTree.getchildren():
						tvItemValues = tmpTopVotedItem.values()
						if (tvItemValues[0] == 'discount'):
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

	topVotedGameStr = "최다 득표 할인 게임 : " + discountTitle + " 할인률 : " + discountPercent + " #bot"
	twt.statuses.update(status=topVotedGameStr)
