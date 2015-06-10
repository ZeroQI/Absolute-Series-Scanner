# -*- coding: utf-8 -*-
__author__  = "Benjamin Brisson  (ZeroQI)"; __maintainer__ = "Benjamin Brisson  (ZeroQI)"; __email__   = "benjamin.brisson@gmail.com";  
__license__ = "GPLv2"; __version__ = "1.0"; __copyright__  = "Copyright 2013-2015"       ; __credits__ = ["Plex original scanner code", "BABS"]

import sys             # sys.getdefaultencoding, titlecase , datetime
import os              # os.uname, os.listdir, os.path.basename, os.path.splitext, os.path.join, os.path.expandvars, os.path.expanduser, os.path.isdir, os.path.isfile
import re              # re.findall, re.match, re.sub, re.search
import fnmatch         # fnmatch used by .plexignore regex
import unicodedata     # unicodedata.normalize
import urllib2         # urllib
from lxml import etree #
import Utils                                                       ### Plex Media Server\Plug-ins\Scanners.bundle\Contents\Resources\Common ###          
# SplitPath           (path, maxdepth=20)                          # Platform-safe function to split a path into a list of path elements.
# ContainsFile        (files, file)                                # Check for a given filename in a list of full paths.
# Log                 (message, level=3, source='Scanners.bundle') # Log to PMS log.
# Unicodize           (s, lang)                                    # Safely return Unicode.
# CleanUpString       (s)                                          # Cleanup string.
# LevenshteinDistance (first, second)                              # Compute Levenshtein distance.
# LevenshteinRatio    (first, second)                              # Levenshtein ratio.
import Stack                                                       ### Plex Media Server\Plug-ins\Scanners.bundle\Contents\Resources\Common ###
# compareFilenames    (elem)                                       # ???
# Scan                (dir, files, mediaList, subdirs)             # Scan for stacked files
import VideoFiles                                                  ### Plex Media Server\Plug-ins\Scanners.bundle\Contents\Resources\Common ###
# def CleanName       (name)                                       # Cleanup folder / filenames
# def Scan            (path, files, mediaList, subdirs, root=None) # Remove files that aren't videos.
# def RetrieveSource  (name)                                       # ???
# def FindYear        (words)                                      # Find the first occurance of a year.
#from mp4file import mp4file, atomsearch                            ### Plex Media Server\Plug-ins\Scanners.bundle\Contents\Resources\Common\mp4file ###
# def getFileSize      (file)                                      # return the filesize of a file
# class Mp4File        file, atoms, AtomWithChildren               # mp4 class
import Media                                                       ### Plex Media Server\Plug-ins\Scanners.bundle\Contents\Resources\Common\Media.py ###
# class MediaRoot     name, year, type, released_at, display_offset, source, parts, subtitles, thumbs, arts, trailers, themes              
# class Movie         name, year, guid
# class Episode       show, season, episode, name, year = year, episodic = True
# class Track         artist, album, name, index, year, disc, album_artist, title, guid, album_guid, artist_guid, album_thumb_url, artist_thumb_url = artist_thumb_url
# class Photo         name

### regular Expressions and variables ################### http://www.zytrax.com/tech/web/regex.htm ### http://regex101.com/#python ####################
season_re_match = [                                                                                                           ### Season folder ### 
  'specials',                                                                                                                 # Season 0 / specials folder
  'season[ -_]?(?P<season>[0-9]{1,2}).*',                                                                                     # US - Season
  'series[ -_]?(?P<season>[0-9]{1,2}).*',                                                                                     # UK - Series
  'saison[ -_]?(?P<season>[0-9]{1,2}).*',                                                                                     # FR - Saison
  '(?P<season>[0-9]{1,2})a? Stagione+.*']                                                                                     # IT - Xa Stagiona
Series_re_search = [                                                                                                          ### Series Numbering ###
  '(^|(?P<show>.*?) )(?P<season>[0-9]{1,2})x(?P<ep>[0-9]{1-3})((x|_[0-9]{1,2}x)(?P<ep2>[0-9]{1,3}))?',                        #   1x01 | 1x01x02 | 1x01_1x02               - title ### # '1x01' # 'x02', '_1x02' # Episode title
  '(^|(?P<show>.*?) )s(?P<season>[0-9]{1,2})(e| e|ep| ep|-)(?P<ep>[0-9]{1,3})(([-_\.]|(e|ep)|[-_\. ](e|ep))(?P<ep2>[0-9]{1,3}))?',   # s01e01 | s01 e01 | s01-02 | s01ep02        - title ### (?P<show>.*?) # Show title # ([sS](?P<season>[0-9]{1,2})[\._ ]?) 's01', 's01.', 's01_', 's01 ' # (e|ep|-)(?P<ep>[0-9]+) # 'e01', 'ep01', '-01' # (([-_\.]|(e|ep)|[-_\. ](e|ep))(?P<ep2>[0-9]{1,3}))? # optional: '-02', 'e02', 'ep02', '-e02', '-ep02'
  '(^|(?P<show>.*?) )(?!Special|S)((e|ep) ?)?(?P<ep>[0-9]{1,3})((e|ep|-e|-ep|-| - )(?P<ep2>[0-9]{1,3})|$| .*)',               #    E01 | E01-E02 | E01-02 | E01E02        - title
  '(^|(?P<show>.*?) )(?P<ep>[0-9]{1,3})[\. -_]of[\. -_]+[0-9]{1,3}([^0-9a-zA-Z]|$)']                                          # 01 of 08 (no stacking for this one ?)
