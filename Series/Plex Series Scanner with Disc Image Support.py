#
# Copyright (c) 2010 Plex Development Team. All rights reserved.
#
import re, os, os.path, datetime, titlecase, unicodedata, sys
import Media, VideoFiles, Stack, Utils, Filter
from mp4file import mp4file, atomsearch

episode_regexps = [
    '(?P<show>.*?)[sS](?P<season>[0-9]+)[\._ ]*[eE](?P<ep>[0-9]+)([- ]?[Ee+](?P<secondEp>[0-9]+))?',                           # S03E04-E05
    '(?P<show>.*?)[sS](?P<season>[0-9]{2})[\._\- ]+(?P<ep>[0-9]+)',                                                            # S03-03
    '(?P<show>.*?)([^0-9]|^)(?P<season>(19[3-9][0-9]|20[0-5][0-9]|[0-9]{1,2}))[Xx](?P<ep>[0-9]+)(-[0-9]+[Xx](?P<secondEp>[0-9]+))?',  # 3x03
    '(.*?)[^0-9a-z](?P<season>[0-9]{1,2})(?P<ep>[0-9]{2})([\.\-][0-9]+(?P<secondEp>[0-9]{2})([ \-_\.]|$)[\.\-]?)?([^0-9a-z%]|$)' # .602.
  ]

date_regexps = [
    '(?P<year>[0-9]{4})[^0-9a-zA-Z]+(?P<month>[0-9]{2})[^0-9a-zA-Z]+(?P<day>[0-9]{2})([^0-9]|$)',                # 2009-02-10
    '(?P<month>[0-9]{2})[^0-9a-zA-Z]+(?P<day>[0-9]{2})[^0-9a-zA-Z(]+(?P<year>[0-9]{4})([^0-9a-zA-Z]|$)', # 02-10-2009
  ]

standalone_episode_regexs = [
  '(.*?)( \(([0-9]+)\))? - ([0-9]+)+x([0-9]+)(-[0-9]+[Xx]([0-9]+))?( - (.*))?',  # Newzbin style, no _UNPACK_
  '(.*?)( \(([0-9]+)\))?[Ss]([0-9]+)+[Ee]([0-9]+)(-[0-9]+[Xx]([0-9]+))?( - (.*))?'   # standard s00e00
  ]
  
season_regex = '.*?(?P<season>[0-9]+)$' # folder for a season

just_episode_regexs = [
    '(?P<ep>[0-9]{1,3})[\. -_]*of[\. -_]*[0-9]{1,3}',       # 01 of 08
    '^(?P<ep>[0-9]{1,3})[^0-9]',                           # 01 - Foo
    'e[a-z]*[ \.\-_]*(?P<ep>[0-9]{2,3})([^0-9c-uw-z%]|$)', # Blah Blah ep234
    '.*?[ \.\-_](?P<ep>[0-9]{2,3})[^0-9c-uw-z%]+',         # Flah - 04 - Blah
    '.*?[ \.\-_](?P<ep>[0-9]{2,3})$',                      # Flah - 04
    '.*?[^0-9x](?P<ep>[0-9]{2,3})$'                        # Flah707
  ]

ends_with_number = '.*([0-9]{1,2})$'

ends_with_episode = ['[ ]*[0-9]{1,2}x[0-9]{1,3}$', '[ ]*S[0-9]+E[0-9]+$']

