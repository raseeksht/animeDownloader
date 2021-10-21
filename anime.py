import requests
from bs4 import BeautifulSoup
import os,re,json,sys,time
import conf
import cloudscraper

scraper = cloudscraper.create_scraper(
	browser={
		'browser': 'firefox',
		'platform': 'windows',
		'mobile': False
	}
)

platform = sys.platform

def flagError(diff):
	print(diff,"is not  allowed")
	helpMenu()

def helpMenu():
	print("-h\t: Print this help info ")
	print("-w\t: website name [animekisa,animixplay] ")
	print("-u\t: url for home page of anime ex:\n\t  -u https://animekisa.tv/one-piece")
	print("-s\t: search for anime. only for animekisa. \n\t  -s takes '-w animekisa' automatically so it's omit -w\n\t  ex: -s 'one piece'")
	print("--get-link \t: Print only the download links")
	print("-gl\t: short form for --get-link")
	exit()

def clear():
	if "win32" in platform:
		os.system("cls")
	else:
		os.system("clear")


allowedWebsite = {
	"animekisa":"https://animekisa.tv/",
	"animixplay":"https://animixplay.to/"
}
flags = ["-w","-u","-s","--get-link","-gl"]

args = sys.argv


class Color:
	def __init__(self):
		self.red = "\u001b[31m"
		self.reset = '\u001b[0m'
		self.green = '\u001b[32m'
		self.yellow = '\u001b[33m'
		self.blue = '\u001b[34m'
		self.magentfa = '\u001b[35m'
		self.cyan = '\u001b[36m'
		self.white = '\u001b[37m'

	def colorize(self,msg,colorName):
		print(eval("self."+colorName)+str(msg)+self.reset)

		

class Animeweb():
	"""docstring for Animeweb"""
	def pae(self,toPrint):
		print(toPrint)
		exit()

	def prettify(self,msg):
		msg = "| "+msg+" |"
		length = len(msg)
		width = os.get_terminal_size().columns
		dash = "-"*length
		print(dash.center(width," "))
		print(msg.center(width," "))
		print(dash.center(width," "))
		


	def dlFromStreamSbPart1(self,url):
		soup = self.getSoup(url)
		contentBox = soup.find('div',{'class':'contentbox'}).table.findAll('tr')
		for quality in conf.quality:
			for each in contentBox:
				if quality in each.td.a.string.lower():
					print("downloading in",each.td.a.string)
					# onclickTxt looks like -> download_video('t8kkg5iufgat','h','6279859-27-34-1622730164-49f74c156122e16221be04e6466b21de')
					onclickTxt = each.td.a['onclick'][16:-1].replace("'",'').split(',')
					return f"https://sbvideo.net/dl?op=download_orig&id={onclickTxt[0]}&mode={onclickTxt[1]}&hash={onclickTxt[2]}"
	


	def iTakeVideoUrlAndDownload(self,url):
		'''give me url containing multiple download sites to choose from gogostrams vidstream'''
		url2,title,site,redirect = self.chooseFromVidStream(url)

		if not redirect:
			# print('downloading directly')
			self.download(url2,title)	
		else:
			# print("redirecting to",url2)
			if "streamsb" in site:
				lastStreamSbUrl = self.dlFromStreamSbPart1(url2)
				# print("redirecting to",lastStreamSbUrl)
				try:
					for i in range(4):
						span = self.getSoup(lastStreamSbUrl).find('span').a['href']
						break
				except Exception:
					span = self.getSoup(lastStreamSbUrl).find('span').a['href']
				
				self.download(span,title)


	def download(self,url,title):
		''' give me direct url for the video'''
		if not os.path.isdir(conf.location):
			os.mkdir(conf.location)
		# os.system(f'''wget -c "{url}" -O "{conf.location}{title}.mp4"''')
		print(f'saving to: {conf.location}{title}.mp4')
		os.system(f'''curl -o "{conf.location}{title}.mp4" -C - {url}''')

	def askForNumber(self,maxNum):
		if maxNum == 1:
			print("only 1 choice is available.Choosing 1 by default..")
			time.sleep(2)
			return 1
		while True:
			try:
				userChoice = int(input(f"choose 1 ... {maxNum} : "))

				if (userChoice > maxNum):
					print('Unavailable Choice: ',userChoice)
					continue
				else:
					return userChoice
			except Exception:
				print("alphabets and special symbol are not accepted...")
	
	def getSoup(self,url):
		# res = requests.get(url)
		res = scraper.get(url)
		
		return BeautifulSoup(res.content,'html.parser')
	
	def chooseFromVidStream(self,url):
		""" works for animekisa """
		# takes one parameter url  from where video iiss to be downloaded
		# vidsUrl  = self.vidstreamingUrl(url)	# site that contains many sites to choose
		url = "https://gogo-stream.com/download?id=" + url.split("?id=")[-1] # avoid human vverificaatiion on otherr siites
		gogostream = self.getSoup(url) 
		# gogostream = self.getSoup(vidsUrl) 

		title = gogostream.find('span',id="title").string.replace(" "," ").replace('(','[').replace(')',']')

		mirrorLinks = gogostream.findAll('div',{'class':"mirror_link"})
		# there  are "two" class mirror_link
		# go through each div.a in each and check preferred site and return url
		for i in range(len(mirrorLinks)): #here len is 2 "most probably"
			# get div inside mirroLinks
			mirrorLinksDivs = mirrorLinks[i].findAll('div')
			# print(vidsUrl)
			for site in conf.sites:				
				for each in mirrorLinksDivs:
					if site in each.a['href'] or site in each.a.string.lower():
						# if site support direct download thiird parameter should be Flase
						
						if site in conf.ddl:
							return each.a['href'],title,site,False
						else:
							return each.a['href'],title,site,True

	

