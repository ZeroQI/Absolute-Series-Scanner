#
# This is an UNSUPPORTED, scanner based on the Plex Movie Scanner as of 2014-02-03.
# Please see handbrake.fr, makemkv.com, and/or Google to learn how to rip your legacy disc images into streamable files.
#
# Mostly Copyright (c) 2014, Plex Development Team. All rights reserved.
#

import re, os, os.path, datetime, titlecase, unicodedata, sys
import Media, VideoFiles, Stack, Utils, Filter
SeriesScanner = __import__('Plex Series Scanner')

nice_match = '(.+) [\(\[]([1-2][0-9]{3})[\)\]]'
standalone_tv_regexs = [ '(.*?)( \(([0-9]+)\))? - ([0-9])+x([0-9]+)(-[0-9]+[Xx]([0-9]+))? - (.*)' ]

# Scans through files, and add to the media list.
def Scan(path, files, mediaList, subdirs, language=None, root=None, **kwargs):
  
  # Scan for video files.
  VideoFilesScan(path, files, mediaList, subdirs, root)
  
  # Check for DVD rips.
  paths = Utils.SplitPath(path)
  video_ts = Utils.ContainsFile(files, 'video_ts.ifo')
  if video_ts is None:
    video_ts = Utils.ContainsFile(files, 'video_ts.bup')
    
  if len(paths) >= 1 and len(paths[0]) > 0 and video_ts is not None:
    print "Found a DVD"
    name = year = None
    
    # Now find the name.
    if paths[-1].lower() == 'video_ts' and len(paths) >= 2:
      # Easiest case.
      (name, year) = CleanName(paths[-2])
    else:
      # Work up until we find a viable candidate.
      backwardsPaths = paths
      backwardsPaths.reverse()
      for p in backwardsPaths:
        if re.match(nice_match, p):
          (name, year) = CleanName(p)
          break
          
      if name is None:
        # Use the topmost path.
        (name, year) = CleanName(paths[0])

    movie = Media.Movie(name, year)
    
    # Add the video_ts file first.
    movie.parts.append(video_ts)

    biggestFile = None
    biggestSize = 0
    
    for i in files:
      if os.path.splitext(i)[1].lower() == '.vob' and os.path.getsize(i) > biggestSize:
        biggestSize = os.path.getsize(i)
        biggestFile = i
       
    # Add the biggest part so that we can get thumbnail/art/analysis from it. 
    if biggestFile is not None:
      movie.parts.append(biggestFile)
        
    if len(movie.parts) > 0:
      movie.guid = checkNfoFile(movie.parts[0], 1)
      mediaList.append(movie)

  # Check for Bluray rips.
  elif len(paths) >= 3 and paths[-1].lower() == 'stream' and paths[-2].lower() == 'bdmv':
    (name, year) = CleanName(paths[-3])
    movie = Media.Movie(name, year)
    for i in files:
      movie.parts.append(i)
    mediaList.append(movie)
    
  else:
    
    # Make movies!
    for i in files:
      file = os.path.basename(i)
      (name, year) = CleanName(os.path.splitext(file)[0])
      
      # If it matches a TV show, don't scan it as a movie.
      tv = False
      for rx in SeriesScanner.episode_regexps[0:-1]:
        if re.match(rx, file):
          print "The file", file, "looked like a TV show so we're skipping it (", rx, ")"
          tv = True
          
      if tv == False:
        # OK, it's a movie
        movie = Media.Movie(name, year)
        movie.source = RetrieveSource(file)
        movie.parts.append(i)
        mediaList.append(movie)

    # Stack the results.
    Stack.Scan(path, files, mediaList, subdirs)

    # Clean the folder name and try a match on the folder.
    if len(path) > 0:
      folderName = os.path.basename(path).replace(' ', ' ').replace(' ','.')
      (cleanName, year) = CleanName(folderName)
      if len(mediaList) == 1 and re.match(nice_match, cleanName):
        res = re.findall(nice_match, cleanName) 
        mediaList[0].name = res[0][0]
        mediaList[0].year = res[0][1]
      elif len(mediaList) == 1 and (len(cleanName) > 1 or year is not None):
        mediaList[0].name = cleanName
        mediaList[0].year = year

    # Check for a folder with multiple 'CD' subfolders and massage
    foundCDsubdirs = {}
    for s in subdirs:
      m = re.match('cd[ ]*([0-9]+)', os.path.basename(s).lower())
      if m:
        foundCDsubdirs[int(m.groups(1)[0])] = s

    # More than one cd subdir, let's stack and whack subdirs.
    if len(foundCDsubdirs) > 1:
      name, year = CleanName(os.path.basename(path))
      movie = Media.Movie(name, year)
      movie.guid = checkNfoFile(os.path.dirname(foundCDsubdirs.values()[0]), 1)
      
      keys = foundCDsubdirs.keys()
      keys.sort()
      for key in keys:
        d = foundCDsubdirs[key]
        subFiles = []
        for f in os.listdir(d):
          subFiles.append(os.path.join(d,f))
        VideoFilesScan(d, subFiles, mediaList, [], None)
        subdirs.remove(d)
        movie.parts += subFiles
        
      if len(movie.parts) > 0:
        mediaList.append(movie)

    # See if we can find a GUID.
    for mediaItem in mediaList:
      if mediaItem.guid is None:
        mediaItem.guid = checkNfoFile(mediaItem.parts[0], len(mediaList))

    if len(mediaList) == 1:
      if mediaList[0].source is None:
        mediaList[0].source = RetrieveSource(path)
         
  # If the subdirectories indicate that we're inside a DVD, when whack things other than audio and video.
  whack = []
  if 'video_ts' in [Utils.SplitPath(s)[-1].lower() for s in subdirs]:
    for dir in subdirs:
      d = os.path.basename(dir).lower()
      if d not in ['video_ts', 'audio_ts']:
        whack.append(dir)
  
  # Finally, if any of the subdirectories match a TV show, don't enter!
  for dir in subdirs:
    for rx in standalone_tv_regexs:
      res = re.findall(rx, dir)
      if len(res):
        whack.append(dir)
        
  for w in whack:
    subdirs.remove(w)

