# Most code here is copyright (c) 2010 Plex Development Team. All rights reserved.
# Source: https://forums.plex.tv/index.php/topic/31081-better-absolute-scanner-babs/
 
import re, os, os.path, sys
import datetime
import Media, VideoFiles, Stack, Utils
from string import maketrans
 
### regular Expressions and variables ################## http://www.zytrax.com/tech/web/regex.htm ###   ### http://regex101.com/#python ####################
ignore_suffixes               = ['dvdmedia']                                                            # Skipped extensions
ignore_files_re_findall       = ['[-\._ ]sample', 'sample[-\._ ]', '-trailer\.', 'trailer[0-9]*\.']     # Skipped files (samples, trailers)
ignore_dirs_re_findall        = ['extras?', '!?samples?', 'bonus', '.*bonus disc.*', '!?trailers?']     # Skipped folders
 
season_re_match               = ['.*?(?P<season>[0-9]+)$', '.*?(?P<saison>[0-9]+)$']                    # Season folder
specials_re_match             = ['specials?', 'seasons? ?0?0', 'saisons? ?0?0', 'temporadas? ?0?0']     # Specials folder
AniDB_re_search               = "^(?P<ep>((OP)|(ED)|(OAV)|(OVA)|(SPECIAL))\d{0,2})"                               #
ends_with_episode_re_sub      = ['[ ]*[0-9]{1,2}x[0-9]{1,3}$', '[ ]*S[0-9]+E[0-9]+$']                   #
ends_with_number_re_sub       = '.*([0-9]{1,2})$'                                                       
episode_re_search             = [                                                                       ### Episode search ###
  '(?P<show>.*?)[sS](?P<season>[0-9]+)[\._ ]*[eE](?P<ep>[0-9]+)([- ]?[Ee+](?P<secondEp>[0-9]+))?',      # S03E04-E05
  '(?P<show>.*?)[sS](?P<season>[0-9]{2})[\._\- ]+(?P<ep>[0-9]+)',                                       # S03-03
  '(?P<show>.*?)([^0-9]|^)(?P<season>[0-9]{1,2})[Xx](?P<ep>[0-9]+)(-[0-9]+[Xx](?P<secondEp>[0-9]+))?'   # 3x03
  ]                                                                                                     
standalone_episode_re_findall = [                                                                       ### Episode Search standalone ###
  '(.*?)( \(([0-9]+)\))? - ([0-9]+)+x([0-9]+)(-[0-9]+[Xx]([0-9]+))?( - (.*))?',                         # Newzbin style, no _UNPACK_
  '(.*?)( \(([0-9]+)\))?[Ss]([0-9]+)+[Ee]([0-9]+)(-[0-9]+[Xx]([0-9]+))?( - (.*))?'                      # standard s00e00
  ]                                                                                                     
just_episode_re_search        = [                                                                       ### eisode search no show name ###
  '(?P<ep>[0-9]{1,3})[\. -_]of[\. -_]+[0-9]{1,3}([^0-9]|$)',                                                      # 01 of 08
  '^(?P<ep>[0-9]{1,3})([^0-9]|$)',                                                                                # 01
  '(^|[ \.\-_])e(p{0,1}|(pisode){0,1})[ \.\-_]*(?P<ep>[0-9]{2,3})([^0-9]|$)',                           # ep234 or Ep 126
  '.*?[ \.\-_](?P<ep>[0-9]{2,3})([^0-9]|$)+',                                                           # Flah - 04 - Blah
  '.*?[ \.\-_](?P<ep>[0-9]{2,3})$',                                                                     # Flah - 04
  '.*?[^0-9x](?<!OP)(?<!ED)(?P<ep>\d{2,3})([^0-9]|$)'                                                             # Flah 107 as long as it isn't preceded by op, ed
  ]
whackRx = [                                                                                             ### Minor cleaning on the file to avoid false matches on H.264, 720p, etc. ###
  '([hHx][\.]?264)[^0-9]',                                                                              # h264, H.264, x.264
  '([Hh]i10[pP]?)', '10bit',                                                                            # Hi10, Hi10p
  'divx ?(5.?1)?',                                                                                      # Divx51
  "DD5.1",                                                                                              # Audio
  'Crf ?24',                                                                                            # Crf24, Crf 24
  '[^[0-9](480|576|720|1080[pPi])',                                                                                   # 480p
  '[^[0-9](24fps)', '[^[0-9](25fps)',                                                                   # 24fps, 25fps
  "Raw", "Remastered", "DVD", "HDTV",                                                                   # raw, remastered, DVD 
  " - Copy", "[0-9]{1,3}[Vv][123]"                                                                      #
  ]                                                                                                     