class Animekisa(Animeweb):
	"""docstring for Animekisa"""
	def __init__(self):
		self.homeUrl = allowedWebsite['animekisa']

	def checkForPointEpisodes(self,soup):
		episodesNumber = []
		for a in soup:
			cv = a.findAll('div',{'class':'centerv'})
			episodesNumber.append(float(cv[1].string))
		episodesNumber= episodesNumber[::-1] #because first in the list is latest episode and 1st episode is at last
		floatedEp = [ep for ep in episodesNumber if ep-int(ep)!=0 ]
		return floatedEp

	def vidstreamingUrl(self,url):
		""" returns url to the vidstream download site conntains multiple download sites"""
		urlLine = re.findall(r'var VidStreaming = [a-zA-Z0-9":/.?=&-]+',str(self.getSoup(url)))[0]
		return re.findall(r'https[a-zA-Z0-9:/?.=&-]+',urlLine)[0].replace('load.php','download')

	def findLinkFromEpisodeNo(self,episode,soup,animeHomePageUrl):
		# return link of the episode
		# takes episode to download and soup containing episodes divs and ...
		# animmeHomePageUrl is just to show user if episode is missing or not found
		
		for a in soup:
			cv = a.findAll('div',{'class':'centerv'})
			if float(cv[1].string) == episode or float(cv[1].string) == episode-0.5:				
				return self.homeUrl+a['href']
		print("Oops episode seems to be missing..")
		print("check if the episode is present browser or click",animeHomePageUrl)

	def downloadFromTo(self,fromEp,toEp,soup,animeHomePageUrl):
		if fromEp>toEp:
			print(f"Order Incorrect... starting episdoe {fromEp} greater than end episode {toEp}")
			return
		elif fromEp == toEp:
			link = self.findLinkFromEpisodeNo(fromEp,soup,animeHomePageUrl)
			vidsUrl  = self.vidstreamingUrl(link)
			self.iTakeVideoUrlAndDownload(vidsUrl)
		else:
			soup = soup[::-1]
			for ep in range(fromEp,toEp+1):
				link = self.findLinkFromEpisodeNo(ep,soup,animeHomePageUrl)
				vidsUrl  = self.vidstreamingUrl(link)

				self.iTakeVideoUrlAndDownload(vidsUrl)

	def downloadAllEpisodes(self,soup):
		# soup contains all anchors with links to the videos
		soup = soup[::-1] # first element is latest episode we need to download from episode 1
		for a in soup:
			# print(self.homeUrl + a['href'])
			vidsUrl  = self.vidstreamingUrl(self.homeUrl + a['href'])
			self.iTakeVideoUrlAndDownload(vidsUrl)

	def howDoYouWantToDownload(self,soup,animeHomePageUrl):
		'''gives user the  choice to download however they like'''
		print("1. Download all episodes\n2. Download single episode\n3. From ep x to y\n")
		userChoice = self.askForNumber(3)
		if userChoice == 1:
			self.downloadAllEpisodes(soup)
		elif userChoice == 2:
			episode = self.askForNumber(len(soup))
			link = self.findLinkFromEpisodeNo(episode,soup,animeHomePageUrl)
			# print(link)
			vidsUrl  = self.vidstreamingUrl(link)
			self.iTakeVideoUrlAndDownload(vidsUrl)
		else:
			print("From : ",end="")
			fromEp = self.askForNumber(len(soup))
			print("To : ",end="")
			toEp = self.askForNumber(len(soup))
			self.downloadFromTo(fromEp,toEp,soup,animeHomePageUrl)

	def search(self,userQuery):
		# userQuery = input("search Anime: ")
		url = self.homeUrl+"search?q="+userQuery.replace(" ",'+')
		soup = self.getSoup(url).find('div',{'class':"lisbox22"})
		initCheck = soup.findAll('div',{'class':'lisbg'})
		initCheck = [each.string for each in initCheck]
		#init check contains ['subbed','dubbed','movie']
		categories = soup.findAll('div',{'class':'similarboxmain'})
		if len(categories)  ==0:
			print("oops... Nothing found!!")
			print("i guess it's typo check your query and try again")
			exit()

		availableAnime = []
		# availableAnime looks like ['subbed',['title','animeHomePageUrl'],'dubbed',['title','animeHomePageUrl'],'movies',['title','animeHomePageUrl']]
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
		clear()
		print("search Results: ")
		for i in range(int(totalCategory/2)):
			# index 0 2 4 contains type(dub,sub,movie),index 1,3,5 contains lists
			print(f"{i+1}. {availableAnime[2*i]} ({len(availableAnime[2*i+1])} contents)")
		
		userChoice1 = self.askForNumber(totalCategory//2)	
		clear()
		print(f"Available {userQuery} ({initCheck[userChoice1-1]})") # aavaiilable One pieece 9subed)

		for index,content in enumerate(availableAnime[2*userChoice1-1]):
			print(f"{index+1}. {content[0]}")

		userChoice2 = self.askForNumber(len(availableAnime[2*userChoice1-1]))
		clear()
		print("your choice :")
		self.prettify(availableAnime[2*userChoice1-1][userChoice2-1][0].strip())
		#sends animeHomePageUrl
		animeHomePageUrl = self.homeUrl + availableAnime[2*userChoice1-1][userChoice2-1][1]
		soup = self.getSoup(animeHomePageUrl).find('div',{'class':'infoepbox'}).findAll('a')
		
		totalEps = soup[0].find('div',{'class':'infoept2'}).div.string
		# check for episodes link 1.5,5.5,etc
		if len(self.checkForPointEpisodes(soup))==0:
			color.colorize(f'{totalEps} episodes available',"green")
		else:
			color.colorize(f'{totalEps} episodes available',"green")
			color.colorize(f'including episode{self.checkForPointEpisodes(soup)}','red')


		self.howDoYouWantToDownload(soup,animeHomePageUrl)
		print(self.checkForPointEpisodes(soup))
			




class Animixplay(Animeweb):
	def __init__(self):
		self.homeUrl = allowedWebsite['animixplay']

	def downloadAllEpisodes(self,episodeDict):
		for epNo in episodeDict.keys():
			self.iTakeVideoUrlAndDownload(episodeDict[epNo])

	def downloadFromTo(self,fromEp,toEp,epdict):
		for ep in range(fromEp,toEp+1):
			self.iTakeVideoUrlAndDownload(epdict[ep]) 

	def search(self,animeHomePageUrl):
		# individual animeHomePgeUrl of animixplay
		streamaniBaseUrl = "https://streamani.net/download?id="
		soup = self.getSoup(animeHomePageUrl).find('div',{'id':'epslistplace'})
		print(soup)
		episodesDetails = json.loads(soup.string)
		totalEpisodesAvaiable = episodesDetails['eptotal']
		epdict = {}
		for index,key in enumerate(episodesDetails.keys()):
			try:
				if (index !=0): # 0th contains totalepisodeAavailable number 
					details = str(episodesDetails[key]).split("?id=")[1]
					_id = details.split('&')[0]
					url = streamaniBaseUrl + _id
					epdict[index] = url

			except Exception as e:
				# some episodes migght be unavailable
				print(index,e)
		clear()
		print(f"{totalEpisodesAvaiable} episodes available")

		print("1. Download all episodes\n2. Download single episode\n3. From ep x to y\n")
		userChoice = self.askForNumber(3)
		if userChoice == 1:
			with open("log.txt","w") as f:
				f.write(json.dumps(epdict,indent=4))
			self.downloadAllEpisodes(epdict)
		elif userChoice == 2:
			episode = self.askForNumber(totalEpisodesAvaiable)
			link = epdict[episode]
			self.iTakeVideoUrlAndDownload(link)
		else:
			print("From : ",end="")
			fromEp = self.askForNumber(totalEpisodesAvaiable)
			print("To : ",end="")
			toEp = self.askForNumber(totalEpisodesAvaiable)
			self.downloadFromTo(fromEp,toEp,epdict)


if __name__ == '__main__':
	args = sys.argv
	usedFlags = [flag for flag in args if flag.startswith("-")]

	validFlag = list(set(flags).intersection(set(usedFlags)))
	diff = list(set(usedFlags).difference(set(flags)))
	if (len(diff) > 0):
		flagError(diff)

	if (len(args)==1):
		helpMenu()

	if (len(diff) > 0):
		flagError(diff)

	color = Color()
	if "-s" in usedFlags:
		try:
			query = args[args.index("-s")+1]
		except IndexError:
			clear()
			print("search term is missing after -s flag")
			query = input("Search Anime (from animekisa) :")
		anime = Animekisa()
		anime.search(query)


			
	elif "-u" in usedFlags:
		website = args[args.index("-u")+1]

		if "animixplay" in website:
			try:
				anime = Animixplay()
				anime.search(args[args.index("-u")+1]) #takes animeHomeurl for animinplay
			except IndexError:
				print("animeHomePage url is missing\n")
				print("like python anime.py -u https://animixplay.to/anime/21/One_Piece")
		else:
			print("website not allowed")
			helpMenu()

