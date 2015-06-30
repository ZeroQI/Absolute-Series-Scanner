# -*- coding: utf-8 -*-
#
### To-Do List ###
# Scanner: try to perfect titles, so that i can include random files with a clean look, so people can't complain about files missing
#   . multi-ep 3 digits
#   . remove crash in 'Plex Media Scanner.log' that cripple speed: "Exception caught determining whether we could skip '' ~ Null value not allowed for this type"
#   . tvdb.id pass through
#   . Single files as season 1 episode 1 if no ep number ?
#   . X-Plex-Token.id in Logs folder to enable a log per Library instead of modifying logs per library
#   . rotate logs like Plex
#   . Add ends_with_number  = '.*([0-9]{1,2})$'
#   . Add ends_with_episode = ['[ ]*[0-9]{1,2}x[0-9]{1,3}$', '[ ]*S[0-9]+E[0-9]+$']
#   . Add year-month-day    =   '(?P<year>[0-9]{4})[^0-9a-zA-Z]+(?P<month>[0-9]{2})[^0-9a-zA-Z]+(?P<day>[0-9]{2})([^0-9]|$)',           # 2009-02-10
#   . Add day-month-year    = '(?P<month>[0-9]{2})[^0-9a-zA-Z]+(?P<day>[0-9]{2})[^0-9a-zA-Z(]+(?P<year>[0-9]{4})([^0-9a-zA-Z]|$)',    # 02-10-2009
#
# Scanner resolved:
#   . source: only available for Movies metadata, not series. Can't see on web gui even for movies anyway
#
# Agent:
#   . anidb reverse apostrophe removal in titles AND text, code not working
#   . change posters for common tvdb serie
#   . trailers function support, start with importing trailer episode range
#   . Specials summaries off season 1...
#   . multi guid: tvdb:xxxxx anidb:xxxx tmdb:xxx
#   . genre weight 400 by default
#
import sys, os, time, re, fnmatch, unicodedata, urllib2, Utils, VideoFiles, Media  ### Plex Media Server\Plug-ins\Scanners.bundle\Contents\Resources\Common ###
from lxml import etree #import Stack

### Log variables, regex, skipped folders, words to remove, character maps ###
PLEX_LIBRARY_URL = "http://127.0.0.1:32400/library/sections/?X-Plex-Token=ACCOUNT_TOKEN_HERE"   # Allow to get the library name to get a log per library https://support.plex.tv/hc/en-us/articles/204059436-Finding-your-account-token-X-Plex-Token
LOG_FILENAME     = 'Plex Media Scanner (custom ASS).log'
LINE_FEED        = "\n"; 

season_rx = [                                                                                                                                             ### Seasons folder + skipped folders ### #http://www.zytrax.com/tech/web/regex.htm  # http://regex101.com/#python
  'Specials',                                                                                                                                             # Specials (season 0)
  '(Season|Series|Book|Saison|Livre)[ _\-]*(?P<season>[0-9]{1,2}).*',                                                                                      # Season|Series|Book|Saison|Livre xx
  '(?P<season>[0-9]{1,2})a? Stagione.*',                                                                                                                  # 1a Stagione
  '(([Ss]tory )?[Aa]r[kc]|[Vv]ideo).*']                                                                                                                   # Arc|Story arc ...   #The last line matches are dropped
series_rx = [                                                                                                                                             ##### Series regex - "serie - xxx - title" ###
  '^(?P<show>.*?)[ _\.\-]*(?P<season>[0-9]{1,2})[Xx](?P<ep>[0-9]{1,3})((|[-_][0-9]{1,2})[Xx](?P<ep2>[0-9]{1,3}))?([ _\.\-]+(?P<title>.*))?$',             # 0 # 1x01
  '^(?P<show>.*?)[ _\.\-]*s(?P<season>[0-9]{1,2})(e| e|ep| ep|-)(?P<ep>[0-9]{1,3})(([-_\.]|(e|ep)|[-_\. ](e|ep))(?P<ep2>[0-9]{1,3}))?($|( | - |)(?P<title>.*)$)',
  '^(?P<title>.*?) \(?(?P<season>(19|20)[0-9]{2})\)$',                                                                                                   # 5 # title (1932).ext
  '^(?P<show>.*?)[ _\.\-]*(?P<season>(19|20)[0-9]{2})([ -_\.]+(?P<title>.*?))$',                                                                          # 2 # 1932 - title
  '^(?P<show>.*?)[ _\.\-]*(?!S)(e|ep|e |ep |e-|ep-)?(?P<ep>[0-9]{1,3})((e|ep|-e|-ep|-)(?P<ep2>[0-9]{1,3}))?(( | - )(?P<title>.*?))?$',            # 3 # E01 | E01-02| E01-E02 | E01E02 
  '^(?P<show>.*?)[ _\.\-]*(?P<ep>[0-9]{1,3})[ _\.\-]?of[ _\.\-]?[0-9]{1,3}([ _\.\-]+(?P<title>.*?))?$']                                                   # 4 # 01 of 08 (no stacking for this one ?)
anidb_rx  = [                                                                                                                                             ### AniDB Specials regex ### 
  '^((?P<show>.*?)[ _\.\-]+)?(S|SP|SPECIAL|OAV) ?(?P<ep>\d{0,2})( .*|$)',                                                                                 #  6 # 001-099 Specials
  '^((?P<show>.*?)[ _\.\-]+)?(OP|NC[ _-]?OP|OPENING) ?(?P<ep>\d{0,2}[a-z]?)$',                                                                            #  7 # 100-149 Openings
  '^((?P<show>.*?)[ _\.\-]+)?(ED|NC[ _-]?ED|ENDING) ?(?P<ep>\d{0,2}[a-z]?)$',                                                                             #  8 # 150-199 Endings
  '^((?P<show>.*?)[ _\.\-]+)?(TRAILER|PROMO|PV|T)($| ?(?P<ep>\d{1,2}))',                                                                                  #  9 # 200-299 Trailer, Promo with a  number
  '^((?P<show>.*?)[ _\.\-]+)?(P|PARODY|PARODIES?) ?(?P<ep>\d{1,2})(.*)',                                                                                  # 10 # 300-399 Parodies
  '^((?P<show>.*?)[ _\.\-]+)?(O|OTHERS?) ?(?P<ep>\d{1,2})(.*)']; AniDBOffset = [0, 100, 150, 200, 300, 400]                                               # 11 # 400-999 Others