AniDB_re_search  = [                                                                                                          ### AniDB Specials numbering ###
  '(^|(?P<show>.*?) )(S|SP|SPECIAL|OAV) ?(?P<ep>\d{0,2})( .*|$)',                                                             # 001-099 Specials
  '(^|(?P<show>.*?) )(OP|NC ?OP|OPENING) ?(?P<ep>\d{0,2}[a-z]?)$',                                                            # 100-149 Openings
  '(^|(?P<show>.*?) )(ED|NC ?ED|ENDING) ?(?P<ep>\d{0,2}[a-z]?)$',                                                             # 150-199 Endings
  '(^|(?P<show>.*?) )(TRAILER|PROMO|PV|T)($| ?(?P<ep>\d{1,2}))',                                                              # 200-299 Trailer, Promo with a  number
  '(^|(?P<show>.*?) )(P|PARODY|PARODIES?) ?(?P<ep>\d{1,2})(.*)',                                                              # 300-399 Parodies
  '(^|(?P<show>.*?) )(O|OTHERS?) ?(?P<ep>\d{1,2})(.*)']; AniDBOffset = [0, 100, 150, 200, 300, 400]                           # 400-999 Others
roman_re_match ="(L?X{0,3})(IX|IV|V?I{0,3})$"  
#negative look-ahead assertion:    ^(?!tbd_).+
#negative look-behind assertion:  (^.{1,3}$|^.{4}(?<!tbd_).*) fixed width patters
#character sets and alternations:  ^([^t]|t($|[^b]|b($|[^d]|d($|[^_])))).*

ignore_dirs_re_findall  = [ 'lost\+found', '.AppleDouble','$Recycle.Bin', 'System Volume Information', 'Temporary Items',     # Filters.py  removed '\..*',        
'Network Trash Folder', 'Extras', 'Samples?', '^bonus', '.*bonus disc.*', 'trailers?', '@eaDir', '.*_UNPACK_.*', '.*_FAILED_.*']# Filters.py 
ignore_files_re_findall = ['[-\._ ]sample', 'sample[-\._ ]', '-Recap\.', 'OST', 'soundtrack']                                                      # Skipped files (samples, trailers)                                                          
ignore_ext_no_warning   = ['plexignore', 'ssa', 'srt', 'ass', 'jpg', 'png', 'gif', 'mp3', 'wav', 'flac', 'pdf', 'db', 'nfo', 'ds_store', 'txt', 'zip', 'ini']           # extensions dropped no warning (useless or list would be too long)
video_exts = [ '3g2', '3gp', 'asf', 'asx', 'avc', 'avi', 'avs', 'bin', 'bivx', 'bup', 'divx', 'dv', 'dvr-ms', 'evo', 'fli', 'flv', 'ifo', 'img', 'iso', 'm2t', 'm2ts', 'm2v',
  'm4v', 'mkv', 'mov', 'mp4', 'mpeg', 'mpg', 'mts', 'nrg', 'nsv', 'nuv', 'ogm', 'ogv', 'tp', 'pva', 'qt', 'rm', 'rmvb', 'sdp', 'svq3', 'strm', 'ts', 'ty', 'vdr', 'viv', 'vob',
  'vp3', 'wmv', 'wpl', 'wtv', 'xsp', 'xvid', 'divx', 'webm', 'swf']                         #

FILTER_CHARS   = "\\/:*?<>|~=._;"                                                                             # Windows file naming limitations + "~-,._" + ';' as plex cut title at this for the agent
CHARACTERS_MAP = {
  50048:'A'  , 50050:'A'  , 50080:'a'  , 50082:'a'  , 50084:'a'  , 50308:'A'  , 50309:'a'  ,                  #'à' ['\xc3', '\xa0'] #'â' ['\xc3', '\xa2'] #'À' ['\xc3', '\x80'] #'Â' ['\xc3', '\x82'] # 'Märchen Awakens Romance', 'Rozen Maiden Träumend'
  50055:'C'  , 50087:'c'  , 50310:'C'  , 50311:'c'  ,                                                         #'Ç' ['\xc3', '\x87'] #'ç' ['\xc3', '\xa7'] 
  50057:'E'  , 50088:'e'  , 50089:'e'  , 50090:'e'  , 50091:'e'  , 50328:'E'  , 50329:'e'  ,                  #'É' ['\xc3', '\x89'] #'è' ['\xc3', '\xa8'] #'é' ['\xc3', '\xa9'] #'ê' ['\xc3', '\xaa'] #'ë' ['\xc3', '\xab']
  50094:'i'  , 50095:'i'  , 50561:'L'  , 50562:'l'  , 50563:'N'  , 50564:'n'  , 50097:'n'  ,                  #'î' ['\xc3', '\xae'] #'ï' ['\xc3', '\xaf'] #'ñ' ['\xc3', '\xb1']
  50067:'O'  , 50072:'O'  , 50100:'o'  , 50099:'o'  , 50578:'OE' , 50579:'oe' ,                               # 'Ø' ['', '']        #'ô' ['\xc3', '\xb4'] #'Œ' ['\xc5', '\x92'] #'œ' ['\xc5', '\x93']
  50586:'S'  , 50587:'s'  , 50079:'ss' , 50105:'u'  , 50107:'u'  , 49842:'²'  , 49843:'³'  ,                  # 'ß' []              #'ù' ['\xc3', '\xb9'] #'û' ['\xc3', '\xbb'] #'²' ['\xc2', '\xb2'] #'³' ['\xc2', '\xb3']
  50617:'Z'  , 50618:'z'  , 50619:'Z'  , 50620:'z'  , 49835:'«'  , 49851:'»'  , 49853:'1-2',                  #'«' ['\xc2', '\xab'] #'»' ['\xc2', '\xbb']# 'R/Ranma ½ Nettou Hen' 
  14844057:"'"  , 14844051:'-'  , 14844070:''   , 15711386:':'  , 14846080:'∀'}                              #['’' \xe2\x80\x99] ['–' \xe2\x80\x93] ['…' \xe2\x80\xa6] # '：' # 12770:'', # '∀ Gundam' no need

