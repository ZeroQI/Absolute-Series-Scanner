# Most code here is copyright (c) 2010 Plex Development Team. All rights reserved.
# Source: https://forums.plex.tv/index.php/topic/31081-better-absolute-scanner-babs/
 
import re, os, os.path
import datetime
import Media, VideoFiles, Stack, Utils
 
### regular Expressions and variables ################## http://www.zytrax.com/tech/web/regex.htm ###   ### http://regex101.com/#python ####################
ignore_suffixes               = ['dvdmedia']                                                            # Skipped extensions
ignore_files_re_findall       = ['[-\._ ]sample', 'sample[-\._ ]', '-trailer\.', 'trailer[0-9]*\.']     # Skipped files (samples, trailers)
ignore_dirs_re_findall        = ['extras?', '!?samples?', 'bonus', '.*bonus disc.*', '!?trailers?']     # Skipped folders
 
season_re_match               = ['.*?(?P<season>[0-9]+)$', '.*?(?P<saison>[0-9]+)$']                    # Season folder
specials_re_match             = ['specials', 'season ?0?0']                                             # Specials folder
 
episode_re_search             = [                                                                       ### Episode search ###
  '(?P<show>.*?)[sS](?P<season>[0-9]+)[\._ ]*[eE](?P<ep>[0-9]+)([- ]?[Ee+](?P<secondEp>[0-9]+))?',      # S03E04-E05
  '(?P<show>.*?)[sS](?P<season>[0-9]{2})[\._\- ]+(?P<ep>[0-9]+)',                                       # S03-03
  '(?P<show>.*?)([^0-9]|^)(?P<season>[0-9]{1,2})[Xx](?P<ep>[0-9]+)(-[0-9]+[Xx](?P<secondEp>[0-9]+))?'   # 3x03
  ]                                                                                                     #
 
standalone_episode_re_findall = [                                                                       ### Episode Search standalone ###
  '(.*?)( \(([0-9]+)\))? - ([0-9]+)+x([0-9]+)(-[0-9]+[Xx]([0-9]+))?( - (.*))?',                         # Newzbin style, no _UNPACK_
  '(.*?)( \(([0-9]+)\))?[Ss]([0-9]+)+[Ee]([0-9]+)(-[0-9]+[Xx]([0-9]+))?( - (.*))?'                      # standard s00e00
  ]                                                                                                     #
 
just_episode_re_search        = [                                                                       ### eisode search no show name ###
  '(?P<ep>[0-9]{1,3})[\. -_]of[\. -_]+[0-9]{1,3}',                                                      # 01 of 08
  '^(?P<ep>[0-9]{1,3})',                                                                                # 01
  '(^|[ \.\-_])e(p{0,1}|(pisode){0,1})[ \.\-_]*(?P<ep>[0-9]{2,3})([^0-9c-uw-z%]|$)',                    # ep234
  '.*?[ \.\-_](?P<ep>[0-9]{2,3})[^0-9c-uw-z%]+',                                                        # Flah - 04 - Blah
  '.*?[ \.\-_](?P<ep>[0-9]{2,3})$',                                                                     # Flah - 04
  '.*?[^0-9x](?<!OP)(?<!ED)(?P<ep>\d{2,3})'                                                             # Flah 107 as long as it isn't preceded by op, ed
  ]
ends_with_episode_re_sub      = ['[ ]*[0-9]{1,2}x[0-9]{1,3}$', '[ ]*S[0-9]+E[0-9]+$']                   #
#ends_with_number_re.sub       = '.*([0-9]{1,2})$'                                                      #
release_groups = ["Hi10", "THORA", "(BD_1080p)", "(Vivid)", "Dn92", " Raw", "%5Banime-koi%5D", "minitheatre.org",
                  "mtHD BD Dual", "1080i","HDTV", "H.264", "DD5.1", "25pfps", "divx51", "Minitheatre.org", "(1)", "(2)", "(3)",
                  "5BAnime-Koi_5D", "encodebyjosh", "kris1986k_vs_htt91", "Mthd", "10bit", "Crf24", "DVD", "v1_EP", "v2_EP", "v3_EP", "Elysium"
]
whackRx = [                                                                                             ### ###
  '([hHx][\.]?264)[^0-9]',                                                                              # h264, x.264
  '([Hh]i10[pP]?)',                                                                                     # Hi10, Hi10p
  '[^[0-9](480[pP])',                                                                                   # 480p
  '[^[0-9](720[pP])',                                                                                   # 720p
  '[^[0-9](1080[pP])'                                                                                   # 1080p
  ]# Minor cleaning on the file to avoid false matches on H.264, 720p, etc.
 
### Allow to display ints even if equal to None at times ################################################
def xint(s):
  if s is not None and not s == "": return str(s)
  return "None"
 
