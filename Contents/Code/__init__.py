# -*- coding: utf-8 -*-

#Import
from PMS import Plugin, Log, XML, HTTP
from PMS.MediaXML import *

#Name and other blaha
PLUGIN_PREFIX	= "/video/viasatplay"
PLUGIN_VERSION	= "0.5.0"
PLUGIN_TITLE	= "Viasat Play"
LOGO_TV3	= "viasat_tv3.png"
LOGO_TV6	= "viasat_tv6.png"
LOGO_TV8	= "viasat_tv8.png"
LOGO_SPORT	= "viasat_sport.png"
LOGO_ALL	= "viasat_alla.png"
LOGO_MAIN	= "icon-default.png"
BACKGROUND	= "art-default.jpg"

#URLs to xml/player
TV3_MAIN_URL 		= "http://viastream.viasat.tv/siteMapData/se/2se/0"
TV6_MAIN_URL 		= "http://viastream.viasat.tv/siteMapData/se/3se/0"
TV8_MAIN_URL		= "http://viastream.viasat.tv/siteMapData/se/4se/0"
SPORT_BACKUP_URL	= "http://viastream.viasat.tv/siteMapData/se/1se/0"
SPORT_MAIN_URL		= "http://viastream.player.mtgnewmedia.se/xml/xmltoplayer.php?type=siteMapData&channel=1se&country=se&category="
SPORT_BACKUP_URL	= "http://viastream.viasat.tv/siteMapData/se/1se/0"
VIASAT_SEASONS_URL_OLD	= "http://viastream.player.mtgnewmedia.se/xml/xmltoplayer.php?type=siteMapData&country=se&category="
VIASAT_SEASONS_URL	= "http://viastream.viasat.tv/siteMapData/se/2se/"
VIASAT_EPISODES_URL_OLD	= "http://viastream.player.mtgnewmedia.se/xml/xmltoplayer.php?type=Products&category="
VIASAT_EPISODES_URL	= "http://viastream.viasat.tv/Products/Category/"
VIASAT_EPISODE_INFO_URL	= "http://viastream.player.mtgnewmedia.se/xml/xmltoplayer.php?type=Products&clipid="
VIASAT_EPISODE_INFO_URL2="http://viastream.viasat.tv/Products/"
PLEX_PLAYER_URL		= "http://www.plexapp.com/player/player.php?url=rtmp://mtgfs.fplive.net/mtg/flash/&clip=/sweden/"
PLEX_PLAYER_LIVE_URL	= "http://www.plexapp.com/player/player.php?url=rtmp://mtglivefs.fplive.net/mtglive-live/&clip=/"

def Start():
	Plugin.AddRequestHandler(PLUGIN_PREFIX, BuildMenus, PLUGIN_TITLE, LOGO_MAIN,  BACKGROUND)
	Plugin.AddViewGroup("Menu", viewMode="InfoList", contentType="items")