whack = [                                                                                                     ### Tags to remove ###
  'x264', 'h264', 'h.264',  'dvxa', 'divx', 'xvid', 'divx', 'divx51', 'divx5.1', 'mp4',                       # Video Codecs
  'ogg','ogm', 'vorbis','aac','dts', 'ac3', '5.1ch','5.1', '7.1ch',                                           # Audio Codecs, channels
  '480p', '576p', '720p', '1080p', '1080i', '1920x1080','1280x720',                                           #       Resolution
  'hi10', 'hi10p', '10bit', 'crf24',  'crf 24',                                                               #       color depth and encoding
  '24fps', '25fps', 'ntsc','pal', 'ntsc-u', 'ntsc-j',                                                         # Refresh rate, Format
  'dc','se', 'extended', 'unrated', 'multi','multisubs', 'dubbed','subbed',                                   # edition (dc = directors cut, se = special edition), subs and dubs
  'limited', 'custom', 'internal', 'repack', 'proper', 'rerip', "raw", "remastered",                          # format
  'retail', 'webrip','web-dl', 'wp','workprint',                                                              # release type: retail, web, work print
  'cd1', 'cd2', 'cd3', 'cd4', '1cd', '2cd', '3cd', '4cd', 'xxx', 'nfo', 'read.nfo', 'readnfo', 'nfofix',      # misc 1
  'fragment','ps3avchd','remux','fs','ws', "- Copy",                                                          # misc 2
  'bdrc','bdrip','bluray','bd','brrip','hdrip','hddvd','hddvdrip',                                            # Source: bluray
  'ddc','dvdrip','dvd','r1','r3','r5',"dvd",'svcd','vcd',                                                     # DVD, VCD, S-VCD
  'dsr','dsrip','hdtv','pdtv','ppv','stv','tvrip','complete movie',                                           # dtv, stv
  'cam','bdscr','dvdscr','dvdscreener','scr','screener','tc','telecine','ts','telesync',                      # screener
  "5Banime-koi_5d", "%5banime-koi%5d", "minitheatre.org", "mthd", "thora",                 #
  "nn92", "kris1986k_vs_htt91", "mthd", "mthd bd dual","elysium", "encodebyjosh", "bd"]            #

### Log function ########################################################################################
global LOG_FILENAME
LOG_FILENAME     = 'Plex Media Scanner (custom ASS).log'
PLEX_LIBRARY_URL = "http://127.0.0.1:32400/library/sections/?X-Plex-Token=ACCOUNT_TOKEN_HERE"   #https://support.plex.tv/hc/en-us/articles/204059436-Finding-your-account-token-X-Plex-Token
try:      platform = sys.platform.lower()                                                       # sys.platform: win32 | darwin | linux2, 
except:                                                                                         #
  try:    platform = Platform.OS.lower()                                                        # Platform.OS:  Windows, MacOSX, or Linux #  
  except: platform = ""                                                                         #
if   (platform == 'win32'  or platform == 'windows'):
  LINE_FEED = "\r\n"; 
  LOG_PATHS = [ '%LOCALAPPDATA%\\Plex Media Server\\Logs',                                      # Windows 8
                '%USERPROFILE%\\Local Settings\\Application Data\\Plex Media Server\\Logs' ]
elif (platform == 'darwin' or platform == 'macosx'):
  LINE_FEED = "\r"
  LOG_PATHS = [ '$HOME/Library/Application Support/Plex Media Server/Logs' ]
