import datetime
TITLE  = 'Viasat Play'
PREFIX = '/video/viasatplay'

ART   = "art-default.jpg"
THUMB = 'icon-default.png'

CHANNELS = [ 
    {
        'title':    'TV3 Play',
        'url':      'http://www.tv3play.se',
        'thumb':    R('viasat_tv3.png'),
        'desc':     unicode('TV3 är kanalen med starka känslor och starka karaktärer. Det är en suverän mix av serier, livsstilsprogram, storfilmer, reportage och intressanta program.')
    },
    {
        'title':    'TV6 Play',
        'url':      'http://www.tv6play.se',
        'thumb':    R('viasat_tv6.png'),
        'desc':     unicode('TV6 En underhållningskanal för den breda publiken. Actionfilmer och den vassaste humorn.')
    },
    {
        'title':    'TV8 Play',
        'url':      'http://www.tv8play.se',
        'thumb':    R('viasat_tv8.png'),
        'desc':     unicode('TV8 är en svensk livsstils- och underhållningskanal med ett brett utbud. Du som gillar bilar, hus och vill veta allt om slottsliv, kommer inte vilja missa våra svenska produktioner i höst.')
    },
    {
        'title':    'TV3 Play Norge',
        'url':      'http://www.tv3play.no',
        'thumb':    R('tv3_norway.png'),
        'desc':     unicode('TV3 er en underholdningskanal for alle. Våre verdier er leken, nyskapende, oppløftende og engasjerende. Kanalens programtilbud består av innkjøpte serier, filmer og norske egenproduserte programmer i ulike kategorier.')
    },
    {
        'title':    'Viasat 4 Play Norge',
        'url':      'http://www.viasat4play.no',
        'thumb':    R('viasat4_norway.png'),
        'desc':     unicode('Viasat 4 er en norsk underholdnings- og sportskanal fra Modern Times Group (MTG). Kanalen startet sendinger 8. september 2007 i forbindelse med utbyggingen av det digitale bakkenettet.')
    },    
    {
        'title':    'TV3 Play Danmark',
        'url':      'http://www.tv3play.dk',
        'thumb':    R('tv3_denmark.png'),
        'desc':     unicode('På TV3 Play kan du se alle TV3’s egne programmer og nogen af vores udenlandske serier. Vi har også ekstramateriale til flere af vores programmer. Mer information om vores programmer findes på TV3.dk')
    },
]

###################################################################################################
def Start():
    DirectoryObject.thumb = R(THUMB)
    ObjectContainer.art   = R(ART)

    HTTP.CacheTime = CACHE_1HOUR  

###################################################################################################
@handler(PREFIX, TITLE, thumb = THUMB, art = ART)
def MainMenu():
    oc = ObjectContainer(title1 = TITLE)
    for channel in CHANNELS:
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        ChannelMenu, 
                        title = channel['title'], 
                        base_url = channel['url'],
                        thumb = channel['thumb']
                    ), 
                title = channel['title'], 
                thumb = channel['thumb'], 
                summary = channel['desc']
            )
        )

    oc.add(InputDirectoryObject(key    = Callback(Search),
                                title  = 'Search Program',
                                prompt = 'Search Program'
                                )
           )
    
    return oc

####################################################################################################
def Search (query):

    query = unicode(query)
    oc = ObjectContainer(title1=TITLE, title2='Search Results')

    for channel in CHANNELS:
        for video in AllPrograms(channel['title'], channel['url']).objects:
            if len(query) == 1 and query.lower() == video.title[0].lower():
                # In case of single character - only compare initial character.
                oc.add(video)
            elif len(query) > 1 and query.lower() in video.title.lower():
                oc.add(video)

    if len(oc) == 0:
        return MessageContainer(
            "Search Results",
            "Did not find any result for '%s'" % query
            )
    else:
        oc.objects.sort(key=lambda obj: obj.title)
        return oc

####################################################################################################
@route(PREFIX + '/ChannelMenu')
def ChannelMenu(title, base_url, thumb):
    oc = ObjectContainer(title1 = TITLE)
    
    oc.add(
        DirectoryObject(
            key = 
                Callback(
                    Episodes, 
                    title = "Latest programs",
                    base_url = base_url, 
                    videos_url = base_url + "/mobileapi/featured",
                    id = 'latest_programs'
                ), 
            title = "Latest programs", 
            thumb = thumb
        )
    ) 

    oc.add(
        DirectoryObject(
            key = 
                Callback(
                    Clips, 
                    base_url = base_url, 
                    videos_url = base_url + "/mobileapi/featured",
                    title = "Latest clips",
                    id    = 'latest_clips'
                ), 
            title = "Latest clips", 
            thumb = thumb
        )
    ) 
    
    oc.add(
        DirectoryObject(
            key = 
                Callback(
                    Episodes, 
                    title = "Recommended",
                    base_url = base_url, 
                    videos_url = base_url + "/mobileapi/featured",
                    id = 'recommended'
                ), 
            title = "Recommended", 
            thumb = thumb
        )
    )  
    
    oc.add(
        DirectoryObject(
            key = 
                Callback(
                    AllPrograms, 
                    title = title, 
                    base_url = base_url
                ), 
            title = "All programs", 
            thumb = thumb
        )
    )
    
    return oc