roman_rx  = [".*? (L?X{0,3})(IX|IV|V?I{0,3})$"]                                                                                                           # 12 # look behind: (?<=S) < position < look forward: (?!S)

ignore_dirs_rx  = [ 'lost\+found', '.AppleDouble','$Recycle.Bin', 'System Volume Information', 'Temporary Items', 'Network Trash Folder', '@eaDir', 'Extras', 'Samples?', 'bonus', '.*bonus disc.*', 'trailers?', '.*_UNPACK_.*', '.*_FAILED_.*', "VIDEO_TS"]# Filters.py  removed '\..*',        
ignore_files_rx = ['[-\._ ]sample', 'sample[-\._ ]', '-Recap\.', 'OST', 'soundtrack']                                                                                                          # Skipped files (samples, trailers)                                                          
ignore_exts     = ['plexignore', 'ssa', 'srt', 'ass', 'jpg', 'png', 'gif', 'mp3', 'wav', 'flac', 'pdf', 'db', 'nfo', 'ds_store', 'txt', 'zip', 'ini', "dvdmedia", "log", "bat", 'idx', 'sub']  # extensions dropped no warning (skipped list would be too long if showed)
video_exts      = [ '3g2', '3gp', 'asf', 'asx', 'avc', 'avi', 'avs', 'bin', 'bivx', 'divx', 'dv', 'dvr-ms', 'evo', 'fli', 'flv', 'img', 'iso', 'm2t', 'm2ts', 'm2v', 'm4v', 'mkv',             # DVD: 'ifo', 'bup', 'vob'
  'mov', 'mp4', 'mpeg', 'mpg', 'mts', 'nrg', 'nsv', 'nuv', 'ogm', 'ogv', 'tp', 'pva', 'qt', 'rm', 'rmvb', 'sdp', 'swf', 'svq3', 'strm', 'ts', 'ty', 'vdr', 'viv', 'vp3', 'wmv',
  'wpl', 'wtv', 'xsp', 'xvid', 'webm']

FILTER_CHARS    = "\\/:*?<>|~.;_"                                                                             # Windows file naming limitations + "~-,._" + ';' as plex cut title at this for the agent
whack_pre_clean = ["x264-FMD Release", "x264-h65", "x264-mSD", "x264-BAJSKORV", "x264-MgB", "x264-SYS", "x264-FQM", "x264-ASAP", "x264-QCF", "x264-W4F", 'x264-w4f', 
  'x264-2hd', "x264-ASAP", 'x264-bajskorv', 'x264-batv', "x264-BATV", "x264-EXCELLENCE", "x264-KILLERS", "x264-LOL", 'x264-MgB', 'x264-qcf', 'x264-SnowDoN', 'x264-xRed', 
  "H.264-iT00NZ", "H.264.iT00NZ", 'H264-PublicHD', "H.264-BS", 'REAL.HDTV', "WEB.DL", "H_264_iT00NZ", 
  'xvid-saints', 'xvid-pfa','xvid-fqm', 'xvid-asap',"xvid-aldi", "XviD-2HD", "XviD-T00NG0D", 'xvid-killer', "XViD-ViCKY", "XviD-LMAO", "XviD-AFG"
  "PROPER-LOL",  "5Banime-koi_5d", "%5banime-koi%5d", "minitheatre.org", "mthd bd dual", "DD5_1", "AAC2_0", "WEB_DL",
  "-Cd 1", "-Cd 2", "Vol 1", "Vol 2", "Vol 3", "Vol 4", "Vol 5", "Vol.1", "Vol.2", "Vol.3", "Vol.4", "Vol.5",
  "HDTV-AFG", "HDTV-LMAO", "XviD-BiA-mOt", 
  "kris1986k_vs_htt91",   'web-dl', "-Pikanet128", "hdtv-lol", "REPACK-LOL", " - DDZ", "OAR XviD-BiA-mOt",
  "AC3.5.1", "AAC2.0", "AAC.2.0", 'DD5.1',  "SD TV","SD DVD", "HD TV", 'divx5.1', "H.264", "-dvdrip", 'xvid',"dvd-jap",  "OAR HDTV-BiA-mOt"] #include spaces, hyphens, dots, underscore, case insensitive
whack = [ #lowercase                                                                                          ### Tags to remove ###
  'x264', 'h264', 'dvxa', 'divx', 'xvid', 'divx51', 'mp4',                                                    # Video Codecs
  'mp3', 'ogg','ogm', 'vorbis','aac','dts', 'ac3', '5.1ch','5.1', '7.1ch',  'qaac',                           # Audio Codecs, channels
  '480p', '576p', '720p', '1080p', '1080i', '1920x1080','1280x720',                                           #       Resolution
  'hi10', 'hi10p', '10bit', 'crf24',  'crf 24',                                                               #       color depth and encoding
  '24fps', '25fps', 'ntsc','pal', 'ntsc-u', 'ntsc-j',                                                         # Refresh rate, Format
  'dc','se', 'extended', 'unrated', 'multi','multisubs', 'dubbed','subbed', "french", "fr", "dub",            # edition (dc = directors cut, se = special edition), subs and dubs
  'limited', 'custom', 'internal', 'repack', 'proper', 'rerip', "raw", "remastered", "uncensored",            # format
  'retail', 'webrip','web-dl', 'wp','workprint',                                                              # release type: retail, web, work print
  'cd1', 'cd2', 'cd3', 'cd4', '1cd', '2cd', '3cd', '4cd', 'xxx', 'nfo', 'read.nfo', 'readnfo', 'nfofix',      # misc 1
  'fragment','ps3avchd','remux','fs','ws', "- copy", "reenc",                                                         # misc 2
  'bdrc','bdrip','bluray','bd','brrip','hdrip','hddvd','hddvdrip', 'wsrip',                                   # Source: bluray
  'ddc','dvdrip','dvd','r1','r3','r5',"dvd",'svcd','vcd', 'sd', 'hd', 'dvb',                                  # DVD, VCD, S-VCD
  'dsr','dsrip','hdtv','pdtv','ppv','stv','tvrip','complete movie',"Hiei", "Metis",                           # dtv, stv
  'cam','bdscr','dvdscr','dvdscreener','scr','screener','tc','telecine','ts','telesync', 'mp4',               # screener
  "mthd", "thora", 'sickrage', 'brrip', 'ac3', "remastered", "yify", "tsr",
  'rikou', 'HOMЯ', "iT00NZ", "nn92", "mthd", "elysium", "encodebyjosh", "krissy", "it00nz", "s4a"]   #