release_groups = [                                                                                      ### Release groups (not in brackets or parenthesis)
  "5BAnime-Koi_5D", "%5Banime-koi%5D", "Minitheatre.org", "minitheatre.org", "mtHD", "THORA",           #
  "(Vivid)", "Dn92", "kris1986k_vs_htt91", "Mthd", "mtHD BD Dual","Elysium", "encodebyjosh",            #
  ]
translation_table = maketrans("`", "'") #("`꞉∕", "':/") 
FILTER_CHARS      = "\\/:*?<>|~-;,._"
 
### Allow to display ints even if equal to None at times ################################################
def xint(s):
  if s is not None and not s == "": return str(s)
  return "None"
 
### Convert Roman numerals ##############################################################################
roman_re_match ="^M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$"
def roman_to_int(string):
  roman_values=[['M',1000],['CM',900],['D',500],['CD',400],['C',100],['XC',90],['L',50],['XL',40],['X',10],['IX',9],['V',5],['IV',4],['I',1]]
  result = 0
  string = string.upper()
  for letter, value in roman_values: #is you use {} the list will be in the wrong order
    while string.startswith(letter):
      result += value
      string = string[len(letter):]
  return str(result)
 
### Log function ########################################################################################
def Log(entry, filename='Plex Media Scanner Custom.log'): #need relative path):
  #Logging = [ ['Synology',          "/volume1/Plex/Library/Application Support/Plex Media Server/Logs/"], #C:\Program Files (x86)\Plex\Plex Media Server>"Plex Media Scanner.exe" --scan --refresh --verbose
  #            ['Synology2',         "../../Plex/Library/Application Support/Plex Media Server/Logs/"], #C:\Program Files (x86)\Plex\Plex Media Server>"Plex Media Scanner.exe" --scan --refresh --verbose
  #            ['Ubuntu-10.04',      "/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Logs/"]
  #            ['windows Vista/7/8', "C:\\Users\\Default\\AppData\\Local\\Plex Media Server\\Logs\\"],
  #            ['Qnap',              ""]
  #          ]
  try: 
    with open(filename, 'a') as file: #with open("/volume1/Plex/Library/Application Support/Plex Media Server/Logs/" + filename, 'a') as file:
      #for line in file:  if entry in line:  file.write  break  else: file.write( line + "\r\n" ) #time now.strftime("%Y-%m-%d %H:%M") + " " + datetime.datetime.now() + " " + 
      #
      # with open("/volume1/Plex/Library/Application Support/Plex Media Server/Logs/" + filename, 'r+') as file:
      #   lines = list()
      #   for line in file: #lines = list(file)
      #     if entry in line: list.insert(entry)
      #     else: list.insert(line)
      #   else: list.insert()
      file.write( entry + "\r\n" )
      print line + "\n"
  except:  pass
    
### Allow to display ints even if equal to None at times ################################################
def clean_filename(string):
  #Log("0: '%s'" % string)
  string = re.sub(r'\(.*?\)', '', string)                                # remove "(xxx)" or "[xxx]" groups as Plex cleanup keep inside () but not inside []
  for group in release_groups:  string = string.replace(group, " ");     # Remove known tags not in '()' or '[]', generally surrounded by '_'
  for rx    in whackRx:         string = re.sub(rx, ' ', string)         # Remove useless tags
  for char in FILTER_CHARS:  string = string.replace(char, ' ')          # replace os forbidden chars with spaces
  string = string.translate(translation_table)                           # translate some chars
  string, misc = VideoFiles.CleanName( string )                          # Take serie name cleaned of "[xxxxx]" groups
  string       = " ".join(string.split(" "))                             # remove duplicates spaces
  return string
 
### Add files into Plex database ###
def add_episode_into_plex(mediaList, files, file, show, season=1, episode=1, episode_title="", year=None, endEpisode = None):
  if endEpisode is None: endEpisode = episode
  for epn in range(episode, endEpisode+1):
    tv_show = Media.Episode(show, season, episode, episode_title, year)
    if endEpisode is not None: tv_show.display_offset = (epn-episode)*100/(endEpisode-episode+1)
  tv_show.parts.append(file)
  mediaList.append(tv_show)  
 
