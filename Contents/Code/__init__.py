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
        'thumb':    R('tv3_norway.png'),
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
                        AllPrograms, 
                        title = channel['title'], 
                        base_url = channel['url']
                    ), 
                title = channel['title'], 
                thumb = channel['thumb'], 
                summary = channel['desc']
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
            oc.add(
                DirectoryObject(
                    key = 
                        Callback(
                            Seasons,
                            title = unicode(program['title']),
                            summary = unicode(program['description']),
                            base_url = base_url,
                            id = program['id']
                        ),
                    title = unicode(program['title']),
                    summary = unicode(program['description']),
                    thumb = GetImgUrl(program['image'])
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
        oc.add(
            DirectoryObject(
                key = 
                    Callback(
                        Episodes, 
                        title = unicode(season['name']),
                        base_url = base_url, 
                        videos_url = season['videos_call'],
                        art = GetImgUrl(seasonsInfo['format']['image'])
                    ), 
                title = unicode(season['name']), 
                summary = summary, 
                thumb = GetImgUrl(season['image']),
                art = GetImgUrl(seasonsInfo['format']['image'])
            )
        )     

    return oc
 
####################################################################################################
@route(PREFIX + '/Episodes')
def Episodes(title, base_url, videos_url, art):
    oc = ObjectContainer(title2 = unicode(title))
    
    try:
        videosInfo = JSON.ObjectFromURL(videos_url)
    
        for video in videosInfo['video_program']:
            oc.add(
                EpisodeObject(
                    url = base_url + '/play/' + video['id'],
                    title = unicode(video['title']),
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

    except:
        pass
        
    if len(oc) < 1:
        oc.header  = "Sorry"
        oc.message = "No programs found."
     
    return oc

####################################################################################################
def GetImgUrl(url):
    return "http://play.pdl.viaplay.com/imagecache/497x280/" + url.replace('\\', '') 