### Convert Roman numerals ##############################################################################
roman_re_match ="^M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$"
def roman_to_int(string):
  roman_values = { 'M':1000, 'CM':900, 'D':500, 'CD':400, 'C':100, 'XC':90, 'L':50, 'XL':40, 'X':10, 'IX':9, 'V':5, 'IV':4, 'I':1 } #  roman_values=[['M',1000],['CM',900],['D',500],['CD',400],['C',100],['XC',90],['L',50],['XL',40],['X',10],['IX',9],['V',5],['IV',4],['I',1]]
  result = 0
  string = string.upper()
  for letter, value in roman_values:
    while string.startswith(letter):
      result += value
      string = string[len(letter):]
  return str(result)
 
### Log function ########################################################################################
def Log(line, filename='Plex Media Scanner Custom.log'): #need relative path):
  #Logging = [ ['Synology',          "/volume1/Plex/Library/Application Support/Plex Media Server/Logs/"], #C:\Program Files (x86)\Plex\Plex Media Server>"Plex Media Scanner.exe" --scan --refresh --verbose
  #            ['Ubuntu-10.04',      "/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Logs/"]
  #            ['windows Vista/7/8', "C:\\Users\\Default\\AppData\\Local\\Plex Media Server\\Logs\\"],
  #            ['Qnap',              ""]
  #          ]
  #if file exist (log+".htm"): 
  #  string = Data.Load(log+".htm")
  #  if entry not in string:  Data.Save(log+".htm", string + entry + "<BR />\r\n")
  try: 
    with open("/volume1/Plex/Library/Application Support/Plex Media Server/Logs/" + filename, 'a') as log:
      log.write( line + "\r\n" ) #time now.strftime("%Y-%m-%d %H:%M") + " " + datetime.datetime.now() + " " + 
      print line + "\n"
  except:  pass
    
