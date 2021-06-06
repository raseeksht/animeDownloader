import requests
import re,os
from bs4 import BeautifulSoup
import conf

animeWebsite = "https://animekisa.tv/"
url =  "https://animekisa.tv/monster-episode-2"
url = "https://animekisa.tv/monster-dubbed-episode-36"
# url = "https://animekisa.tv/one-piece-episode-976"

requests = requests.session()


def getSoup(url):
	res = requests.get(url)
	return BeautifulSoup(res.content,'html.parser')

def postSoup(url,data):
	headers = {
		"User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:89.0) Gecko/20100101 Firefox/89.0"
	}
	res = requests.post(url,data=data,headers=headers)
	return BeautifulSoup(res.content,'html.parser')

def vidstreamingUrl(url):
	urlLine = re.findall(r'var VidStreaming = [a-zA-Z0-9":/.?=&]+',str(getSoup(url)))[0]
	return re.findall(r'https[a-zA-Z0-9:/?.=&]+',urlLine)[0].replace('load.php','download')


def chooseFromVidStream(url):
	# takes two parameter url andd dlsite from where video iiss to be downloaded
	vidsUrl  = vidstreamingUrl(url)	# site that contains many sites to choose
	gogostream =getSoup(vidsUrl) 
	title = gogostream.find('span',id="title").string.replace(" ","\ ").replace('(','[').replace(')',']')

	mirrorLinks = gogostream.findAll('div',{'class':"mirror_link"})
	# there  are "two" class mirror_link
	# go through each div.a in each and check preferred site and return url
	for i in range(len(mirrorLinks)): #here len is 2 "most probably"
		# get div inside mirroLinks

		mirrorLinksDivs = mirrorLinks[i].findAll('div')
		# print(vidsUrl)
		for site in conf.sites:
			
			for each in mirrorLinksDivs:
				# print(each.a.string,each.a['href'])
				# print(f"{site} in {each.a['href']} => {site in each.a['href']}")
				# print(f"{site} in {each.a['href']}")
				# print(f"{site} in {each.a.string}")
				if site in each.a['href'] or site in each.a.string.lower():

					

					# print("site found=>",each.a['href'])
					# if site support direct download thiird parameter should be Flase
					if site in conf.ddl:
						return each.a['href'],title,site,False
					else:
						return each.a['href'],title,site,True


def download(url,title):
	if not os.path.isdir(conf.location):
		os.mkdir(conf.location)
	os.system(f'wget -c {url} -O {conf.location}{title}.mp4')


def dlFromStreamSbPart1(url):
	soup = getSoup(url)
	contentBox = soup.find('div',{'class':'contentbox'}).table.findAll('tr')
	for quality in conf.quality:
		for each in contentBox:
			if quality in each.td.a.string.lower():
				print("downloading in",each.td.a.string)
				# onclickTxt looks like -> download_video('t8kkg5iufgat','h','6279859-27-34-1622730164-49f74c156122e16221be04e6466b21de')
				onclickTxt = each.td.a['onclick'][16:-1].replace("'",'').split(',')
				# print(onclickTxt)
# t8kkg5iufgat&mode=n&hash=6279859-27-34-1622729627-b97c3c9c0d57ab3f1c3f410f857273a6
				return f"https://sbvideo.net/dl?op=download_orig&id={onclickTxt[0]}&mode={onclickTxt[1]}&hash={onclickTxt[2]}"
	

def dlFromMp4uploadPart1(url):

	print("downloading from mp4upload is not supported yet. change priority in conf.py ")
	exit()
	soup = getSoup(url)
	form = soup.find('form',{'id':'form'})
	print(form)
	data = {
		'op':'download2',
		# 'op':form.find('input',{'name':'op'})['value'],
		'usr_login':form.find('input',{'name':'usr_login'})['value'],
		'id':form.find('input',{'name':'id'})['value'],
		'fname':form.find('input',{'name':'fname'})['value'],
		# 'referer':form.find('input',{'name':'referer'})['value'],
		'referer':url,
		'method_free':form.find('input',{'name':'method_free'})['value'],
	}
	postdata = f"op=download2&id={data['id']}&rand=&referer={url}&method_free=+&method_premium="
	# soup = postSoup(url,data).find('form')
	# print("form data\n\n\n\n",soup)
	os.system(f"wget --post-data '{postdata}' {url}")
	exit()

	



def iTakeVideoUrlAndDownload(url):
	#  give me url containing video
	url2,title,site,redirect = chooseFromVidStream(url)
	if not redirect:
		print('downloading directly')
		download(url2,title)	
	else:
		print("redirecting to",url2)
		if "streamsb" in site:
			lastStreamSbUrl = dlFromStreamSbPart1(url2)
			print("redirecting to",lastStreamSbUrl)
			try:
				for i in range(4):
					span = getSoup(lastStreamSbUrl).find('span').a['href']
					break
			except Exception:
				span = getSoup(lastStreamSbUrl).find('span').a['href']
			
			download(span,title)
		if "mp4upload" in site:
			# code above here is okay
			dlFromMp4uploadPart1(url2)


			


