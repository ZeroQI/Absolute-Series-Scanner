# -*- coding: utf-8 -*-

###### library  ########################################################### Functions, Constants #####
import sys                                                           # getdefaultencoding, getfilesystemencoding, platform, argv
import os                                                            # path, listdir
import tempfile                                                      # NamedTemporaryFile
import time                                                          # strftime
import datetime                                                      # datetime
import re                                                            # match, compile, sub
import fnmatch                                                       # translate
import logging, logging.handlers                                     # FileHandler, Formatter, getLogger, DEBUG | RotatingFileHandler
import Utils                                                         # SplitPath
import Media                                                         # Episode
import VideoFiles                                                    # Scan
import Stack                                                         # Scan
import inspect                                                       # getfile, currentframe
import ssl                                                           # SSLContext
import zipfile                                                       # ZipFile, namelist
import json                                                          # loads
from lxml import etree                                               # fromstring
try:                 from ssl import PROTOCOL_TLS    as SSL_PROTOCOL # Python >= 2.7.13 #ssl.PROTOCOL_TLSv1
except ImportError:  from ssl import PROTOCOL_SSLv23 as SSL_PROTOCOL # Python <  2.7.13
try:                 from urllib.request import urlopen, Request     # Python >= 3.0
except ImportError:  from urllib2        import urlopen, Request     # Python == 2.x

### Log variables, regex, skipped folders, words to remove, character maps ###                                                                                                      ### http://www.zytrax.com/tech/web/regex.htm  # http://regex101.com/#python
#ssl._create_default_https_context = ssl._create_unverified_context
SSL_CONTEXT               = ssl.SSLContext(SSL_PROTOCOL)                                                                                                                            #
TVDB_HTTP_API_URL         = 'http://thetvdb.com/api/A27AD9BE0DA63333/series/%s/all/en.xml'                                                                                          #
ASS_MAPPING_URL           = 'https://rawgit.com/ZeroQI/Absolute-Series-Scanner/master/tvdb4.mapping.xml'                                                                            #
ANIDB_TVDB_MAPPING        = 'https://rawgit.com/ScudLee/anime-lists/master/anime-list-master.xml'                                                                                   #
ANIDB_TVDB_MAPPING_MOD    = 'https://rawgit.com/ZeroQI/Absolute-Series-Scanner/master/anime-list-corrections.xml'                                                                   #
ANIDB_TVDB_MAPPING_CUSTOM = 'anime-list-custom.xml'                                                                                                                                 # custom local correction for ScudLee mapping file url
SOURCE_IDS                = '\[((?P<source>(anidb|anidb2|tvdb|tvdb2|tvdb3|tvdb4|tvdb5|tmdb|tsdb|imdb|youtube|youtube2))-)?(?P<id>[^\]]*)\]'                                         #
SOURCE_ID_FILES           = ["anidb.id", "anidb2.id", "tvdb.id", "tvdb2.id", "tvdb3.id", "tvdb4.id", "tvdb5.id", "tmdb.id", "tsdb.id", "imdb.id", "youtube.id"]                     #
TVDB_MODE_IDS             = ".*?\[tvdb(?P<mode>(2|3|4|5))-(tt)?(?P<guid>[0-9]{1,7})(-s[0-9]{1,3}(e[0-9]{1,3})?)?\]"                                                                 #
TVDB_MODE_ID_OFFSET       = ".*? ?\[(?P<source>(tvdb|tvdb2|tvdb3|tvdb4|tvdb5))-(tt)?[0-9]{1,7}-(?P<season>s[0-9]{1,3})?(?P<episode>e[0-9]{1,3})?\]"                                 #
ANIDB2_MODE               = ".*? ?\[anidb2-(?P<guid>[0-9]{1,7})\]"                                                                                                                  #
SEASON_RX                 = [                                                                                                                                                       ### Seasons Folders 
                              'Specials',                                                                                                                                           # Specials (season 0)
                              '(Season|Series|Book|Saison|Livre|S)[ _\-]*(?P<season>[0-9]{1,2}).*',                                                                                 # Season ##, Series #Book ## Saison ##, Livre ##, S##, S ##
                              '(?P<show>.*?)[\._\- ]+[sS](?P<season>[0-9]{2})',                                                                                                     # (title) S01
                              '(?P<season>[0-9]{1,2}).*',	                                                                                                                          # ##
                              '^.*([Ss]aga]|([Ss]tory )?[Aa][Rr][KkCc]).*$'                                                                                                         # Last entry in array, folder name droped but files kept: Story, Arc, Ark, Video
                            ]                                                                                                                                                       #
SERIES_RX                 = [                                                                                                                                                       ######### Series regex - "serie - xxx - title" ###
  '(^|(?P<show>.*?)[ _\.\-]+)(?P<season>[0-9]{1,2})[Xx](?P<ep>[0-9]{1,3})(([_\-Xx]|[_\-][0-9]{1,2}[Xx])(?P<ep2>[0-9]{1,3}))?([ _\.\-]+(?P<title>.*))?$',                            #  0 # 1x01
  '(^|(?P<show>.*?)[ _\.\-]+)s(?P<season>[0-9]{1,2})([ _\.\-])?(e| e|ep| ep)(?P<ep>[0-9]{1,3})(([ _\.\-]|(e|ep)|[ _\.\-](e|ep))(?P<ep2>[0-9]{1,3}))?($|( | - |)(?P<title>.*?)$)',   #  1 # s01e01-02 | ep01-ep02 | e01-02 | s01-e01 | s01 e01'(^|(?P<show>.*?)[ _\.\-]+)(?P<ep>[0-9]{1,3})[ _\.\-]?of[ _\.\-]?[0-9]{1,3}([ _\.\-]+(?P<title>.*?))?$',                                                              #  2 # 01 of 08 (no stacking for this one ?)
  '^(?P<show>.*?) - (E|e|Ep|ep|EP)?(?P<ep>[0-9]{1,3})(-(?P<ep2>[0-9]{1,3}))?(v[0-9]{1})?( - |.)?(?P<title>.*)$',                                                                    #  2 # Serie - xx - title.ext | ep01-ep02 | e01-02
  '^(?P<show>.*?) \[(?P<season>[0-9]{1,2})\] \[(?P<ep>[0-9]{1,3})\] (?P<title>.*)$']                                                                                                #  3 # Serie [Sxx] [Exxx] title.ext                     
#|Ep #
DATE_RX         = [ '(?P<year>[0-9]{4})[^0-9a-zA-Z]+(?P<month>[0-9]{2})[^0-9a-zA-Z]+(?P<day>[0-9]{2})([^0-9]|$)',           # 2009-02-10
                    '(?P<month>[0-9]{2})[^0-9a-zA-Z]+(?P<day>[0-9]{2})[^0-9a-zA-Z(]+(?P<year>[0-9]{4})([^0-9a-zA-Z]|$)',    # 02-10-2009
                  ]  #https://support.plex.tv/articles/200381053-naming-date-based-tv-shows/
ANIDB_OFFSET    = [0, 100, 150, 200, 400, 0, 0];                                                                                                                                               ###### AniDB Specials episode offset value array
ANIDB_RX        = [                                                                                                                                                                            ###### AniDB Specials episode offset regex array
                    '(^|(?P<show>.*?)[ _\.\-]+)(SP|SPECIAL|OAV)[ _\.]?(?P<ep>\d{1,2})(-(?P<ep2>[0-9]{1,3}))?(v0|v1|v2|v3|v4|v5)?[ _\.]?(?P<title>.*)$',                                        #  0 # 001-099 Specials
                    '(^|(?P<show>.*?)[ _\.\-]+)(OP|NCOP|OPENING)[ _\.]?(?P<ep>\d{1,2}[a-z]?)?[ _\.]?(v0|v1|v2|v3|v4|v5)?([ _\.\-]+(?P<title>.*))?$',                                           #  1 # 100-149 Openings
                    '(^|(?P<show>.*?)[ _\.\-]+)(ED|NCED|ENDING)[ _\.]?(?P<ep>\d{1,2}[a-z]?)?[ _\.]?(v0|v1|v2|v3|v4|v5)?([ _\.\-]+(?P<title>.*))?$',                                            #  2 # 150-199 Endings
                    '(^|(?P<show>.*?)[ _\.\-]+)(TRAILER|PROMO|PV|T)[ _\.]?(?P<ep>\d{1,2})[ _\.]?(v0|v1|v2|v3|v4|v5)?([ _\.\-]+(?P<title>.*))?$',                                               #  3 # 200-299 Trailer, Promo with a  number  '(^|(?P<show>.*?)[ _\.\-]+)((?<=E)P|PARODY|PARODIES?) ?(?P<ep>\d{1,2})? ?(v2|v3|v4|v5)?(?P<title>.*)$',                                                                        # 10 # 300-399 Parodies
                    '(^|(?P<show>.*?)[ _\.\-]+)(O|OTHERS?)(?P<ep>\d{1,2})[ _\.]?(v0|v1|v2|v3|v4|v5)?[ _\.\-]+(?P<title>.*)$',                                                                  #  4 # 400-499 Others
                    '(^|(?P<show>.*?)[ _\.\-]+)(e|ep|e[ _\.]|ep[ _\.]|e-|ep-)?(?P<ep>[0-9]{1,3})((e|ep|-e|-ep|-)(?P<ep2>[0-9]{1,3})|)?[ _\.]?(v0|v1|v2|v3|v4|v5)?([ _\.\-]+(?P<title>.*))?$',  #  5 # E01 | E01-02| E01-E02 | E01E02                                                                                                                       # __ # look behind: (?<=S) < position < look forward: (?!S)
                    '(^|(?P<show>.*?)[ _\.\-]+)SP?[ _\.]?(?P<ep>\d{1,2})[ _\.]?(?P<title>.*)$']                                                                                                #  6 # 001-099 Specials #'S' moved to the end to make sure season strings are not caught in prev regex
IGNORE_DIRS_RX  = [ '@Recycle', '.@__thumb', 'lost\+found', '.AppleDouble','$Recycle.Bin', '$RECYCLE.BIN', 'System Volume Information', 'Temporary Items', 'Network Trash Folder', '@eaDir',        ###### Ignored folders
                    'Extras', 'Samples?', 'bonus', '.*bonus disc.*', 'trailers?', '.*_UNPACK_.*', '.*_FAILED_.*', 'misc', '_Misc'] #, "VIDEO_TS"]                                   #      source: Filters.py  removed '\..*',        