### Look for episodes ###################################################################################
def Scan(path, files, mediaList, subdirs, language=None, root=None):
  if len(files) == 0:  return #    Log("No files, skipping folder")
  Log("================================================================================")
  Log("Scan: path=%s, files: %s, subdirs: %s, language: %s, root: %s)" % (path, str(files), str(subdirs), str(language), str(root)))
  VideoFiles.Scan(path, files, mediaList, subdirs, root)
  reversepaths = Utils.SplitPath(path)  # Take top two as show/season, but require at least the top one.
  reversepaths.reverse()
  
  ### Skip unwanted folders ###
  for rx in ignore_dirs_re_findall :
    result = re.findall(rx, reversepaths[0])   
    if len(result): 
      Log("Regex ignore_dirs_findall : match for '%s'" % reversepaths[0])
      Log("Folder: '%s'" % reversepaths[0], "Plex Media Scanner Custom - Skipped files")
      return
 
  ### Remove season folder ###
  folder_season = None
  if len(reversepaths) > 1:  ### 2 folders at least, Check if last folder is a season folder ###
    for rx in specials_re_match:
      match = re.match(rx, reversepaths[0], re.IGNORECASE)
      if match:
        Log("Regex specials_regex: match for '%s'" % reversepaths[0])
        reversepaths.pop(0) #your_list.pop(-1), path.remove(thing), array.remove(array[0])
        folder_season = 0
        break
    else:
      for rx in season_re_match:
        match = re.match(rx, reversepaths[0], re.IGNORECASE)
        if match:
          Log("Regex season_regex_match: match for '%s'" % reversepaths[0])
          folder_season = int(match.group( reversepaths[0]) )
          reversepaths.pop(0) #remove first item from list
          break
 
  ### Clean folder name and get year if present ###
  (misc,        folder_year) = VideoFiles.CleanName(                        reversepaths[0])    # Take folder year
  (folder_show, misc       ) = VideoFiles.CleanName( re.sub(r'\(\w*\)', '', reversepaths[0]) )  # Remove (xxx) groups and take serie name
  Log("From folder, show: '%s', year: '%s'" % (folder_show, xint(folder_year)))
 
  ### File loop ###
  for file in files:
    filename = os.path.basename(file)
    
    ### Filter unwanted file extensions ###
    ext = file.split('.')[-1]
    if ext in ignore_suffixes: 
      Log("'%s' ignore_suffixes: match" % filename)
      Log(file, "Plex Media Scanner Custom - ignored suffixes.log")
      files.remove(file)
      continue
 
    ### Filter trailers and sample files ###
    for rx in ignore_files_re_findall:
      result = re.findall(rx, file)
      if len(result): 
        Log("'%s' ignore_files_findall: match" % filename)
        Log(file, "Plex Media Scanner Custom - Ignored files.log")
        files.remove(file)
        break
 
    ### Cleanup filename ###
    ep = os.path.splitext(filename)[0]                               # Show name is the filename without extension
    ep = ep.replace(";", ' ')
    if not folder_show == "": ep = re.sub(folder_show, '', ep)       # remove cleaned folder name (if exist) from the show name
    for group in release_groups: ep = ep.replace(group, " ");
    (misc, year) = VideoFiles.CleanName(ep)                          # Get the year
    (ep,   misc) = VideoFiles.CleanName(re.sub(r'\(\w*\)', '', ep))  # remove all groups in parenthesis (cleanup remove them, not the content), then cleanup remove brackets groups 
    if not folder_show == "":                                        # If containing folder exist or has name different from "_" (scrubed to "")
      ep = re.sub(folder_show, '', ep)                               # And remove the cleaned folder name from the now cleaned show, just in case the directory is off by things CleanName handles
      for rx in whackRx:  ep = re.sub(rx, '', ep)                    # Remove useless tags
      ep = ep.lstrip()                                               # Remove left spaces
      if ep == "": ep = folder_show                                  # If nothing is left, take the folder
      match = re.match(roman_re_match, ep, re.IGNORECASE)
      if match:  ep = roman_to_int(ep)                               # If a roman number    #   convert to int then string
      for special, offset in [['S',0], ['OP',100], ['ED',150], ['T',200], ['P',300], ['O',400] ]:
        if ep.upper().startswith(special) and len(ep)<=4 and (ep[ len(special): ].isdigit() or len(ep)==2):
          season = 0
          try:    episode = str(offset + int( "1" if ep[ len(special):]=="" else ep[ len(special):] )) 
          except: Log("AniDB numbering - issue - ep: '%s', offset: '%d', string: '%s'" % (ep, offset,  ep[ len(special):]))
          else:   ep = "s00e" + episode
          
    ### Check for standalone_episode_re_findall ###
    for rx in standalone_episode_re_findall:
      match = re.findall(rx, ep) #filename
      if len(match): 
        show, junk, year, season, episode, junk, endEpisode, junk, title = match[0]
        episode    = int(episode)
        endEpisode = int(episode) if len(endEpisode) == 0 else int(endEpisode)
        for ep in range(episode, endEpisode+1):
          tv_show                = Media.Episode(show if not len(show) == 0 else folder_show, season, episode, title, year)
          tv_show.display_offset = (ep-episode)*100/(endEpisode-episode+1)
          tv_show.parts.append(file)
          mediaList.append(tv_show)
        Log("show: '%s', year: '%s', season: '%s', ep: %s found usingstandalone_episode_re_findall on cleaned string '%s' gotten from filename '%s'" % (show, xint(year), xint(season), xint(episode), ep, filename))
        break #return
    else:
      
      ### Check for episode_re_search ###
      for rx in episode_re_search:
        match = re.search(rx, ep, re.IGNORECASE)
        if match:  ### Extract data from episode###       
          Log("match group show: " + match.group('show') )
          show, year = VideoFiles.CleanName( match.group('show') )
          show = show if len(show) else folder_show
          #for rx in ends_with_episode_re_sub:  show  = re.sub(rx, '', show)
          season     = int(match.group('season'  ))
          episode    = int(match.group('ep'      ))
          endEpisode = int(match.group('secondEp')) if match.groupdict().has_key('secondEp') and match.group('secondEp') else episode
          for ep in range(episode, endEpisode+1):
            tv_show                = Media.Episode(show, season, episode, 'title', year)
            tv_show.display_offset = (ep-episode)*100/(endEpisode-episode+1)
            tv_show.append([season, int(ep)])
            tv_show.parts.append(file)
            mediaList.append(tv_show)
          Log("show: '%s', year: '%s', season: '%s', ep: %s found using episode_re_search on cleaned string '%s' gotten from filename '%s'" % (show, xint(year), xint(season), xint(episode), ep, filename))
          break
      else:
        
        ### Check for just_episode_re_search ### #if re.match('.+ \([1-2][0-9]{3}\)', show): 
        for rx in just_episode_re_search:
          match = re.search(rx, ep, re.IGNORECASE)
          if match:
            season  = 1
            if folder_season is not None: season = folder_season                                                                       
            episode    = int(match.group('ep'))
            if folder_show == "" or len(ep)>8:
              show = ep[:ep.find(match.group('ep'))-1] # ep.replace(match.group('ep'), "").rstrip() #Blue submarine 6 12
            else: show = folder_show
            if episode >= 100 and int(episode / 100) == season: episode = episode % 100                # See if we accidentally parsed the episode as season.
            tv_show = Media.Episode(show, season, episode, None, year)
            tv_show.parts.append(file)
            mediaList.append(tv_show)
            Log("show: '%s', year: '%s', season: '%s', ep: %s found using just_episode_re_search on cleaned string '%s' gotten from filename '%s'" % (show, xint(year), xint(season), xint(episode), ep, filename))
            break
        else:
 
          ### No regular expression worked ###
          Log("*no show found found on cleaned string '%s' gotten from filename '%s'" % (ep, filename))
          Log(file, "Plex Media Scanner Custom - Skipped files.log")
