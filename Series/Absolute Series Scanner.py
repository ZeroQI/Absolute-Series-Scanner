# -*- coding: utf-8 -*-
# Most code here is copyright (c) 2010 Plex Development Team. All rights reserved.
# Modified by ZeroQI from BABS scanner: https://forums.plex.tv/index.php/topic/31081-better-absolute-scanner-babs/

__author__     = "Benjamin Brisson (ZeroQI)"
__maintainer__ = "Benjamin Brisson (ZeroQI)"
__email__      = "benjamin.brisson@gmail.com"
__credits__    = ["Benjamin Brisson (ZeroQI)", "Plex original scanner code", "BABS"]
__copyright__  = "Copyright 2013-2015"
__license__    = "GPLv2"
__version__    = "1.0"
 
 
import sys                       # titlecase , datetime
import unicodedata               #
import os                        # Python       - os.uname, os.listdir
import os.path                   # Python       - os.path.basename, os.path.splitext, os.path.join, os.path.expandvars, os.path.expanduser, os.path.isdir, os.path.isfile
import re                        # Python       - re.findall, re.match, re.sub, re.search
import fnmatch                   # Python       - fnmatch used by .plexignore regex
import string                    # Python       - string
import time                      # Python       - 
import Utils                     # Plex library - Utils - Utils.SplitPath
import Media                     # Plex library - ALL   - Media.Episode, 
import Stack                     # Plex library - VIDEO - Stack
import VideoFiles                # Plex library - VIDEO - VideoFiles.Scan
from mp4file import mp4file, atomsearch
 
### regular Expressions and variables ################### http://www.zytrax.com/tech/web/regex.htm ### http://regex101.com/#python ####################
video_exts = ['3g2', '3gp', 'asf', 'asx', 'avc', 'avi', 'avs' , 'bin', 'bivx', 'bup', 'divx', 'dv' , 'dvr-ms',#
  'evo' , 'fli', 'flv', 'ifo', 'img', 'iso', 'm2t', 'm2ts', 'm2v', 'm4v' , 'mkv', 'mov' , 'mp4', 'mpeg'  ,    #
  'mpg' , 'mts', 'nrg', 'nsv', 'nuv', 'ogm', 'ogv', 'tp'  , 'pva', 'qt'  , 'rm' , 'rmvb', 'sdp', 'svq3'  ,    #
  'strm', 'ts' , 'ty' , 'vdr', 'viv', 'vob', 'vp3', 'wmv' , 'wpl', 'wtv' , 'xsp', 'xvid', 'webm']             #

ignore_dirs_re_findall  = ['[Ee]xtras?', '!?[Ss]amples?', '[Bb]onus', '.*[Bb]onus disc.*', '!?[Tt]railers?',  # Skipped folders
  '@eaDir', '.*_UNPACK_.*', '.*_FAILED_.*', 'lost\+found', '.AppleDouble',                                    # Filters.py  '\..*', 
  '\$Recycle.Bin', 'System Volume Information', 'Temporary Items', 'Network Trash Folder']                    # Filters.py 
season_re_match         = [                                                                                   ### Season folder ### 
  '.*?(SEASON|Season|season)[ -_]?(?P<season>[0-9]+).*',                                                      # US - Season
  '.*?(SERIES|Series|series)[ -_]?(?P<season>[0-9]+).*',                                                      # UK - Series
  '.*?(SAISON|Saison|saison)[ -_]?(?P<season>[0-9]+).*',                                                      # FR - Saison
  '(?P<season>[0-9]{1,2})a? Stagione+.*']                                                                     # IT - Xa Stagiona
specials_re_match = ['(SPECIALS|Specials|specials)']                                                          # Specials

ignore_files_re_findall = ['[-\._ ]sample', 'sample[-\._ ]', '-Recap\.', '.DS_Store', 'Thumbs.db']            # Skipped files (samples, trailers)                                                          
episode_re_search = [                                                                             ### Episode search ###
  '(?P<show>.*?)[sS](?P<season>[0-9]+)[\._ -]*(e|E|ep|Ep|x)(?P<ep>[0-9]+)[-._x]((E|e|ep)(?P<secondEp>[0-9]+))?', # S03E04-E05, S03E04E05, S03e04-05,  
  '(?P<show>.*?)[sS](?P<season>[0-9]{2})[\._\- ]+(?P<ep>[0-9]+)',                                             # S03-03
  '(?P<show>.*?)([^0-9]|^)(?P<season>[0-9]{1,2})[Xx](?P<ep>[0-9]+)(-[0-9]+[Xx](?P<secondEp>[0-9]+))?'         # 3x03
  ]                                                                                                      