IGNORE_FILES_RX = ['[ _\.\-]sample', 'sample[ _\.\-]', '-Recap\.', 'OST', 'soundtrack', 'Thumbs.db', '\.xml$', '\.smi$', '^\._']#, '\.plexignore', '.*\.id']            #, '.*\.log$'                   # Skipped files (samples, trailers)                                                          
VIDEO_EXTS      = [ '3g2', '3gp', 'asf', 'asx', 'avc', 'avi', 'avs', 'bin', 'bivx', 'divx', 'dv', 'dvr-ms', 'evo', 'fli', 'flv', 'img', 'iso', 'm2t', 'm2ts', 'm2v',                #
                    'm4v', 'mkv', 'mov', 'mp4', 'mpeg', 'mpg', 'mts', 'nrg', 'nsv', 'nuv', 'ogm', 'ogv', 'tp', 'pva', 'qt', 'rm', 'rmvb', 'sdp', 'swf', 'svq3', 'strm',             #
                    'ts', 'ty', 'vdr', 'viv', 'vp3', 'wmv', 'wpl', 'wtv', 'xsp', 'xvid', 'webm', 'ifo', 'disc']                                                                             # DVD: 'ifo', 'bup', 'vob'
FILTER_CHARS    = "\\/:*?<>|~;"  #_;.                                                                                                                                               # Windows file naming limitations + "~-,._" + ';' as plex cut title at this for the agent
WHACK_PRE_CLEAN = [ "x264-FMD Release", "x264-h65", "x264-mSD", "x264-BAJSKORV", "x264-MgB", "x264-SYS", "x264-FQM", "x264-ASAP", "x264-QCF", "x264-W4F", 'x264-w4f', "x264-AAC", 
                    'x264-2hd', "x264-ASAP", 'x264-bajskorv', 'x264-batv', "x264-BATV", "x264-EXCELLENCE", "x264-KILLERS", "x264-LOL", 'x264-MgB', 'x264-qcf', 'x264-SnowDoN', 'x264-xRed', 
                    "H.264-iT00NZ", "H.264.iT00NZ", 'H264-PublicHD', "H.264-BS", 'REAL.HDTV', "WEB.DL", "H_264_iT00NZ", "www.crazy-torrent.com", "ReourceRG Kids Release",
                    "By UniversalFreedom", "XviD-2HD", "XviD-AFG", "xvid-aldi", 'xvid-asap', "XviD-AXED", "XviD-BiA-mOt", 'xvid-fqm', "xvid-futv", 'xvid-killer', "XviD-LMAO", 'xvid-pfa',
                    'xvid-saints', "XviD-T00NG0D", "XViD-ViCKY", "XviD-BiA", "XVID-FHW", "PROPER-LOL", "5Banime-koi_5d", "%5banime-koi%5d", "minitheatre.org", "mthd bd dual", "WEB_DL",
                    "HDTV-AFG", "HDTV-LMAO", "ResourceRG Kids", "kris1986k_vs_htt91",   'web-dl', "-Pikanet128", "hdtv-lol", "REPACK-LOL", " - DDZ", "OAR XviD-BiA-mOt", "3xR", "(-Anf-)",
                    "Anxious-He", "Coalgirls", "Commie", "DarkDream", "Doremi", "ExiledDestiny", "Exiled-Destiny", "Exiled Destiny", "FFF", "FFFpeeps", "Hatsuyuki", "HorribleSubs", 
                    "joseole99", "(II Subs)", "OAR HDTV-BiA-mOt", "Shimeji", "(BD)", "(RS)", "Rizlim", "Subtidal", "Seto-Otaku", "OCZ", "_dn92__Coalgirls__", 
                    "(BD 1920x1080 Hi10P, JPN+ENG)", "(BD 1280x720 Hi10P)", "(DVD_480p)", "(1080p_10bit)", "(1080p_10bit_DualAudio)", "(Tri.Audio)", "(Dual.Audio)", "(BD_720p_AAC)", "x264-RedBlade",
                    "BD 1080p", "BD 960p", "BD 720p", "BD_720p", "TV 720p", "DVD 480p", "DVD 476p", "DVD 432p", "DVD 336p", "1080p.BluRay", "FLAC5.1", "x264-CTR", "1080p-Hi10p", "FLAC2.0",
                    "1920x1080", "1280x720", "848x480", "952x720", "(DVD 720x480 h264 AC3)", "(720p_10bit)", "(1080p_10bit)", "(1080p_10bit", "(BD.1080p.AAC)", "[720p]",
                    "H.264_AAC", "Hi10P", "Hi10", "x264", "BD 10-bit", "DXVA", "H.264", "(BD, 720p, FLAC)", "Blu-Ray", "Blu-ray",  "SD TV", "SD DVD", "HD TV",  "-dvdrip", "dvd-jap", "(DVD)", 
                    "FLAC", "Dual Audio", "AC3", "AC3.5.1", "AC3-5.1", "AAC2.0", "AAC.2.0", "AAC2_0", "AAC", 'DD5.1', "5.1",'divx5.1', "DD5_1", "TV-1", "TV-2", "TV-3", "TV-4", "TV-5",
                    "(Exiled_Destiny)", "1080p", "720p", "480p", "_BD", ".XVID", "(xvid)", "dub.sub_ja+.ru+", "dub.sub_en.ja", "dub_en",
                    "-Cd 1", "-Cd 2", "Vol 1", "Vol 2", "Vol 3", "Vol 4", "Vol 5", "Vol.1", "Vol.2", "Vol.3", "Vol.4", "Vol.5",
                    "%28", "%29", " (1)", "(Clean)", "vostfr", "HEVC", "(Bonus inclus)", "(BD 1920x1080)", "10Bits-WKN", "WKN", "(Complet)", "Despair-Paradise", "Shanks@", "[720p]", "10Bits", 
                    "(TV)", "[DragonMax]", "INTEGRALE", "MKV", "MULTI", "DragonMax", "Zone-Telechargement.Ws", "Zone-Telechargement", "AniLibria.TV", "HDTV-RIP"
                  ]                                                                                                                                                               #include spaces, hyphens, dots, underscore, case insensitive
WHACK           = [                                                                                                                                                               ### Tags to remove (lowercase) ###
                    'x264', 'h264', 'dvxa', 'divx', 'xvid', 'divx51', 'mp4', "avi", '8bit', '8-bit', 'hi10', 'hi10p', '10bit', '10-bit', 'crf24', 'crf 24', 'hevc',               # Video Codecs (color depth and encoding)
                    '480p', '576p', '720p', '1080p', '1080i',                                                                                                                     # Resolution
                    '24fps', '25fps', 'ntsc', 'pal', 'ntsc-u', 'ntsc-j',                                                                                                          # Refresh rate, Format
                    'mp3', 'ogg', 'ogm', 'vorbis', 'aac', 'dts', 'ac3', 'ac-3', '5.1ch', '5.1', '7.1ch',  'qaac',                                                                 # Audio Codecs, channels
                    'dc', 'se', 'extended', 'unrated', 'multi', 'multisubs', 'dubbed', 'dub', 'subbed', 'sub', 'engsub', 'eng', 'french', 'fr', 'jap', "JPN+ENG",                 # edition (dc = directors cut, se = special edition), subs and dubs
                    'custom', 'internal', 'repack', 'proper', 'rerip', "raw", "remastered", "uncensored", 'unc', 'cen',                                                           # format
                    'cd1', 'cd2', 'cd3', 'cd4', '1cd', '2cd', '3cd', '4cd', 'xxx', 'nfo', 'read.nfo', 'readnfo', 'nfofix', 'fragment', 'fs', 'ws', "- copy", "reenc", "hom",      # misc
                    'retail', 'webrip', 'web-dl', 'wp', 'workprint', "mkv",  "v1", "v2", "v3", "v4", "v5"                                                                         # release type: retail, web, work print
                    'bdrc', 'bdrip', 'bluray', 'bd', 'brrip', 'hdrip', 'hddvd', 'hddvdrip', 'wsrip',                                                                              # Source: bluray
                    'ddc', 'dvdrip', 'dvd', 'r1', 'r3', 'r5', "dvd", 'svcd', 'vcd', 'sd', 'hd', 'dvb', "release", 'ps3avchd',                                                     # Source: DVD, VCD, S-VCD
                    'dsr', 'dsrip', 'hdtv', 'pdtv', 'ppv', 'stv', 'tvrip', 'complete movie', "hiei", "metis", "norar",                                                            # Source: dtv, stv
                    'cam', 'bdscr', 'dvdscr', 'dvdscreener', 'scr', 'screener', 'tc', 'telecine', 'ts', 'telesync', 'mp4',                                                        # Source: screener
                    "mthd", "thora", 'sickrage', 'brrip', "remastered", "yify", "tsr", "reidy", "gerdhanse", 'remux',                                                             #'limited', 
                    'rikou', 'hom?', "it00nz", "nn92", "mthd", "elysium", "encodebyjosh", "krissy", "reidy", "it00nz", "s4a"                                                      # Release group
                  ]
CHARACTERS_MAP =  {                                                                                                                                                                #Specials characters to re-map
                    14844057:"'", 14844051:'-', 14844052:'-', 14844070:'...', 15711386:':', 14846080:'∀', 15711646:'~',                                                           #['’' \xe2\x80\x99] ['–' \xe2\x80\x93] ['…' \xe2\x80\xa6] # '：' # 12770:'', # '∀ Gundam' no need #'´' ['\xc2', '\xb4']
                    50048:'A' , 50050:'A' , 50052:'Ä' , 50080:'a' , 50082:'a' , 50084:'a' , 50305:'a' , 50308:'A' , 50309:'a' ,  50055:'C' , 50087:'c' , 50310:'C' , 50311:'c' ,  #'à' ['\xc3', '\xa0'] #'â' ['\xc3', '\xa2'] #'Ä' ['\xc3', '\x84'] #'ā' ['\xc4', '\x81'] #'À' ['\xc3', '\x80'] #'Â' ['\xc3', '\x82'] # 'Märchen Awakens Romance', 'Rozen Maiden Träumend' #'Ç' ['\xc3', '\x87'] #'ç' ['\xc3', '\xa7'] 
                    50057:'E' , 50088:'e' , 50089:'e' , 50090:'e' , 50091:'e' , 50323:'e' , 50328:'E' , 50329:'e' ,                                                               #'É' ['\xc3', '\x89'] #'è' ['\xc3', '\xa8'] #'é' ['\xc3', '\xa9'] #'ē' ['\xc4', '\x93'] #'ê' ['\xc3', '\xaa'] #'ë' ['\xc3', '\xab']
                    50094:'i' , 50095:'i' , 50347:'i' , 50561:'L' , 50562:'l' , 50563:'N' , 50564:'n' , 50097:'n' ,                                                               #'î' ['\xc3', '\xae'] #'ï' ['\xc3', '\xaf'] #'ī' ['\xc4', '\xab'] #'ñ' ['\xc3', '\xb1']
                    50067:'O' , 50068:'Ô' , 50072:'O' , 50099:'o' , 50100:'o' , 50102:'o' , 50573:'o' , 50578:'OE', 50579:'oe',                                                   #'Ø' ['', '']         #'Ô' ['\xc3', '\x94'] #'ô' ['\xc3', '\xb4'] #'ō' ['\xc5', '\x8d'] #'Œ' ['\xc5', '\x92'] #'œ' ['\xc5', '\x93']
                    53423:'Я' , 50586:'S' , 50587:'s' , 50079:'ss', 50105:'u' , 50107:'u' , 50108:'u' , 50071:'x' , 50617:'Z' , 50618:'z' , 50619:'Z' , 50620:'z' ,               #'Я' ['\xd0', '\xaf'] #'ß' []               #'ù' ['\xc3', '\xb9'] #'û' ['\xc3', '\xbb'] #'ü' ['\xc3', '\xbc'] #'²' ['\xc2', '\xb2'] #'³' ['\xc2', '\xb3'] #'×' ['\xc3', '\x97'],
                    49835:'«' , 49842:'²' , 49843:'³' , 49844:"'" , 49847:' ' , 49848:'¸',  49851:'»' , 49853:'½' , 52352:''  , 52353:''                                          #'«' ['\xc2', '\xab'] #'·' ['\xc2', '\xb7'] #'»' ['\xc2', '\xbb']# 'R/Ranma ½ Nettou Hen'  #'¸' ['\xc2', '\xb8'] #'̀' ['\xcc', '\x80'] #  ['\xcc', '\x81'] 
                  }
