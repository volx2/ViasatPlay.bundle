# -*- coding: utf-8 -*-
import re
import datetime

###################################################################################################

PLUGIN_TITLE  = 'Viasat Play'
PLUGIN_PREFIX = '/video/viasatplay'

BASE_URL_TV3 = 'http://www.tv3play.se'
XML_URL_TV3  = 'http://viastream.viasat.tv/siteMapData/se/2se/'

BASE_URL_TV6 = 'http://www.tv6play.se'
XML_URL_TV6  = 'http://viastream.viasat.tv/siteMapData/se/3se/'

BASE_URL_TV8 = 'http://www.tv8play.se'
XML_URL_TV8  = 'http://viastream.viasat.tv/siteMapData/se/4se/'  

BASE_URL_TV3_NORWAY = 'http://www.tv3play.no'
XML_URL_TV3_NORWAY  = 'http://viastream.viasat.tv/siteMapData/no/2no/0'

CACHE_INTERVAL = CACHE_1HOUR

# Default artwork and icon(s)
PLUGIN_ARTWORK      = 'art-default.jpg'
PLUGIN_ICON_DEFAULT = 'icon-default.png'
PLUGIN_ICON_MORE    = 'icon-more.png'

TV3_ICON_DEFAULT        = R('viasat_tv3.png')
TV6_ICON_DEFAULT        = R('viasat_tv6.png')
TV8_ICON_DEFAULT        = R('viasat_tv8.png')
TV3_NORWAY_ICON_DEFAULT = R('tv3_norway.png')

ART   = "art-default.jpg"
THUMB = 'icon-default.png'

###################################################################################################
def Start():
  Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
  Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, PLUGIN_TITLE, PLUGIN_ICON_DEFAULT, PLUGIN_ARTWORK)

  DirectoryObject.art = R(ART)
  DirectoryObject.thumb = R(THUMB)
  ObjectContainer.view_group  = "InfoList"
  ObjectContainer.art = R(ART)
  EpisodeObject.art = R(ART)
  EpisodeObject.thumb = R(THUMB)
  TVShowObject.art = R(ART)
  TVShowObject.thumb = R(THUMB)

  # Set the default cache time
  HTTP.CacheTime = CACHE_INTERVAL

###################################################################################################
@handler('/video/viasatplay', PLUGIN_TITLE, thumb=THUMB, art=ART)
def MainMenu():
  menu = ObjectContainer(title1=PLUGIN_TITLE)
  menu.add(DirectoryObject(key=Callback(AllPrograms, title="TV3 Play", channel="3", url=BASE_URL_TV3, xmlurl=XML_URL_TV3, thumb=TV3_ICON_DEFAULT), title="TV3 Play", thumb=TV3_ICON_DEFAULT))
  menu.add(DirectoryObject(key=Callback(AllPrograms, title="TV6 Play", channel="6", url=BASE_URL_TV6, xmlurl=XML_URL_TV6, thumb=TV6_ICON_DEFAULT), title="TV6 Play", thumb=TV6_ICON_DEFAULT))
  menu.add(DirectoryObject(key=Callback(AllPrograms, title="TV8 Play", channel="8", url=BASE_URL_TV8, xmlurl=XML_URL_TV8, thumb=TV8_ICON_DEFAULT), title="TV8 Play", thumb=TV8_ICON_DEFAULT))
  menu.add(DirectoryObject(key=Callback(AllPrograms, title="TV3 Play Norge", channel="3", url=BASE_URL_TV3_NORWAY, xmlurl=XML_URL_TV3_NORWAY, thumb=TV3_NORWAY_ICON_DEFAULT), title="TV3 Play Norge", thumb=TV3_NORWAY_ICON_DEFAULT))
  return menu

####################################################################################################
@route('/video/viasatplay/AllPrograms')
def AllPrograms(title, channel, url, xmlurl, thumb):
  dir = ObjectContainer(title2=title)
  
  alreadyAdded = []
  programs     = []
  
  programsInfo = JSON.ObjectFromURL(url + "/mobileapi/format")
  for section in programsInfo['sections']:
    for program in section['formats']:
      p         = {}
      p["name"] = program['title']
      p["id"]   = program['id']
      p["desc"] = program['description']
      p["img"]  = getImgUrl(program['image'])
      programs.append(p)
        
      alreadyAdded.append(program['title'])
                                             
  xmlElement  = XML.ElementFromURL(xmlurl + "0")
  xmlPrograms = xmlElement.xpath("//siteMapData//siteMapNode")
  pageElement = HTML.ElementFromURL(url + "/program")
  for item in pageElement.xpath("//div[contains(@id, 'content')]//div[contains(@class, 'column')]//ul//a"):
    name = item.xpath("./text()")[0]
    for xmlProgram in xmlPrograms:
      if name == xmlProgram.xpath("./@title")[0] and name not in alreadyAdded:
        program         = {}
        program["name"] = name 
        program["id"]   = xmlProgram.xpath("./@id")[0]
        program["desc"] = None
        program["img"]  = thumb
        programs.append(program)
        
           
  sortedPrograms = sorted(programs, key=lambda program: program["name"])
           
  for program in sortedPrograms:
    dir.add(DirectoryObject(key = Callback(Seasons,
                                           title = program['name'],
                                           channel = channel,
                                           summary = program['desc'],
                                           thumb = program['img'],
                                           xmlurl = xmlurl,
                                           id = program['id']),
                            title = program['name'],
                            summary = program['desc'],
                            thumb = program['img'])
             )
  
  return dir

####################################################################################################
@route('/video/viasatplay/Seasons')
def Seasons(title, channel, summary, thumb, xmlurl, id):
  dir = ObjectContainer(title2=title)
  
  xmlElement = XML.ElementFromURL(xmlurl + id)
  for xmlSeason in xmlElement.xpath("//siteMapData//siteMapNode"):
    season          = {}
    season["id"]    = xmlSeason.xpath("./@id")[0]
    season["title"] = xmlSeason.xpath("./@title")[0]
    
    dir.add(DirectoryObject(key = Callback(Episodes, 
                                           title = season["title"],
                                           channel = channel, 
                                           xmlurl = xmlurl, 
                                           id = season["id"]), 
                            title=season["title"], 
                            summary = summary, 
                            thumb = thumb))

  return dir
 
####################################################################################################
@route('/video/viasatplay/Episodes')
def Episodes(title, channel, xmlurl, id):
  dir = ObjectContainer(title2=title)

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
        url = "http://www.tv" + channel + "play.se/play/" + id,
        title = video["title"],
        summary = video["desc"],
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
