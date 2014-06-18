#
# Copyright (c) 2010 Plex Development Team. All rights reserved.
# Copyright (c) 2013 Modified by Cyrille Lefevre to allow episode names w/o episode number
#
import re, os, os.path
import Media, VideoFiles, Utils, CustomVideoFiles, CustomStack
from mp4file import mp4file, atomsearch

#import sys
#import logging
#logger = logging.getLogger("series")
#fhd = logging.FileHandler("series.log")
#fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
#fhd.setFormatter(fmt)
#logger.addHandler(fhd)
#logger.setLevel(logging.DEBUG)

episode_regexps = [
    # S03E03, S03.03, S03_03, S03 03, S03E03 E04, S03E03 S03E04, S03E03 +04, S03E03-E04, S03E03-S03E04, S03E03-+04,
    # S03E03 title, S03E03. title, ..., show S03E03, ..., show S03E03 title, ...
    '(?P<show>.*?)[sS](?P<season>[0-9]+)[\._ ]*[eE](?P<ep>[0-9]+)([- ]?([sS][0-9]+)?[Ee+](?P<secondEp>[0-9]+))?(\.? +(?P<title>.+)$)?',
    # S03-03, S03-03 title, S03-03. title, show S03-03, show S03-03 title, ...
    '(?P<show>.*?)[sS](?P<season>[0-9]{2,4})[\._\- ]+(?P<ep>[0-9]+)(\.? +(?P<title>.+)$)?',
    # 3x03, 3x03-04, 3x03-3x04, 03x03, 03x03-04, 03x03-3x04,
    # 3x03 title, 3x03. title, ..., show 3x03, ..., show 3x03 title, ...
    '(?P<show>.*?)([^0-9]|^)(?P<season>[0-9]{1,4})[Xx](?P<ep>[0-9]+)(-([0-9]+[Xx])?(?P<secondEp>[0-9]+))?(\.? +(?P<title>.+)$)?',
    '(.*?)[^0-9a-z](?P<season>[0-9]{1,2})(?P<ep>[0-9]{2})([\.\-][0-9]+(?P<secondEp>[0-9]{2})([ \-_\.]|$)[\.\-]?)?([^0-9a-z%]|$)' # .602.
  ]

date_regexps = [
    '(?P<year>[0-9]{4})[^0-9a-zA-Z]+(?P<month>[0-9]{2})[^0-9a-zA-Z]+(?P<day>[0-9]{2})([^0-9]|$)',		 # 2009-02-10
    '(?P<month>[0-9]{2})[^0-9a-zA-Z]+(?P<day>[0-9]{2})[^0-9a-zA-Z(]+(?P<year>[0-9]{4})([^0-9a-zA-Z]|$)', # 02-10-2009
  ]

standalone_episode_regexs = [
  '(.*?)( \(([0-9]+)\))? - ([0-9]+)+x([0-9]+)(-[0-9]+[Xx]([0-9]+))?( - (.*))?',	 # Newzbin style, no _UNPACK_
  '(.*?)( \(([0-9]+)\))?[Ss]([0-9]+)+[Ee]([0-9]+)(-[0-9]+[Xx]([0-9]+))?( - (.*))?'   # standard s00e00
  ]

season_regex = '.*?(?P<season>[0-9]+)$' # folder for a season

just_episode_regexs = [
    '(?P<ep>[0-9]{1,3})[\. -_]*of[\. -_]*[0-9]{1,3}',	    # 01 of 08
    '^(?P<ep>[0-9]{1,3})[^0-9]',			   # 01 - Foo
    'e[a-z]*[ \.\-_]*(?P<ep>[0-9]{2,3})([^0-9c-uw-z%]|$)', # Blah Blah ep234
    '.*?[ \.\-_](?P<ep>[0-9]{2,3})[^0-9c-uw-z%]+',	   # Flah - 04 - Blah
    '.*?[ \.\-_](?P<ep>[0-9]{2,3})$',			   # Flah - 04
    '.*?[^0-9x](?P<ep>[0-9]{2,3})$'			   # Flah707
  ]

ends_with_number = '.*([0-9]{1,2})$'

ends_with_episode = ['[ ]*[0-9]{1,2}x[0-9]{1,3}$', '[ ]*S[0-9]+E[0-9]+$']

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
      for rx in standalone_episode_regexs:
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
	      #print >> sys.stderr, ('media2:', show, season, ep, title, year)
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

	  for rx in episode_regexps:

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
		    if re.search('^[0-9]+[- ]', file):
		      # Let the episode matcher have it.
		      break

		    # Treat the whole thing as an episode.
		    episode = episode + the_season*100
		    if endEpisode is not None:
		      endEpisode = endEpisode + the_season*100

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

	  # OK, next let's see if we're dealing with something that looks like an episode.
	  # Begin by cleaning the filename to remove garbage like "h.264" that could throw
	  # things off.
	  #
	  (file, fileYear) = CustomVideoFiles.CleanName(file)

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

	      #print >> sys.stderr, ('media5:', show, the_season, the_episode, None, year)
	      tv_show = Media.Episode(show, the_season, the_episode, None, year)
	      tv_show.parts.append(i)
	      mediaList.append(tv_show)
	      done = True
	      break

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