def checkNfoFile(file, fileCount):
  try:
    path = None
    
    # Depending on how many media files we have, check differently.
    if fileCount == 1:
      # Look for any NFO file.
      for f in os.listdir(os.path.dirname(file)):
        if f[-4:].lower() == '.nfo':
          path = os.path.join(os.path.dirname(file), f)
          break
    else:
      # Look for a sidecar NFO file.
      path = os.path.splitext(file)[0] + '.nfo'

    if path is not None and os.path.exists(path):
      nfoText = open(path).read()
      m = re.search('(tt[0-9]+)', nfoText)
      if m:
        return m.groups(1)[0]
  except:
    print "Warning, couldn't read NFO file."

  return None

video_exts = ['3g2', '3gp', 'asf', 'asx', 'avc', 'avi', 'avs', 'bin', 'bivx', 'bup', 'divx', 'dv', 'dvr-ms', 'evo', 'fli', 'flv', 'ifo', 'img', 
              'iso', 'm2t', 'm2ts', 'm2v', 'm4v', 'mkv', 'mov', 'mp4', 'mpeg', 'mpg', 'mts', 'nrg', 'nsv', 'nuv', 'ogm', 'ogv', 'tp',
              'pva', 'qt', 'rm', 'rmvb', 'sdp', 'svq3', 'strm', 'ts', 'ty', 'vdr', 'viv', 'vob', 'vp3', 'wmv', 'wpl', 'wtv', 'xsp', 'xvid', 'webm']