HEADERS        =  {'Content-type': 'application/json'}
                  
### Check config files on boot up then create library variables ###    #platform = xxx if callable(getattr(sys,'platform')) else "" 
PLEX_ROOT  = os.path.abspath(os.path.join(os.path.dirname(inspect.getfile(inspect.currentframe())), "..", ".."))
if not os.path.isdir(PLEX_ROOT):
  path_location = { 'Windows': '%LOCALAPPDATA%\\Plex Media Server',
                    'MacOSX':  '$HOME/Library/Application Support/Plex Media Server',
                    'Linux':   '$PLEX_HOME/Library/Application Support/Plex Media Server' }
  PLEX_ROOT = os.path.expandvars(path_location[Platform.OS.lower()] if Platform.OS.lower() in path_location else '~')  # Platform.OS:  Windows, MacOSX, or Linux

### Sanitize string
def os_filename_clean_string(string):
  for char, subst in zip(list(FILTER_CHARS), [" " for x in range(len(FILTER_CHARS))]) + [("`", "'"), ('"', "'")]:    # remove leftover parenthesis (work with code a bit above)
    if char in string:  string = string.replace(char, subst)                                                         # translate anidb apostrophes into normal ones #s = s.replace('&', 'and')
  return string

### Set Logging to proper logging file
def set_logging(foldername='', filename='', backup_count=0, format='%(message)s', mode='w'):#%(asctime)-15s %(levelname)s - 
  global Log, handler, CACHE_PATH, LOG_FILE
  CACHE_PATH = os.path.join(PLEX_ROOT, 'Plug-in Support', 'Data', 'com.plexapp.agents.hama', 'DataItems', '_Logs')
  if foldername: CACHE_PATH = os.path.join(CACHE_PATH, os_filename_clean_string(foldername))
  if not os.path.exists(CACHE_PATH):  os.makedirs(CACHE_PATH)
  
  filename = os_filename_clean_string(filename) if filename else '_root_.scanner.log'
  LOG_FILE = os.path.join(CACHE_PATH, filename)
  if handler: Log.removeHandler(handler)
  if backup_count:  handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=10*1024*1024, backupCount=backup_count)
  else:             handler = logging.FileHandler                 (LOG_FILE, mode=mode)
  handler.setFormatter(logging.Formatter(format))
  handler.setLevel(logging.DEBUG)
  Log.addHandler(handler)

### Log + CACHE_PATH calculated once for all calls ###
handler          = None
Log              = logging.getLogger('main');  Log.setLevel(logging.DEBUG);  set_logging()
CACHE_PATH       = ""
LOG_FILE         = ""
PLEX_LIBRARY     = {}
PLEX_LIBRARY_URL = "http://127.0.0.1:32400/library/sections/"    # Allow to get the library name to get a log per library https://support.plex.tv/hc/en-us/articles/204059436-Finding-your-account-token-X-Plex-Token
if os.path.isfile(os.path.join(PLEX_ROOT, "X-Plex-Token.id")):
  Log.info("'X-Plex-Token.id' file present")
  with open(os.path.join(PLEX_ROOT, "X-Plex-Token.id"), 'r') as token_file:  PLEX_LIBRARY_URL += "?X-Plex-Token=" + token_file.read().strip()
try:
  library_xml = etree.fromstring(urlopen(PLEX_LIBRARY_URL, context=SSL_CONTEXT).read())
  for library in library_xml.iterchildren('Directory'):
    for path in library.iterchildren('Location'):
      PLEX_LIBRARY[path.get("path")] = library.get("title")
except:  Log.info("Place Plex token string in file in Plex root '.../Plex Media Server/X-Plex-Token.id' to have a log per library - https://support.plex.tv/hc/en-us/articles/204059436-Finding-your-account-token-X-Plex-Token")

def Dict(var, *arg, **kwarg):  #Avoid TypeError: argument of type 'NoneType' is not iterable
  """ Return the value of an (imbricated) dictionnary, if all fields exist else return "" unless "default=new_value" specified as end argument
      Ex: Dict(variable_dict, 'field1', 'field2', default = 0)
  """
  for key in arg:
    if isinstance(var, dict) and key and key in var:  var = var[key]
    else:  return kwarg['default'] if kwarg and 'default' in kwarg else ""   # Allow Dict(var, tvdbid).isdigit() for example
  return kwarg['default'] if var in (None, '', 'N/A', 'null') and kwarg and 'default' in kwarg else "" if var in (None, '', 'N/A', 'null') else var

### replace a string by another while retaining original string case ##############################################################################################
def replace_insensitive (ep, word, sep=" "):
  if ep.lower()==word.lower(): return ""
  position = ep.lower().find(word.lower())
  if position > -1 and len(ep)>len(word):  return ("" if position==0 else ep[:position].lstrip()) + (sep if len(ep) < position+len(word) else ep[position+len(word):].lstrip())
  return ep

### Turn a string into a list of string and number chunks  "z23a" -> ["z", 23, "a"] ###############################################################################
def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):  return [int(text) if text.isdigit() else text.lower() for text in re.split(_nsre, s)]

### Return number of bytes of Unicode characters ########################################################
def unicodeCharLen (char):                                       # count consecutive 1 bits since it represents the byte numbers-1, less than 1 consecutive bit (128) is 1 byte , less than 23 bytes is 1
  for x in range(1,6):                                           # start at 1, 6 times 
    if ord(char) < 256-pow(2, 7-x)+(2 if x==6 else 0): return x  # 256-2pow(x) with x(7->0) = 128 192 224 240 248 252 254 255 = 1 to 8 bits at 1 from the left, 256-2pow(7-x) starts form left
 
### Return correct String length even with Unicode characters ########################################################
def unicodeLen (string): 
  length = 0
  for char in string:  length += unicodeCharLen(char)
  return length
  
### Decode string back to Unicode ###   #Unicodize in utils?? #fixEncoding in unicodehelper
def encodeASCII(string, language=None): #from Unicodize and plex scanner and other sources
  if string=="": return ""
  ranges = [ {"from": u"\u3300" , "to": u"\u33ff" }, #
             {"from": u"\ufe30" , "to": u"\ufe4f" }, #
             {"from": u"\uf900" , "to": u"\ufaff" }, #compatibility ideographs
             {"from": u"\u30a0" , "to": u"\u30ff" }, #cjk radicals supplement                 - Japanese Kana    
             {"from": u"\u2e80" , "to": u"\u2eff" }, #cjk radicals supplement                 - Japanese Kana    
             {"from": u"\u4e00" , "to": u"\u9fff" }, #CJK Unified Ideographs                  - Chinese Han Ideographs, Common
             {"from": u"\uF900" , "to": u"\uFAFF" }, #CJK Compatibility Ideographs            - Chinese Han Ideographs, Rare, historic
             {"from": u"\u3400" , "to": u"\u4DBF" }, #CJK Unified Ideographs Extension A      - Chinese Han Ideographs, Rare
             {"from": u"\u20000", "to": u"\u2A6DF"}, #CJK Unified Ideographs Extension B      - Chinese Han Ideographs, Rare, historic
             {"from": u"\u2A700", "to": u"\u2B73F"}, #CJK Unified Ideographs Extension C      - Chinese Han Ideographs, Rare, historic
             {"from": u"\u2B740", "to": u"\u2B81F"}, #CJK Unified Ideographs Extension D      - Chinese Han Ideographs, Uncommon, some in current use
             {"from": u"\u2B820", "to": u"\u2CEAF"}, #CJK Unified Ideographs Extension E      - Chinese Han Ideographs, Rare, historic
             {"from": u"\u2F800", "to": u"\u2FA1F"}] #CJK Compatibility Ideographs Supplement - Chinese Han Ideographs, Duplicates, unifiable variants, corporate characters
  encodings, encoding = ['iso8859-1', 'utf-16', 'utf-16be', 'utf-8'], ord(string[0])                                                                          #
  if 0 <= encoding < len(encodings):  string = string[1:].decode('cp949') if encoding == 0 and language == 'ko' else string[1:].decode(encodings[encoding])   # If we're dealing with a particular language, we might want to try another code page.
  if sys.getdefaultencoding() not in encodings:
    try:     string = string.decode(sys.getdefaultencoding())
    except:  pass
  if not sys.getfilesystemencoding()==sys.getdefaultencoding():
    try:     string = string.decode(sys.getfilesystemencoding())
    except:  pass
  string = string.strip('\0')
  try:       string = unicodedata.normalize('NFKD', string)    # Unicode  to ascii conversion to corect most characters automatically
  except:    pass
  try:       string = re.sub(RE_UNICODE_CONTROL, '', string)   # Strip control characters.
  except:    pass
  try:       string = string.encode('ascii', 'replace')        # Encode into Ascii
  except:    pass
  original_string, string, i = string, list(string), 0
  asian_language = False
  while i < len(string):                                       ### loop through unicode and replace special chars with spaces then map if found ###
    if ord(string[i])<128:  i = i+1
    else: #non ascii char
      char, char2, char_list, char_len = 0, "", [], unicodeCharLen(string[i])
      for x in range(0, char_len):
        char = 256*char + ord(string[i+x]); char2 += string[i+x]; char_list.append(string[i+x])
        if x:   string[i] += string[i+x]; string[i+x]=''
      try:
        asian_language = any([mapping["from"] <= x <= mapping["to"] for mapping in ranges for x in char_list])
        Log.info("str: '%s'" % str([mapping["from"] <= x <= mapping["to"] for mapping in ranges for x in char_list]))
      except: asian_language = False
      if char in CHARACTERS_MAP:  string[i]=CHARACTERS_MAP.get( char ); Log.info("*Character remapped in CHARACTERS_MAP: %d:'%s'  , #'%s' %s, string: '%s'" % (char, char2, char2, char_list, original_string))
      elif not asian_language:    Log.warning("*Character missing in CHARACTERS_MAP: %d:'%s'  , #'%s' %s, string: '%s'" % (char, char2, char2, char_list, original_string))
      i += char_len
  return original_string if asian_language else ''.join(string)