standalone_episode_re_findall = [                                                                             ### Episode Search standalone ###
  '(.*?)( \(([0-9]+)\))? - ([0-9]+)+x([0-9]+)(-[0-9]+[Xx]([0-9]+))?( - (.*))?',                               # Newzbin style, no _UNPACK_
  '(.*?)( \(([0-9]+)\))?[Ss]([0-9]+)+[Ee]([0-9]+)(-[0-9]+[Xx]([0-9]+))?( - (.*))?'                            # standard s00e00
  ]                                                                                                       
just_episode_re_search        = [                                                                             ### Episode search no show name ###
  '(?P<ep>[0-9]{1,3})[\. -_]of[\. -_]+[0-9]{1,3}([^0-9]|$)',                                                  # 01 of 08 (no stacking for this one ?)
  '^(?P<ep>[0-9]{1,3})([^0-9]|$)',                                                                            # 01
  '(^|[ \.\-_])e(p? ?|(pisode){0,1})[ \.\-_]*(?P<ep>[0-9]{1,3})([^0-9]|$)',                                   # ep234 or Ep 126
  '.*?[ \.\-_](?P<ep>[0-9]{1,3})([^0-9]|$)+',                                                                 # Flah - 04 - Blah
  '.*?[ \.\-_](?P<ep>[0-9]{1,3})$',                                                                           # Flah - 04
  '.*?[^0-9x](?<!OP)(?<!ED)(?P<ep>\d{1,3})([^0-9]|$)',                                                        # Flah 107 as long as it isn't preceded by op, ed
  '^[^\-]*\-[ ]*(?P<ep>[0-9]{1,3})[ ]*\-.+$'                                                                  # Byousoku 5 Centimeter - 1 - The Chosen Cherry Blossoms - [RAW](3d312152) ###by TiS
  ]   
AniDB_re_search   = [                                                                                         ### AniDB Specials numbering ###
  ["(?P<show>.*?)(S|SP|SPECIALS?) ?(?P<ep>\d{1,2})(.*)",           0],                                        # 001-099 Specials
  ["(?P<show>.*?)(NC ?)?(OP|OPENING) ?(?P<ep>\d{0,2})(.*)",      100],                                        # 100-149 Openings
  ["(?P<show>.*?)(NC ?)?(ED|ENDING) ?(?P<ep>\d{0,2})(.*)",       150],                                        # 150-199 Endings
  ["(?P<show>.*?)(TRAILER|PROMO|PV|T|PV) ?(?P<ep>(\d{1,2}|$))",  200],                                        # 200-299 Trailer, Promo with a  number
  ["(?P<show>.*?)(TRAILER|PROMO|PV)$",                           200],                                        #         Trailer, Promo without number
  ["(?P<show>.*?)(P|PARODY|PARODIES?) ?(?P<ep>\d{1,2})(.*)",     300],                                        # 300-399 Parodies
  ["(?P<show>.*?)(O|OTHERS?) ?(?P<ep>\d{1,2})(.*)",              400]                                         # 400-999 Others
]
date_regexps = [                                                                                              ### Date format ###
  '(?P<year>[0-9]{4})[^0-9a-zA-Z]+(?P<month>[0-9]{2})[^0-9a-zA-Z]+(?P<day>[0-9]{2})([^0-9]|$)',               # 2009-02-10
  '(?P<month>[0-9]{2})[^0-9a-zA-Z]+(?P<day>[0-9]{2})[^0-9a-zA-Z(]+(?P<year>[0-9]{4})([^0-9a-zA-Z]|$)',        # 02-10-2009
  ]