ignore_samples = ['[-\._ ]sample', 'sample[-\._ ]']
ignore_trailers = ['-trailer\.']
ignore_dirs =  ['extras?', '!?samples?', 'bonus', '.*bonus disc.*']
ignore_suffixes = ['.dvdmedia']

source_dict = {'bluray':['bdrc','bdrip','bluray','bd','brrip','hdrip','hddvd','hddvdrip'],'cam':['cam'],'dvd':['ddc','dvdrip','dvd','r1','r3','r5'],'retail':['retail'],
               'dtv':['dsr','dsrip','hdtv','pdtv','ppv'],'stv':['stv','tvrip'],'screener':['bdscr','dvdscr','dvdscreener','scr','screener'],
               'svcd':['svcd'],'vcd':['vcd'],'telecine':['tc','telecine'],'telesync':['ts','telesync'],'web':['webrip','web-dl'],'workprint':['wp','workprint']}
source = []
for d in source_dict:
  for s in source_dict[d]:
    if source != '':
      source.append(s)

audio = ['([^0-9])5\.1[ ]*ch(.)','([^0-9])5\.1([^0-9]?)','([^0-9])7\.1[ ]*ch(.)','([^0-9])7\.1([^0-9])']
subs = ['multi','multisubs']
misc = ['cd1','cd2','1cd','2cd','custom','internal','repack','read.nfo','readnfo','nfofix','proper','rerip','dubbed','subbed','extended','unrated','xxx','nfo','dvxa']
format = ['ac3','dc','divx','fragment','limited','ogg','ogm','ntsc','pal','ps3avchd','r1','r3','r5','720i','720p','1080i','1080p','remux','x264','xvid','vorbis','aac','dts','fs','ws','1920x1080','1280x720','h264']
edition = ['dc','se'] # dc = directors cut, se = special edition
yearRx = '([\(\[\.\-])([1-2][0-9]{3})([\.\-\)\]_,+])'

# Cleanup folder / filenames
def CleanName(name):
  
  orig = name

  # Make sure we pre-compose.  Try to decode with reported filesystem encoding, then with UTF-8 since some filesystems lie.
  try:
    name = unicodedata.normalize('NFKC', name.decode(sys.getfilesystemencoding()))
  except:
    try:
      name = unicodedata.normalize('NFKC', name.decode('utf-8'))
    except:
      pass

  name = name.lower()

  # grab the year, if there is one. set ourselves up to ignore everything after the year later on.
  year = None
  yearMatch = re.search(yearRx, name)
  if yearMatch:
    yearStr = yearMatch.group(2)
    yearInt = int(yearStr)
    if yearInt > 1900 and yearInt < (datetime.date.today().year + 1):
      year = int(yearStr)
      name = name.replace(yearMatch.group(1) + yearStr + yearMatch.group(3), ' *yearBreak* ')
    
  # Take out things in brackets. (sub acts weird here, so we have to do it a few times)
  done = False
  while done == False:
    (name, count) = re.subn(r'\[[^\]]+\]', '', name, re.IGNORECASE)
    if count == 0:
      done = True
  
  # Take out bogus suffixes.
  for suffix in ignore_suffixes:
    rx = re.compile(suffix + '$', re.IGNORECASE)
    name = rx.sub('', name)
  
  # Take out audio specs, after suffixing with space to simplify rx.
  name = name + ' '
  for s in audio:
    rx = re.compile(s, re.IGNORECASE)
    name = rx.sub(' ', name)
  
  # Now tokenize.
  tokens = re.split('([^ \-_\.\(\)+]+)', name)
  
  # Process tokens.
  newTokens = []
  for t in tokens:
    t = t.strip()
    if not re.match('[\.\-_\(\)+]+', t) and len(t) > 0:
    #if t not in ('.', '-', '_', '(', ')') and len(t) > 0:
      newTokens.append(t)

  # Now build a bitmap of good and bad tokens.
  tokenBitmap = []

  garbage = subs
  garbage.extend(misc)
  garbage.extend(format)
  garbage.extend(edition)
  garbage.extend(source)
  garbage.extend(video_exts)
  garbage = set(garbage)
  
  for t in newTokens:
    if t.lower() in garbage:
      tokenBitmap.append(False)
    else:
      tokenBitmap.append(True)
  
  # Now strip out the garbage, with one heuristic; if we encounter 2+ BADs after encountering
  # a GOOD, take out the rest (even if they aren't BAD). Special case for director's cut.
  numGood = 0
  numBad  = 0
  
  finalTokens = []
  
  for i in range(len(tokenBitmap)):
    good = tokenBitmap[i]
    
    # If we've only got one or two tokens, don't whack any, they might be part of
    # the actual name (e.g. "Internal Affairs" "XXX 2")
    #
    if len(tokenBitmap) <= 2:
      good = True
    
    if good and numBad < 2:
      if newTokens[i] == '*yearBreak*':
        #if we have a year, we can ignore everything after this.
        break
      else:
        finalTokens.append(newTokens[i])
    elif not good and newTokens[i].lower() == 'dc':
      finalTokens.append("(Director's cut)")
    
    if good == True:
      numGood += 1
    else:
      numBad += 1

  # If we took *all* the tokens out, use the first one, otherwise we'll end up with no name at all.
  if len(finalTokens) == 0 and len(newTokens) > 0:
    finalTokens.append(newTokens[0])
    
  #print "CLEANED [%s] => [%s]" % (orig, u' '.join(finalTokens))
  #print "TOKENS: ", newTokens
  #print "BITMAP: ", tokenBitmap
  #print "FINAL:  ", finalTokens
  
  cleanedName = ' '.join(finalTokens)
  cleanedName = cleanedName.encode('utf-8')
  return (titlecase.titlecase(cleanedName), year)