CHARACTERS_MAP = { 14844057:"'", 14844051:'-', 14844070:'...', 15711386:':', 14846080:'∀',                    #['’' \xe2\x80\x99] ['–' \xe2\x80\x93] ['…' \xe2\x80\xa6] # '：' # 12770:'', # '∀ Gundam' no need #'´' ['\xc2', '\xb4']
  50048:'A' , 50050:'A' , 50052:'Ä' , 50080:'a' , 50082:'a' , 50084:'a' , 50305:'a' , 50308:'A' , 50309:'a' , #'à' ['\xc3', '\xa0'] #'â' ['\xc3', '\xa2'] #'Ä' ['\xc3', '\x84'] #'ā' ['\xc4', '\x81'] #'À' ['\xc3', '\x80'] #'Â' ['\xc3', '\x82'] # 'Märchen Awakens Romance', 'Rozen Maiden Träumend'
  50055:'C' , 50087:'c' , 50310:'C' , 50311:'c' ,                                                             #'Ç' ['\xc3', '\x87'] #'ç' ['\xc3', '\xa7'] 
  50057:'E' , 50088:'e' , 50089:'e' , 50090:'e' , 50091:'e' , 50323:'e' , 50328:'E' , 50329:'e' ,             #'É' ['\xc3', '\x89'] #'è' ['\xc3', '\xa8'] #'é' ['\xc3', '\xa9'] #'ē' ['\xc4', '\x93'] #'ê' ['\xc3', '\xaa'] #'ë' ['\xc3', '\xab']
  50094:'i' , 50095:'i' , 50347:'i' , 50561:'L' , 50562:'l' , 50563:'N' , 50564:'n' , 50097:'n' ,             #'î' ['\xc3', '\xae'] #'ï' ['\xc3', '\xaf'] #'ī' ['\xc4', '\xab'] #'ñ' ['\xc3', '\xb1']
  50067:'O' , 50068:'Ô' , 50072:'O' , 50100:'o' , 50099:'o' , 50573:'o' , 50578:'OE', 50579:'oe',             #'Ø' ['', '']         #'Ô' ['\xc3', '\x94'] #'ô' ['\xc3', '\xb4'] #'ō' ['\xc5', '\x8d'] #'Œ' ['\xc5', '\x92'] #'œ' ['\xc5', '\x93']
  53423:'Я'  ,                                                                                                #'Я' ['\xd0', '\xaf']
  50586:'S' , 50587:'s' , 50079:'ss', 50105:'u' , 50107:'u' , 50108:'u' ,                                     #'ß' []               #'ù' ['\xc3', '\xb9'] #'û' ['\xc3', '\xbb'] #'ü' ['\xc3', '\xbc'] #'²' ['\xc2', '\xb2'] #'³' ['\xc2', '\xb3']
  50617:'Z' , 50618:'z' , 50619:'Z' , 50620:'z' ,                                                             #
  49835:'«' , 49842:'²' , 49843:'³' , 49844:"'" , 49848:'¸',  49851:'»' , 49853:'½'}                        #'«' ['\xc2', '\xab'] #'»' ['\xc2', '\xbb']# 'R/Ranma ½ Nettou Hen'                                                                                                 #'¸' ['\xc2', '\xb8']  

### LOG_PATH calculated once for all calls ####################################################################
#platform = sys.platform.lower() if "platform" in dir(sys) and callable(getattr(sys,'platform')) else "" 
try:      platform = sys.platform.lower()                                                                                              # sys.platform: win32 | darwin | linux2, 
except:                                                                                                                                #
  try:    platform = Platform.OS.lower()                                                                                               # Platform.OS:  Windows, MacOSX, or Linux #  
  except: platform = ""  
if   platform in ('win32', 'windows'):   LOG_PATHS = [ '%LOCALAPPDATA%\\Plex Media Server\\Logs',                                       #
                                                       '%USERPROFILE%\\Local Settings\\Application Data\\Plex Media Server\\Logs' ]     # CR \r seem added to LF (\N) on windows 
elif platform in ('darwin', 'macosx'):  LOG_PATHS = [ '$HOME/Library/Application Support/Plex Media Server/Logs' ]                     # LINE_FEED = "\r"
elif 'linux' in platform:               LOG_PATHS = [ '$PLEX_HOME/Library/Application Support/Plex Media Server/Logs',                 # Linux
                                                      '/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Logs',   # Debian, Fedora, CentOS, Ubuntu
                                                      '/usr/local/plexdata/Plex Media Server/Logs',                                    # FreeBSD
                                                      '/usr/pbi/plexmediaserver-amd64/plexdata/Plex Media Server/Logs',                # FreeNAS
                                                      '/c/.plex/Library/Application Support/Plex Media Server/Logs',                   # ReadyNAS
                                                      '/share/MD0_DATA/.qpkg/PlexMediaServer/Library/Plex Media Server/Logs',          # QNAP
                                                      '/volume1/Plex/Library/Application Support/Plex Media Server/Logs',              # Synology, Asustor
                                                      '/volume2/Plex/Library/Application Support/Plex Media Server/Logs' ]             # Synology, if migrated a second raid volume as unique volume in new box         
