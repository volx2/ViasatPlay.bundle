# -*- coding: utf-8 -*-
import re
import datetime

###################################################################################################

PLUGIN_TITLE  = 'Viasat Play'
PLUGIN_PREFIX = '/video/viasatplay'

CHANNELS = [ 
	{
		'title': 	'TV3 Play',
		'url':		'http://www.tv3play.se',
		'xmlurl':	'http://viastream.viasat.tv/siteMapData/se/2se/',
		'thumb':	R('viasat_tv3.png'),
		'desc':		u'TV3 är kanalen med starka känslor och starka karaktärer. Det är en suverän mix av serier, livsstilsprogram, storfilmer, reportage och intressanta program.'
	},
	{
		'title': 	'TV6 Play',
		'url':		'http://www.tv6play.se',
		'xmlurl':	'http://viastream.viasat.tv/siteMapData/se/3se/',
		'thumb':	R('viasat_tv6.png'),
		'desc':		u'TV6 En underhållningskanal för den breda publiken. Actionfilmer och den vassaste humorn.'
	},
	{
		'title': 	'TV8 Play',
		'url':		'http://www.tv8play.se',
		'xmlurl':	'http://viastream.viasat.tv/siteMapData/se/4se/',
		'thumb':	R('viasat_tv8.png'),
		'desc':		u'TV8 är en svensk livsstils- och underhållningskanal med ett brett utbud. Du som gillar bilar, hus och vill veta allt om slottsliv, kommer inte vilja missa våra svenska produktioner i höst.'
	},
	{
		'title': 	'TV3 Play Norge',
		'url':		'http://www.tv3play.no',
		'xmlurl':	'http://viastream.viasat.tv/siteMapData/no/2no/',
		'thumb':	R('tv3_norway.png'),
		'desc':		u'TV3 er en underholdningskanal for alle. Våre verdier er leken, nyskapende, oppløftende og engasjerende. Kanalens programtilbud består av innkjøpte serier, filmer og norske egenproduserte programmer i ulike kategorier.'
	},
	{
		'title': 	'Viasat 4 Play Norge',
		'url':		'http://www.viasat4play.no',
		'xmlurl':	'http://viastream.viasat.tv/siteMapData/no/23no/',
		'thumb':	R('viasat4_norway.png'),
		'desc':		u'Viasat 4 er en norsk underholdnings- og sportskanal fra Modern Times Group (MTG). Kanalen startet sendinger 8. september 2007 i forbindelse med utbyggingen av det digitale bakkenettet.'
	},	
	{
		'title': 	'TV3 Play Danmark',
		'url':		'http://www.tv3play.dk',
		'xmlurl':	'http://viastream.viasat.tv/siteMapData/dk/2dk/',
		'thumb':	R('tv3_norway.png'),
		'desc':		u'På TV3 Play kan du se alle TV3’s egne programmer og nogen af vores udenlandske serier. Vi har også ekstramateriale til flere af vores programmer. Mer information om vores programmer findes på TV3.dk'
	},
]

CACHE_INTERVAL = CACHE_1HOUR

# Default artwork and icon(s)
PLUGIN_ARTWORK      = 'art-default.jpg'
PLUGIN_ICON_DEFAULT = 'icon-default.png'
PLUGIN_ICON_MORE    = 'icon-more.png'

ART   = "art-default.jpg"
THUMB = 'icon-default.png'

###################################################################################################
def Start():
  Plugin.AddViewGroup("InfoList", viewMode = "InfoList", mediaType = "items")
  Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, PLUGIN_TITLE, PLUGIN_ICON_DEFAULT, PLUGIN_ARTWORK)

  DirectoryObject.art        = R(ART)
  DirectoryObject.thumb      = R(THUMB)
  ObjectContainer.view_group = "InfoList"
  ObjectContainer.art        = R(ART)
  EpisodeObject.art          = R(ART)
  EpisodeObject.thumb        = R(THUMB)
  TVShowObject.art           = R(ART)
  TVShowObject.thumb         = R(THUMB)

  # Set the default cache time
  HTTP.CacheTime = CACHE_INTERVAL

###################################################################################################
@handler('/video/viasatplay', PLUGIN_TITLE, thumb = THUMB, art = ART)
def MainMenu():
  menu = ObjectContainer(title1 = PLUGIN_TITLE)
  for channel in CHANNELS:
    menu.add( DirectoryObject(key = Callback(AllPrograms, title = channel['title'], 
                                                          url = channel['url'], 
                                                          xmlurl = channel['xmlurl'], 
                                                          thumb = channel['thumb']), 
                                title = channel['title'], 
                                thumb = channel['thumb'], 
                                summary = channel['desc'])
    )
    
  return menu