elif 'linux' in platform:
  LINE_FEED = "\n"
  LOG_PATHS = [ '$PLEX_HOME/Library/Application Support/Plex Media Server/Logs',                 #Linux
                '/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Logs',   #Debian, Fedora, CentOS, Ubuntu
                '/usr/local/plexdata/Plex Media Server/Logs',                                    #FreeBSD
                '/usr/pbi/plexmediaserver-amd64/plexdata/Plex Media Server/Logs',                #FreeNAS
                '/c/.plex/Library/Application Support/Plex Media Server/Logs',                   #ReadyNAS
                '/share/MD0_DATA/.qpkg/PlexMediaServer/Library/Plex Media Server/Logs',          #QNAP
                '/volume1/Plex/Library/Application Support/Plex Media Server/Logs',              #Synology, Asustor
                '/volume2/Plex/Library/Application Support/Plex Media Server/Logs' ]             #Synology, if migrated a second raid volume as unique volume in new box         
else:
  LINE_FEED = "\n"
  LOG_PATHS = [ '$HOME' ]                                                                        #home folder as backup "C:\users\User.Machine" in windows 8, "users\Plex" on synology
for folder in LOG_PATHS:
  LOG_PATH = os.path.expandvars(folder)
  if os.path.isdir(LOG_PATH):  break
else: LOG_PATH = os.path.expanduser('~')

def Log(entry, filename=""): ### Allow to log to the same folder Plex writes its logs in #############################################
  if filename=="":  global LOG_FILENAME
  with open(os.path.join(LOG_PATH, LOG_FILENAME if filename=="" else filename), 'a') as file:
    file.write( entry + LINE_FEED)
    print entry     # when ran from console for entry in error_log[log]:

### Allow to display ints even if equal to None at times ################################################
def xint(s): 
  return str(s) if s is not None and not s=="" else "None"

### Convert Roman numerals ##############################################################################
def roman_to_int(string):                                    # Regex for matching #M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})
  roman_values=[['X',10],['IX',9],['V',5],['IV',4],['I',1]]  # ['M',1000],['CM',900],['D',500],['CD',400],['C',100],['XC',90],['L',50],['XL',40]
  result = 0
  string = string.upper()
  for letter, value in roman_values: #is you use {} the list will be in the wrong order
    while string.startswith(letter):
      result += value
      string = string[len(letter):]
  return str(result)

### Return number of bytes of Unicode characters ########################################################
def unicodeLen (char):                         # count consecutive 1 bits since it represents the byte numbers-1, less than 1 consecutive bit (128) is 1 byte , less than 23 bytes is 1
  for x in range(0,5):                         # start at 0, 5 times 
    if ord(char) < 256-pow(2, 6-x): return x+1 #     2pow(x) with x(7->0) = 128 064 032 016 008 004 002 001
  return 6                                     # 256-2pow(x) with x(7->0) = 128 192 224 240 248 252 254 255 = 1 to 8 bits at 1 from the left, 256-2pow(7-x) starts form left

### Decode string back to Unicode ###   #Unicodize in utils?? #fixEncoding in unicodehelper
def encodeASCII(string, language=None): #from Unicodize and plex scanner and other sources
  ranges = [
    {"from": ord(u"\u3300"),     "to": ord(u"\u33ff")},     # compatibility ideographs
    {"from": ord(u"\ufe30"),     "to": ord(u"\ufe4f")},     # compatibility ideographs
    {"from": ord(u"\uf900"),     "to": ord(u"\ufaff")},     # compatibility ideographs
    {"from": ord(u"\u30a0"),     "to": ord(u"\u30ff")},     # Japanese Kana
    {"from": ord(u"\u2e80"),     "to": ord(u"\u2eff")},     # cjk radicals supplement
    {"from": ord(u"\u4e00"),     "to": ord(u"\u9fff")},
    {"from": ord(u"\u3400"),     "to": ord(u"\u4dbf")},
    {"from": ord(u"\U00020000"), "to": ord(u"\U0002a6df")},
    {"from": ord(u"\U0002a700"), "to": ord(u"\U0002b73f")},
    {"from": ord(u"\U0002b740"), "to": ord(u"\U0002b81f")},
    {"from": ord(u"\U0002b820"), "to": ord(u"\U0002ceaf")}, # included as of Unicode 8.0
    {"from": ord(u"\U0002F800"), "to": ord(u"\U0002fa1f")}  # compatibility ideographs
  ] #def is_cjk(char):  return any([range["from"] <= ord(char) <= range["to"] for range in ranges])
  if string=='': return ""
  encoding  = ord(string[0])
  encodings = ['iso8859-1', 'utf-16', 'utf-16be', 'utf-8']
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
  string = list(string)
  i = 0
  while i < len(string):
    if ord(string[i])<128:  i = i+1
    else: #non ascii char
      char = 0; char2 = ""; char3 = []
      char_len = unicodeLen(string[i])
      for x in range(0, char_len):
        char = 256*char + ord(string[i+x]); char2 += string[i+x]; char3.append(string[i+x])
        if not x==0: string[i] += string[i+x]; string[i+x]='' #string[i+x] = ''
      if char in CHARACTERS_MAP:  string[i]=CHARACTERS_MAP.get( char )
      elif not any([mapping["from"] <= ord("".join(char3).decode('utf8')) <= mapping["to"] for mapping in ranges]):  Log("*Character missing in CHARACTERS_MAP: %d:'%s'  , #'%s' %s, string: '%s'" % (char, char2, char2, char3, string))
      i += char_len
  return ''.join(string)
  