else:                                   LOG_PATHS = [ '$HOME' ]                                                                        # home folder as backup "C:\users\User.Machine" in windows 8, "users\Plex" on synology
for LOG_PATH in LOG_PATHS:
  if '%' in LOG_PATH: LOG_PATH = os.path.expandvars(LOG_PATH)
  if os.path.isdir(LOG_PATH):  break
else: LOG_PATH = os.path.expanduser('~')

### Allow to log to the same folder Plex writes its logs in #############################################
def Log(entry, filename=LOG_FILENAME): 
  with open(os.path.join(LOG_PATH, filename if filename else LOG_FILENAME), 'a') as file:
    file.write( time.strftime("%Y-%m-%d %H:%M:%S") + " " + entry + LINE_FEED)
    print entry  # when ran from console ### Allow to display ints even if equal to None at times ### def xint(s):   return str(s) if s is not None and not s=="" else "None"

### Convert Roman numerals ##############################################################################
def roman_to_int(string):  # Regex for matching #M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})
  string, result = string.upper(), 0
  for roman_number, value in [['M',1000],['CM',900],['D',500],['CD',400],['C',100],['XC',90],['L',50],['XL',40]['X',10],['IX',9],['V',5],['IV',4],['I',1]]:  # if you use {} the list will be in the wrong order 
    while string.startswith(roman_number):
      result += value
      string  = string[len(roman_number):]
  return str(result)

### replace a string by another while retaining original string case ###############################################################################
def replace_insensitive (ep, word, sep=" "):
  if ep.lower()==word.lower(): return ""
  position = ep.lower().find(word.lower()) #Log("position: '%d', ep: '%s', word: '%s'" % (position, ep, word))
  if position > -1 and len(ep)>len(word):  return (""  if position==0 else ep[:position].lstrip()) + (sep if len(ep) < position+len(word) else ep[position+len(word):].lstrip()) #remove word without touching case #Log("'%s', '%d', '%s', '%d', '%d'" % (ep, position, word, len(word), len(ep))) 

### Turn a string into a list of string and number chunks  "z23a" -> ["z", 23, "a"] ###############################################################################
def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
  return [int(text) if text.isdigit() else text.lower() for text in re.split(_nsre, s)]

### Return number of bytes of Unicode characters ########################################################
def unicodeLen (char):                         # count consecutive 1 bits since it represents the byte numbers-1, less than 1 consecutive bit (128) is 1 byte , less than 23 bytes is 1
  for x in range(1,6):                                           # start at 1, 6 times 
    if ord(char) < 256-pow(2, 7-x)+(2 if x==6 else 0): return x  # 256-2pow(x) with x(7->0) = 128 192 224 240 248 252 254 255 = 1 to 8 bits at 1 from the left, 256-2pow(7-x) starts form left

### Decode string back to Unicode ###   #Unicodize in utils?? #fixEncoding in unicodehelper
def encodeASCII(string, language=None): #from Unicodize and plex scanner and other sources
  if string=="": return ""
  ranges = [ {"from": ord(u"\u3300"), "to": ord(u"\u33ff")}, {"from": ord(u"\ufe30"), "to": ord(u"\ufe4f")}, {"from": ord(u"\uf900"), "to": ord(u"\ufaff")},  # compatibility ideographs
             {"from": ord(u"\u30a0"), "to": ord(u"\u30ff")}, {"from": ord(u"\u2e80"), "to": ord(u"\u2eff")}, # Japanese Kana    # cjk radicals supplement
             {"from": ord(u"\u4e00"), "to": ord(u"\u9fff")}, {"from": ord(u"\u3400"), "to": ord(u"\u4dbf")}] 
             #windows: TypeError: ord() expected a character, but string of length 2 found #{"from": ord(u"\U00020000"), "to": ord(u"\U0002a6df")}, #{"from": ord(u"\U0002a700"), "to": ord(u"\U0002b73f")}, #{"from": ord(u"\U0002b740"), "to": ord(u"\U0002b81f")}, #{"from": ord(u"\U0002b820"), "to": ord(u"\U0002ceaf")}, # included as of Unicode 8.0                             #{"from": ord(u"\U0002F800"), "to": ord(u"\U0002fa1f")}  # compatibility ideographs
  encodings, encoding = ['iso8859-1', 'utf-16', 'utf-16be', 'utf-8'], ord(string[0])
  if 0 <= encoding < len(encodings):  string = string[1:].decode('cp949') if encoding == 0 and language == 'ko' else string[1:].decode(encodings[encoding])      # If we're dealing with a particular language, we might want to try another code page.
  if sys.getdefaultencoding() not in encodings:
    try:    string = string.decode(sys.getdefaultencoding())
    except: pass
  if sys.getfilesystemencoding() not in encodings and not sys.getfilesystemencoding()==sys.getdefaultencoding():
    try:    string = string.decode(sys.getfilesystemencoding())
    except: pass
  if string: string = string.strip('\0')
  try:     string = unicodedata.normalize('NFKD', string)    # Unicode  to ascii conversion to corect most characters automatically
  except:  pass
  try:     string = re.sub(RE_UNICODE_CONTROL, '', string)   # Strip control characters.
  except:  pass
  try:     string = string.encode('ascii', 'replace')        # Encode into Ascii
  except:  pass
 
  ### loop through unicode and replace special chars with spaces then map if found ###
  original_string, string, i = string, list(string), 0
  while i < len(string):
    if ord(string[i])<128:  i = i+1
    else: #non ascii char
      char, char2, char3, char_len = 0, "", [], unicodeLen(string[i])
      for x in range(0, char_len):
        char = 256*char + ord(string[i+x]); char2 += string[i+x]; char3.append(string[i+x])
        if not x==0: string[i] += string[i+x]; string[i+x]=''
      try:    asian_language = any([mapping["from"] <= ord("".join(char3).decode('utf8')) <= mapping["to"] for mapping in ranges])
      except: asian_language = False
      if char in CHARACTERS_MAP:  string[i]=CHARACTERS_MAP.get( char )
      elif not asian_language:  Log("*Character missing in CHARACTERS_MAP: %d:'%s'  , #'%s' %s, string: '%s'" % (char, char2, char2, char3, original_string))
      i += char_len
  return ''.join(string)