####################################################################################################
@route(PREFIX + '/AllPrograms')
def AllPrograms(title, base_url):
    oc = ObjectContainer(title2 = title)
    programsInfo = JSON.ObjectFromURL(base_url + "/mobileapi/format")
    for section in programsInfo['sections']:
        for program in section['formats']:
            # Samsung causes troubles with empty Descriptions...
            mySummary = None
            if program['description'] != "":
                mySummary = unicode(program['description'])
            oc.add(
                DirectoryObject(
                    key = 
                        Callback(
                            Seasons,
                            title    = unicode(program['title']),
                            summary  = mySummary,
                            base_url = base_url,
                            id       = program['id']
                        ),
                    title   = unicode(program['title']),
                    summary = mySummary,
                    thumb   = GetImgUrl(program['image'])
                )
             )
  
    return oc

####################################################################################################
@route(PREFIX + '/Seasons')
def Seasons(title, summary, base_url, id):
    if summary:
        summary = unicode(summary)

    oc = ObjectContainer(title2 = unicode(title))
  
    seasonsInfo = JSON.ObjectFromURL(base_url + "/mobileapi/detailed?formatid=" + id)
    for season in seasonsInfo['formatcategories']:
        seasonName   = unicode(season['name'])
        seasonImgUrl = GetImgUrl(seasonsInfo['format']['image'])
        videos_url   = season['videos_call']
        if len(seasonsInfo['formatcategories']) > 1:
            oc.add(
                DirectoryObject(
                    key = 
                    Callback(Episodes, 
                             title      = seasonName,
                             base_url   = base_url, 
                             videos_url = videos_url,
                             id         = 'video_program',
                             art        = seasonImgUrl
                        ), 
                    title   = seasonName, 
                    summary = summary, 
                    thumb   = GetImgUrl(season['image']),
                    art     = seasonImgUrl
                    )
                )
        else:
            return Episodes(seasonName,
                            base_url,
                            videos_url,
                            'video_program',
                            seasonImgUrl)

    return oc
 
####################################################################################################
@route(PREFIX + '/Episodes')
def Episodes(title, base_url, videos_url, id = None, art = None):
    oc        = ObjectContainer(title2 = unicode(title))
    episodeOc = ObjectContainer(title2 = unicode(title))

    try:
        videosInfo = JSON.ObjectFromURL(videos_url)
    except:
        oc.header  = "Sorry"
        oc.message = "No programs found."
        return oc

    if id:
        videos = videosInfo[id]
    else:
        videos = videosInfo

    if id == 'video_program' and videosInfo['video_clip'] != None:
        oc.add(DirectoryObject(
                key = Callback(Clips,
                               base_url   = base_url,
                               videos_url = videos_url,
                               title      = title,
                               id         = 'video_clip',
                               art        = art
                               ), 
                title = "Klipp", 
                thumb = R(THUMB), 
                art   = R(ART)
                )
               )
    if videos != None:
        for video in videos:
            episodeOc.add(
                EpisodeObject(
                    url = base_url + '/play/' + video['id'],
                    title = unicode(video['title'] + " - " + video['summary']),
                    summary = unicode(video['description']),
                    show = unicode(video['formattitle']),
                    art = art,
                    thumb = GetImgUrl(video['image']),
                    originally_available_at = Datetime.ParseDate(video['airdate'].split(" ")[0]).date(),
                    duration = int(video['length']) * 1000,
                    season = int(video['season']),
                    index = int(video['episode'])
                    )
                )
        sortOnAirData(episodeOc)
        for ep in episodeOc.objects:
            oc.add(ep)
    elif id == 'video_program' and videosInfo['video_clip'] == None:
        oc.header  = "Sorry"
        oc.message = "No programs found."

    return oc

####################################################################################################
@route(PREFIX + '/Clips')
def Clips(base_url, videos_url, title, id, art=None):

    oc = ObjectContainer(title2 = unicode(title))

    videosInfo = JSON.ObjectFromURL(videos_url)

    if id:
        videos = videosInfo[id]
    else:
        videos = videosInfo
    
    for clip in videos:
        
        oc.add(
            VideoClipObject(
                url = base_url + '/play/' + clip['id'],
                title = unicode(clip['title']),
                summary = unicode(clip['summary']),
                thumb = GetImgUrl(clip['image']),
                art = art,
                originally_available_at = datetime.date.fromtimestamp(int(clip['created'])),
                duration = int(clip['length']) * 1000
                )
            )
    sortOnAirData(oc)
    return oc

####################################################################################################
def GetImgUrl(url):
    return "http://play.pdl.viaplay.com/imagecache/497x280/" + url.replace('\\', '') 

def sortOnAirData(Objects):
    for obj in Objects.objects:
        if obj.originally_available_at == None:
            Log("JTDEBUG - air date missing for %s" % obj.title)
            return Objects.objects.reverse()
    return Objects.objects.sort(key=lambda obj: (obj.originally_available_at,obj.title))