####################################################################################################
@route('/video/viasatplay/AllPrograms')
def AllPrograms(title, url, xmlurl, thumb):
  dir = ObjectContainer(title2 = title)
  
  alreadyAdded = []
  programs     = []
  
  programsInfo = JSON.ObjectFromURL(url + "/mobileapi/format")
  for section in programsInfo['sections']:
    for program in section['formats']:
      p         = {}
      p["name"] = unicode(program['title'])
      p["id"]   = program['id']
      p["desc"] = unicode(program['description'])
      p["img"]  = getImgUrl(program['image'])
      programs.append(p)
        
      alreadyAdded.append(program['title'])
  
  try:                                           
    xmlElement  = XML.ElementFromURL(xmlurl + "0")
    xmlPrograms = xmlElement.xpath("//siteMapData//siteMapNode")
    pageElement = HTML.ElementFromURL(url + "/program")
    for item in pageElement.xpath("//div[contains(@id, 'content')]//div[contains(@class, 'column')]//ul//a"):
      name = item.xpath("./text()")[0]
      for xmlProgram in xmlPrograms:
        if name == xmlProgram.xpath("./@title")[0] and name not in alreadyAdded:
          program         = {}
          program["name"] = unicode(name) 
          program["id"]   = xmlProgram.xpath("./@id")[0]
          program["desc"] = None
          program["img"]  = thumb
          programs.append(program)
  except:
    pass      
           
  sortedPrograms = sorted(programs, key=lambda program: program["name"])
           
  for program in sortedPrograms:
    dir.add(DirectoryObject(key = Callback(Seasons,
                                           title = program['name'],
                                           summary = program['desc'],
                                           thumb = program['img'],
                                           url = url,
                                           xmlurl = xmlurl,
                                           id = program['id']),
                            title = program['name'],
                            summary = program['desc'],
                            thumb = program['img'])
             )
  
  return dir

####################################################################################################
@route('/video/viasatplay/Seasons')
def Seasons(title, summary, thumb, url, xmlurl, id):
  dir = ObjectContainer(title2 = unicode(title))
  
  xmlElement = XML.ElementFromURL(xmlurl + id)
  for xmlSeason in xmlElement.xpath("//siteMapData//siteMapNode"):
    season          = {}
    season["id"]    = xmlSeason.xpath("./@id")[0]
    season["title"] = unicode(xmlSeason.xpath("./@title")[0])
    
    dir.add(DirectoryObject(key = Callback(Episodes, 
                                           title = season["title"],
                                           url = url, 
                                           xmlurl = xmlurl, 
                                           id = season["id"]), 
                            title = season["title"], 
                            summary = summary, 
                            thumb = thumb))

  return dir
 
####################################################################################################
@route('/video/viasatplay/Episodes')
def Episodes(title, url, xmlurl, id):
  dir = ObjectContainer(title2 = unicode(title))

  episodeIDsXML = XML.ElementFromURL("http://viastream.viasat.tv/Products/Category/" + id)
  for episodeID in episodeIDsXML.xpath("//Products//Product"):
    id = episodeID.xpath("./ProductId/text()")[0]
    
    try:
      episodeXML = XML.ElementFromURL("http://viastream.viasat.tv/playProduct/" + id)
    except:
      episodeXML = XML.ElementFromURL("http://viastream.viasat.tv/Product/" + id) 
        
    for episode in episodeXML.xpath("//Products//Product"):
      if not int(episode.xpath("./ClipType/text()")[0]) == 1:
        continue
        
      video          = {}
      video["url"]   = episode.xpath("./Videos//Video//Url/text()")[0]
      video["title"] = episode.xpath("./Title/text()")[0]
      video["img"]   = episode.xpath("./Images//ImageMedia//Url/text()")[1]
      video["desc"]  = episode.xpath("./LongDescription/text()")[0]
        
      try:
        broadcastDate    = episode.xpath("./BroadcastDate/text()")[0]
        broadcastTime    = episode.xpath("./BroadcastTime/text()")[0]
        video["airtime"] = datetime.datetime.strptime(broadcastDate + broadcastTime,"%Y%m%d%H%M")
      except:
        video["airtime"] = None
          
      dir.add(EpisodeObject(
        url = url + '/play/' + id,
        title = unicode(video["title"]),
        summary = unicode(video["desc"]),
        show = None,
        season = None,
        index = None,
        art = episode.xpath("./Images//ImageMedia//Url/text()")[0],
        thumb = video["img"],
        originally_available_at = video["airtime"],
        rating = None))
     
  return dir

####################################################################################################
def getImgUrl(url):
  newUrl = "http://play.pdl.viaplay.com/imagecache/497x280/" + url.replace('\\', '') 
  return newUrl