### Allow to display ints even if equal to None at times ################################################
def clean_filename(string, delete_parenthesis=False):
  if not string: return ""
  try:   string.decode('ascii')                                                                 # If string have non-ASCII characters
  except UnicodeDecodeError:  string=encodeASCII(string)                                        # Translate them
  if "(" in string and delete_parenthesis:  string = re.sub(r'\(.*?\)', '', string)  #or not delete_parenthesis and not re.search('.*?\((19[0-9]{2}|20[0-2][0-9])\).*?', string, re.IGNORECASE) 
  if "[" in string or "{" in string:  string = re.sub(r'[\[\{].*?[\]\}]', '', string)           # remove "[xxx]" groups as Plex cleanup keep inside () but not inside []
  if ", The" in string:               string = "The " + ''.join( string.split(", The", 1) )     # ", The" is rellocated in front
  if ", A"   in string:               string = "A "   + ''.join( string.split(", A"  , 1) )     # ", A"   is rellocated in front
  if "`"     in string:               string = string.replace("`", "'")                         # translate anidb apostrophes into normal ones #s = s.replace('&', 'and')       
  for word in whack_pre_clean:        string = replace_insensitive(string, word) if word.lower() in string.lower() else string
  for char in  FILTER_CHARS:          string = string.replace(char, ' ') if char in string else string  # replace os forbidden chars with spaces
  string = " ".join([word for word in filter(None, string.split()) if word.lower() not in whack])                          # remove wouble spaces + words present in "whack" list #filter(None, string.split())
  for rx in ("-", "- ","v1", "v2", "v3"):             string=string[  len(rx):] if string.lower().startswith(rx) else string  # In python 2.2.3: string = string.strip(string, " -_")
  for rx in (" -", "-", "v1", "v2", "v3", "- copy"):  string=string[:-len(rx) ] if string.lower().endswith  (rx) else string  # In python 2.2.3: string = string.strip(string, " -_")
  return string.strip()

### Add files into Plex database ########################################################################
def add_episode_into_plex(mediaList, files, file, root, path, show, season=1, ep=1, title="", year=None, ep2 = None, rx=""):
  if title==title.lower() or title==title.upper() and title.count(" ")>0: title = title.title()
  if not ep2:               ep2 = ep                                                        # make ep2 same as ep for loop and tests
  if ep > ep2 or show=="":  Log("Warning - show: '%s', s%02de%03d-%03d, file: '%s' has ep1 > ep2, or show empty" % (show, season, ep, ep2, file))
  else:
    for epn in range(ep, ep2+1):
      tv_show, tv_show.display_offset = Media.Episode(show, season, epn, title, year), (epn-ep)*100/(ep2-ep+1)
      tv_show.parts.append(file)
      mediaList.append(tv_show) #otherwise only one episode per multi-episode is showing despite log below correct
    index = str(series_rx.index(rx)) if rx in series_rx else str(anidb_rx.index(rx)+len(series_rx)) if rx in anidb_rx else "" #rank of the regex used from 0
    Log("s%02de%03d%s \"%s\"%s%s" % (season, ep, "" if ep==ep2 else "-%03d" % ep2, os.path.basename(file), " \"%s\"" % index if index else "", " \"%s\" " % title if title else ""))  #Stack.Scan(path, files, mediaList, [])
    
### Add files into array ################################################################################
def explore_path(root, subdir, file_tree, plexignore_files=[], plexignore_dirs=[]):
  fullpath=os.path.join(subdir, ".plexignore")
  if os.path.isfile(fullpath):
    with open(fullpath, 'r') as plexignore:                                                      # Log(".plexignore")
      for pattern in plexignore:                                                                 #
        pattern = pattern.strip()                                                                # remove useless spaces at both ends
        if pattern == '' or pattern[0] == '#': continue                                          # skip comment and emopy lines, go to next for iteration
        if '/' not in pattern:  plexignore_files.append(fnmatch.translate(pattern))              # patterns for this folder gets converted and added to files.
        elif pattern[0] != '/': plexignore_dirs.append(pattern)                                  # patterns for subfolders added to folders
  files, dirs = [], []                                                                           ### Process all files and folders ###
  for item in os.listdir(subdir):                                                                # Loop current folder files and folders
    fullpath = os.path.join(subdir, item)                                                        #
    if os.path.isdir(fullpath):                                                                  ### dirs
      for rx in ignore_dirs_rx:                                                                  # Loop through unwanted folders list
        if re.match(rx, item, re.IGNORECASE):                                                    #
          Log("Folder: '%s' match ignore_dirs_rx '%s'" % (fullpath[len(root):], rx))             #if:ignore_dirs_rx.index(rx)>15: # to only log 
          break                                                                                  # If folder in list of skipped folder exit this loop  #if len(result):  break
      else:  dirs.append(fullpath)                                                               # .plexignore subfolder restrictions management
    elif os.path.isfile(fullpath):                                                               ### is a file ###
      for rx in ignore_files_rx+plexignore_files:                                                # Filter trailers and sample files
        if re.match(rx, item, re.IGNORECASE): 
          Log("File:   '%s' match %s: '%s'" %("ignore_files_rx" if rx in ignore_files_rx else "plexignore_files", fullpath[len(root):], rx))
          break                                                                                  #Log("'%s' ignore_files_findall: match" % item)
      else: # file not ignored
        if   '.' in item and item.lower().rsplit('.', 1)[1] in video_exts:                 files.append(fullpath)
        elif '.' in item and item.lower().rsplit('.', 1)[1] not in ignore_exts:  Log("File:   '%s' extension not in video_exts" %(fullpath[len(root):]))                                        ### files
  dirs.sort(); files.sort(key=natural_sort_key)
  for item in dirs:
    plexignore_recursive_files = plexignore_recursive_dirs = []                                  # Split recursive entries, this one for next folder's subfolders
    for rx in plexignore_dirs:                                                                   # On each patter string
      pattern = rx.split("/")                                                                    # Create array splitting by / so all folders separated and patter last
      if pattern[0].lower() == Utils.SplitPath(item)[-1].lower():                                # first folder the same
        if len(pattern) == 2: plexignore_recursive_files.append(fnmatch.translate(pattern[1]))   # One folder, for next folder current files
        if len(pattern) >= 3: plexignore_recursive_dirs.append( "",join(pattern[1:]))            # 2+ folders, for next folder subfolders
    explore_path(root, item, file_tree, plexignore_recursive_files, plexignore_recursive_dirs)   # call next folder and will inherit restrictions
  if files:  file_tree["" if subdir==root else subdir.replace(root, "")[1:]] = files             # 