whackRx = [                                                                                                   ### Tags to remove ###
  '([hHx][\.]?264)[^0-9]',  'dvxa', 'divx', 'xvid', 'divx ?(5.?1)?',                                          # Video Codecs
  '[^[0-9](480|576|720|1080[pPi])', '1920x1080','1280x720',                                                   #       Resolution
  '([Hh]i10[pP]?)', '10bit', 'Crf ?24'                                                                        #       color depth and encoding
#  '([^0-9])5\.1[ ]*ch(.)','([^0-9])5\.1([^0-9]?)', '([^0-9])7\.1[ ]((*ch(.))|([^0-9]))'                      #       Channels
]
whackRx = [                                                                                                   ### Tags to remove ###
  '([hHx][\.]?264)[^0-9]',  'dvxa', 'divx', 'xvid', 'divx ?(5.?1)?',                                          # Video Codecs
  'ogg','ogm', 'vorbis','aac','dts', 'ac3',                                                                   # Audio Codecs
  '[^[0-9](480|576|720|1080[pPi])', '1920x1080','1280x720',                                                   #       Resolution
  '([Hh]i10[pP]?)', '10bit', 'Crf ?24'                                                                        #       color depth and encoding
#  '([^0-9])5\.1[ ]*ch(.)','([^0-9])5\.1([^0-9]?)', '([^0-9])7\.1[ ]((*ch(.))|([^0-9]))'                      #       Channels
  '24fps', '25fps', 'ntsc','pal', 'ntsc-u', 'ntsc-j',                                                         # Refresh rate, Format
  'dc','se', 'extended', 'unrated',                                                                           # edition (dc = directors cut, se = special edition)
  'multi','multisubs', 'dubbed','subbed',                                                                     # subs and dubs
  'limited', 'custom', 'internal', 'repack', 'proper', 'rerip', "Raw", "Remastered",                          # format
  'retail', 'webrip','web-dl', 'wp','workprint'                                                               # release type: retail, web, work print
  'cd1[1234]', '[1234]cd', 'xxx', 'nfo', 'read.nfo', 'readnfo', 'nfofix',                                     # misc 1
  'fragment','ps3avchd','remux','fs','ws', " - Copy",                                                         # misc 2
  'bdrc','bdrip','bluray','bd','brrip','hdrip','hddvd','hddvdrip',                                            # Source: bluray
  'ddc','dvdrip','dvd','r1','r3','r5',"DVD",'svcd','vcd',                                                     # DVD, VCD, S-VCD
  'dsr','dsrip','hdtv','pdtv','ppv','stv','tvrip','HDTV'                                                      # dtv, stv
  'cam','bdscr','dvdscr','dvdscreener','scr','screener','tc','telecine','ts','telesync'                       # screener
  ]
release_groups = [                                                                                            ### Release groups (not in brackets or parenthesis)
  "5BAnime-Koi_5D", "%5Banime-koi%5D", "Minitheatre.org", "minitheatre.org", "mtHD", "THORA",                 #
  "(Vivid)", "Dn92", "kris1986k_vs_htt91", "Mthd", "mtHD BD Dual","Elysium", "encodebyjosh",                  #
  ]
FILTER_CHARS   = "\\/:*?<>|~=._;"                                                                             # Windows file naming limitations + "~-,._" + ';' as plex cut title at this for the agent
CHARACTERS_MAP = { 50309:'a',50311:'c',50329:'e',50562:'l',50564:'n',50099:'o',50587:'s',50618:'z',50620:'z', 
                   50308:'A',50310:'C',50328:'E',50561:'L',50563:'N',50067:'O',50586:'S',50617:'Z',50619:'Z',    
                   50072:'O'  , # 'CØDE：BREAKER'
                12360258:':'  , # 'CØDE：BREAKER'
                   50084:'a'  , # 'Märchen Awakens Romance', 'Rozen Maiden Träumend'
                14846080:'∀'  , # 12770:'', # '∀ Gundam' no need
                   49853:'1-2', # 'R/Ranma ½ Nettou Hen'
                   50079:'ss' , # 'Weiß Kreuz'
}

### Log function ########################################################################################
try:      platform = sys.platform.lower()                                                       # sys.platform: win32 | darwin | linux2, 
except:                                                                                         #
  try:    platform = Platform.OS.lower()                                                        # Platform.OS:  Windows, MacOSX, or Linux #  
  except: platform = ""                                                                         #
