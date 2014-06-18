#
# Copyright (c) 2013 Jorge Schrauwen. All rights reserved.
#
# AniDB Is a scanner that will parse files renamed using adbren.pl using the following format:
# %anime_name_romaji% - %episode% - %episode_name% - [%group_short%](%crc32%).%filetype%
#
 
import re, os, os.path
import Media, VideoFiles, Stack, Utils
 
# parse episode number
def parseEpisode(ep, season=1):
  try:
    int(ep)
    return [[season, int(ep)]]
  except ValueError:
    if season > 0:
      if ep[0:1].upper() == 'S':
        return parseEpisode(ep[1:], 0)
      else:
        if ep.find('-') > 0:
          mep = ep.split('-')
          mepr = []
          try:
            for ep in range(int(mep[0]), (int(mep[1]) + 1)):
              mepr.append([season, int(ep)])
          except:
            pass
          finally:
            if len(mepr) > 0:
              return mepr
            else:
              return None
    else:
      return None
 
# Scans through files, and add to the media list.
def Scan(path, files, mediaList, subdirs, language=None, root=None):
  # Just look for video files.
  VideoFiles.Scan(path, files, mediaList, subdirs, root)
 
  # Add them all.
  for path in files:
    (show, year) = VideoFiles.CleanName(os.path.basename(path))
    file = Utils.SplitPath(path)[-1]
    ext = file.split('.')[-1]
    name = '.'.join(file.split('.')[0:-1])
    nameChunks = name.split(' - ')
 
    # correct for "-" in show name or title
    if len(nameChunks) > 4:
      if parseEpisode(nameChunks[1]) == None:
        if len(nameChunks[1]) >= 4:
          if parseEpisode(nameChunks[2]) <> None:
            extra = nameChunks.pop(1)
            nameChunks[0] = "%s - %s" % (nameChunks[0], extra)
      else:
        while len(nameChunks) > 4:
          extra = nameChunks.pop(3)
          nameChunks[2] = "%s - %s" % (nameChunks[2], extra)
 
    try:
      sep = parseEpisode(nameChunks[1])
      if sep <> None:
        if len(sep) == 1:
          anime_ep = Media.Episode(nameChunks[0], sep[0][0], sep[0][1], nameChunks[2])
          anime_ep.parts.append(path)
          mediaList.append(anime_ep)
        else:
          for ep in sep:
            beginEp = sep[0][1]
            endEp = sep[-1][1]
 
            anime_ep = Media.Episode(nameChunks[0], ep[0], ep[1], nameChunks[2])
            anime_ep.display_offset = (ep[1]-beginEp)*100/(endEp-beginEp+1)
            anime_ep.parts.append(path)
            mediaList.append(anime_ep)
 
    except:
      with open('/tmp/adb-unmatchables.log', 'a') as log:
        log.write("%s\n" % file)