### Allow to display ints even if equal to None at times ################################################
def clean_filename(string):
  if not string: return ""
  if "["     in string:  string = re.sub(r'\[.*?\]', '', string)                                # remove "[xxx]" groups as Plex cleanup keep inside () but not inside []
  if "{"     in string:  string = re.sub(r'\{.*?\}', '', string)                                # remove "{xxx}" groups as Plex cleanup keep inside () but not inside []
  if ", The" in string:  string = "The " + ''.join( string.split(", The", 1) )
  if "`"     in string:  string = string.replace("`", "'")                                      # translate anidb apostrophes into normal ones #s = s.replace('&', 'and')       
  for char in  FILTER_CHARS:  string = string.replace(char, ' ')                                # replace os forbidden chars with spaces
  try:   string.decode('ascii')                                                                 # If string have non-ASCII characters
  except UnicodeDecodeError:  string=encodeASCII(string)                                        # Translate them
  words  = string.split(" ")                                                                    # Split in words
  for word in words:                                                                            # For each word
    if word.lower() in whack:  words.remove(word)                                               # remove if in blacklist #Log("word: '%s', words: '%s', rx: '%s'" % (word, str(words), rx))
  string = " ".join(words).strip()
  string = " ".join(string.split())#   # Also avoid multiple spaces, hence doing transpositions first
  for rx in ("- ", " -", "-" ):
    if string.startswith(rx):  string=string[  len(rx):]
    if string.endswith(  rx):  string=string[:-len(rx) ]
  if len(string)>1 and string[0].lower()=='e' and string[1].isdigit(): string = string[1:]
  for rx in ("ep ", "ep", "e ", "e", "tv "):
    if string.lower().startswith(rx) and len(string)>=len(rx) and string[len(rx)].isdigit():
      string=string[len(rx):]
      break
  string = string.strip()
  for rx in ("v2", "v3"):
    if string.lower().endswith(rx):
      string=string[:-len(rx)]
      break
  return string.strip()

### Add files into Plex database ########################################################################
def add_episode_into_plex(mediaList, files, file, path, show, season=1, episode=1, episode_title="", year=None, ep2 = None, text=""):
  if ep2 is None: ep2 = episode
  for epn in range(episode, ep2+1):
    tv_show                = Media.Episode(show, season, epn, episode_title, year)
    tv_show.display_offset = (epn-episode)*100/(ep2-episode+1)
    tv_show.parts.append(file)
    mediaList.append(tv_show)
  Log(text)
  Stack.Scan(path, files, mediaList, [])

### Turn a string into a list of string and number chunks  "z23a" -> ["z", 23, "a"] ###############################################################################
#def natural_keys(s):
# return [ try int(c) for c in re.split('([0-9]+)', s) ]
def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
  return [int(text) if text.isdigit() else text.lower() for text in re.split(_nsre, s)]
  
    ### Add files into array ################################################################################
def explore_path(root, subdir, file_tree, plexignore_files=[], plexignore_dirs=[]):
  fullpath=os.path.join(subdir, ".plexignore")
  if os.path.isfile(fullpath):
    with open( fullpath, 'r') as plexignore:                                                     # Log(".plexignore")
      for pattern in plexignore:                                                                 #
        pattern = pattern.strip()                                                                # remove useless spaces at both ends
        if pattern == '' or pattern[0] == '#': continue                                          # skip comment and emopy lines, go to next for iteration
        if '/' not in pattern:  plexignore_files.append(fnmatch.translate(pattern))              # patterns for this folder gets converted and added to files.
        elif pattern[0] != '/': plexignore_dirs.append(pattern)                                  # patterns for subfolders added to folders
    Log("Plexignore: '%s', files: '%s', dir: '%s' (include inherited ones)" % (fullpath[len(root):], plexignore_files, plexignore_dirs))  
  files=[]; dirs=[]                                                                              ### Process all files and folders ###
  for item in os.listdir(subdir):                                                                # Loop current folder files and folders
    fullpath     = os.path.join(subdir, item)
    if os.path.isdir (fullpath ):                                                                ### dirs
      for rx in ignore_dirs_re_findall:                                                          # Loop through unwanted folders list
        if re.findall(rx, item): ###recode var, if rx in item:
          Log("Folder:     '%s' match ignore_dirs_re_findall '%s'" % (fullpath[len(root):], rx))
          break                                                                                  # If folder in list of skipped folder exit this loop  #if len(result):  break
      else:  dirs.append(fullpath)                                                               # .plexignore subfolder restrictions management
    else:
      for rx in ignore_files_re_findall+plexignore_files:                                        # Filter trailers and sample files
        if re.findall(rx, item): 
          if rx in ignore_files_re_findall: Log("File:       '%s' match ignore_files_re_findall: '%s'" % (fullpath[len(root):], rx))
          else:                             Log("File:       '%s' match plexignore_files: '%s'"        % (fullpath[len(root):], rx))
          break                                                                                  #Log("'%s' ignore_files_findall: match" % item)
      else: #ignore_ext_no_warning
        if   '.' in item and item.lower().rsplit('.', 1)[1] in video_exts:                 files.append(fullpath)                              ### item is a file   
        elif '.' in item and item.lower().rsplit('.', 1)[1] not in ignore_ext_no_warning:  Log("File:       '%s' extension not in video_exts" %(fullpath[len(root):]))                                        ### files
  dirs.sort(); files.sort(key=natural_sort_key)
  for item in dirs:
    plexignore_recursive_files=[]; plexignore_recursive_dirs =[]                                 # Split recursive entries, this one for next folder's subfolders
    for rx in plexignore_dirs:                                                                   # On each patter string
      pattern = rx.split("/")                                                                    # Create array splitting by / so all folders separated and patter last
      if pattern[0].lower() == Utils.SplitPath(item)[-1].lower():                                # first folder the same
        if len(pattern) == 2: plexignore_recursive_files.append(fnmatch.translate(pattern[1]))   # One folder, for next folder current files
        if len(pattern) >= 3: plexignore_recursive_dirs.append( "",join(pattern[1:]))            # 2+ folders, for next folder subfolders
    explore_path(root, item, file_tree, plexignore_recursive_files, plexignore_recursive_dirs)   # call next folder and will inherit restrictions
  if not files == []:  file_tree[subdir] = files    

