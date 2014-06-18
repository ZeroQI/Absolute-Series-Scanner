#Another Plex Series Scanner
#Version 1.0 - December 01, 2013
#BreezWaveFun

import re, os, os.path
import Media, VideoFiles, Stack, Utils
from mp4file import mp4file, atomsearch

episode_id_regexps = [
    '([sS])?(?P<fileSeasonNum>[0-9]+)[eEx](?P<fileEpisodeNum>[0-9]+)',
    '(?P<fileTitle>[a-zA-Z0-9\-\s\']+)\((?P<fileYear>[0-9]+)-(?P<fileMonth>[0-9]+)-(?P<fileDay>[0-9]+)\)',
    '(?P<fileYear>[0-9]+)-(?P<fileMonth>[0-9]+)-(?P<fileDay>[0-9]+)'
  ]

episode_seperators = [
  ' - '
  ]

season_dir_regexp = '([sS])?(eason\s)?(\ires\s)?(?P<dirSeasonNum>[0-9]+)(\s\((?P<dirSeasonYears>[0-9-]+)?\))?'

# Look for episodes.
def Scan(path, files, mediaList, subdirs, language=None, root=None):
  #print "jpss"
  
  # Scan for video files.
  VideoFiles.Scan(path, files, mediaList, subdirs, root)
  
  if len(files) ==  0:
   #print "WARN: No Files: ", path
   return
  
  # Take top two as show/season, but require at least the top one.
  paths = Utils.SplitPath(path)
  
  if len(paths) != 2:
    print "WARN: file found not in season dir: path: ", path, " : len(paths): ", len(paths)

  if len(paths) > 2:
    print "ERR: File Too Deep, not checking: len(paths) > 2"
    return

  root_dir_match = None
  season_dir_match = None
  
  if len(paths) > 0:
    #print "paths[0]: ", paths[0]
    dirShowNameFull = paths[0].strip()
    splits = paths[0].split("(")
    if len(splits) > 2:
      print "WARN: Multiple '(' in directory name: Len: ", len(splits)
    dirShowNameShort = splits[0].strip()
  
  if len(paths) > 1: 
    #print "paths[1]: ", paths[1]
    season_dir_match = re.search(season_dir_regexp, paths[1], re.IGNORECASE)
    #print "season_dir_match: ", season_dir_match.groupdict()

  for filepath in files:
    filename = os.path.basename(filepath)
    #print "filename: ", filename
    file_matchs = []
    fileShowName = None
    for sepstr in episode_seperators:
      splits = filename.split(sepstr)
      if len(splits) == 3:
	fileShowName = splits[0]
      for splitstr in splits:
	#print "splitstr: ", splitstr
	foundEpisode = False
	for rx in episode_id_regexps:
	  file_match = re.search(rx, splitstr, re.IGNORECASE)
	  if file_match is not None:
	    #print "file_match: ", file_match.groupdict()
	    file_matchs.append(file_match)
	    if file_match.groupdict().has_key('fileEpisodeNum'):
	      foundEpisode = True
	      
    decodeError = False
	
    showName = None
    if fileShowName is None:
      showName = dirShowNameShort
    else:
      showName = fileShowName.strip()
      if dirShowNameFull is not None:
	if (dirShowNameFull != showName) and (dirShowNameShort != showName):
	  print "WARN: dirShowName and fileShowName dont match, Using fileShowName! dirShowNameFull: ", dirShowNameFull, " dirShowNameShort: ", dirShowNameShort, " file: ", fileShowName 
    if showName is None:
      print "ERR: Showname is None!"
      decodeError = True
    
    showYear = None   
    if root_dir_match is not None:
     if root_dir_match.groupdict().has_key('dirShowYears'):
      showYear = root_dir_match.group('dirShowYears')
      if showYear is not None:
	showYear = showYear.strip()
    
    dirSeasonNum = None   
    if season_dir_match is not None:
     if season_dir_match.groupdict().has_key('dirSeason'):
      dirSeasonNum = season_dir_match.group('dirSeason')
      if dirSeasonNum is not None:
	dirSeasonNum = dirSeasonNum.strip()
    
    seasonNumMatchCount = 0
    episodeNumMatchCount = 0
    yearMatchCount = 0
    monthMatchCount = 0
    dayMatchCount = 0
    titleMatchCount = 0
    seasonNum = None
    episodeNum = None
    year = None
    month = None
    day = None
    title = None
    for match in file_matchs:
      #print "file_match: ", match.groupdict()
      if match.groupdict().has_key('fileSeasonNum'):
	temp = match.group('fileSeasonNum')
	if temp is not None:
	  temp = temp.strip()
	  if dirSeasonNum is not None:
	    if temp != dirSeasonNum:
	      print "WARN: fileSeasonNum doesnt match dirSeasonNum. Using fileSeasonNum! first: ", leSeasonNum, " latest: ", dirSeasonNum
	  if (seasonNumMatchCount > 0) and (temp.strip() != seasonNum):
	    print "WARN: multiple fileSeasonNum and they dont match, Using first! first: ", seasonNum, " latest: ", temp
	  else:
	    seasonNum = temp
	  seasonNumMatchCount = seasonNumMatchCount + 1
      if match.groupdict().has_key('fileEpisodeNum'):
	temp = match.group('fileEpisodeNum')
	if temp is not None:
	  temp = temp.strip()
	  if (episodeNumMatchCount > 0) and (temp.strip() != episodeNum):
	    print "WARN: multiple episodeNum and they dont match, Using first! first: ", episodeNum, " latest: ", temp
	  else:
	    episodeNum = temp
	  episodeNumMatchCount = episodeNumMatchCount + 1
      if match.groupdict().has_key('fileYear'):
	temp = match.group('fileYear')
	if temp is not None:
	  temp = temp.strip()
	  if (yearMatchCount > 0) and (temp.strip() != year):
	    print "WARN: multiple year and they dont match, Using first! first: ", year, " latest: ", temp
	  else:
	    year = temp
	  yearMatchCount = yearMatchCount + 1
      if match.groupdict().has_key('fileMonth'):
	temp = match.group('fileMonth')
	if temp is not None:
	  temp = temp.strip()
	  if (monthMatchCount > 0) and (temp.strip() != month):
	    print "WARN: multiple month and they dont match, Using first! first: ", month, " latest: ", temp
	  else:
	    month = temp
	  monthMatchCount = monthMatchCount + 1
      if match.groupdict().has_key('fileDay'):
	temp = match.group('fileDay')
	if temp is not None:
	  temp = temp.strip()
	  if (dayMatchCount > 0) and (temp.strip() != day):
	    print "WARN: multiple fileEpisodeNum and they dont match, Using first! first: ", day, " latest: ", temp
	  else:
	    day = temp
	  dayMatchCount = dayMatchCount + 1
      if match.groupdict().has_key('fileTitle'):
	temp = match.group('fileTitle')
	if temp is not None:
	  temp = temp.strip()
	  if (titleMatchCount > 0) and (temp.strip() != title):
	    print "WARN: multiple fileEpisodeNum and they dont match, Using first! first: ", title, " latest: ", temp
	  else:
	    title = temp
	  titleMatchCount = titleMatchCount + 1
    
    
    if (episodeNum is None) and (day is None):
      print "ERR: No episode number or date!"
      decodeError = True
    
    #print "RESULT:", decodeError, ":",showName,",",seasonNum,",",episodeNum,",",title,":", paths[0], "/", paths[1], "/", filename
    
    if decodeError == False:
      tv_show = Media.Episode(showName, seasonNum, episodeNum, title, showYear)
      if (year is not None) and (month is not None) and (day is not None):
	tv_show.released_at = '%d-%02d-%02d' % (int(year), int(month), int(day))
      tv_show.parts.append(filepath)
      mediaList.append(tv_show)
    else:
      print "FilePath: ", filepath
      #if paths[1] is not None:
	#print "RESULT:", decodeError, ":",showName,",",seasonNum,",",episodeNum,",",title,":", paths[0], "/", paths[1], "/", filename
      #else:
	#if paths[0] is not None:
	  #print "RESULT:", decodeError, ":",showName,",",seasonNum,",",episodeNum,",",title,":", paths[0], "/", filename
        #else:
          #print "RESULT:", decodeError, ":",showName,",",seasonNum,",",episodeNum,",",title,":", filename

      
  # Stack the results.
  Stack.Scan(path, files, mediaList, subdirs)
  

import sys
    
if __name__ == '__main__':
  print "Hello, world!"
  path = sys.argv[1]
  files = [os.path.join(path, file) for file in os.listdir(path)]
  media = []
  Scan(path[1:], files, media, [])
  print "Media:", media