def BuildMenus(parameter, count):


	#List channels
	if(count == 0):
		dir = MediaContainer(art=BACKGROUND, viewGroup="Menu", title1=PLUGIN_TITLE)
		name = ["Alla kanaler", "TV3", "TV6", "TV8", "Viasat Sport"]
		#name = ["TV3", "TV6", "TV8", "Viasat Sport"]
		logo = [LOGO_ALL, LOGO_TV3, LOGO_TV6, LOGO_TV8, LOGO_SPORT]
		#logo = [LOGO_TV3, LOGO_TV6, LOGO_TV8, LOGO_SPORT]

		for i in range(0,5):
			thumb = Plugin.ExposedResourcePath(logo[i])
			dir.AppendItem(DirectoryItem(name[i], name[i], thumb))

		return dir.ToXML()

	#List series (channels for sport)
	#Added fix for null-pointers
	if(count == 1):
		dir = MediaContainer(art=BACKGROUND, viewGroup="Menu", title1=PLUGIN_TITLE, title2=parameter[0])
		if(parameter[0] == "TV3"):
			tempXML	= XML.ElementFromURL(TV3_MAIN_URL)
			try:
				series = tempXML.xpath("siteMapNode")
			except:
				Log.Add("Exception: TV3 Unavailable")
			logo = LOGO_TV3
		if(parameter[0] == "TV6"):
			tempXML	= XML.ElementFromURL(TV6_MAIN_URL)
			try:
				series = tempXML.xpath("siteMapNode")
			except:
				Log.Add("Exception: TV6 Unavailable")
			logo = LOGO_TV6
		if(parameter[0] == "TV8"):
			tempXML	= XML.ElementFromURL(TV8_MAIN_URL)
			try:
				series = tempXML.xpath("siteMapNode")
			except:
				Log.Add("Exception: TV8 Unavailable")
			logo = LOGO_TV8
		if(parameter[0] == "Viasat Sport"):
			try:
				tempXML = XML.ElementFromURL(SPORT_BACKUP_URL)
			except:
				tempXML = XML.ElementFromURL(SPORT_MAIN_URL)
			try:
				series = tempXML.xpath("siteMapNode")
			except:
				Log.Add("Exception: Sport Unavailable")
			logo = LOGO_SPORT
		if(parameter[0] == "Alla kanaler"):
			try:
				tempXML = XML.ElementFromURL(SPORT_BACKUP_URL)
			except:
				tempXML = XML.ElementFromURL(SPORT_MAIN_URL)
			try:
				series = tempXML.xpath("siteMapNode")
			except:
				Log.Add("Exception: Sport Unavailable")
				series = ""
			tempXML	= XML.ElementFromURL(TV3_MAIN_URL)
			try:
				series = series +tempXML.xpath("siteMapNode")
			except:
				Log.Add("Exception: TV3 Unavailable")
			tempXML	= XML.ElementFromURL(TV6_MAIN_URL)
			try:
				series = series +tempXML.xpath("siteMapNode")
			except:
				Log.Add("Exception: TV6 Unavailable")
			tempXML	= XML.ElementFromURL(TV8_MAIN_URL)
			try:
				series = series +tempXML.xpath("siteMapNode")
			except:
				Log.Add("Exception: TV8 Unavailable")
			sort=[]
			for serie in series:
				title = (serie.get("title"))
				title = title + "---" + serie.get("id")
				sort.append(title)
			sort.sort(key=unicode)
			logo = LOGO_ALL
			for item in sort:
				split = item.split("---")
				title = split[0]
				id = split[1]
				thumb = Plugin.ExposedResourcePath(logo)
				if(checkDeadLinks(id, parameter[0])):
					dir.AppendItem(DirectoryItem(id, title, thumb))

			return dir.ToXML()

		for serie in series:
			title = (serie.get("title"))
			id = serie.get("id")
			thumb = Plugin.ExposedResourcePath(logo)
			if(checkDeadLinks(id, parameter[0])):
				dir.AppendItem(DirectoryItem(id, title, thumb))

		return dir.ToXML()

	elif(count == 2):
		if(parameter[0] == "Viasat Sport"):
			showTitle = XML.ElementFromURL(VIASAT_SEASONS_URL_OLD + parameter[1]).get("title")
			dir = MediaContainer(art=BACKGROUND, viewGroup="Menu", title1=PLUGIN_TITLE, title2=showTitle)
		else:
			showTitle = XML.ElementFromURL(VIASAT_SEASONS_URL + parameter[1]).get("title")
			dir = MediaContainer(art=BACKGROUND, viewGroup="Menu", title1=PLUGIN_TITLE, title2=showTitle)

		xml = XML.ElementFromURL(VIASAT_SEASONS_URL + parameter[1])
		if not xml.xpath("siteMapNode"):
			xml = XML.ElementFromURL(VIASAT_SEASONS_URL_OLD + parameter[1])

		seasons = xml.xpath("siteMapNode")

		if(parameter[0] == "TV3"):
			logo = LOGO_TV3
		if(parameter[0] == "TV6"):
			logo = LOGO_TV6
		if(parameter[0] == "TV8"):
			logo = LOGO_TV8
		if(parameter[0] == "Viasat Sport"):
			logo = LOGO_SPORT
		if(parameter[0] == "Alla kanaler"):
			logo = LOGO_ALL

		for season in seasons:
			title = season.get("title")
			id = season.get("id")
			articles = int(season.get("articles"))
			if(articles >0 and id != "2407"):
				thumb = getSeriesImage(id, parameter[0])
				Log.Add("sport id: %s" % (logo))
				if (len(thumb) == 0):
					thumb=Plugin.ExposedResourcePath(logo)
				dir.AppendItem(DirectoryItem(id, title, thumb))

		return dir.ToXML()

	#List all the episodes in the season/event
	elif(count == 3):
		if(parameter[0] == "Viasat Sport"):
			showTitle = XML.ElementFromURL(VIASAT_SEASONS_URL_OLD + parameter[1]).get("title")
			dir = MediaContainer(art=BACKGROUND, viewGroup="Menu", title1=PLUGIN_TITLE, title2=showTitle)
		else:
			showTitle = XML.ElementFromURL(VIASAT_SEASONS_URL + parameter[1]).get("title")
			dir = MediaContainer(art=BACKGROUND, viewGroup="Menu", title1=PLUGIN_TITLE, title2=showTitle)

		xml1 = XML.ElementFromURL(VIASAT_EPISODES_URL + parameter[2])
		if not xml1.xpath("Product"):
			xml1= XML.ElementFromURL(VIASAT_EPISODES_URL_OLD + parameter[2])
		episodes = xml1.xpath("Product")

		for episode in episodes:
			if(parameter[0] == "TV3"):
				logo = LOGO_TV3
			if(parameter[0] == "TV6"):
				logo = LOGO_TV6
			if(parameter[0] == "TV8"):
				logo = LOGO_TV8
			if(parameter[0] == "Viasat Sport"):
				logo = LOGO_SPORT
			if(parameter[0] == "Alla kanaler"):
				logo = LOGO_ALL
			title = episode.xpath("./Title/text()")[0]
			id = episode.xpath("./ProductId/text()")[0]
			xml= XML.ElementFromURL(VIASAT_EPISODE_INFO_URL + id)
			if not xml.xpath("Product/Images/ImageMedia/Url/text()"):
				xml =  XML.ElementFromURL(VIASAT_EPISODE_INFO_URL2 + id)
			episodeInfo =xml.xpath("Product/LongDescription/text()")[0]
			thumb =xml.xpath("Product/Images/ImageMedia/Url/text()")[0]
			if(".jpg" not in thumb):
				thumb=Plugin.ExposedResourcePath(logo)
			clipLink = xml.xpath("Product/Videos/Video/Url/text()")[0]
			splitLink = clipLink.split('/')
			if(len(splitLink)>10):
				link = PLEX_PLAYER_URL + splitLink[6] + "/" + splitLink[7] + "/" + splitLink[8] + "/" + splitLink[9] + "/" + splitLink[10] + "&live=true"
			elif(len(splitLink)>9):
				link = PLEX_PLAYER_URL + splitLink[6] + "/" + splitLink[7] + "/" + splitLink[8] + "/" + splitLink[9] + "&live=true"
			elif(len(splitLink)>8):
				link = PLEX_PLAYER_URL + splitLink[6] + "/" + splitLink[7] + "/" + splitLink[8] + "&live=true"
			elif(len(splitLink)>5):
				link = PLEX_PLAYER_LIVE_URL + splitLink[4] + "/" + splitLink[5] + "&live=true"
			Log.Add("Link: %s" % (link))
			dir.AppendItem(WebVideoItem(link, title, episodeInfo, None, thumb))

		return dir.ToXML()

