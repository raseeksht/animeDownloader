import requests
import re
from bs4 import BeautifulSoup
import conf


url =  "https://animekisa.tv/monster-episode-2"


def getSoup(url):
	res = requests.get(url)
	return BeautifulSoup(res.content,'html.parser')

def vidstreamingUrl(url):
	match = re.compile(r'var VidStreaming = ')
	urlLine = re.findall(r'var VidStreaming = [a-zA-Z0-9":/.?=&]+',str(getSoup(url)))[0]
	return re.findall(r'https[a-zA-Z0-9:/?.=&]+',urlLine)[0].replace('load.php','download')


def chooseFromVidStream(url):
	# takes two parameter url andd dlsite from where video iiss to be downloaded
	vidsUrl  = vidstreamingUrl(url)
	print(vidsUrl)
	gogostream =getSoup(vidsUrl)

	mirrorLinks = gogostream.findAll('div',{'class':"mirror_link"})
	# there  are "two" claass witth mirror_link
	# go through each div.ad in each and check preferred site and return url
	for i in range(len(mirrorLinks)): #here len is 2 "most probably"
		# get div inside mirroLinks
		mirrorLinksDivs = mirrorLinks[i].findAll('div')
		for each in mirrorLinksDivs:
			for site in conf.sites:
				print(each.a.string,each.a['href'])
				# print(f"{site} in {each.a['href']} => {site in each.a['href']}")
				if site in each.a['href'] or site in each.a.string.lower():
					# print("site found=>",each.a['href'])
					return each.a['href']


url2 = chooseFromVidStream(url)
print('returned',url2)
# https://storage.googleapis.com/winter-dynamics-311908/I41TARIX1OA2/23a_1622674805_162421.mp4