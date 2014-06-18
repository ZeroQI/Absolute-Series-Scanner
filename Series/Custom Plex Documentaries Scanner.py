#
# Copyright (c) 2010 Plex Development Team. All rights reserved.
# Copyright (c) 2013 Modified by Cyrille Lefevre to allow episode names w/o episode number
#
import re, os, os.path
import Media, VideoFiles, Utils, CustomVideoFiles, CustomStack
from mp4file import mp4file, atomsearch
SeriesScanner = __import__('Custom Plex Series Scanner')

# the last regexp eat years such as 1929 as season 19 episode 29
# so, for instance, get rid of it...
#SeriesScanner.episode_regexps = SeriesScanner.episode_regexps[:-1]

#import sys

#import logging
#logger = logging.getLogger("series")
#fhd = logging.FileHandler("series.log")
#fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
#fhd.setFormatter(fmt)
#logger.addHandler(fhd)
#logger.setLevel(logging.DEBUG)

# Look for episodes.
def Scan(path, files, mediaList, subdirs, language=None, root=None):

  # Scan for video files.
  VideoFiles.Scan(path, files, mediaList, subdirs, root)

  #logger.info("Custom Plex Series Scanner")
  #logger.debug('path: %s' % path)
  #print >> sys.stderr, ('path: %s' % path)
  #print >> sys.stderr, ('subdirs: %s' % subdirs)
  #print >> sys.stderr, ('files: %s' % files)

  # Take top two as show/season, but require at least the top one.
  paths = Utils.SplitPath(path)
  shouldStack = True

  if len(paths) == 1 and len(paths[0]) == 0:

    # Run the select regexps we allow at the top level.
    for i in files:
      file = os.path.basename(i)
      #print >> sys.stderr, ('file0: %s' % file)
      for rx in SeriesScanner.episode_regexps[0:-1]:
	match = re.search(rx, file, re.IGNORECASE)
	if match:

	  # Extract data.
	  show = match.group('show')
	  season = int(match.group('season'))
	  episode = int(match.group('ep'))
	  endEpisode = episode
	  if match.groupdict().has_key('secondEp') and match.group('secondEp'):
	    endEpisode = int(match.group('secondEp'))
	  title = None
	  if match.groupdict().has_key('title') and match.group('title'):
	    title = match.group('title')

	  # Clean title.
	  (name, year) = CustomVideoFiles.CleanName(show)
	  if len(name) > 0:
	    for ep in range(episode, endEpisode+1):
	      #print >> sys.stderr, ('media0:', name, season, ep, title, year)
	      tv_show = Media.Episode(name, season, ep, title, year)
	      tv_show.display_offset = (ep-episode)*100/(endEpisode-episode+1)
	      tv_show.parts.append(i)
	      mediaList.append(tv_show)

  elif len(paths) > 0 and len(paths[0]) > 0:
    done = False

    # See if parent directory is a perfect match (e.g. a directory like "24 - 8x02 - Day 8_ 5_00P.M. - 6_00P.M")
    if len(files) == 1:
      for rx in SeriesScanner.standalone_episode_regexs:
	res = re.findall(rx, paths[-1])
	if len(res):
	  (show, junk, year, season, episode, junk, endEpisode, junk, title) = res[0]

	  # If it didn't have a show, then grab it from the directory.
	  if len(show) == 0:
	    (show, year) = CustomVideoFiles.CleanName(paths[0])

	  episode = int(episode)
	  if len(endEpisode) > 0:
	    endEpisode = int(endEpisode)
	  else:
	    endEpisode = episode

	  for ep in range(episode, endEpisode+1):
	    #print >> sys.stderr, ('media1:', show, season, ep, title, year)
	    tv_show = Media.Episode(show, season, ep, title, year)
	    tv_show.display_offset = (ep-episode)*100/(endEpisode-episode+1)
	    tv_show.parts.append(files[0])
	    mediaList.append(tv_show)

	  done = True
	  break

    #print >> sys.stderr, ('done1: %s' % done)
    if done == False:

      # Not a perfect standalone match, so get information from directories. (e.g. "Lost/Season 1/s0101.mkv")
      season = None
      seasonNumber = None

      (show, year) = CustomVideoFiles.CleanName(paths[0])

      # Which component looks like season?
      if len(paths) >= 2:
	season = paths[len(paths)-1]
	match = re.match(SeriesScanner.season_regex, season, re.IGNORECASE)
	if match:
	  seasonNumber = int(match.group('season'))

      # Make sure an episode name didn't make it into the show.
      for rx in SeriesScanner.ends_with_episode:
	show = re.sub(rx, '', show)

      epcount = 0
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
		for rx in SeriesScanner.episode_regexps[:-1]:
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
	      #print >> sys.stderr, ('media2:', show, season, ep, title, year)
	      tv_show = Media.Episode(m4show, m4season, m4ep, title, m4year)
	      tv_show.parts.append(i)
	      mediaList.append(tv_show)
	      continue

	  except:
	    pass

	# Check for date-based regexps first.
	for rx in SeriesScanner.date_regexps:
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
	    #print >> sys.stderr, ('media3:', show, year, None, None, None)
	    tv_show = Media.Episode(show, year, None, None, None)
	    tv_show.released_at = '%d-%02d-%02d' % (year, month, day)
	    tv_show.parts.append(i)
	    mediaList.append(tv_show)

	    done = True
	    break

	#print >> sys.stderr, ('done3: %s' % done)
	if done == False:

	  # Take the year out, because it's not going to help at this point.
	  (cleanName, cleanYear) = CustomVideoFiles.CleanName(file)
	  if cleanYear != None:
	    file = file.replace(str(cleanYear), 'XXXX')

	  # already done by VideoFiles.CleanName()
	  # Minor cleaning on the file to avoid false matches on H.264, 720p, etc.
	  # whackRx = ['([hHx][\.]?264)[^0-9]', '[^[0-9](720[pP])', '[^[0-9](1080[pP])', '[^[0-9](480[pP])']
	  # for rx in whackRx:
	  #   file = re.sub(rx, ' ', file)

	  for rx in SeriesScanner.episode_regexps[:-1]:

	    match = re.search(rx, file, re.IGNORECASE)
	    if match:
	      # Parse season and episode.
	      the_season = int(match.group('season'))
	      episode = int(match.group('ep'))
	      endEpisode = episode
	      if match.groupdict().has_key('secondEp') and match.group('secondEp'):
		endEpisode = int(match.group('secondEp'))
	      title = None
	      if match.groupdict().has_key('title') and match.group('title'):
		title = match.group('title')

	      for ep in range(episode, endEpisode+1):
		#print >> sys.stderr, ('media4:', show, the_season, ep, title, year)
		tv_show = Media.Episode(show, the_season, ep, title, year)
		tv_show.display_offset = (ep-episode)*100/(endEpisode-episode+1)
		tv_show.parts.append(i)
		mediaList.append(tv_show)

	      done = True
	      break

	#print >> sys.stderr, ('done4: %s' % done)
	if done == False:
	  if len(paths) > 0 and len(paths[0]) > 0:
	    (title, junk) = CustomVideoFiles.CleanName(file,True)
	    epcount = epcount + 1
	    #print >> sys.stderr, ('media5: ',	show, 0, epcount, title, None)
	    tv_show = Media.Episode(show, 0, epcount, title, None)
	    tv_show.parts.append(i)
	    mediaList.append(tv_show)
	    done = True

	#print >> sys.stderr, ('done5: %s' % done)
	if done == False:
	    print "Got nothing for:", file

  # Stack the results.
  if shouldStack:
    CustomStack.Scan(path, files, mediaList, subdirs)

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