# Remove files that aren't videos.
def VideoFilesScan(path, files, mediaList, subdirs, root=None):
  
  # Filter out bad stuff.
  Filter.Scan(path, files, mediaList, subdirs, video_exts, root)
  
  filesToRemove = []
  for i in files:
    # Remove files that aren't video.
    (file, ext) = os.path.splitext(i)
      
    # Remove sample files if they're smaller than 300MB.
    for rx in ignore_samples:
      if re.search(rx, i, re.IGNORECASE) and os.path.getsize(i) < 300 * 1024 * 1024:
        filesToRemove.append(i)

    # Remove trailer files.
    for rx in ignore_trailers:
      if re.search(rx, i, re.IGNORECASE):
        filesToRemove.append(i)
        
  # Uniquify and remove.
  filesToRemove = list(set(filesToRemove))
  for i in filesToRemove:
    files.remove(i)
      
  # Check directories, but not at the top-level.
  ignore_dirs_total = []
  if len(path) > 0:
    ignore_dirs_total += ignore_dirs
  
  whack = []
  for dir in subdirs:
    baseDir = os.path.basename(dir)
    for rx in ignore_dirs_total:
      if re.match(rx, baseDir, re.IGNORECASE):
        whack.append(dir)
        break
  
  for w in whack:
    subdirs.remove(w)
      
def RetrieveSource(name):
  name = os.path.basename(name)
  wordSplitter = re.compile(r"[^a-zA-Z0-9']+", re.IGNORECASE)
  words = wordSplitter.split(name.upper())
  sources = source
  foundSources = []
  
  # Return the first one we find.
  for d in source_dict:
    for s in source_dict[d]:
      if s.upper() in words:
        return d

# Find the first occurance of a year.
def FindYear(words):
  yearRx = '^[1-2][0-9]{3}$'
  i = 0
  for w in words:
    if re.match(yearRx, w):
      year = int(w)
      if year > 1900 and year < datetime.date.today().year + 1:
        return i
    i += 1
    
  return None