### Look for episodes ###################################################################################
def Scan(path, files, mediaList, subdirs, language=None, root=None, **kwargs):
  if not path == "":
    #Log("=== Scan called: ========================================================================")
    #Log("Root: \"%s\", Path: \"%s\", subdirs: \"%s\", mediaList: \"%s\"" % (root, path, subdirs, str(mediaList)))
    return 0# Exit every other iteration than the root scan

  ### Rename log file with library name if XML file can be accessed ###
  global LOG_FILENAME
  try:
    result = urllib2.urlopen(PLEX_LIBRARY_URL)
    if result is not None: Log(str(result.getcode()))
    string = result.read()
  except:
    if "ACCOUNT_TOKEN_HERE" not in PLEX_LIBRARY_URL:  Log("except http library xml - Token replaced in source code but still fails")
  else:
    library_xml = etree.fromstring(string)
    for library in library_xml.iterchildren('Directory'):
      for library_root in library.iterchildren('Location'):
        if library_root.get("path") == root:  #if root path match the scanner, we have the libray name for which the scanner is ran
          LOG_FILENAME = LOG_FILENAME[:-4] + " - " + library.get("title") + LOG_FILENAME[-4:]
          break       # found, break second loop
      else: continue  # next iteration of first loop, if second loop wasn't broken, therefound found nothing
      break           # break first loop if second loop was broken, #cascade-break
    else: Log("except http library xml - No library name to append at end of log filename despite access to file. Please forward to developer xml: '%s' " % PLEX_LIBRARY_URL)

  Log("=== Scan ================================================================================================================")
  Log("Log path: \"%s\"" % LOG_PATH)
  Log("Root:     \"%s\", Platform: \"%s\"" % (root, platform))  
  Log("--- Skipped mediums -----------------------------------------------------------------------------------------------------")
  file_tree = {}                                           # initialize file_tree
  explore_path(root, root, file_tree)                      # initialize file_tree with files on root  #for path in sorted(file_tree):  Log("\"%s\"" % file_tree[path]) 
  Log("=========================================================================================================================")
  for path in sorted(file_tree):                           # Loop to add all series while on the root folder Scan call, which allows subfolders to work
    subdirs      = []                                      # Recreate normal scanner coding: subfolders empty
    files        = file_tree[path]                         #
    path         = path.replace(root, "")                  # Recreate normal scanner coding: path is relative to root
    if path.startswith("/"):  path = path[1:]              # Recreate normal scanner coding: path doesn't start with "/"   
    reverse_path  = Utils.SplitPath(path)                  # Take top two as show/season, but require at least the top one, and reverse them
    reverse_path.reverse()                                 # Reverse the order of the folders
   
    ### bluray folder management ###
    # source: https://github.com/doublerebel/plex-series-scanner-bdmv/blob/master/Plex%20Series%20Scanner%20(with%20disc%20image%20support).py
    if len(reverse_path) >= 3 and reverse_path[0].lower() == 'stream' and reverse_path[1].lower() == 'bdmv':
      for rx in episode_re_search[0:-1]:
        match = re.search(rx, reverse_path[2], re.IGNORECASE)
        if match:
          episode    = int(match.group('ep'))
          endEpisode = int(match.group('secondEp')) if match.groupdict().has_key('secondEp') and match.group('secondEp') else episode
          show, year = VideoFiles.CleanName( match.group('show') )
          if len(show) > 0:
            for ep in range(episode, endEpisode+1):
              tv_show                = Media.Episode(show, int(match.group('season')), ep, '', year)
              tv_show.display_offset = (ep-episode)*100/(endEpisode-episode+1)
              for i in files:  tv_show.parts.append(i)
            mediaList.append(tv_show)
            Log("show: '%s', year: '%s', season: '%2s', ep: %3s found using Bluray convention (bdmv/stream)" % (show, xint(year), str(int(match.group('season'))), xint(episode)) )
            break
      else: Log("*no show found for ep: '%s', folder_show: '%s' using Bluray convention (bdmv/stream)" % (episode, folder_show))
      continue
      
    ### DVD folder support ###
    if   'video_ts.ifo' in files:  video_ts = os.path.join(subdir, 'video_ts.ifo')
    elif 'video_ts.bup' in files:  video_ts = os.path.join(subdir, 'video_ts.bup')
    else:                          video_ts = None
    if len(reverse_path) >= 1 and len(reverse_path[0]) > 0 and video_ts is not None:
      ep = reverse_path[0]
      if len(reverse_path)>1:  reverse_path.remove(ep)
      Log("DVD folder detected - ep: '%s', video_ts: '%s', reverse_path: '%s'" % (ep, video_ts, reverse_path[0]))
      
    ### Check if folder is a season folder and remove it do reduce complexity ###
    folder_year   = None
    folder_season = None
    for folder in reverse_path[:-1]:                   # remove root folder from test, [:-1] Doesn't thow errors but gives an empty list if items don't exist, might not be what you want in other cases
      for rx in season_re_match :                      # in anime, more specials folders than season folders, so doing it first
        match = re.match(rx, folder, re.IGNORECASE)
        if match:
          folder_season = int( match.group('season')) if match.groupdict().has_key('season') else 0    #use "if var is | is not None:" as it's faster than "==None" and "if var:" is false if the variable is: False, 0, 0.0, "", () , {}, [], set()
          reverse_path.remove(folder)                                                                  #All ways to remove: reverse_path.pop(-1), reverse_path.remove(thing|array[0])
          break
      if match: break  #Breaking second for loop doesn't exist parent for / else: continue then break nex line would also work
    folder_show = clean_filename( reverse_path[0] )
    Log("Path: \"%s\", show: \"%s\"%s" % (path, folder_show, ", Season: \"%d\"" % (folder_season) if folder_season is not None else "") )
     
    ### Main File loop to start adding files now ###
    AniDB_op = {}
    for file in files:                                                   # "files" is a list of media files full path, File is one of the entries
      filename = os.path.basename(file)                                  # strip the folders
      show     = folder_show                                             #
      year     = folder_year                                             # Get the year before all '()' are stripped drom the filename without the extension  ### Year? ###  #if re.match('.+ \([1-2][0-9]{3}\)', paths[-1]): #misc, year      = VideoFiles.CleanName(filename_no_ext)
      season   = 1 if folder_season is None else folder_season           #
      ep = ep2 = clean_filename(os.path.splitext(filename)[0])           # Strip [], all, ep contain the serie name and ep number for now
      
      if len(files)==1 and (ep==folder_show or "movie" in ep.lower()+folder_show.lower() or "gekijouban" in folder_show.lower()):  ep = ep2 = "01" ### Movies ###
      else:  ### Cleanup episode filename If parent Folder contain serie name ###
        if folder_season and ep.startswith("s%2d "  % folder_season):  ep =  ep.replace("s%2d "  % folder_season, "")
        if folder_season and ep.startswith("s%02d " % folder_season):  ep =  ep.replace("s%02d " % folder_season, "")
          
        folder_use = False                                                 # Bolean to keep track if folder name in case it is included in the filename
        if folder_show is not None and not folder_show=="":                # If containing folder exist or has name different from "_" (scrubed to "")
          if folder_show.lower() in ep.lower() or ep.replace(" ", "").lower() in folder_show.replace(" ", "").lower():
            misc = ep.lower().replace(folder_show.lower(), '')               # remove cleaned folder name (if exist) from the show name
            if len(misc)==len(ep):  junk = ep.replace(" ", "").lower().replace(folder_show.replace(" ", "").lower(), '') # misc = ep.replace(folder_show, "")         # remove cleaned folder name (if exist) from the show name
            if len(misc)>2 and misc.lower().startswith('s '):  misc = misc[2:]
            if len(misc) < len(ep) or len(junk)<len(ep.replace(" ", "").lower()):                 # And remove the cleaned folder name from the now cleaned show, just in case the directory is off by things CleanName handles
              ep         = misc                                              # Removed folder serie name from episode filename
              folder_use = True                                              # indicate to latter use folder name since it is present in filename
        if "(" in ep:  ep = re.sub(r'\(.*?\)', '', ep)                     # remove "(xxx)" groups, not in clean as i want to keep (year) in some titles
        ep = ep2 = clean_filename(ep)                                      #misc = ep.rsplit(' ', 1) #if misc in folder_show: folder_use = True, if len(misc)>1,  ep.rsplit(' ', 1)[1] 
        
        ### if format "Serie - 001 - Episode Title .ext" or serie name in filename and only ep number left ###
        if ep.lower().startswith("special") or ep.lower().startswith("picture drama") or ep.lower().startswith("omake"):  season = 0
        words=ep.split(' - ',3)
        if len(words)==1: words=ep.split(' ')
        if len(words)>1: #2 or 3, if using naming convention, will have removed serie name
          misc = " ".join( [clean_filename(os.path.basename(file)) for file in files])
          for word in words:
            word2 = clean_filename(word)
            if word2.isdigit() or len(word2)>1 and word2[1:].isdigit() or len(word2)>2 and word2[2:].isdigit(): 
              if misc.count(word2)>3:  continue #number part of filename
              if words.index(word) ==1 and not folder_use and words[0].lower() not in ("special", "oav", "movie"):  show   = words[0]  # Use local name if folder name NOT contained in finename
              ep = ep2 = word2
              break
        if ep=="":  ep=ep2="01"
      if ep.isdigit():
        if season==1 and int(ep)==0:  episode="01"; season=0
        add_episode_into_plex(mediaList, files, file, path, show, season, int(ep), "", year, int(ep2), "show: \"%s\" s%02de%03d \"%s\" \"%s\"" % (show, int(season), int(ep), ep, filename))
        continue
        
      ### Check for Series_re_search + AniDB_re_search ###
      old_ep = ep
      for rx in Series_re_search + AniDB_re_search:
        match = re.search(rx, ep, re.IGNORECASE)
        if match:
          ep = ep2 = match.group('ep') if match.groupdict().has_key('ep') and match.group('ep') is not None and not match.group('ep')=="" else "01"
          if rx in AniDB_re_search:
            season = 0 # AniDB Specials are season 0
            offset = AniDBOffset [ AniDB_re_search.index(rx) ]                        # 100 for OP, 150 for ED
            if not ep.isdigit() and len(ep)>1 and ep[:-1].isdigit():                  ### OP/ED with letter version Example: op2a
              AniDB_op [ offset + int(ep[:-1]) ] = ord( ep[-1:].lower() ) - ord('a')  # {100: 0 for a/1 for b} ...  #Log("AniDB Opening?, ep: '%d', '%d', '%d', '%s'" % (int( match.group('ep')[:-1] ), int(match.group('ep')[-1:]) , str(AniDB_op)))
              offset                            += sum( AniDB_op.values() )           # sum( AniDB_op.vlaues())[key] for key in AniDB_op )
              ep = ep2 = str( int( ep[:-1] ) )                               # "if xxx isdigit() else 1" implied since OP1a for example...
            ep = ep2 = str( offset + int(ep))
          else: #rx in Series_re_search:
            if match.groupdict().has_key('ep2'   ) and match.group('ep2'   ) and match.group('ep2'   ).isdigit():  ep2    = match.group('ep2') 
            if match.groupdict().has_key('season') and match.group('season') and match.group('season').isdigit():  season = int(match.group('season'))
            if match.groupdict().has_key('show'  ) and match.group('show'  ) and not folder_use:                   show   = clean_filename( match.group('show'))
            elif not folder_use and not ep[:ep.find(match.group('ep'))].rstrip()=="":                              show   = clean_filename( ep[:ep.find(match.group('ep'))].rstrip() ) # remove eveything from the episode number
            if not (show=="" or "special" in show.lower()): 
              if show.rfind(" ") != -1 and show.rsplit(' ', 1)[1] in ["ep", "Ep", "EP", "eP", "e", "E"]:  show = show.rsplit(' ', 1)[0] # remove ep at the end
            if int(ep)==0:  episode="01"; season=0          
          add_episode_into_plex(mediaList, files, file, path, show, season, int(ep), "", year, int(ep2), "show: \"%s\" s%02de%03d%s \"%s\" \"%s\", rx: \"%s\"" % (show, int(season), int(ep), "" if ep==ep2 else "-%03d" % int(ep2), old_ep, filename, rx))          #add_episode_into_plex(mediaList, files, file, show, season, ep, "", year, ep2, "show: '%s' (%s) s%02de%03d%s on '%s' from '%s'" % (show, xint(year), int(season), ep, "" if ep==ep2 else "-"+str(ep2), rx, filename))
          break
      if match: continue
     
      ### Roman numbers ### doesn't work is ep title present
      ep_nb = clean_filename(ep if ' ' in ep else ep.rsplit(' ', 1)[1]) # If there is no space (and ep title) / If there is a space ep_nb is the last part hoping there is no episode title
      match = re.match(roman_re_match, ep_nb, re.IGNORECASE)
      if match:
        ep_nb = roman_to_int(ep_nb)
        add_episode_into_plex(mediaList, files, file, folder_show, 1, int(ep_nb), "", year, None, "show: \"%s\" s%02de%03d \"%s\" \"%s\" rx: \"%s\"" % (folder_show, 1, int(ep_nb), ep, filename, roman_re_match))
        continue
      
      Log("*no show found for ep: \"%s\", filename: \"%s\"" % (ep, filename))
    Log("-------------------------------------------------------------------------------------------------------------------------")
    Stack.Scan(path, files, mediaList, subdirs)
  Log("")  #  time.strftime("%H:%M:%S")   # VideoFiles.Scan(path, files, mediaList, subdirs, root) # Filter out bad stuff and duplicates.
if __name__ == '__main__':
  print "Absolute Series Scanner command line execution"
  path  = sys.argv[1]; files = [os.path.join(path, file) for file in os.listdir(path)]; media = []
  Scan(path[1:], files, media, [])
  print "Media:", media