if   (platform == 'win32'  or platform == 'windows'):  LOG_PATHS = [ 
               '%LOCALAPPDATA%\\Plex Media Server\\Logs',                                       # Windows 8
               '%USERPROFILE%\\Local Settings\\Application Data\\Plex Media Server\\Logs' ]
elif (platform == 'darwin' or platform == 'macosx'):  LOG_PATHS = [ 
               '$HOME/Library/Application Support/Plex Media Server/Logs' ]
elif 'linux' in platform:  LOG_PATHS = [
               '$PLEX_HOME/Library/Application Support/Plex Media Server/Logs',                 #Linux
               '/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Logs',   #Debian, Fedora, CentOS, Ubuntu
               '/usr/local/plexdata/Plex Media Server/Logs',                                    #FreeBSD
               '/usr/pbi/plexmediaserver-amd64/plexdata/Plex Media Server/Logs',                #FreeNAS
               '/c/.plex/Library/Application Support/Plex Media Server/Logs',                   #ReadyNAS
               '/share/MD0_DATA/.qpkg/PlexMediaServer/Library/Plex Media Server/Logs',          #QNAP
               '/volume1/Plex/Library/Application Support/Plex Media Server/Logs',              #Synology, Asustor
               '/volume2/Plex/Library/Application Support/Plex Media Server/Logs' ]             #Synology, if migrated a second raid volume as unique volume in new box         
else: LOG_PATHS = [ '$HOME' ]                                                                   #home folder as backup "C:\users\User.Machine" in windows 8, "users\Plex" on synology
for folder in LOG_PATHS:
  LOG_PATH = os.path.expandvars(folder)
  if os.path.isdir(LOG_PATH):  break
else: LOG_PATH = os.path.expanduser('~')

### Allow to log to the same folder Plex writes its logs in #############################################
def Log(entry, filename='Plex Media Scanner (custom ASS).log'):
  filename=os.path.join(LOG_PATH, filename)
  with open(filename, 'a') as file:
    file.write( entry + "\r\n" )
    print entry     # when ran from console

### Allow to display ints even if equal to None at times ################################################
def xint(s): 
  return str(s) if s is not None and not s=="" else "None"

### Convert Roman numerals ##############################################################################
roman_re_match ="^(L?X{0,3})(IX|IV|V?I{0,3})$"                  
def roman_to_int(string):                                    # Regex for matching #M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})
  roman_values=[['X',10],['IX',9],['V',5],['IV',4],['I',1]]  # ['M',1000],['CM',900],['D',500],['CD',400],['C',100],['XC',90],['L',50],['XL',40]
  result = 0
  string = string.upper()
  for letter, value in roman_values: #is you use {} the list will be in the wrong order
    while string.startswith(letter):
      result += value
      string = string[len(letter):]
  return str(result)

def unicodeLen (char):
  for x in range(1,6):
    if ord(char) < 256-pow(2, 7-x): return x
  return 6
  
### Allow to display ints even if equal to None at times ################################################
def encodeASCII(text, language=None): #from Unicodize and plex scanner and other sources
  if text=='': return
  string = text
 
  ### Decode string back to Unicode ###
  encoding  = ord(text[0])
  encodings = ['iso8859-1', 'utf-16', 'utf-16be', 'utf-8']
  if 0 <= encoding < len(encodings):       # If we're dealing with a particular language, we might want to try another code page.
    if encoding == 0 and language == 'ko':  string = string[1:].decode('cp949')
    else:                                   string = string[1:].decode(encodings[encoding])
  if sys.getdefaultencoding() not in encodings:
    try:    string = string.decode(sys.getdefaultencoding())
    except: pass
  if sys.getfilesystemencoding() not in encodings and not sys.getfilesystemencoding()==sys.getdefaultencoding():
    try:    string = string.decode(sys.getfilesystemencoding())
    except: pass
  if string: string = string.strip('\0')
 
  ### Unicode to ASCII conversion ###
  try:     string = unicodedata.normalize('NFKD', string)    # Unicode  to ascii conversion to corect most characters automatically
  except:  pass
  try:     string = re.sub(RE_UNICODE_CONTROL, '', string)   # Strip control characters.
  except:  pass
  try:     string = string.encode('ascii', 'replace')        # Encode into Ascii
  except:  pass
 
  ### loop through unicode and replace special chars with spaces then map if found ###
  string = list(string)
  i = 0 ; delta = 0
  while i < len(string):
    if ord(string[i])>127:
      char = 0; char2 = ""; char3 = []
      char_len = unicodeLen(string[i])
      for x in range(0, char_len):
        char = 256*char + ord(string[i+x+delta])
        char2 += string[i+x]
        char3.append(string[i+x])
        string[i+x]=''
      if char in CHARACTERS_MAP:  string[i]=CHARACTERS_MAP.get( char )
      else:  Log("*Character missing in CHARACTERS_MAP: '%d', char: '%s%s', len: '%d', string: '%s'" % (char, char2, char3, char_len, string))
      delta   += char_len-1
      i+=char_len-1
    i = i+1
  return ''.join(string)
  