### Allow to display ints even if equal to None at times ################################################
def clean_string(string, no_parenthesis=False, no_whack=False, no_dash=False, no_underscore=False):
  if not string: return ""                                                                                                                                    # if empty return empty string
  if no_parenthesis:                                                                                                                                          # delete parts between parenthesis if needed
    while re.match(".*\([^\(\)]*?\).*", string):                 string = re.sub(r'\([^\(\)]*?\)', ' ', string)                                               #   support imbricated parrenthesis like: "Cyborg 009 - The Cyborg Soldier ((Cyborg) 009 (2001))"
  if re.search("(\[|\]|\{|\})", string):                         string = re.sub("(\[|\]|\{|\})", "", re.sub(r'[\[\{](?![0-9]{1,3}[\]\}]).*?[\]\}]', ' ', string))  # remove "[xxx]" groups but ep numbers inside brackets as Plex cleanup keep inside () but not inside [] #look behind: (?<=S) < position < look forward: (?!S)
  if not no_whack:
    for word in WHACK_PRE_CLEAN:                                 string = replace_insensitive(string, word) if word.lower() in string.lower() else string     # Remove words present in pre-clean list
  string = re.sub(r'(?P<a>[^0-9Ssv])(?P<b>[0-9]{1,3})\.(?P<c>[0-9]{1,2})(?P<d>[^0-9])', '\g<a>\g<b>DoNoTfIlTeR\g<c>\g<d>', string)                            # Used to create a non-filterable special ep number (EX: 13.5 -> 13DoNoTfIlTeR5) # Restricvted to max 999.99 # Does not start with a season/special char 'S|s' (s2.03) or a version char 'v' (v1.2)
  for char, subst in zip(list(FILTER_CHARS), [" " for x in range(len(FILTER_CHARS))]) + [("`", "'"), ("(", " ( "), (")", " ) ")]:                             # remove leftover parenthesis (work with code a bit above)
    if char in string:                                           string = string.replace(char, subst)                                                         # translate anidb apostrophes into normal ones #s = s.replace('&', 'and')
  string = string.replace("DoNoTfIlTeR", '.')                                                                                                                 # Replace 13DoNoTfIlTeR5 into 13.5 back
  if re.match(".*?[\(\[\{]?[0-9a-fA-F]{8}[\[\)\}]?.*", string):  string = re.sub('[0-9a-fA-F]{8}', ' ', string)                                               # CRCs removal
  if re.search("[0-9]{3,4} ?[Xx] ?[0-9]{3,4}", string):          string = re.sub('[0-9]{3,4} ?[Xx] ?[0-9]{3,4}', ' ', string)                                 # Video size ratio removal
  if string.endswith(", The"):                                   string = "The " + ''.join( string.split(", The", 1) )                                        # ", The" is rellocated in front
  if string.endswith(", A"  ):                                   string = "A "   + ''.join( string.split(", A"  , 1) )                                        # ", A"   is rellocated in front
  if not no_whack:                                               string = " ".join([word for word in filter(None, string.split()) if word.lower() not in WHACK]).strip()  # remove double spaces + words present in "WHACK" list #filter(None, string.split())
  if no_dash:                                                    string = re.sub("-", " ", string)                                                            # replace the dash '-'
  if no_underscore:                                              string = re.sub("_", " ", string)                                                            # replace the underscore '_'
  string = re.sub(r'\([-Xx]?\)', '', re.sub(r'\( *(?P<internal>[^\(\)]*?) *\)', '(\g<internal>)', string))                                                    # Remove internal spaces in parenthesis then remove empty parenthesis
  string = " ".join([word for word in filter(None, string.split())]).strip()                                                                                  # remove multiple spaces
  for rx in ("-"):                                               string = string[len(rx):   ].strip() if string.startswith(rx)       else string              # In python 2.2.3: string = string.strip(string, " -_") #if string.startswith(("-")): string=string[1:]
  for rx in ("-", "- copy"):                                     string = string[ :-len(rx) ].strip() if string.lower().endswith(rx) else string              # In python 2.2.3: string = string.strip(string, " -_")
  return string

### Add files into Plex database ########################################################################
def add_episode_into_plex(media, file, root, path, show, season=1, ep=1, title="", year=None, ep2="", rx="", tvdb_mapping={}, unknown_series_length=False, offset_season=0, offset_episode=0, mappingList={}):
  # Mapping List 
  ep_orig        = "s{}e{}{}".format(season, ep, "" if not ep2 or ep==ep2 else "-{}".format(ep2))
  ep_orig_single = "s{}e{}".format  (season, ep)
  ep_orig_padded = "s{:>02d}e{:>03d}{}".format(int(season), int(ep), "    " if not ep2 or ep==ep2 else "-{:>03d}".format(int(ep2)))
  if ep_orig_single in mappingList:
    multi_ep   = 0 if ep_orig == ep_orig_single else ep2-ep
    season, ep = mappingList[ep_orig_single][1:].split("e")
    if '-' in ep or  '+' in ep:  ep, ep2 = ep.split("+"); ep2 = int(ep2) if ep2 and ep2.isdigit() else None
    season, ep, ep2 = int(season), int(ep), int(ep)+multi_ep if multi_ep else ep2
  elif 's%d' % season in mappingList and int(mappingList['s%d' % season][0])<=ep and ep<=int(mappingList['s%d' % season][1]):  ep, season = ep + int (mappingList['s%d' % season][2]), int(mappingList['s%d' % season][3])
  elif season > 0:  season, ep, ep2 = season+offset_season if offset_season >= 0 else 0, ep+offset_episode, ep2+offset_episode if ep2 else None
  
  if title==title.lower() or title==title.upper() and title.count(" ")>0: title           = title.title()  # capitalise if all caps or all lowercase and one space at least
  if ep==0:                                                               season, ep, ep2 = 0, 1, 1        # s01e00 and S00e00 => s00e01
  if not ep2 or ep > ep2:                                                 ep2             = ep             #  make ep2 same as ep for loop and tests
  if tvdb_mapping and season > 0 :
    max_ep_num, season_buffer = max(tvdb_mapping.keys()), 0 if unknown_series_length else 1
    if   ep  in tvdb_mapping:               season, ep  = tvdb_mapping[ep ]
    elif ep  > max_ep_num and season == 1:  season      = tvdb_mapping[max_ep_num][0]+season_buffer
    if   ep2 in tvdb_mapping:               season, ep2 = tvdb_mapping[ep2]
    elif ep2 > max_ep_num and season == 1:  season      = tvdb_mapping[max_ep_num][0]+season_buffer
  ep_final = "s%de%d" % (season, ep)
  if not os.path.exists(file):  file = os.path.join(root, path, file)
  filename=os.path.basename(file)
  for epn in range(ep, ep2+1):
    if len(show) == 0: Log.warning("show: '%s', s%02de%03d-%03d, file: '%s' has show empty, report logs to dev ASAP" % (show, season, ep, ep2, file))
    else:
      tv_show, tv_show.display_offset = Media.Episode(show, season, epn, title, year), (epn-ep)*100/(ep2-ep+1)
      if filename.upper()=="VIDEO_TS.IFO":  
        for item in os.listdir(os.path.dirname(file)) if os.path.dirname(file) else []:
          if item.upper().startswith("VTS_01_") and not item.upper()=="VTS_01_2.VOB":  tv_show.parts.append(os.path.join(os.path.dirname(file), item))
      else:  tv_show.parts.append(file)
      media.append(tv_show)   # at this level otherwise only one episode per multi-episode is showing despite log below correct
  index = "SERIES_RX-"+str(SERIES_RX.index(rx)) if rx in SERIES_RX else "ANIDB_RX-"+str(ANIDB_RX.index(rx)) if rx in ANIDB_RX else rx  # rank of the regex used from 0
  Log.info('"{show}" s{season:>02d}e{episode:>03d}{range:s}{before} "{regex}" "{title}" "{file}"'.format(show=show, season=season, episode=ep, range='    ' if not ep2 or ep==ep2 else '-{:>03d}'.format(ep2), before=" (Orig: %s)" % ep_orig_padded if ep_orig!=ep_final else "".ljust(20, ' '), regex=index or '__', title=title if clean_string(title).replace('_', '') else "", file=filename))

### Get the tvdbId from the AnimeId #######################################################################################################################
def anidbTvdbMapping(AniDB_TVDB_mapping_tree, anidbid):
  mappingList                  = {}
  for anime in AniDB_TVDB_mapping_tree.iter('anime') if AniDB_TVDB_mapping_tree else []:
    if anime.get("anidbid") == anidbid and anime.get('tvdbid').isdigit():
      mappingList['episodeoffset'] = anime.get('episodeoffset')
      try:
        for season in anime.iter('mapping'):
          if season.get("offset"):  mappingList[ 's'+season.get("anidbseason")] = [season.get("start"), season.get("end"), season.get("offset"), season.get("tvdbseason")]
          for string2 in filter(None, season.text.split(';')) if season.text else []:  mappingList[ 's'+season.get("anidbseason") + 'e' + string2.split('-')[0] ] = 's' + season.get("tvdbseason") + 'e' + string2.split('-')[1] 
      except: Log.error("anidbTvdbMapping() - mappingList creation exception, mappingList: '%s'" % (str(mappingList)))
      else:   Log.info("anidbTvdbMapping() - anidb: '%s', tvbdid: '%s', defaulttvdbseason: '%s', name: '%s', mappingList: '%s'" % (anidbid, anime.get('tvdbid'), anime.get('defaulttvdbseason'), anime.xpath("name")[0].text, str(mappingList)) )
      return anime.get('tvdbid'), anime.get('defaulttvdbseason'), mappingList
  Log.error("anidbTvdbMapping() - No valid tvbdbid: found for anidbid '%s'" % (anidbid))
  return "", "", {}

### extension, as os.path.splitext ignore leading dots so ".plexignore" file is splitted into ".plexignore" and "" ###
def extension(file):  return file[1:] if file.count('.')==1 and file.startswith('.') else os.path.splitext(file)[1].lstrip('.').lower()
  
