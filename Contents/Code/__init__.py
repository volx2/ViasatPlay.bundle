TITLE  = 'Viasat Play'
PREFIX = '/video/viasatplay'

ART   = "art-default.jpg"
THUMB = 'icon-default.png'

MAX_SEARCH_ITEMS = 25

CHANNELS = [ 
    {
        'title':    'TV3 Play',
        'base_url': 'http://www.tv3play.se',
        'thumb':    R('viasat_tv3.png'),
        'desc':     unicode('TV3 är kanalen med starka känslor och starka karaktärer. Det är en suverän mix av serier, livsstilsprogram, storfilmer, reportage och intressanta program.')
    },
    {
        'title':    'TV6 Play',
        'base_url': 'http://www.tv6play.se',
        'thumb':    R('viasat_tv6.png'),
        'desc':     unicode('TV6 En underhållningskanal för den breda publiken. Actionfilmer och den vassaste humorn.')
    },
    {
        'title':    'TV8 Play',
        'base_url': 'http://www.tv8play.se',
        'thumb':    R('viasat_tv8.png'),
        'desc':     unicode('TV8 är en svensk livsstils- och underhållningskanal med ett brett utbud. Du som gillar bilar, hus och vill veta allt om slottsliv, kommer inte vilja missa våra svenska produktioner i höst.')
    },
    {
        'title':    'TV10 Play',
        'base_url': 'http://www.tv10play.se',
        'thumb':    R('viasat_tv10.png'),
        'desc':     unicode('På TV10 Play ser du alla TV10:s egna program och vissa av våra livesändningar och utländska serier. Vi har dessutom extramaterial till många av våra program. Mer information om våra program finns på TV10.se.')
    },
    {
        'title':    'TV3 Play Norge',
        'base_url': 'http://www.tv3play.no',
        'thumb':    R('tv3_norway.png'),
        'desc':     unicode('TV3 er en underholdningskanal for alle. Våre verdier er leken, nyskapende, oppløftende og engasjerende. Kanalens programtilbud består av innkjøpte serier, filmer og norske egenproduserte programmer i ulike kategorier.')
    },
    {
        'title':    'Viasat 4 Play Norge',
        'base_url': 'http://www.viasat4play.no',
        'thumb':    R('viasat4_norway.png'),
        'desc':     unicode('Viasat 4 er en norsk underholdnings- og sportskanal fra Modern Times Group (MTG). Kanalen startet sendinger 8. september 2007 i forbindelse med utbyggingen av det digitale bakkenettet.')
    },	
    {
        'title':    'TV3 Play Danmark',
        'base_url': 'http://www.tv3play.dk',
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
                        base_url = channel['base_url'],
                        thumb = channel['thumb']
                    ), 
                title = channel['title'], 
                thumb = channel['thumb'], 
                summary = channel['desc']
            )
        )

    oc.add(
        InputDirectoryObject(
            key = Callback(Search),
            title  = 'Search Program',
            prompt = 'Search Program'
        )
    )
    
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
@route(PREFIX + '/Search', offset = int)
def Search(query, offset = 0):
    oc = ObjectContainer(title1 = TITLE, title2 = 'Search Results')

    query   = unicode(query)
    results = []
    counter = 0

    for channel in CHANNELS:
        videos = AllPrograms(channel['title'], channel['base_url']).objects
        
        for video in videos:                
            # In case of single character - only compare initial character.
            if len(query) > 1 and query.lower() in video.title.lower() or \
               len(query) == 1 and query.lower() == video.title[0].lower():
                    
                results.append(
                    {
                        'video': video, 
                        'title': video.title, 
                        'channel_title': channel['title'], 
                        'thumb': channel['thumb']
                    }
                )
    
    results = sorted(results, key = lambda result: result['title'])           
    for result in results:
        counter = counter + 1
            
        if counter <= offset:
            continue
        
        video = result['video']         
        video.summary = result['channel_title'] + "\r\n\r\n" + video.summary
        video.art = result['thumb']
                
        oc.add(video)
                    
        if len(oc) >= MAX_SEARCH_ITEMS:
            oc.objects.sort(key = lambda obj: obj.title)
                
            oc.add(
                NextPageObject(
                    key =
                        Callback(
                            Search,
                            query = query,
                            offset = counter
                        ),
                    title = "Next..."
                )
            )
                    
            return oc

    if len(oc) == 0:
        return NoProgramsFound(oc)
    else:
        oc.objects.sort(key = lambda obj: obj.title)
        return oc


####################################################################################################
@route(PREFIX + '/AllPrograms')
def AllPrograms(title, base_url):
    oc = ObjectContainer(title2 = title)
    programsInfo = JSON.ObjectFromURL(base_url + "/mobileapi/format")
    
    for section in programsInfo['sections']:
        for program in section['formats']:
            oc.add(
                DirectoryObject(
                    key = 
                        Callback(
                            Seasons,
                            title = unicode(program['title']),
                            summary = unicode(program['description']) + " ", # NOTE: Samsung causes troubles with empty Descriptions...
                            base_url = base_url,
                            id = program['id']
                        ),
                    title = unicode(program['title']),
                    summary = unicode(program['description']),
                    thumb = GetImageURL(program['image'])
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
    seasonImgUrl = GetImageURL(seasonsInfo['format']['image'])
    
    if len(seasonsInfo['formatcategories']) == 1:
        return Episodes(
                    title = unicode(seasonsInfo['formatcategories'][0]['name']),
                    base_url = base_url,
                    videos_url = seasonsInfo['formatcategories'][0]['videos_call'],
                    id = 'video_program',
                    art = seasonImgUrl
        ) 
    
    else:
        for season in seasonsInfo['formatcategories']:
            seasonName = unicode(season['name']) 

            oc.add(
                DirectoryObject(
                    key = 
                        Callback(
                            Episodes, 
                            title      = seasonName,
                            base_url   = base_url, 
                            videos_url = season['videos_call'],
                            id         = 'video_program',
                            art        = seasonImgUrl
                        ), 
                    title   = seasonName, 
                    summary = summary, 
                    thumb   = GetImageURL(season['image']),
                    art     = seasonImgUrl
                )
            ) 

    return oc
 
####################################################################################################
@route(PREFIX + '/Episodes')
def Episodes(title, base_url, videos_url, id = None, art = None):
    oc = ObjectContainer(title2 = unicode(title))

    try:
        videosInfo = JSON.ObjectFromURL(videos_url)
    except:
        return NoProgramsFound(oc)

    if id:
        videos = videosInfo[id]
    else:
        videos = videosInfo
    
    if videos:
        for video in videos:
            try:
                oc.add(
                    EpisodeObject(
                        url = base_url + '/play/' + video['id'],
                        title = unicode(video['title'] + " - " + video['summary']),
                        summary = unicode(video['description']),
                        show = unicode(video['formattitle']),
                        art = art,
                        thumb = GetImageURL(video['image']),
                        originally_available_at = Datetime.ParseDate(video['airdate'].split(" ")[0]).date(),
                        duration = int(video['length']) * 1000,
                        season = int(video['season']),
                        index = int(video['episode'])
                    )
                )
            except:
                # If not all attributes, especially duration, are present
                # for an episode, it won't play either, so we skip those.
                continue
            
    if len(oc) < 1:
        return NoProgramsFound(oc)

    return oc

####################################################################################################
def NoProgramsFound(oc):
    oc.header  = "Sorry"
    oc.message = "No programs found."
     
    return oc

####################################################################################################
def GetImageURL(url):
    return "http://play.pdl.viaplay.com/imagecache/497x280/" + url.replace('\\', '') 