### Allow to display ints even if equal to None at times ################################################
def clean_filename(string):
  if not string: return ""
  string=encodeASCII(string)
  #string = re.sub(r'\(.*?\)', '', string)                                # remove "(xxx)" groups
  string = re.sub(r'\[.*?\]', '', string)                                # remove "[xxx]" groups as Plex cleanup keep inside () but not inside []
  string = re.sub(r'\{.*?\}', '', string)                                # remove "{xxx}" groups as Plex cleanup keep inside () but not inside []
  for char in  FILTER_CHARS:  string = string.replace(char, ' ')          # replace os forbidden chars with spaces
  for group in release_groups:  string = string.replace(group, " ");     # Remove known tags not in '()' or '[]', generally surrounded by '_'
  string = string.replace("`", "'")                                      # translate anidb apostrophes into normal ones
  words  = string.split(" ")
  for word in words:
    if word !="":
      for rx in whackRx:
        if re.sub(rx, "", word.lower())=="":
          try:    words.remove(word)
          except: pass #Log("word: '%s', words: '%s', rx: '%s'" % (word, str(words), rx))
  string = " ".join(words)
  string = string.replace("  ", " ").strip() # remove duplicates spaces, not working:"".join(string.split()) #
  if string.endswith(" -"):  string = string[:-len(" -")]
  return string

### Add files into Plex database ########################################################################
def add_episode_into_plex(mediaList, files, file, show, season=1, episode=1, episode_title="", year=None, endEpisode = None):
  if endEpisode is None: endEpisode = episode
  for epn in range(episode, endEpisode+1):
    tv_show = Media.Episode(show, season, epn, episode_title, year)
    tv_show.display_offset = (epn-episode)*100/(endEpisode-episode+1)
    tv_show.parts.append(file)
    mediaList.append(tv_show)
  #Stack.Scan(path, files, mediaList, []) #miss path var