# Go deaper in the tree and check if any links is live
def checkDeadLinks(id, parameter):
	xml = XML.ElementFromURL(VIASAT_SEASONS_URL + id)
	if not xml.xpath("siteMapNode"):
		xml = XML.ElementFromURL(VIASAT_SEASONS_URL_OLD + id)

	seasons = xml.xpath("siteMapNode")
	if(len(seasons)>0):
		for season in seasons:
			articles = int(season.get("articles"))
			Log.Add("Articles: %s" % (articles))
			if(articles > 0):
				return True

	return False

# Fetch image for series on step higher in the tree
def getSeriesImage(id,parameter):
	xml1 = XML.ElementFromURL(VIASAT_EPISODES_URL + id)
	if not xml1.xpath("Product"):
		xml1 = XML.ElementFromURL(VIASAT_EPISODES_URL_OLD + id)
	episodes = xml1.xpath("Product")
	if(len(episodes)>0):
		firstId = episodes[0].xpath("./ProductId/text()")[0]
		xml= XML.ElementFromURL(VIASAT_EPISODE_INFO_URL + firstId)
		if not xml.xpath("Product/Images/ImageMedia/Url/text()"):
			xml =  XML.ElementFromURL(VIASAT_EPISODE_INFO_URL2 + firstId)
		thumb = xml.xpath("Product/Images/ImageMedia/Url/text()")[0]
		if(".jpg" in thumb):
			return thumb
	return ""