### Look for episodes ###################################################################################
def Scan(path, files, mediaList, subdirs, language=None, root=None):
  
  ### Root scan for OS information that i need to complete the Log function ###
  if path == "":
    Log("================================================================================")
    try:
      os_uname=""
      for string in os.uname(): os_uname += string
      Log("os.uname():   '%s'" % os_uname)          #(sysname, nodename, release, version, machine)  #
      Log("Sys.platform: '%s'" % sys.platform)      #
      Log("os.name:      '%s'" % os.name)           # 'posix', 'nt', 'os2', 'ce', 'java', 'riscos'.) 
      Log("os.getcwd:    '%s'" % os.getcwd())       # Current dir: /volume1/homes/plex
    except: pass
 
  ### Skip folder if empty ###
  if len(files) == 0:  return
  
  ### Scan information and uild reverse_path array ###
  Log("================================================================================")
  Log("Scan: (root: '%s', path='%s', files: %s, subdirs: %s, language: '%s')" % (root, path, str(files), str(subdirs), language))
  VideoFiles.Scan(path, files, mediaList, subdirs, root)  #
  relative_path = path.replace(root, " ")                 #/group/serie/season/ep folder
  reverse_path  = Utils.SplitPath(relative_path)          # Take top two as show/season, but require at least the top one.
  reverse_path.reverse()
  
  ### Skip unwanted folders ###
  for rx in ignore_dirs_re_findall :
    result = re.findall(rx, reverse_path[0])   
    if len(result): 
      Log("Regex ignore_dirs_findall : match for '%s'" % reverse_path[0])
      Log("[Folder] '%s'" % reverse_path[0], "Plex Media Scanner Custom - Skipped files")
      return
 
  ### File loop for unwanted files, allow to use the number of actual files in folder accurately ###
  for file in files:                   # "files" is a list of media files full path
    filename = os.path.basename(file)  # filename contain just the filename of the file
    
    ### Filter unwanted file extensions ###
    if file.split('.')[-1] in ignore_suffixes:  #compare file extention to blacklist
      Log("'%s' ignore_suffixes: match" % filename)
      Log(file, "Plex Media Scanner Custom - ignored suffixes.log")
      files.remove(file) #in case we reprocess the lsit latter to precise matches or count number of files
      continue
 
    ### Filter trailers and sample files ###
    for rx in ignore_files_re_findall:
      match = re.findall(rx, file)
      if len(match): 
        Log("'%s' ignore_files_findall: match" % filename)
        Log(file, "Plex Media Scanner Custom - Ignored files.log")
        files.remove(file) #in case we reprocess the lsit latter to precise matches, or count number of files
        break
 
  ### Check if folder is a season folder and remove it do reduce complexity ###
  folder_season = None
  for folder in reverse_path[:-1]:                  #Doesn't thow errors but gives an empty list if items don't exist, might not be what you want in other cases
    for rx in specials_re_match + season_re_match:  #in anime, more specials folders than season folders, so doing it first
      match = re.match(rx, folder, re.IGNORECASE)
      if match:
        folder_season = 0 if rx in specials_re_match else int( match.group(folder) )  #use "if var is | is not None:" as it's faster than "==None" and "if var:" is false if the variable is: False, 0, 0.0, "", () , {}, [], set()
        Log("Regex specials_regex/season_regex_match: Regex '%s' match for '%s', season: '%d'" % (rx, folder, folder_season) )
        reverse_path.remove(folder)  #All ways to remove: reverse_path.pop(-1), reverse_path.remove(thing|array[0])
        break
    if match: break  #Breaking second for loop doesn't exist parent for
 
  ### Clean folder name and get year if present ###
  misc, folder_year = VideoFiles.CleanName( reverse_path[0] )                    # Take folder year
  folder_show       = clean_filename(       reverse_path[0] )                    #
  Log("From folder, show: '%s', year: '%s'" % (folder_show, xint(folder_year)))  #
  
  ### Main File loop to start adding files now ####
  for file in files:                                                   # "files" is a list of media files full path, File is one of the entries
    filename        = os.path.basename(file)                           # filename        is the filename of the file
    filename_no_ext = os.path.splitext(filename)[0]                    # filename_no_ext is the filename of the file, albeit with no extension
    misc, year      = VideoFiles.CleanName(filename_no_ext)            # Get the year before all '()' are stripped drom the filename without the extension  ### Year? ###  #if re.match('.+ \([1-2][0-9]{3}\)', paths[-1]):
    ep              = clean_filename      (filename_no_ext)            # Strip () [], all, ep contain the serie name and ep number for now
    
    ### Cleanup episode filename If parent Folder contain serie name ###
    folder_use = False                                                 # Bolean to keep track if folder name in case it is included in the filename
    if folder_show is not None and not folder_show == "":              # If containing folder exist or has name different from "_" (scrubed to "")
      misc = re.sub(folder_show, '', ep, flags=re.IGNORECASE).lstrip() # misc = ep.replace(folder_show, "")                               # remove cleaned folder name (if exist) from the show name
      if len(misc) < len(ep):                                          # And remove the cleaned folder name from the now cleaned show, just in case the directory is off by things CleanName handles
        folder_use = True                                              # indicate to latter use folder name since it is present in filename
        ep         = folder_show + " 01" if misc == "" else misc       # episode string name stripped of the folder name If nothing is left, take the folder (movie)
    ep_nb = ep if ep.rfind(" ") == -1 else ep.rsplit(' ', 1)[1]      # If there is no space (and ep title) / If there is a space ep_nb is the last part hoping there is no episode title
    #show, ep, title = ep.partition(match.group('ep'))                 # split keeping the separator, spare a line and keep the title
    
    ### Roman numbers ### doesn't work is ep title present
    match = re.match(roman_re_match, ep_nb, re.IGNORECASE)
    if match:
      ep_nb2 = ep_nb
      ep_nb = roman_to_int(ep_nb)
      if len(ep_nb2) == len(ep) and not folder_use:  ep = clean_filename( os.path.splitext(filename)[0])
      ep = ep.replace(ep_nb2, ep_nb)
      
    ### Check for AniDB_re_search ###
    match = re.search(AniDB_re_search, ep_nb, re.IGNORECASE)
    if match: 
      show = folder_show if folder_use else ep.rsplit(' ', 1)[0]
      for special, offset in [ ['OAV',0], ['OVA',0], ['SPECIAL',0], ['S',0], ['OP',100], ['NCOP',100], ['ED',150], ['NCED',150], ['T',200], ['P',300], ['O',400] ]:
        if ep_nb.upper().startswith(special):  # and len(ep_nb)<=4 and (ep_nb[ len(special): ].isdigit() or len(ep_nb)==2):
          try:    episode = int(offset + int( "1" if ep_nb[ len(special):]=="" else ep_nb[ len(special):] )) 
          except: Log("AniDB numbering - issue - ep_nb: '%s', offset: '%d', string: '%s'" % (ep_nb, offset, ep_nb[ len(special):]))
          else:
            add_episode_into_plex(mediaList, files, file, show, 0, episode, "", year, None)
            Log("show: '%s', year: '%s', season: '%s', ep: %3s found using AniDB_re_search on cleaned string '%s' gotten from filename '%s'" % (show, xint(year), "0", xint(episode), ep, filename))
          break
      continue    
    
    ### Check for standalone_episode_re_findall ###
    for rx in standalone_episode_re_findall:
      match = re.findall(rx, ep)
      if len(match): 
        show, misc, year2, season, episode, misc, endEpisode, misc, episode_title = match[0]
        endEpisode = int(episode) if len(endEpisode) == 0 else int(endEpisode)
        episode = int(episode)
        add_episode_into_plex(mediaList, files, file, folder_show if folder_use else show, season, int(episode), episode_title, year, endEpisode)
        Log("show: '%s', year: '%s', season: '%s', ep: %s found using standalone_episode_re_findall on cleaned string '%s' gotten from filename '%s'" % (folder_show if folder_use else show, xint(year), xint(season), xint(episode), ep, filename))
        break #return
    if match: continue  # Used "for ... else" before but needed each sub-section shifted, and want to be able to swap the order quickly
 
    ### Check for episode_re_search ###
    for rx in episode_re_search:
      match = re.search(rx, ep, re.IGNORECASE)
      if match:
        Log("match group show: " + match.group('show') )
        show       = clean_filename( match.group('show'    )) if not folder_use            else folder_show
        season     =             int(match.group('season'  )) if     folder_season is None else folder_season
        episode    =             int(match.group('ep'))
        endEpisode =             int(match.group('secondEp')) if match.groupdict().has_key('secondEp') and match.group('secondEp') else episode
        add_episode_into_plex(mediaList, files, file, show, season, episode, "", year, endEpisode)
        Log("show: '%s', year: '%s', season: '%s', ep: %s found using episode_re_search on cleaned string '%s' gotten from filename '%s' also ep_nb: '%s'" % (show, xint(year), xint(season), xint(episode), ep, filename), ep_nb)
        break
    if match: continue  # Used "for ... else" before but needed each sub-section shifted, and want to be able to swap the order quickly
    
    ### Check for just_episode_re_search ###
    for rx in just_episode_re_search:
      match = re.search(rx, ep, re.IGNORECASE)
      if match:
        season  = 1 if folder_season is None else folder_season                                                                       
        episode = int(match.group('ep'))
        if folder_use:  show = folder_show
        else:
          show = ep[:ep.find(match.group('ep'))].rstrip() # remove eveything from the episode number
          if show.rfind(" ") != -1 and show.rsplit(' ', 1)[1] in ["ep", "Ep", "EP", "eP", "e", "E"]:  show = show.rsplit(' ', 1)[0] # remove ep at the end
        add_episode_into_plex(mediaList, files, file, show, season, episode, "", year, None)
        Log("show: '%s', year: '%s', season: '%s', ep: %3s found using just_episode_re_search on cleaned string '%s' gotten from filename '%s'" % (show, xint(year), xint(season), xint(episode), ep, filename))
        break
    if match: continue  # Used "for ... else" before but needed each sub-section shifted, and want to be able to swap the order quickly
    
    ### No regular expression worked ###
    Log("*no show found on cleaned string '%s' gotten from filename '%s'" % (ep, filename))
    Log(file, "Plex Media Scanner Custom - Skipped files.log")