### Add files into array ################################################################################
def explore_path(subdir, file_tree, plexignore_files=[], plexignore_dirs=[]):
  if os.path.isfile(os.path.join(subdir, ".plexignore")):
    #Log(".plexignore")
    with open( os.path.join(subdir, ".plexignore"), 'r') as plexignore:
      for pattern in plexignore:
        pattern = pattern.strip()                                                                # remove useless spaces at both ends
        if pattern == '' or pattern[0] == '#': continue                                          # skip comment and emopy lines, go to next for iteration
        if '/' not in pattern:  plexignore_files.append(fnmatch.translate(pattern))              # patterns for this folder gets converted and added to files.
        elif pattern[0] != '/': plexignore_dirs.append(pattern)                                  # patterns for subfolders added to folders
  
  files=[]; dirs=[]                                                                              ### Process all files and folders ###
  for item in os.listdir(subdir):                                                                # Loop current folder files and folders
    fullpath = os.path.join(subdir, item)
    if os.path.isdir (fullpath ):                                                                ### dirs
      for rx in ignore_dirs_re_findall:                                                          # Loop through unwanted folders list
        if re.findall(rx, item):
          Log("Folder: '%s' matched ignore_dirs_re_findall regex: '%s'" % (item, rx))
          break                                                                                  # If folder in list of skipped folder exit this loop  #if len(result):  break
      else:  dirs.append(fullpath)                                                               # .plexignore subfolder restrictions management
    if os.path.isfile(fullpath) and item[-3:] in video_exts:                                     ### files
      for rx in ignore_files_re_findall:                                                         # Filter trailers and sample files
        if re.findall(rx, item): 
          Log("File: '%s' matched ignore_files_re_findall regex: '%s'" % (item, rx))
          break                                                           #Log("'%s' ignore_files_findall: match" % item)
      else:
        for rx in plexignore_files:                         
          if re.findall(rx, os.path.basename(item)):
            Log("File: '%s' matched plexignore_files pattern: '%s'" % (item, rx))
            break 
        else:  files.append(fullpath)
  dirs.sort()
  files.sort()
  
  for item in dirs:
    plexignore_recursive_files=[]; plexignore_recursive_dirs =[]                                 # Split recursive entries, this one for next folder's subfolders
    for rx in plexignore_dirs:                                                                   # On each patter string
      pattern = rx.split("/")                                                                    # Create array splitting by / so all folders separated and patter last
      if pattern[0].lower() == Utils.SplitPath(item)[-1].lower():                                # first folder the same
        if len(pattern) == 2: plexignore_recursive_files.append(fnmatch.translate(pattern[1]))   # One folder, for next folder current files
        if len(pattern) >= 3: plexignore_recursive_dirs.append( "",join(pattern[1:]))            # 2+ folders, for next folder subfolders
    explore_path(item, file_tree, plexignore_recursive_files, plexignore_recursive_dirs)     # call next folder and will inherit restrictions
  if not files == []:
    file_tree[subdir] = files    