### Look for episodes ###################################################################################
def Scan(path, files, media, dirs, language=None, root=None, **kwargs): #get called for root and each root folder, path relative files are filenames, dirs fullpath
  reverse_path = list(reversed(Utils.SplitPath(path)))
  log_filename = path.split(os.sep)[0] if path else '_root_' + root.replace(os.sep, '-')
  #VideoFiles.Scan(path, files, media, dirs, root)  # If enabled does not allow zero size files
    
  ### .plexignore file ###
  plexignore_dirs, plexignore_files, msg, source, id = [], [], [], '', ''
  path_split = [""]+path.split(os.sep) if path else [""]
  for index, dir in enumerate(path_split):                                                   #enumerate to have index, which goes from 0 to n-1 for n items
    
    # Process Subdirectory pattern from previous folder(s)
    for entry in plexignore_dirs[:] if index>0 else []:                                      #
      plexignore_dirs.remove(entry)                                                          #  
      if entry.startswith(dir+'/'):                                                          #
        pattern = entry.replace(dir+'/', '')                                                 #   msg.append("bazinga, pattern.count('/'): '{}', index+1: '{}', len(path_split): '{}', entry: '{}', dir: '{}', pattern: '{}'".format(pattern.count('/'), index+1, len(path_split), entry, dir, pattern))
        if pattern.count('/')>0:        plexignore_dirs.append(pattern)                      # subfolder match so remove subfolder name and carry on
        elif index+1==len(path_split):  plexignore_files.append(fnmatch.translate(pattern));  msg.append("# - pattern: '{}'".format(pattern)) #Only keep pattern for named folder, not subfolders
    
    # Process file patterns
    file = os.path.join(root, os.sep.join(path_split[1:index+1]), '.plexignore')             #
    if os.path.isfile(file):                                                                 #
      msg.append("# " + file)
      msg.append("".ljust(len(file)+ 2, '-'))
      with open(file, 'r') as plexignore:                                                    # open file with auto close
        for pattern in plexignore:                                                           # loop through each line
          pattern = pattern.strip()                                                          # remove useless spaces at both ends
          if pattern == '' or pattern.startswith('#'):  continue                             # skip comment and emopy lines, go to next for iteration
          msg.append("# - " + pattern)
          if '/' not in pattern:  plexignore_files.append(fnmatch.translate(pattern))        # patterns for this folder and subfolders gets converted and added to files.
          elif pattern[0]!='/':   plexignore_dirs.append (pattern)                           # patterns for subfolders added to folders
        msg.append(''.ljust(157, '-'))
        
  ### bluray/DVD folder management ### # source: https://github.com/doublerebel/plex-series-scanner-bdmv/blob/master/Plex%20Series%20Scanner%20(with%20disc%20image%20support).py
  if len(reverse_path) >= 3 and reverse_path[0].lower() == 'stream' and reverse_path[1].lower() == 'bdmv' or "VIDEO_TS.IFO" in str(files).upper():
    for temp in ['stream', 'bdmv', 'video_ts']:
      if reverse_path[0].lower() == temp:  reverse_path.pop(0)
    ep, disc = clean_string(reverse_path[0], True), True
    if len(reverse_path)>1:  reverse_path.pop(0)  #Log.info("BluRay/DVD folder detected - using as equivalent to filename ep: '%s', show: '%s'" % (ep, reverse_path[0]))
  else: disc = False
  
  ### Extract season folder to reduce complexity and use folder as serie name ###
  folder_season, season_folder_first =  None, False
  for folder in reverse_path[:-1]:                 # remove root folder from test, [:-1] Doesn't thow errors but gives an empty list if items don't exist, might not be what you want in other cases
    for rx in SEASON_RX:                                # in anime, more specials folders than season folders, so doing it first
      match = re.match(rx, folder, re.IGNORECASE)  #
      if match:                                         # get season number but Skip last entry in seasons (skipped folders)
        if rx!=SEASON_RX[-1]: 
          folder_season = int( match.group('season')) if match.groupdict().has_key('season') and match.group('season') else 0 #break
          if len(reverse_path)>=2 and folder==reverse_path[-2]:  season_folder_first = True
        reverse_path.remove(folder)                # Since iterating slice [:] or [:-1] doesn't hinder iteration. All ways to remove: reverse_path.pop(-1), reverse_path.remove(thing|array[0])
        ### YouTube playlist on season folder
        #match = re.search('\[((?P<source>(anidb|anidb2|tvdb|tvdb2|tvdb3|tvdb4|tvdb5|tmdb|tsdb|imdb|youtube))-)?(?P<id>PL[^\[\]]*)\]', folder, re.IGNORECASE)
        #if match:
        #  id     = match.group('id'    ) if match.groupdict().has_key('id'    ) and match.group('id'    ) else '' 
        #  source = match.group('source') if match.groupdict().has_key('source') and match.group('source') else 'YouTube'
        break
    if not kwargs and len(reverse_path)>1 and path.count(os.sep):  return       #if not grouping folder scan, skip grouping folder
  
  ### Create *.filelist.log file ###
  set_logging(foldername=PLEX_LIBRARY[root] if root in PLEX_LIBRARY else '', filename=log_filename+'.filelist.log', mode='w') #add grouping folders filelist
  Log.info("".ljust(157, '='))
  Log.info("Library: '{}', root: '{}', path: '{}', files: '{}', dirs: '{}', {} scan date: {}".format(PLEX_LIBRARY[root] if root in PLEX_LIBRARY else "no valid X-Plex-Token.id", root, path, len(files or []), len(dirs or []), "Manual" if kwargs else "Plex", time.strftime("%Y-%m-%d %H:%M:%S")))
  Log.info("plexignore_files: '{}', plexignore_dirs: '{}'".format(plexignore_files, plexignore_dirs))
  Log.info("".ljust(157, '='))

  ### Remove directories un-needed (mathing IGNORE_DIRS_RX) ###
  for subdir in dirs:
    for rx in IGNORE_DIRS_RX:
      if re.match(rx, os.path.basename(subdir), re.IGNORECASE):
        dirs.remove(subdir)
        Log.info("# Folder: '{}' match '{}' pattern: '{}'".format(os.path.relpath(subdir, root), 'IGNORE_DIRS_RX', rx))
        break  #skip dirs to be ignored
    else:  Log.info("[folder] " + os.path.relpath(subdir, root))
  
  ### Remove files un-needed (ext not in VIDEO_EXTS, mathing IGNORE_FILES_RX or .plexignore pattern) ###
  for entry in msg:  Log.info(entry)
  for file in sorted(files or [], key=natural_sort_key):  #sorted create list copy allowing deleting in place
    ext = file[1:] if file.count('.')==1 and file.startswith('.') else os.path.splitext(file)[1].lstrip('.').lower()  # Otherwise ".plexignore" file is splitted into ".plexignore" and ""
    if ext in VIDEO_EXTS:
      for rx in IGNORE_FILES_RX + plexignore_files:  # Filter trailers and sample files
        if re.match(rx, os.path.basename(file), re.IGNORECASE):
          Log.info("# File: '{}' match '{}' pattern: '{}'".format(os.path.relpath(file, root), 'IGNORE_FILES_RX' if rx in IGNORE_FILES_RX else '.plexignore', rx))
          files.remove(file)
          break
      else:
        try:                    Log.info("[file] " + os.path.relpath(file, root))
        except Exception as e:  Log.info('exception: {}, file: {}, root: {}'.format(e, file, root))
    else:
      files.remove(file)
      Log.info("# File: '{}' not in '{}'".format(os.path.relpath(file, root), 'VIDEO_EXTS'))
      
      ### ZIP ###
      if ext == 'zip':
        Log.info(file)
        zip_archive = zipfile.ZipFile(file)
        for zip_archive_filename in zip_archive.namelist():
          zname, zext = os.path.splitext(zip_archive_filename)
          zext        = zext[1:]
          if zext in VIDEO_EXTS:
            files.append( zip_archive_filename)  #filecontents = zip_archive.read(zip_archive_filename)
            Log.info('- '+zip_archive_filename) 
      
      ### 7zip ###
      ### RAR ###
      #import rarfile  https://rarfile.readthedocs.io/en/latest/api.html
      #rar_archive = rarfile.RarFile('myarchive.rar')
      #for rar_archive_filename in rar_archive.infolist():
      #  zname, zext = os.path.splitext(rar_archive_filename.filename); zext = zext[1:]
      #  if zext in VIDEO_EXTS:  files.append(rar_archive_filename.filenamee)  #filecontents = rar_archive.read(rar_archive_filename)
      
  if not files:
    Log.info("[no files detected]")
    if path:  return  #Grouping folders could call subfolders so cannot return if path is empty aka for root call
  Log.info("")
  
  ### Logging to *.scanner.log ###
  global LOG_FILE
  recent = os.stat(LOG_FILE[:-len('.filelist.log')]+'.scanner.log').st_mtime + 3600 > time.time() if os.path.exists(LOG_FILE[:-len('.filelist.log')]+'.scanner.log') else False
  set_logging(foldername=PLEX_LIBRARY[root] if root in PLEX_LIBRARY else '', filename=log_filename+'.scanner.log', mode='a' if recent else 'w') #if recent or kwargs else 'w'
  Log.info("".ljust(157, '='))
  Log.info("Library: '{}', root: '{}', path: '{}', files: '{}', dirs: '{}', {} scan date: {}".format(PLEX_LIBRARY[root] if root in PLEX_LIBRARY else "no valid X-Plex-Token.id", root, path, len(files or []), len(dirs or []), "Manual" if kwargs else "Plex", time.strftime("%Y-%m-%d %H:%M:%S")))
  Log.info("".ljust(157, '='))
  
  #### Folders, Forced ids, grouping folders ###
  folder_show  = reverse_path[0] if reverse_path else ""
  misc_words, misc_count = [], {}
  tvdb_mapping, unknown_series_length, tvdb_mode_search = {}, False, re.search(TVDB_MODE_IDS, folder_show, re.IGNORECASE)
  mappingList, offset_season, offset_episode            = {}, 0, 0
  
  if path:
    
    #### Grouping folders skip , unless single series folder ###
    if not kwargs and len(reverse_path)>1 and not season_folder_first:  
      parent_dir = os.path.dirname(os.path.join(root, path))
      parent_dir_nb= len([file for dir in os.listdir(parent_dir) if os.path.isdir(os.path.join(parent_dir, dir))])
      if parent_dir_nb>1:  return  #Grouping folders Plex call, but mess after one season folder is ok
  
    ### Forced guid modes ###
    guid=""
    match = re.search(SOURCE_IDS, folder_show, re.IGNORECASE)
    if not match and len(reverse_path)>1:  match = re.search('(.* )?\[((?P<source>(|youtube))-)?(?P<id>.*)\]', reverse_path[1], re.IGNORECASE)
    if source or id:
      Log.info("Forced ID in season folder: '{}' with id '{}' in series folder".format(source, id))
    elif match:
      id     = match.group('id'    ) if match.groupdict().has_key('id'    ) and match.group('id'    ) else '' 
      source = match.group('source') if match.groupdict().has_key('source') and match.group('source') else 'youtube' 
      Log.info("Forced ID in series folder: '{}' with id '{}'".format(source, id))
    else:
      for file in SOURCE_ID_FILES:
        if os.path.isfile(os.path.join(root, os.sep.join(list(reversed(reverse_path))), file)):
          with open(os.path.join(root, os.sep.join(list(reversed(reverse_path))), file), 'r') as guid_file:
            source = file.rstrip('.id')
            id     = guid_file.read().strip()
            Log.info("Forced Series folder ID file: '{}' with id '{}'".format(file, id))
            folder_show = "%s [%s-%s]" % (clean_string(reverse_path[0]), os.path.splitext(file)[0], id)
          break
      else:
        Log.info('No forced guid found in folder name nor id file')
        source, id = "", ""
        folder_show = folder_show.replace(" - ", " ").split(" ", 2)[2] if folder_show.lower().startswith(("saison","season","series","Book","Livre")) and len(folder_show.split(" ", 2))==3 else clean_string(folder_show) # Dragon Ball/Saison 2 - Dragon Ball Z/Saison 8 => folder_show = "Dragon Ball Z"
    
    if source.startswith('tvdb'):
      
      ### Calculate offset for season or episode ###
      offset_match = re.search(TVDB_MODE_ID_OFFSET, folder_show, re.IGNORECASE)
      if offset_match:
        source, match_season, match_episode = offset_match.group('source'), "", ""
        if offset_match.groupdict().has_key('season' ) and offset_match.group('season' ):  match_season,  offset_season  = offset_match.group('season' ), int(offset_match.group('season' )[1:])-1
        if offset_match.groupdict().has_key('episode') and offset_match.group('episode'):  match_episode, offset_episode = offset_match.group('episode'), int(offset_match.group('episode')[1:])-1
        if tvdb_mapping and match_season!='s0': 
          season_ep1      = min([e[1] for e in tvdb_mapping.values() if e[0] == offset_season+1]) if source in ['tvdb3','tvdb4'] else 1
          offset_episode += list(tvdb_mapping.keys())[list(tvdb_mapping.values()).index((offset_season+1,season_ep1))] - 1
        folder_show = folder_show.replace("-"+match_season+match_episode+"]", "]")
        if offset_season+offset_episode:  Log.info("offset_season = %s, offset_episode = %s" % (offset_season, offset_episode))

      #tvdb2, tvdb3 - Absolutely numbered serie displayed with seasons with episodes re-numbered (tvdb2) or staying absolute (tvdb3, for long running shows without proper seasons like dbz, one piece)
      if source in ('tvdb2', 'tvdb3'): 
        Log.info("TVDB season mode ({}) enabled".format(source))
        try:
          global HEADERS
          if 'Authorization' in HEADERS:  Log.info('authorised, HEADERS: {}'.format(HEADERS))   #and not timed out
          else:                    
            Log.info('not authorised, HEADERS: {}'.format(HEADERS))
            page = urlopen(Request("https://api.thetvdb.com/login", headers=HEADERS), data=json.dumps({"apikey": "A27AD9BE0DA63333"}), context=SSL_CONTEXT).read()
            HEADERS['Authorization'] = 'Bearer ' + json.loads(page)['token'];  Log.info('not authorised, HEADERS: {}'.format(HEADERS))
          
          #Load series episode pages and group them in one dict
          episodes_json, page = [], 1
          while page not in (None, '', 'null'):
            episodes_json_page = json.loads(urlopen(Request('https://api.thetvdb.com/series/{}/episodes?page={}'.format(id, page), headers=HEADERS), context=SSL_CONTEXT).read())
            episodes_json.extend(episodes_json_page['data'] if 'data' in episodes_json_page else [])  #Log.Info('TVDB_EPISODES_URL: {}, links: {}'.format(TVDB_EPISODES_URL % (TVDBid, page), Dict(episodes_json_page, 'links')))
            page = Dict(episodes_json_page, 'links', 'next')
          
          # SORT JSON EPISODES
          sorted_episodes_json = {}
          for episode_json in episodes_json: sorted_episodes_json['s{:02d}e{:03d}'.format(Dict(episode_json, 'airedSeason'), Dict(episode_json, 'airedEpisodeNumber'))] = episode_json
          sorted_episodes_index_list = sorted(sorted_episodes_json, key=natural_sort_key)  #Log.Info('len: {}, sorted_episodes_index_list: {}'.format(len(sorted_episodes_index_list), sorted_episodes_index_list))
          
          # Loop through sorted episodes list
          absolute_number, tvdb_mapping = 0, {}
          for index in sorted_episodes_index_list:
            if Dict(sorted_episodes_json[index], 'airedSeason')>0: #continue
              absolute_number = absolute_number + 1
              tvdb_mapping[int(absolute_number)] = (Dict(sorted_episodes_json[index], 'airedSeason'), Dict(sorted_episodes_json[index], 'airedEpisodeNumber') if source =='tvdb2' else int(absolute_number))

        except Exception as e:  Log.error("json loading issue, Exception: %s" % e)

      #tvdb4 - Absolute numbering in any season arrangements aka saga mode
      elif source=='tvdb4' and folder_season==None:  #1-folders nothing to do, 2-local, 3-online
        try:
          url = os.path.join(root, path, "tvdb4.mapping")
          if   os.path.isfile(url):  tvdb4_mapping_content = open(url).read().strip();  Log.info("TVDB4 local file missing: '%s'" % url)
          else:
            url                   = ASS_MAPPING_URL
            tvdb4_anime           = etree.fromstring( urlopen(url, context=SSL_CONTEXT).read().strip() )
            tvdb4_mapping_content = tvdb4_anime.xpath("/tvdb4entries/anime[@tvdbid='%s']" % id)[0].text.strip()
          Log.info("TVDB season mode (%s) enabled, tvdb4 mapping url: '%s'" % (id, url))
          for line in filter(None, tvdb4_mapping_content.replace("\r","\n").split("\n")):
            season = line.strip().split("|")
            for absolute_episode in range(int(season[1]), int(season[2])+1):  tvdb_mapping[absolute_episode] = (int(season[0]), int(absolute_episode)) 
            if "(unknown length)" in season[3].lower(): unknown_series_length = True
        except Exception as e:
          tvdb_mapping, tvdb4_mapping_content = {}, "" 
          if str(e) == "list index out of range":  Log.error("tvdbid: '%s' not found in online season mapping file" % id)
          else:                                    Log.error("Error opening url '%s', Exception: '%s'" % (url, e))
        
      #tvdb5 - 'Star wars: Clone attack' chronological order, might benefit other series
      elif source=='tvdb5': ##S
        Log.info("TVDB season mode (%s) enabled, tvdb serie rl: '%s'" % (source, TVDB_HTTP_API_URL % id))
        id_url= TVDB_HTTP_API_URL % id
        try:
          tvdbanime = etree.fromstring( urlopen(tvdb_guid_url, context=SSL_CONTEXT).read() )
          for episode in tvdbanime.xpath('Episode'):
            if episode.xpath('SeasonNumber')[0].text != '0' and episode.xpath('absolute_number')[0].text:
              mappingList['s%se%s'%(episode.xpath('SeasonNumber')[0].text, episode.xpath('EpisodeNumber')[0].text)] = "s1e%s" % episode.xpath('absolute_number')[0].text
          Log.info("mappingList: '%s'" % str(mappingList))
        except Exception as e:  Log.error("xml loading issue, Exception: '%s''" % e)
      
      if tvdb_mapping:  Log.info("unknown_series_length: %s, tvdb_mapping: %s (showing changing seasons/episodes only)" % (unknown_series_length, str({x:tvdb_mapping[x] for x in tvdb_mapping if tvdb_mapping[x]!=(1,x)})))  #[for x in tvdb_mapping if tvdb_mapping[x]!=(1,x)]
      Log.info("".ljust(157, '-'))
        
    ### forced guid modes - anidb2 (requires ScudLee's mapping xml file) ###
    anidb2_match = re.search(ANIDB2_MODE, folder_show, re.IGNORECASE)
    a2_tvdbid, a2_defaulttvdbseason, scudlee_mapping_content = "", "", None
    if anidb2_match:
      
      # Local custom mapping file
      anidb_id, dir = anidb2_match.group('guid').lower(), os.path.join(root, path)
      while dir and os.path.splitdrive(dir)[1] != os.sep:
        scudlee_filename_custom = os.path.join(dir, ANIDB_TVDB_MAPPING_CUSTOM)
        if os.path.exists( scudlee_filename_custom ):
          with open(scudlee_filename_custom, 'r') as scudlee_file:
            try:     scudlee_mapping_content = etree.fromstring( scudlee_file.read() )
            except:  Log.info("Invalid local custom mapping file content")
            else:
              Log.info("Loading local custom mapping from local: %s" % scudlee_filename_custom)
              a2_tvdbid, a2_defaulttvdbseason, mappingList = anidbTvdbMapping(scudlee_mapping_content, anidb_id)
              break
        dir = os.path.dirname(dir)

      # Online mod mapping file = ANIDB_TVDB_MAPPING_MOD 
      if not a2_tvdbid:
        tmp_file         = tempfile.NamedTemporaryFile(delete=False); tmp_filename = tmp_file.name; tmp_file.close()
        scudlee_filename = tmp_filename.replace(os.path.basename(tmp_filename), 'anime-list-corrections.xml')
        try:
          if os.path.exists(scudlee_filename) and int(time.time() - os.path.getmtime(scudlee_filename)) <= 86400:
            Log.info("Use existing: '%s'" % scudlee_filename)
            del tmp_file
            with open(scudlee_filename, 'r') as scudlee_file:  scudlee_file_content = scudlee_file.read()
          else:
            Log.info("Updating: '%s' from '%s'" % (scudlee_filename, ANIDB_TVDB_MAPPING_MOD) if os.path.exists(scudlee_filename) else "Creating: "+ scudlee_filename)
            with open(tmp_filename, 'w') as scudlee_file:
              scudlee_file_content = urlopen(ANIDB_TVDB_MAPPING_MOD, context=SSL_CONTEXT).read()
              scudlee_file.write( scudlee_file_content )
            if os.path.exists(scudlee_filename): os.remove(scudlee_filename)
            os.rename(tmp_filename, scudlee_filename)
        except Exception as e:  Log.error("Error downloading ASS's file mod from local/GitHub '%s', Exception: '%s'" % (ANIDB_TVDB_MAPPING_MOD, e)) 
        else:
          try:                    a2_tvdbid, a2_defaulttvdbseason, mappingList = anidbTvdbMapping(etree.fromstring( scudlee_file_content ), anidb_id)
          except Exception as e:  Log.error("Error parsing ASS's file mod content, Exception: '%s'" % e)
      
      #ANIDB_TVDB_MAPPING
      if not a2_tvdbid:
        tmp_file         = tempfile.NamedTemporaryFile(delete=False); tmp_filename = tmp_file.name; tmp_file.close()
        scudlee_filename = tmp_filename.replace(os.path.basename(tmp_filename), 'ASS-tmp-anime-list-master.xml')
        try:
          if os.path.exists(scudlee_filename) and int(time.time() - os.path.getmtime(scudlee_filename)) <= 86400:
            Log.info("Use existing: '%s'" % scudlee_filename)
            del tmp_file
            with open(scudlee_filename, 'r') as scudlee_file:  scudlee_file_content = scudlee_file.read()
          else:
            Log.info("Updating: '%s' from '%s'" % (scudlee_filename, ANIDB_TVDB_MAPPING) if os.path.exists(scudlee_filename) else "Creating: "+ scudlee_filename)
            with open(tmp_filename, 'w') as scudlee_file:
              scudlee_file_content = urlopen(ANIDB_TVDB_MAPPING, context=SSL_CONTEXT).read()
              scudlee_file.write( scudlee_file_content )
            if os.path.exists(scudlee_filename): os.remove(scudlee_filename)
            os.rename(tmp_filename, scudlee_filename)
        except Exception as e:  Log.error("Error downloading ScudLee's file from local/GitHub '%s', Exception: '%s'" % (ANIDB_TVDB_MAPPING, e))
        else:
          try:                    a2_tvdbid, a2_defaulttvdbseason, mappingList = anidbTvdbMapping(etree.fromstring(scudlee_file_content), anidb_id)
          except Exception as e:  Log.error("Error parsing ScudLee's file content, Exception: '%s'" % e)
          
      #Build AniDB2 Offsets
      if a2_tvdbid:
        folder_show    = clean_string(folder_show)+" [tvdb-%s]" % a2_tvdbid
        offset_season  = int(a2_defaulttvdbseason)-1 if a2_defaulttvdbseason and a2_defaulttvdbseason.isdigit() else 0
        if 'episodeoffset' in mappingList and mappingList['episodeoffset']:  offset_episode = 0-int(mappingList['episodeoffset'][1:]) if mappingList['episodeoffset'].startswith('-') else int(mappingList['episodeoffset'])
        else:                                                                offset_episode = 0
      Log.info("".ljust(157, '-'))
    
    ### Youtube ###
    def getmtime(name):  return os.path.getmtime(os.path.join(root, path, name))
    if source.startswith('youtube') and id.startswith('PL'):
      try:
        with open(os.path.join(PLEX_ROOT, 'Plug-in Support', 'Preferences', 'com.plexapp.agents.youtube.xml'), 'r') as file:
          xml = etree.fromstring( file.read() )
          API_KEY = xml.xpath("/PluginPreferences/yt_apikey")[0].text.strip()
        Log.info("API_KEY: '{}'".format(API_KEY))
      except Exception as e:  Log.info('exception: {}'.format(e)); API_KEY='AIzaSyC2q8yjciNdlYRNdvwbb7NEcDxBkv1Cass'
      
      YOUTUBE_PLAYLIST_ITEMS = 'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50&playlistId={}&key='+API_KEY
      iteration, json_full, json_page = 0, {}, {'nextPageToken': None}
      while 'nextPageToken' in json_page and iteration <= 20:
        url=YOUTUBE_PLAYLIST_ITEMS.format(id)+( '&pageToken='+Dict(json_full, 'nextPageToken') if Dict(json_page, 'nextPageToken') else '')
        Log.info('[{:>2}] {}'.format(iteration, url))
        try:                                  json_page = json.loads(urlopen(url, context=SSL_CONTEXT).read())
        except Exception as e:                json_page={};  Log.info('exception: {}, url: {}'.format(e, url))
        else:
          if json_full:  json_full['items'].extend(json_page['items'])
          else:          json_full = json_page
        iteration +=1
      Log.info('---- count: {}'.format(len(json_full['items'])))
      
      if json_full:
        for file in os.listdir(os.path.join(root, path)):
          if extension(file) not in VIDEO_EXTS or os.path.isdir(os.path.join(root, path, file)):
            continue  #files only with video extensions
          for rank, video in enumerate(Dict(json_full, 'items') or {}, start=1):
            VideoID = video['snippet']['resourceId']['videoId']
            if VideoID and VideoID in file.decode('utf-8'):
              #Log.info('[{}] rank: {:>3} in file: {}'.format(VideoID, rank, file))
              add_episode_into_plex(media, os.path.join(root, path, file), root, path, folder_show, int(folder_season if folder_season is not None else 1), rank, video['snippet']['title'].encode('utf8'), "", rank, 'YouTube', tvdb_mapping, unknown_series_length, offset_season, offset_episode, mappingList)
              break
          else:  Log.info('None of video IDs found in filename: {}'.format(file))
        return  
      else:  Log.info('json_full is empty')
    files_per_date = []
    if id.startswith('UC'):
      files_per_date = sorted(os.listdir(os.path.join(root, path)), key=getmtime, reverse=True)
      Log.info('files_per_date: {}'.format(files_per_date))
      
    ### Build misc variable to check numbers in titles ###
    misc, misc_words, misc_count = "|", (), {} # put all filenames in folder in a string to count if ep number valid or present in multiple files ###clean_string was true ###
    array = ()
    length=0
    files.sort(key=natural_sort_key)
    if folder_show:
      array = (folder_show, clean_string(folder_show), clean_string(folder_show, True), clean_string(folder_show, no_dash=True), clean_string(folder_show, True, no_dash=True))
      for file in files:                     # build misc variable, to avoid numbers in titles if present in multiple filenames
        length2=len(os.path.basename(file))  # http://stackoverflow.com/questions/29776299/aligning-japanese-characters-in-python
        if length<length2: length = length2  # max len longest - dirname(file)
        for prefix in array:                 # remove cleansed folder name from cleansed filename and remove potential space
          if prefix.lower() in file.lower():  misc+= clean_string(os.path.basename(file).lower().replace(prefix.lower(), " "), True)+"|"; break
        else:   misc+= clean_string(os.path.basename(file), True)+"|"
      for separator in [' ', '.', '-', '_']:  misc = misc.replace(separator, '|') 
      misc = "|".join([s for s in misc.split('|') if s])  #Log.info("misc: '%s'" % misc)
      for item in misc.split('|'):  misc_count[item] = misc_count[item]+1 if item in misc_count else 1
      for item in misc_count:
        if item and (misc_count[item] >= len(files) and len(files)>=6 or misc_count[item]== max(misc_count.values()) and max(misc_count.values())>3 ):  misc_words = misc_words + (item,)
        misc = misc.replace("|%s|" % item, '|')  #Log.info("misc_words: '%s', misc_count: '%s'" % (str(misc_words), str(misc_count)))
      Log.info('misc_count: {}'.format(misc_count))
  
  ### File main loop ###
  counter = 500
  for file in files:
    show, season, ep2, title, year = folder_show, folder_season if folder_season is not None else 1, None, "", ""
    ext = file[1:] if file.count('.')==1 and file.startswith('.') else os.path.splitext(file)[1].lstrip('.').lower()  # Otherwise ".plexignore" file is splitted into ".plexignore" and ""
    if ext not in VIDEO_EXTS:  continue
    
    #DVD/BluRay folders
    if ext=="ifo" and not file.upper()=="VIDEO_TS.IFO":  continue
    if disc:  filename = ep
    else:
      filename = os.path.splitext(os.path.basename(file))[0]
      encodeASCII(filename)
    
    ### remove cleansed folder name from cleansed filename or keywords otherwise ###
    if path:
      if clean_string(filename, True,no_dash=True)==clean_string(folder_show, True, no_dash=True):  ep, title  = "01", folder_show                  ### If a file name matches the folder name, place as episode 1
      else:
        for prefix in array:
          if prefix.lower() in filename.lower():  filename = clean_string(filename.lower().replace(prefix.lower(), " "), True); break
        else:
          filename = clean_string(filename, False)
          for item in misc_words:  filename = filename.lower().replace(item, ' ', 1)
    else:  filename     = clean_string(filename, False)
    ep = filename
    if not path and " - Complete Movie" in ep:  ep, title, show = "01", ep.split(" - Complete Movie")[0], ep.split(" - Complete Movie")[0];   ### Movies ### If using WebAOM (anidb rename) and movie on root
    elif len(files)==1 and (not re.search("\d+(\.\d+)?", clean_string(filename, True)) or "-m" in folder_show.split()):
      ep, title = "01", folder_show  #if  ("movie" in ep.lower()+folder_show.lower() or "gekijouban" in folder_show.lower()) or "-m" in folder_show.split():  ep, title,      = "01", folder_show                  ### Movies ### If only one file in the folder & contains '(movie|gekijouban)' in the file or folder name
    if folder_show and folder_season >= 1:                                                                                                                                         # 
      for prefix in ("s%d" % folder_season, "s%02d" % folder_season):                                                         #"%s %d " % (folder_show, folder_season), 
        if prefix in ep.lower() or prefix in misc_count and misc_count[prefix]>1:  ep = replace_insensitive(ep, prefix , "").lstrip()   # Series S2  like transformers (bad naming)  # Serie S2  in season folder, Anidb specials regex doesn't like
    if folder_show and ep.lower().startswith("special") or "omake" in ep.lower() or "picture drama" in ep.lower():  season, title = 0, ep.title()                        # If specials, season is 0 and if title empty use as title ### 
    
    ### YouTube Channel numbering ###
    if source.startswith('youtube') and id.startswith('UC'):
      filename = os.path.basename(file)
      folder_season = time.gmtime(os.path.getmtime(os.path.join(root, path, filename)) )[0]
      ep            = files_per_date.index(filename)+1 if filename in files_per_date else 0
      add_episode_into_plex(media, os.path.join(root, path, filename), root, path, folder_show if id in folder_show else folder_show+'['+id+']', int(folder_season if folder_season is not None else 1), ep, filename, folder_season, ep, 'YouTube', tvdb_mapping, unknown_series_length, offset_season, offset_episode, mappingList)
      continue
      
    ### Date Regex ###
    #DATE_RX
    #match = re.search(rx, ep, re.IGNORECASE)
    for r in DATE_RX:
      if re.search(r, ep):
        year  = int(match.group('year' ))
        month = int(match.group('month'))
        day   = int(match.group('day'  ))
        Log.Info('year: {}, mont: {}, day: {}, ep: {}, file: {}'.format(year, month, day, ep, file))
        continue
        # Use the year as the season.
        #tv_show = Media.Episode(show, year, None, None, None)
        #tv_show.released_at = '%d-%02d-%02d' % (year, month, day)
        #tv_show.parts.append(i)
        #mediaList.append(tv_show)
           
    ### Word search for ep number in scrubbed title ###
    words, loop_completed, rx = filter(None, ep.split()), False, "Word Search"                                                                                                         #
    for word in words:                                                                                                                                              #
      ep=word.lower().strip()                                                                                                                                       # cannot use words[words.index(word)] otherwise# if word=='': continue filter prevent "" on double spaces
      for prefix in ["ep", "e", "act", "s"]:                                                                                                                        #
        if ep.startswith(prefix) and len(ep)>len(prefix) and re.match("^\d+(\.\d+)?$", ep[len(prefix):]):
          #Log.info('misc_count[word]: {}, filename.count(word)>=2: {}'.format(misc_count[word] if word in misc_count else 0, filename.count(word)))
          ep, season = ep[len(prefix):], 0 if prefix=="s" and (word not in misc_count or filename.count(word)==1 and misc_count[word]==1 or filename.count(word)>=2 and misc_count[word]==2) else season  # E/EP/act before ep number ex: Trust and Betrayal OVA-act1 # to solve s00e002 "Code Geass Hangyaku no Lelouch S5 Picture Drama 02 'Stage 3.25'.mkv" "'Stage 3 25'"
      if ep.endswith(("v1", "v2", "v3", "v4", "v5")):                                                          ep=ep[:-2].rstrip('-')                               #
      if '-' in ep and len(filter(None, ep.split('-',1)))==2:                                                                                                       # If separator in string
        if re.match("^(?P<ep>[0-9]{1,3})-(?P<ep2>[0-9]{1,3})$", ep, re.IGNORECASE):                            ep, ep2 = ep.split('-'); break
        if re.match("^(ep?[ -]?)?(?P<ep>[0-9]{1,3})(-|ep?|-ep?)(?P<ep2>[0-9]{1,3})", ep, re.IGNORECASE):       ep="Skip"; break                                     # if multi ep: make it non digit and exit so regex takes care of it
        elif path and ( (misc.count(ep)==1 and len(files)>=2) or ep not in clean_string(folder_show, True).lower().split() ):
          ep = ep.split('-',1)[0] if ''.join(letter for letter in ep.split('-',1)[0] if letter.isdigit()) else ep.split('-',1)[1];                                  # otherwise all after separator becomes word#words.insert(words.index(word)+1, "-".join(ep.split("-",1)[1:])) #.insert(len(a), x) is equivalent to a.append(x). #???
        else:                                                                                                  continue
      if re.match("((t|o)[0-9]{1,3}$|(sp|special|oav|op|ncop|opening|ed|nced|ending|trailer|promo|pv|others?)($|[0-9]{1,3}$))", ep):  break                         # Specials go to regex # 's' is ignored as dealt with later in prefix processing # '(t|o)' require a number to make sure a word is not accidently matched
      if ''.join(letter for letter in ep if letter.isdigit())=="":                                             continue                                             # Continue if there are no numbers in the string
      if path and ep in misc_count.keys() and misc_count[ep]>=2:                                               continue                                             # Continue if not root folder and string found in in any other filename
      if ep in clean_string(folder_show, True).split() and clean_string(filename, True).split().count(ep)!=2:  continue                                             # Continue if string is in the folder name & string is not in the filename only twice
      if   ep.isdigit() and len(ep)==4 and (int(ep)< 1900 or folder_season and int(ep[0:2])==folder_season):   season, ep = int(ep[0:2]), ep[2:4]                   # 1206 could be season 12 episode 06  #Get assigned from left ot right
      elif ep.isdigit() and len(ep)==4:  filename = clean_string( " ".join(words).replace(ep, "(%s)" % ep));   continue                                             # take everything after supposed episode number
      if "." in ep and ep.split(".", 1)[0].isdigit() and ep.split(".")[1].isdigit():                           season, ep, title = 0, ep.split(".", 1)[0], "Special " + ep; break # ep 12.5 = "12" title "Special 12.5"
      if not path  and not " - Complete Movie" in file:  show = clean_string( " ".join(words[:words.index(word)]) if words.index(word)>0 else "No title", False)    # root folder and 
      title = clean_string( " ".join(words[words.index(word):])[" ".join(words[words.index(word):]).lower().index(ep)+len(ep):] )                                   # take everything after supposed episode number
      break
    else:  loop_completed = True
    if not loop_completed and ep.isdigit():
      add_episode_into_plex(media, file, root, path, show, season, int(ep), title, year, int(ep2) if ep2 and ep2.isdigit() else None, rx, tvdb_mapping, unknown_series_length, offset_season, offset_episode, mappingList)
      continue

    ### Check for Regex: SERIES_RX + ANIDB_RX ###
    movie_list, AniDB_op, ep = {}, {}, filename
    for rx in SERIES_RX + ANIDB_RX:
      match = re.search(rx, ep, re.IGNORECASE)
      if match:
        if match.groupdict().has_key('show'  ) and match.group('show'  ) and not path:  show   = clean_string( match.group('show' ))  # Mainly if file at root or _ folder
        if match.groupdict().has_key('title' ) and match.group('title' ):               title  = clean_string( match.group('title'))
        if match.groupdict().has_key('season') and match.group('season'):               season = int(match.group('season'))
        if match.groupdict().has_key('ep2'   ) and match.group('ep2'   ):               ep2    = match.group('ep2') 
        if match.groupdict().has_key('ep'    ) and match.group('ep'    ):               ep     = match.group('ep')
        elif rx in ANIDB_RX[:-2] or rx == ANIDB_RX[-1]:                                 ep     = "01"
        else:                                                                                                                                                   #No ep number, anidb usefull ?????
          movie_list[season] = movie_list[season]+1 if season in movie_list else 1                                                                              # if no ep in regex and anidb special#add movies using year as season, starting at 1  # Year alone is season Year and ep incremented, good for series, bad for movies but cool for movies in series folder...
          ep                 = str(movie_list[season])
        if rx in ANIDB_RX[:-2] or rx == ANIDB_RX[-1]:                                                                                                           ### AniDB Specials ################################################################
          offset, season = ANIDB_OFFSET [ ANIDB_RX.index(rx) ], 0                                                                                               # offset = 100 for OP, 150 for ED, etc... #Log.info("ep: '%s', rx: '%s', file: '%s'" % (ep, rx, file))
          if not ep.isdigit() and len(ep)>1 and ep[:-1].isdigit():                                                                                              ### OP/ED with letter version Example: op2a
            AniDB_op [ offset + int(ep[:-1]) ] = ord( ep[-1:].lower() ) - ord('a')                                                                              # {101: 0 for op1a / 152: for ed2b} and the distance between a and the version we have hereep, offset                         = str( int( ep[:-1] ) ), offset + sum( AniDB_op.values() )                             # "if xxx isdigit() else 1" implied since OP1a for example... # get the offset (100, 150, 200, 300, 400) + the sum of all the mini offset caused by letter version (1b, 2b, 3c = 4 mini offset)
            ep, offset                         = int( ep[:-1] ), offset + sum( AniDB_op.values() )                                                       # "if xxx isdigit() else 1" implied since OP1a for example... # get the offset (100, 150, 200, 300, 400) + the sum of all the mini offset caused by letter version (1b, 2b, 3c = 4 mini offset)
          if offset == 100 and not(match.groupdict().has_key('title' ) and match.group('title' )):  title = "Opening " + str(int(ep))                           # Dingmatt fix for opening with just the ep number
          if offset == 150 and not(match.groupdict().has_key('title' ) and match.group('title' )):  title = "Ending "  + str(int(ep))                           # Dingmatt fix for ending  with just the ep number
          ep = offset + int(ep) 
        add_episode_into_plex(media, file, root, path, show, int(season), int(ep), title, year, int(ep2) if ep2 and ep2.isdigit() else int(ep), rx, tvdb_mapping, unknown_series_length, offset_season, offset_episode, mappingList)
        break
    if match: continue  # next file iteration
    
    ### Ep not found, adding as season 0 episode 501+ ###
    if " - " in ep and len(ep.split(" - "))>1:  title = clean_string(" - ".join(ep.split(" - ")[1:])).strip()
    counter = counter+1                                          #                    #
    #Log.info('counter "{}"'.format(counter))
    add_episode_into_plex(media, file, root, path, show if path else title, 0, counter, title or clean_string(filename, False, no_underscore=True), year, "", "")
  if not files:  Log.info("[no files detected]");  Log.info("")
  if files:  Stack.Scan(path, files, media, dirs)

  ### root level manual call to Grouping folders ###
  if not path:
    Log.info("root level manual call to Grouping folders")
    folder_count, subfolders = {}, dirs[:]
    while subfolders:  #Allow to add to the list while looping, any other method failed ([:], enumerate)
      full_path = subfolders.pop(0)
      path      = os.path.relpath(full_path, root)

      ### Ignore dirs ###
      for rx in IGNORE_DIRS_RX:                                   # loop rx for folders to ignore
        if re.match(rx, os.path.basename(path), re.IGNORECASE):  # if folder match rx
          Log.info("# Folder: '{}' match '{}' pattern: '{}'".format(path, 'IGNORE_DIRS_RX', rx))
          break
      else:  ### Not skipped
        
        ### Extract season and transparent folder to reduce complexity and use folder as serie name ###
        reverse_path, season_folder_first = list(reversed(Utils.SplitPath(path))), False
        for folder in reverse_path[:-1]:                 # remove root folder from test, [:-1] Doesn't thow errors but gives an empty list if items don't exist, might not be what you want in other cases
          for rx in SEASON_RX :                          # in anime, more specials folders than season folders, so doing it first
            if re.match(rx, folder, re.IGNORECASE):      # get season number but Skip last entry in seasons (skipped folders)
              reverse_path.remove(folder)                # Since iterating slice [:] or [:-1] doesn't hinder iteration. All ways to remove: reverse_path.pop(-1), reverse_path.remove(thing|array[0])
              if rx!=SEASON_RX[-1] and len(reverse_path)>=2 and folder==reverse_path[-2]:  season_folder_first = True
              break
        
        ### Process subfolders ###
        subdir_dirs, subdir_files = [], []
        folder_count[path]        = 0
        for file in os.listdir(full_path):
          path_item = os.path.join(full_path, file) 
          if os.path.isdir(path_item):                 subdir_dirs.append(path_item);  folder_count[path] +=1  #Fullpath
          elif extension(file) in VIDEO_EXTS+['zip']:  subdir_files.append(path_item)                          #Fullpath
        if not subdir_files and subdir_dirs:  # Only add in subfolders if no valid video files in the folder
          Log.info(''.ljust(157, '-'))
          for x in subdir_dirs:  Log.info("[Added] " + x);  subfolders.append(x)
          
        ### Call Grouping folders series ###
        #if subdir_files:                                                           ### Calling Scan for every folder with files ###
        #if subdir_files and not(len(reverse_path)>1 and not season_folder_first):  ### Calling Scan normal    subfolders only ###
        grouping_dir = full_path.rsplit(os.sep, full_path.count(os.sep)-1-root.count(os.sep))[0]
        root_folder  = os.path.relpath(grouping_dir, root).split(os.sep, 1)[0]
        if subdir_files and len(reverse_path)>1 and not season_folder_first and folder_count[root_folder]>1:  ### Calling Scan for grouping folders only ###
          if grouping_dir in dirs:
            Log.info(''.ljust(157, '-'))
            Log.info("[{}] Grouping folder (contain {} dirs)".format(root_folder, folder_count[root_folder]))
            dirs.remove(grouping_dir)  #Prevent grouping folders from being called by Plex normal call to Scan() 
          Log.info("- {:<60}, subdir_files: {:>3}, reverse_path: {:<40}".format(path, len(subdir_files), reverse_path))
          Scan(path, sorted(subdir_files), media, sorted(subdir_dirs), language=language, root=root, kwargs_trigger=True)  #relative path for dir or it will show only grouping folder series
          set_logging(foldername=PLEX_LIBRARY[root] if root in PLEX_LIBRARY else '', filename='_root_'+root.replace(os.sep, '-')+'.scanner.log', mode='a')

### Command line scanner call ###
if __name__ == '__main__':  #command line
  print "Absolute Series Scanner by ZeroQI"
  path  = sys.argv[1]
  files = [os.path.join(path, file) for file in os.listdir(path)]
  media = []
  Scan(path[1:], files, media, [])
  print "Files detected: ", media
