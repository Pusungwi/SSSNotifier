import urllib.request
import io
from lxml import etree

SEARCH_URL = 'http://store.steampowered.com'

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

	print("최다 득표 할인 게임 :", discountTitle, "할인률 :", discountPercent)