### Look for episodes ###################################################################################
def Scan(path, files, mediaList, subdirs, language=None, root=None, **kwargs):

  if not path == "":  return  # Exit every other iteration than the root scan
  Log("=== Scan ================================================================================================================")
  Log("Platform: '%s', Logs location: '%s'" % (platform, LOG_PATH))
  Log("Scan: (root: '%s', path='%s', subdirs: '%s', Files: '%s', language: '%s')" % (root if root is not None else "", path, str(subdirs), str(files), language))
  file_tree = {}                                           # initialize file_tree
  Log("--- Skipped mediums -----------------------------------------------------------------------------------------------------")
  explore_path(root, file_tree)                            # initialize file_tree with files on root
  Log("=========================================================================================================================")
  for path in sorted(file_tree):#for path, files in file_tree.iteritems():                # Loop to add all series while on the root folder Scan call, which allows subfolders to work
    files   = file_tree[path]
    path    = path.replace(root, "")                        # Recreate normal scanner coding: path is relative to root
    subdirs = []                                             # Recreate normal scanner coding: subfolders empty
    if path.startswith("/"):  path = path[1:]              # Recreate normal scanner coding: path doesn't start with "/"   
    relative_path = path.replace(root, " ")                # Foe exemple /group/serie/season/ep folder
    reverse_path  = Utils.SplitPath(relative_path)         # Take top two as show/season, but require at least the top one, and reverse them
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

    ### Check if folder is a season folder and remove it do reduce complexity ###
    folder_season = None
    for folder in reverse_path[:-1]:                   # Doesn't thow errors but gives an empty list if items don't exist, might not be what you want in other cases
      for rx in specials_re_match + season_re_match :  # in anime, more specials folders than season folders, so doing it first
        match = re.match(rx, folder, re.IGNORECASE)
        if match:
          folder_season = 0 if rx in specials_re_match else int( match.group('season') )  #use "if var is | is not None:" as it's faster than "==None" and "if var:" is false if the variable is: False, 0, 0.0, "", () , {}, [], set()
          Log("Season folder: '%s' found using Regex specials_re_match '%s' on folder name '%s'" % (str(folder_season), rx, folder) )
          reverse_path.remove(folder)  #All ways to remove: reverse_path.pop(-1), reverse_path.remove(thing|array[0])
          break
      if match: break  #Breaking second for loop doesn't exist parent for

    ### Clean folder name and get year if present ###
    folder_year = None #misc, folder_year = VideoFiles.CleanName( reverse_path[0] )          # Take folder year
    
    folder_show = clean_filename( reverse_path[0] )          
    Log("Path: '%s', show: '%s', year: '%s'" % (path, folder_show, xint(folder_year)))  #

    ### Main File loop to start adding files now ###
    for file in files:                                                   # "files" is a list of media files full path, File is one of the entries
      filename        = os.path.basename(file)                           # filename        is the filename of the file
      filename_no_ext = os.path.splitext(filename)[0]                    # filename_no_ext is the filename of the file, albeit with no extension
      year=None #misc, year      = VideoFiles.CleanName(filename_no_ext)            # Get the year before all '()' are stripped drom the filename without the extension  ### Year? ###  #if re.match('.+ \([1-2][0-9]{3}\)', paths[-1]):
      ep              = clean_filename      (filename_no_ext)            # Strip () [], all, ep contain the serie name and ep number for now
    
      ### Cleanup episode filename If parent Folder contain serie name ###
      folder_use = False                                                 # Bolean to keep track if folder name in case it is included in the filename
      if folder_show is not None and not folder_show == "":              # If containing folder exist or has name different from "_" (scrubed to "")
        misc = re.sub(folder_show,                          '', ep, flags=re.IGNORECASE).lstrip() # misc = ep.replace(folder_show, "")         # remove cleaned folder name (if exist) from the show name
        junk = re.sub(folder_show.replace(" ", "").lower(), '', ep, flags=re.IGNORECASE).lstrip() # misc = ep.replace(folder_show, "")         # remove cleaned folder name (if exist) from the show name
        if len(misc) < len(ep) or len(junk)< len(ep) :                   # And remove the cleaned folder name from the now cleaned show, just in case the directory is off by things CleanName handles
          folder_use = True                                              # indicate to latter use folder name since it is present in filename
          ep         = folder_show + " 01" if misc == "" else misc       # episode string name stripped of the folder name If nothing is left, take the folder (movie)
      ep_nb = ep if ep.rfind(" ") == -1 else ep.rsplit(' ', 1)[1]        # If there is no space (and ep title) / If there is a space ep_nb is the last part hoping there is no episode title
      #show, ep, title = ep.partition(match.group('ep'))                 # split keeping the separator, spare a line and keep the title
    
      ### Check for date-based regexps first. ###
      for rx in date_regexps:
        match = re.search(rx, ep)
        if match:  # Make sure there's not a stronger season/ep match for the same file.
          try:
            for r in episode_regexps[:-1] + standalone_episode_regexs:
              if re.search(r, file):  raise
          except:  break   
          year    = int(match.group('year' ))
          month   = int(match.group('month'))
          day     = int(match.group('day'  ))
          tv_show = Media.Episode(show, year, None, None, None) # Use the year as the season.
          tv_show.released_at = '%d-%02d-%02d' % (year, month, day)
          tv_show.parts.append(i)
          mediaList.append(tv_show)
          break
      if match: continue
      
      ### Check for episode_re_search ###
      for rx in episode_re_search:
        match = re.search(rx, ep, re.IGNORECASE)
        if match:
          show       = clean_filename( match.group('show'    )) if not folder_use and not match.group('show')=="" else folder_show
          season     =             int(match.group('season'  )) if     folder_season is None else folder_season
          episode    =             int(match.group('ep'))
          endEpisode =             int(match.group('secondEp')) if match.groupdict().has_key('secondEp') and match.group('secondEp') else episode
          add_episode_into_plex(mediaList, files, file, show, season, episode, "", year, endEpisode)
          if episode==endEpisode:  Log("show: '%s', year: '%s', season: '%s', ep: '%s'      found using regex episode_re_search '%s' on cleaned string '%s' gotten from filename '%s' also ep_nb: '%s'" % (show, xint(year), xint(season), xint(episode),                   rx, ep, filename, ep_nb))
          else:                    Log("show: '%s', year: '%s', season: '%s', ep: '%s-%s' found using regex episode_re_search '%s' on cleaned string '%s' gotten from filename '%s' also ep_nb: '%s'"   % (show, xint(year), xint(season), xint(episode), xint(endEpisode), rx, ep, filename, ep_nb))
          break
      if match: continue
    
      ### Check for standalone_episode_re_findall ###
      for rx in standalone_episode_re_findall:
        match = re.findall(rx, ep)
        if len(match): 
          show, misc, year2, season, episode, misc, endEpisode, misc, episode_title = match[0]
          endEpisode = int(episode) if len(endEpisode) == 0 else int(endEpisode)
          episode    = int(episode)
          add_episode_into_plex(mediaList, files, file, folder_show if folder_use or show=="" else show, season, int(episode), episode_title, year, endEpisode)
          Log("show: '%s', year: '%s', season: '%s', ep: %s found using regex standalone_episode_re_findall '%s' on cleaned string '%s' gotten from filename '%s'" % (folder_show if folder_use else show, xint(year), xint(season), xint(episode), rx, ep, filename))
          break
      if match: continue

      ### Check for AniDB_re_search ###
      for rx, offset in AniDB_re_search:
        match = re.search(rx, ep, re.IGNORECASE)
        if match:
          show = clean_filename( match.group('show')) if not folder_use else folder_show
          if not show: show = folder_show
          episode = offset + 1 if match.group('ep') == "" or not match.group('ep').isdigit() else offset + int( match.group('ep') )
          Log("show: '%s', year: '%s', season: '%s', ep: %3s found using regex AniDB_re_search '%s' on cleaned string '%s' gotten from filename '%s'" % (show, xint(year), "0", xint(episode), rx, ep, filename))
          add_episode_into_plex(mediaList, files, file, show, 0, episode, "", year, None)
          break
      if match: continue
 
      ### Check for just_episode_re_search ###
      for rx in just_episode_re_search:
        match = re.search(rx, ep, re.IGNORECASE)
        if match: #          if rx == just_episode_re_search[0]:  shouldStack = False
          season  = 1 if folder_season is None else folder_season                                                                       
          episode = int(match.group('ep'))
          if folder_use:  show = folder_show
          else:
            show = ep[:ep.find(match.group('ep'))].rstrip() # remove eveything from the episode number
            if show.endswith(" -"):  show = show[:-len(" -")]
            if show.rfind(" ") != -1 and show.rsplit(' ', 1)[1] in ["ep", "Ep", "EP", "eP", "e", "E"]:  show = show.rsplit(' ', 1)[0] # remove ep at the end
            if show == "" or show.lower() in folder_show.lower(): show = folder_show  # cut down forms of title point to folder anyway
                                                                                    # In case of ep filename "EP 01 title of the episode" fallback to folder name
          add_episode_into_plex(mediaList, files, file, show, season, episode, "", year, None)
          Log("show: '%s', year: '%s', season: '%s', ep: %3s found using regex just_episode_re_search '%s' on cleaned string '%s' gotten from filename '%s'" % (show, xint(year), xint(season), xint(episode), rx, ep, filename))
          break
      if match: continue

      ### Roman numbers ### doesn't work is ep title present
      match = re.match(roman_re_match, ep_nb, re.IGNORECASE)
      if match:
        ep_nb = roman_to_int(ep_nb)
        Log("show: '%s', year: '%s', season: '%s', ep: %3s found using regex roman_re_matchroman_re_match '%s' on cleaned string '%s' gotten from filename '%s'" % (folder_show, xint(year), "1", xint(ep_nb), rx, ep, filename))
        add_episode_into_plex(mediaList, files, file, folder_show, 1, int(ep_nb), "", year, None)
        continue
      
      ### No regular expression worked ###
      Log("*no show found for ep: '%s', eb_nb: '%s', filename '%s', folder_show: '%s' " % (ep, ep_nb, filename, folder_show))

    Log("-------------------------------------------------------------------------------------------------------------------------")
  Log("")

def find_data(atom, name):
  child = atomsearch.find_path(atom, name)
  data_atom = child.find('data')
  if data_atom and 'data' in data_atom.attrs:
    return data_atom.attrs['data']

if __name__ == '__main__':
  print "Absolute Series Scanner command line execution"
  path  = sys.argv[1]
  files = [os.path.join(path, file) for file in os.listdir(path)]
  media = []
  Scan(path[1:], files, media, [])
  print "Media:", media