def fromTo(max):
	return f"1 ... {max}"

def askForNumber(maxNum):
	while True:
		try:
			userChoice = int(input(f"choose {fromTo(maxNum)} : "))
			if (userChoice > maxNum):
				print('Unavailable Choice: ',userChoice)
				continue
			else:
				return userChoice
		except Exception:
			print("alphabets and special symbol are not accepted...")

def search():
	# search and returns homepage of desired anime
	userQuery = input("search Anime: ")
	url = animeWebsite+"search?q="+userQuery.replace(" ",'+')
	soup = getSoup(url).find('div',{'class':"lisbox22"})
	initCheck = soup.findAll('div',{'class':'lisbg'})
	initCheck = [each.string for each in initCheck]

	categories = soup.findAll('div',{'class':'similarboxmain'})
	if len(categories)  ==0:
		print("oops... Nothing found!!")
		print("i guess it's typo check your query and try again")
		exit()

	availableAnime = []
	for index,each in enumerate(categories): #3 categories possible (subbed,dubbed and movies)
		anchors = each.div.findAll('a')
		tempAnime = []

		for anchor in anchors:
			title = anchor.find('div',{'class':'similardd'}).string
			if title!='\n':
				tempAnime.append([title,anchor['href']])
		availableAnime.append(initCheck[index])
		availableAnime.append(tempAnime)

	totalCategory = len(availableAnime) # including type(dub,sub,mov)
	# print(totalCategory)
	print("search Results: ")
	for i in range(int(totalCategory/2)):
		# index 0 2 4 contains type(dub,sub,movie),index 1,3,5 contains lists
		print(f"{i+1}. {availableAnime[2*i]} ({len(availableAnime[2*i+1])} contents)")
	
	userChoice1 = askForNumber(totalCategory//2)	

	print(f"Available {userQuery} ({initCheck[userChoice1-1]})")

	for index,content in enumerate(availableAnime[2*userChoice1-1]):
		print(f"{index+1}. {content[0]}")


	userChoice2 = askForNumber(len(availableAnime[2*userChoice1-1]))

	print("your choice :",availableAnime[2*userChoice1-1][userChoice2-1][0])
	return animeWebsite + availableAnime[2*userChoice1-1][userChoice2-1][1]

	
def downloadAllEpisodes(soup):
	# soup contains all anchors with links to the videos
	soup = soup[::-1] # first element is latest episode we need to download from episode 1
	for a in soup:
		iTakeVideoUrlAndDownload(animeWebsite + a['href'])


def findLinkFromEpisodeNo(episode,soup,frontUrl):
	# return link of the episode
	# takes episode to download and soup containing episodes
	# frontUrl is just to show user if episode is missing or not found
	for a in soup:
		cv = a.findAll('div',{'class':'centerv'})
		if int(cv[1].string) == episode:
			return animeWebsite+a['href']
	print("Oops episode seems to be missing..")
	print("check if the episode is present browser or click",frontUrl)

def downloadFromTo(fromEp,toEp,soup,frontUrl):
	if fromEp>toEp:
		print(f"Order Incorrect... starting episdoe {fromEp} greater than end episode {toEp}")
		return
	elif fromEp == toEp:
		link = findLinkFromEpisodeNo(fromEp,soup,frontUrl)
		iTakeVideoUrlAndDownload(link)
	else:
		soup = soup[::-1]
		for ep in range(fromEp,toEp+1):
			link = findLinkFromEpisodeNo(ep,soup,frontUrl)
			iTakeVideoUrlAndDownload(link)



frontUrl = search()
soup = getSoup(frontUrl).find('div',{'class':'infoepbox'}).findAll('a')
# print(soup)
# print(type(soup))
totalEps = soup[0].find('div',{'class':'infoept2'}).div.string

print(f'{totalEps} episodes available')

print("1. Download all episodes\n2. Download single episode\n2. From ep x to y")
userChoice = askForNumber(3)
if userChoice == 1:
	downloadAllEpisodes(soup)
elif userChoice == 2:
	episode = askForNumber(len(soup))
	link = findLinkFromEpisodeNo(episode,soup,frontUrl)
	iTakeVideoUrlAndDownload(link)
else:
	print("From : ",end="")
	fromEp = askForNumber(len(soup))
	print("To : ",end="")
	toEp = askForNumber(len(soup))

	downloadFromTo(fromEp,toEp,soup,frontUrl)






 