### Look for episodes ###################################################################################
def Scan(path, files, mediaList, subdirs, language=None, root=None, **kwargs):
  if not path == "":  return 0# Exit every other iteration than the root scan

  ### Rename log file with library name if XML file can be accessed ###
  global LOG_FILENAME
  try:
    result = urllib2.urlopen(PLEX_LIBRARY_URL)
    if result is not None: Log(str(result.getcode()))
    string = result.read()
  except:
    if "ACCOUNT_TOKEN_HERE" in PLEX_LIBRARY_URL:  Log("Place Plex token PLEX_LIBRARY_URL variable to have a log per library - https://support.plex.tv/hc/en-us/articles/204059436-Finding-your-account-token-X-Plex-Token")
    else:                                         Log("except http library xml - Token replaced in source code but still fails")
  else:
    library_xml = etree.fromstring(string)
    for library in library_xml.iterchildren('Directory'):
      for library_root in library.iterchildren('Location'):
        if library_root.get("path") == root:  #if root path match the scanner, we have the libray name for which the scanner is ran
          LOG_FILENAME = LOG_FILENAME[:-4] + " - " + library.get("title") + LOG_FILENAME[-4:]
          break                                                                                          # found, break second loop
      else: continue                                                                                     # next iteration of first loop, if second loop wasn't broken, therefound found nothing
      break                                                                                              # break first loop if second loop was broken, #cascade-break
    else: Log("except http library xml - No library name to append at end of log filename despite access to file. Please forward to developer xml: '%s' " % PLEX_LIBRARY_URL)

  Log("=== Scan ================================================================================================================")
  Log("Log path: \"%s\"" % LOG_PATH)
  Log("Root:     \"%s\", Platform: \"%s\"" % (root, platform))  
  Log("--- Skipped mediums -----------------------------------------------------------------------------------------------------")
  file_tree = {}; explore_path(root, root, file_tree)                                                    # Build file_tree wwhich output skipped medium in logs
  Log("=========================================================================================================================")
  with open(os.path.join(LOG_PATH, LOG_FILENAME[:-4] + " - filelist" + LOG_FILENAME[-4:]), 'w') as file: ### Create a log with the library files relative path in logs folder for T/S 
    for folder in sorted(file_tree):                                                                     # convert to ansi, then notepad++ to replace \r\n to \n if needed + batch to recreate dummy library for tests
      for filename in file_tree[folder]:  file.write( filename.replace(root, "")[1:] + "\n")             # for each folder, for each file, write the relative path with windows line ending 
  
  ### Main loop for folders ###
  for path in sorted(file_tree):                                                                         # Loop to add all series while on the root folder Scan call, which allows subfolders to work
    files, folder_year, folder_season, reverse_path, AniDB_op, counter = file_tree[path], None, None, Utils.SplitPath(path), {}, 1 #
    reverse_path.reverse()                                                                               # Take top two as show/season, but require at least the top one, and reverse them
    
    ### bluray folder management ###                                                                     # source: https://github.com/doublerebel/plex-series-scanner-bdmv/blob/master/Plex%20Series%20Scanner%20(with%20disc%20image%20support).py
    if len(reverse_path) >= 3 and reverse_path[0].lower() == 'stream' and paths[1].lower() == 'bdmv':
      if reverse_path[0].lower() == 'stream': reverse_path.pop(0)
      if reverse_path[0].lower() == 'bdmv' :  reverse_path.pop(0)
      ep = clean_filename(reverse_path[0], True)
      if len(reverse_path)>1:
        reverse_path.pop(0)
        Log("BluRay folder detected - using as equivalent to filename ep: '%s', reverse_path: '%s'" % (ep, reverse_path[0]))
      else: Log("BluRay folder detected - using as equivalent to filename ep: '%s'" % ep)
      
    ### Extract season folder to reduce complexity and use folder as serie name ###
    for folder in reverse_path[:-1]:                   # remove root folder from test, [:-1] Doesn't thow errors but gives an empty list if items don't exist, might not be what you want in other cases
      for rx in season_rx :                      # in anime, more specials folders than season folders, so doing it first
        match = re.match(rx, folder, re.IGNORECASE)
        if match:
          if rx!=season_rx[-1]:  folder_season = season = int( match.group('season')) if match.groupdict().has_key('season') and match.group('season') else 0
          reverse_path.remove(folder)                                                                         # All ways to remove: reverse_path.pop(-1), reverse_path.remove(thing|array[0])
          if rx!=season_rx[-1]:  break 
          match = None #continue as if nothing happend, will go to second folder
      if match: break
    else:  season = 1
    
    ### Capture title form anidb.id or use folder name ###
    guid_table = ("anidb.id", "Extras/anidb.id") #, "tvdb.id", "Extras/tvdb.id", "tmdb.id", "imdbid") #agent will need upgrading
    for file_path in guid_table:
      if os.path.isfile(os.path.join(root, path, file_path)):
        with open(os.path.join(root, path, file_path), 'r') as guid_file:
          guid        = guid_file.read().strip() #"%s:%s" % ( os.path.splitext(os.path.basename(file_path))[0], guid_file.read().strip() )  #agent will need upgrading
          folder_show = "aid:"+guid              #folder_show = "[%s] "% guid + clean_filename( reverse_path[0] )  #agent will need upgrading
        break
    else:  folder_show, guid = clean_filename( reverse_path[0] ), "" # Serie name is folder name (since we removed season folders)
    if folder_show.lower().startswith(("saison","season","series")) and len(folder_show.split(" ", 2))==3:  folder_show = (folder_show.replace(" - ", " ") if " - " in folder_show else folder_show).split(" ", 2)[2]  # Dragon Ball/Saison 2 - Dragon Ball Z/Saison 8
    Log("\"%s\"%s%s" % (folder_show, " from foldername: \"%s\"" % path if path!=folder_show else "", ", Season: \"%d\"" % (folder_season) if folder_season is not None else "") )
    
    movie_list={}
    ### Main File loop to start adding files now ###
    for file in files:                                                                                                                        # "files" is a list of media files full path, File is one of the entries
      filename = os.path.splitext(os.path.basename(file))[0] #remove folders and extension(mp4)
      season = 1 if folder_season is None else folder_season
      show, year, ep, ep2, title, folder_use = folder_show, folder_year, clean_filename(filename, True), None, "", False       #if re.match('.+ \([1-2][0-9]{3}\)', paths[-1]): #misc, year      = VideoFiles.CleanName(filename_no_ext)
      if len(files)==1 and (ep==folder_show or "movie" in ep.lower()+folder_show.lower() or "gekijouban" in folder_show.lower()):  ep, title = "01", folder_show  ### Movies ### 
      elif folder_show:                                                                                                                       ### Remove folder name from file name to reduce complexity and favor folder name over filename ### (who put crappy folder names and clean filenames anyway?)  # if not at root and containing folder exist and has name different from "_" (scrubed to "")
        if ep.lower().startswith(folder_show.lower()):  ep, folder_use = ep[len(folder_show):].lstrip()[2:] if len(ep)>2 and ep.lower().startswith('s ') else ep[len(folder_show):].lstrip(), True #remove cleansed folder name from cleansed filename and remove potential space
        if folder_season and ep.startswith(("S%d"   % folder_season, "s%d"   % folder_season)):  ep =  replace_insensitive(ep, "S%d"   % folder_season, "").lstrip() #Series S2  like transformers (bad naming)                                                                       # Serie S2  in season folder, Anidb specials regex doesn't like
        if folder_season and ep.startswith(("S%02d" % folder_season, "s%02d" % folder_season)):  ep =  replace_insensitive(ep, "S%02d" % folder_season, "").lstrip() #Series S02 like transformers (bad naming)                                                                      # Serie S02 in season folder, Anidb specials regex doesn't like
        if ep.lower().startswith(("special", "picture drama", "omake")):  season, title = 0, ep.title()                                                                                                              ### If specials, season is 0 and if title empty use as title ### 
        
        words, misc, buffer = filter(None, ep.split()), " ".join( [clean_filename(os.path.basename(x), True) for x in files]), clean_filename(folder_show.lower(), False) #re.sub(r'[\[\{\(].*?[\]\}\)]', '', clean_filename(folder_show.lower(), True))                               # put all filenames in folder in a string to count if ep number valid or present in multiple files ###clean_filename was true ###
        for word in words:                                                                                                                                                                                                                 # if word=='': continue filter prevent "" on double spaces
          ep=word.strip()  #cannot use words[words.index(word)] otherwise
          if ep in ("", "-"):  continue
          elif "-" in ep:                # if -
            ep = ep.strip("-")           #remove on both sides
            if len(ep.split("-",1))==2:  # if it splits in two parts
              if re.match("^(e|ep|e |ep |e-|ep-)?(?P<ep>[0-9]{1,3})((e|ep|-e|-ep|-)(?P<ep2>[0-9]{1,3}))", ep, re.IGNORECASE): #if multi ep
                ep="Skip"
                break
              if len(words)>words.index(word)+1:  words.insert(words.index(word)+1, "-".join(ep.split("-",1)[1:])) #???
              else:                               words.append("-".join(ep.split("-",1)[1:]))
              ep = ep.split("-",1)[0]
          ep = ep.strip()
          if ep=="trailer":  season, ep, title = 0, "201", "Trailer"
          if len(ep)==6 and ep[0]=='(' and ep[5]==')' and ep[1:4].isdigit():  ep = ep [1:4]          #Log("ep: '%s', word: '%s', buffer: '%s', filename.count(ep): '%d', misc.count(ep): '%d', test: '%s'" % (ep, word, buffer, filename.count(ep), misc.count(ep), str(filename.count(ep)<2 and (misc.count(ep)>=3 or not folder_use and ep.lower() in buffer and ep.lower() not in clean_filename(buffer, True) and len(buffer)==len(ep)+len(clean_filename(buffer, True)) ))  ))
          if not folder_use and (misc.count(ep)>=3 or ep.lower() in buffer and ep.lower() not in clean_filename(buffer, True) ):  buffer= buffer.replace(ep.lower(), "", 1) #  and len(buffer)==len(ep)+len(clean_filename(buffer, True))# skip word if: present in 3+ filenames, or in buffer (not year) and length of buffer = length word + length buffer no parenthesis
          elif ''.join(letter for letter in ep if letter.isdigit()):                                                                                                                                                                     ### if digit in current word we found the ep number normally ###
            if ep.isdigit() and len(ep)==4:                                                                                                                                                                                            #
              if int(ep)< 1900 or int(ep[0:1])==folder_season:  season, ep = int(ep[0:1]), ep[2:3]                                                                                         #1206 could be season 12 episode 06  #Get assigned from left ot right
              else:
                filename = clean_filename( " ".join(words).replace(ep, "(%s)" % ep))                                                                                                               # take everything after supposed episode number
                ep = "(%s)" % word
                continue
            title = clean_filename( " ".join(words[ words.index(word)+1:]) if len(words)-words.index(word)>1 else "", False).strip("-").strip()                                                                                                               # take everything after supposed episode number
            if word.lower().startswith("ep" ) and len(ep)>2 and ep[len("ep" ):].isdigit():  ep = ep[len("ep" ):]     #E   before ep number
            if word.lower().startswith("e"  ) and len(ep)>1 and ep[len("e"  ):].isdigit():  ep = ep[len("e"  ):]     #EP  before ep number
            if word.lower().startswith("act") and len(ep)>3 and ep[len("act"):].isdigit():  ep = ep[len("act"):]     #act before ep number ex: Trust and Betrayal OVA-act1
            if word.lower().startswith("s"  ) and len(ep)>1 and ep[len("s"  ):].isdigit():
              if len(words)==words.index(word)+1:  ep, season = ep[len("s" ):], 0  #S1 at the end, nothing afterwards 
              else: continue #Season 2 without folder season like s00e002 seen for "[HorribleSubs] Hakkenden - Eight Dogs of the East S2 - E15 [720p].mkv"
            break
      if ep.isdigit():
        if season==1 and int(ep)==0:  ep,  season = "01", 0 #s01e00 becomes s00e01
        if len(title)>=3 and title[0  ].lower()=="e"  and title[1:2].isdigit():  ep, title = title[1:2], "" if len(title)==3 else title[3:]
        if len(title)>=4 and title[0:1].lower()=="ep" and title[2:3].isdigit():  ep, title = title[3:3], "" if len(title)==4 else title[4:]
        add_episode_into_plex(mediaList, files, file, root, path, show, season, int(ep), title, year, int(ep2) if ep2 and ep2.isdigit() else None, "None")
        continue
      
      ### Check for series_rx + anidb_rx + roman_rx ###
      ep = clean_filename(filename, False)
      for rx in series_rx + anidb_rx + roman_rx:
        #if rx in roman_rx:  ep = clean_filename(ep.rsplit(' ', 1)[1] if ' ' in ep else ep) ### move that to chech from the beginning ?
        match = re.search(rx, ep, re.IGNORECASE)
        if match:
          show   = clean_filename( match.group('show' )) if match.groupdict().has_key('show' ) and match.group('show' ) and not folder_use and show =="" else show # Mainly if file at root or _ folder
          title  = clean_filename( match.group('title')) if match.groupdict().has_key('title') and match.group('title') else ""
          if rx in series_rx:                                                       ### Normal Regex ########################################################################
            if match.groupdict().has_key('season') and match.group('season') and match.group('season').isdigit():  season = int(match.group('season'))
            if match.groupdict().has_key('ep2'   ) and match.group('ep2'   ) and match.group('ep2'   ).isdigit():  ep2    = match.group('ep2') 
          if match.groupdict().has_key('ep') and match.group('ep') is not None and not match.group('ep')=="":   ep          = match.group('ep')
          else:                                                                                                 
            movie_list[season] = 1 if season not in movie_list else movie_list[season] + 1 #add movies using year as season, starting at 1
            ep = str(movie_list[season]) # Year alone is season Year and ep incremented, good for series, bad for movies but cool for movies in series folder...
          if rx in anidb_rx:                                                          ### AniDB Specials ################################################################
            offset, season = AniDBOffset [ anidb_rx.index(rx) ], 0                    # offset = 100 for OP, 150 for ED, etc...
            if not ep.isdigit() and len(ep)>1 and ep[:-1].isdigit():                  ### OP/ED with letter version Example: op2a
              AniDB_op [ offset + int(ep[:-1]) ] = ord( ep[-1:].lower() ) - ord('a')  # {101: 0 for op1a / 152: for ed2b} and the distance between a and the version we have here
              ep      = str( int( ep[:-1] ) )                                         # "if xxx isdigit() else 1" implied since OP1a for example...
              offset += sum( AniDB_op.values() )                                      # get the offset (100, 150, 200, 300, 400) + the sum of all the mini offset caused by letter version (1b, 2b, 3c = 4 mini offset)
            ep = str( offset + int(ep))                                               # Add episode number to the offset, 01 by default from the match group above
          elif rx in series_rx:                                                       ### Normal Regex ########################################################################
            if int(ep)==0:  episode, season = "01", 0                                 # Swap s01e00 and s00e01
          #elif rx in roman_rx:  ep = roman_to_int(ep)                           ### Roman numbers ### doesn't work is ep title present
          add_episode_into_plex(mediaList, files, file, root, path, show, season, int(ep), title, year, int(ep2) if ep2 and ep2.isdigit() else None, rx)
          break
      if match: continue  # next file iteration
      Log("*no episode number found for ep: \"%s\", filename: \"%s\", word: '%s'" % (ep, filename, word))
    Log("-------------------------------------------------------------------------------------------------------------------------")  #Scan(path, files, mediaList, [])
  Log("")  # VideoFiles.Scan(path, files, mediaList, [], root) # Filter out bad stuff and duplicates.

if __name__ == '__main__':
  print "Absolute Series Scanner:"
  path, files, media = sys.argv[1], [os.path.join(path, file) for file in os.listdir(path)], []
  Scan(path[1:], files, media, [])
  print "Media:", media