# Look for episodes.
def Scan(path, files, mediaList, subdirs, language=None, root=None):
  
  # Scan for video files.
  VideoFilesScan(path, files, mediaList, subdirs, root)
  
  # Take top two as show/season, but require at least the top one.
  paths = Utils.SplitPath(path)
  shouldStack = True
  
  if len(paths) == 1 and len(paths[0]) == 0:
  
    # Run the select regexps we allow at the top level.
    for i in files:
      file = os.path.basename(i)
      for rx in episode_regexps[0:-1]:
        match = re.search(rx, file, re.IGNORECASE)
        if match:
          
          # Extract data.
          show = match.group('show')
          season = int(match.group('season'))
          episode = int(match.group('ep'))
          endEpisode = episode
          if match.groupdict().has_key('secondEp') and match.group('secondEp'):
            endEpisode = int(match.group('secondEp'))
          
          # Clean title.
          name, year = CleanName(show)
          if len(name) > 0:
            for ep in range(episode, endEpisode+1):
              tv_show = Media.Episode(name, season, ep, '', year)
              tv_show.display_offset = (ep-episode)*100/(endEpisode-episode+1)
              tv_show.parts.append(i)
              mediaList.append(tv_show)
  
  elif len(paths) > 0 and len(paths[0]) > 0:
    done = False
        
    # See if parent directory is a perfect match (e.g. a directory like "24 - 8x02 - Day 8_ 5_00P.M. - 6_00P.M")
    if len(files) == 1:
      for rx in standalone_episode_regexs:
        res = re.findall(rx, paths[-1])
        if len(res):
          show, junk, year, season, episode, junk, endEpisode, junk, title = res[0]
          
          # If it didn't have a show, then grab it from the directory.
          if len(show) == 0:
            (show, year) = CleanName(paths[0])
            
          episode = int(episode)
          if len(endEpisode) > 0:
            endEpisode = int(endEpisode)
          else:
            endEpisode = episode
            
          for ep in range(episode, endEpisode+1):
            tv_show = Media.Episode(show, season, ep, title, year)
            tv_show.display_offset = (ep-episode)*100/(endEpisode-episode+1)
            tv_show.parts.append(files[0])
            mediaList.append(tv_show)
            
          done = True
          break
          
    if done == False:

      # Not a perfect standalone match, so get information from directories. (e.g. "Lost/Season 1/s0101.mkv")
      season = None
      seasonNumber = None

      (show, year) = CleanName(paths[0])
      
      # Which component looks like season?
      if len(paths) >= 2:
        season = paths[len(paths)-1]
        match = re.match(season_regex, season, re.IGNORECASE)
        if match:
          seasonNumber = int(match.group('season'))
      
      # Make sure an episode name didn't make it into the show.
      for rx in ends_with_episode:
        show = re.sub(rx, '', show)

      for i in files:
        done = False
        file = os.path.basename(i)
        (file, ext) = os.path.splitext(file)
        
        if ext.lower() in ['.mp4', '.m4v', '.mov']:
          m4season = m4ep = m4year = 0
          m4show = title = ''
          try: 
            mp4fileTags = mp4file.Mp4File(i)
            
            # Show.
            try: m4show = find_data(mp4fileTags, 'moov/udta/meta/ilst/tvshow').encode('utf-8')
            except: pass
              
            # Season.
            try: m4season = int(find_data(mp4fileTags, 'moov/udta/meta/ilst/tvseason'))
            except: pass
              
            # Episode.
            m4ep = None
            try:
              # tracknum (can be 101)
              m4ep = int(find_data(mp4fileTags, 'moov/udta/meta/ilst/tracknum'))
            except:
              try:
                # tvepisodenum (can be S2E16)
                m4ep = find_data(mp4fileTags, 'moov/udta/meta/ilst/tvepisodenum')
              except:
                # TV Episode (can be 101)
                m4ep = int(find_data(mp4fileTags, 'moov/udta/meta/ilst/tvepisode'))
            
            if m4ep is not None:
              found = False
              try:
                # See if it matches regular expression.
                for rx in episode_regexps[:-1]:
                  match = re.search(rx, file, re.IGNORECASE)
                  if match:
                    m4season = int(match.group('season'))
                    m4ep = int(match.group('ep'))
                    found = True
              
                if found == False and re.match('[0-9]+', str(m4ep)):
                  # Carefully convert to episode number.
                  m4ep = int(m4ep) % 100
                elif found == False:
                  m4ep = int(re.findall('[0-9]+', m4ep)[0])
              except:
                pass

            # Title.
            try: title = find_data(mp4fileTags, 'moov/udta/meta/ilst/title').encode('utf-8')
            except: pass
              
            # Year.
            try: m4year = int(find_data(mp4fileTags, 'moov/udta/meta/ilst/year')[:4])
            except: pass
            
            if year and m4year == 0:
              m4year = year

            # If we have all the data we need, add it.
            if len(m4show) > 0 and m4season > 0 and m4ep > 0:
              tv_show = Media.Episode(m4show, m4season, m4ep, title, m4year)
              tv_show.parts.append(i)
              mediaList.append(tv_show)
              continue

          except:
            pass
        
        # Check for date-based regexps first.
        for rx in date_regexps:
          match = re.search(rx, file)
          if match:

           # Make sure there's not a stronger season/ep match for the same file.
            try:
              for r in episode_regexps[:-1] + standalone_episode_regexs:
                if re.search(r, file):
                  raise
            except:
              break

            year = int(match.group('year'))
            month = int(match.group('month'))
            day = int(match.group('day'))

            # Use the year as the season.
            tv_show = Media.Episode(show, year, None, None, None)
            tv_show.released_at = '%d-%02d-%02d' % (year, month, day)
            tv_show.parts.append(i)
            mediaList.append(tv_show)

            done = True
            break

        if done == False:

          # Take the year out, because it's not going to help at this point.
          cleanName, cleanYear = CleanName(file)
          if cleanYear != None:
            file = file.replace(str(cleanYear), 'XXXX')
            
          # Minor cleaning on the file to avoid false matches on H.264, 720p, etc.
          whackRx = ['([hHx][\.]?264)[^0-9]', '[^[0-9](720[pP])', '[^[0-9](1080[pP])', '[^[0-9](480[pP])']
          for rx in whackRx:
            file = re.sub(rx, ' ', file)
          
          for rx in episode_regexps:
            
            match = re.search(rx, file, re.IGNORECASE)
            if match:
              # Parse season and episode.
              the_season = int(match.group('season'))
              episode = int(match.group('ep'))
              endEpisode = episode
              if match.groupdict().has_key('secondEp') and match.group('secondEp'):
                endEpisode = int(match.group('secondEp'))
                
              # More validation for the weakest regular expression.
              if rx == episode_regexps[-1]:
                
                # Look like a movie? Skip it.
                if re.match('.+ \([1-2][0-9]{3}\)', paths[-1]):
                  done = True
                  break
                  
                # Skip episode 0 on the weak regex since it's pretty much never right.
                if the_season == 0:
                  break
                  
                # Make sure this isn't absolute order.
                if seasonNumber is not None:
                  if seasonNumber != the_season:
                    # Something is amiss, see if it starts with an episode numbers.
                    if re.search('^[0-9]+[ -]', file):
                      # Let the episode matcher have it.
                      break
                    
                    # Treat the whole thing as an episode.
                    episode = episode + the_season*100
                    if endEpisode is not None:
                      endEpisode = endEpisode + the_season*100

              for ep in range(episode, endEpisode+1):
                tv_show = Media.Episode(show, the_season, ep, None, year)
                tv_show.display_offset = (ep-episode)*100/(endEpisode-episode+1)
                tv_show.parts.append(i)
                mediaList.append(tv_show)
              
              done = True
              break
              
        if done == False:
          
          # OK, next let's see if we're dealing with something that looks like an episode.
          # Begin by cleaning the filename to remove garbage like "h.264" that could throw
          # things off.
          #
          (file, fileYear) = CleanName(file)

          # if don't have a good year from before (when checking the parent folders) AND we just got a good year, use it.
          if not year and fileYear: 
            year = fileYear

          for rx in just_episode_regexs:
            episode_match = re.search(rx, file, re.IGNORECASE)
            if episode_match is not None:
              the_episode = int(episode_match.group('ep'))
              the_season = 1
              
              # Now look for a season.
              if seasonNumber is not None:
                the_season = seasonNumber
                
                # See if we accidentally parsed the episode as season.
                if the_episode >= 100 and int(the_episode / 100) == the_season:
                  the_episode = the_episode % 100

              # Prevent standalone eps matching the "XX of YY" regex from stacking.
              if rx == just_episode_regexs[0]:
                shouldStack = False
              
              tv_show = Media.Episode(show, the_season, the_episode, None, year)
              tv_show.parts.append(i)
              mediaList.append(tv_show)
              done = True
              break
          
        if done == False:
          print "Got nothing for:", file
          
  # Stack the results.
  if shouldStack:
    Stack.Scan(path, files, mediaList, subdirs)
  
def find_data(atom, name):
  child = atomsearch.find_path(atom, name)
  data_atom = child.find('data')
  if data_atom and 'data' in data_atom.attrs:
    return data_atom.attrs['data']

import sys
    
if __name__ == '__main__':
  print "Hello, world!"
  path = sys.argv[1]
  files = [os.path.join(path, file) for file in os.listdir(path)]
  media = []
  Scan(path[1:], files, media, [])
  print "Media:", media


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
