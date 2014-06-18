#
# Copyright (c) 2010 Plex Development Team. All rights reserved.
#
import re, os, os.path
import Media, VideoFiles, Stack
from mp4file import mp4file, atomsearch

episode_regexps = [
    '(.*?)[sS](?P<season>[0-9]+)[\._ ]*[eE](?P<ep>[0-9]+)([- ]?[Ee+](?P<secondEp>[0-9]+))?',                           # S03E04-E05
    '(.*?)[sS](?P<season>[0-9]+)[\._\- ]*(?P<ep>[0-9]+)',                                                              # S03-03
    '(.*?)([^0-9]|^)(?P<season>[0-9]{1,2})[Xx](?P<ep>[0-9]+)(-[0-9]+[Xx](?P<secondEp>[0-9]+))?',                       # 3x03
    '(.*?)[^0-9a-z](?P<season>[0-9]{1,2})(?P<ep>[0-9]{2})([\.\-][0-9]+(?P<secondEp>[0-9]{2})([ \-_\.]|$)[\.\-]?)?([^0-9a-z]|$)' # .602.
  ]

date_regexps = [
    '(?P<year>[0-9]{4})[^0-9a-zA-Z]+(?P<month>[0-9]{2})[^0-9a-zA-Z]+(?P<day>[0-9]{2})([^0-9]|$)',                # 2009-02-10
    '(?P<month>[0-9]){2}[^0-9a-zA-Z]+(?P<day>[0-9]{2})[^0-9a-zA-Z(]+(?P<year>[0-9]{4})[^0-9a-zA-Z)]+([^0-9]|$)', # 02-10-2009
  ]

standalone_episode_regexs = [
  '(.*?)( \(([0-9]+)\))? - ([0-9]+)+x([0-9]+)(-[0-9]+[Xx]([0-9]+))?( - (.*))?',  # Newzbin style, no _UNPACK_
  '(.*?)( \(([0-9]+)\))?[Ss]([0-9]+)+[Ee]([0-9]+)(-[0-9]+[Xx]([0-9]+))?( - (.*))?'   # standard s00e00
  ]
  
season_regex = '(.*)[ \.\-_]([0-9]{4})?([Ss](eason)?)([0-9]+)(.*)' # folder for a season

just_episode_regexs = [
    '^(?P<ep>[0-9]{2,3})[^0-9]',                           # 01 - Foo
    'e[a-z]*[ \.\-_]*(?P<ep>[0-9]{2,3})([^0-9c-uw-z%]|$)', # Blah Blah ep234
    '.*?[ \.\-_](?P<ep>[0-9]{2,3})[^0-9c-uw-z%]+',         # Flah - 04 - Blah
    '.*?[ \.\-_](?P<ep>[0-9]{2,3})$'                       # Flah - 04
  ]

ends_with_number = '.*([0-9]{1,2})$'

ends_with_episode = ['[ ]*[0-9]{1,2}x[0-9]{1,3}$', '[ ]*S[0-9]+E[0-9]+$']

# Look for episodes.
def Scan(path, files, mediaList, subdirs):
  
  # Scan for video files.
  VideoFiles.Scan(path, files, mediaList, subdirs)
  
  # Take top two as show/season, but require at least the top one.
  paths = path.split('/')

  
  fparts=[]
  format=''
  seasonep=''
  showname=''
  itemnum=0
  season=0
  filename=''
  
  if len(files) > 0:
    print (files)
    for file in files:
        fparts=[]
        format=''
        seasonep=''
        showname=''
        itemnum=0
        season=0
        filename=''

        print (file)
        filename=file.split('/')[-1]
        fparts = file.split('.')
        format=fparts[-1]
        seasonep=fparts[-2]
        count=0
        showname=''
        try:
            filename="_" + filename
            (showname, season, episode)=re.findall('_(.+?)\.[Ss]([0-9]+)\.[Ee]([0-9]+)',filename)[0]
        except:
            pass
        if showname == '':
            try:
              (showname, season, episode)=re.findall('_(.+?)\.[Ss]([0-9]+)[Ee]([0-9]+)',filename)[0]
            except:
              continue
        filename=file.replace("_","")
        showname=showname.replace("_",":")
        print (showname)
        print (season)
        print (episode)
        tv_show = Media.Episode(showname, season, episode)
        print ('huh')
        tv_show.parts.append(file)
        print ("goodbye")
        mediaList.append(tv_show)
        


  
  
  
  
  
  if len(paths) > 0 and len(paths[0]) > 0:
    done = False
        
    # See if parent directory is a perfect match (e.g. a directory like "24 - 8x02 - Day 8_ 5_00P.M. - 6_00P.M")
    if len(files) == 1:
      for rx in standalone_episode_regexs:
        res = re.findall(rx, paths[-1])
        if len(res):
          show, junk, year, season, episode, junk, endEpisode, junk, title = res[0]
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
      
      if len(paths) == 1:
        #let's check to see if this is a season dir
        res = re.findall(season_regex,paths[0])
        if len(res):
          show, year, junk, junk, season, junk = res[0]
        else:
          show = paths[0]
      else:
        show, season = paths[0], paths[1]
        m = re.match('s.*?([0-9]+)$', season, re.IGNORECASE)
        if m:
          seasonNumber = int(m.group(1))

      oldShow = show
      (show, year) = VideoFiles.CleanName(show)

      # Make sure an episode name didn't make it into the show.
      for rx in ends_with_episode:
        show = re.sub(rx, '', show)

      for i in files:
        done = False
        file = os.path.basename(i)
        (file, ext) = os.path.splitext(file)
        
        if ext == '.m4v':
          m4season = m4ep = m4year = 0
          m4show = title = ''
          mp4fileTags = mp4file.Mp4File(i)
          try: m4show = find_data(mp4fileTags, 'moov/udta/meta/ilst/tvshow')
          except: pass
          try: m4season = int(find_data(mp4fileTags, 'moov/udta/meta/ilst/tvseason'))
          except: pass
          try: m4ep = int(find_data(mp4fileTags, 'moov/udta/meta/ilst/tvepisode'))
          except: pass
          try: title = find_data(mp4fileTags, 'moov/udta/meta/ilst/title')
          except: pass
          try: m4year = int(find_data(mp4fileTags, 'moov/udta/meta/ilst/year')[:4])
          except: pass
          #print find_data(mp4fileTags, 'moov/udta/meta/ilst/description')
          #print 'show=%s, season=%s, ep=%s, title=%s, year=%s' % (show, season, ep, title, year)
          if len(m4show) > 0 and m4season > 0 and m4ep > 0:
            tv_show = Media.Episode(str(m4show), m4season, m4ep, str(title), m4year)
            tv_show.parts.append(i)
            mediaList.append(tv_show)
            continue
        
        # Check for date-based regexps first.
        for rx in date_regexps:
          match = re.search(rx, file)
          if match:
            year = int(match.group('year'))
            month = int(match.group('month'))
            day = int(match.group('day'))

            # Use the year if there is no season.
            theSeason = season
            if theSeason is None:
              theSeason = year

            tv_show = Media.Episode(show, theSeason, None, None, None)
            tv_show.released_at = '%d-%02d-%02d' % (year, month, day)
            tv_show.parts.append(i)
            mediaList.append(tv_show)

            done = True
            break
        
        if done == False:
          for rx in episode_regexps:
            
            # We're only going to run the weak one (.603.) if we have a season folder.
            if rx == episode_regexps[-1] and len(paths) == 1:
              continue

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
                
                # Make sure this isn't absolute order.
                if seasonNumber is not None:
                  if seasonNumber != the_season:
                    # Treat the whole thing as an episode.
                    episode = episode + the_season*100
                    if endEpisode is not None:
                      endEpisode = endEpisode + the_season*100
                    the_season = int(m.group(1))

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
          (file, year) = VideoFiles.CleanName(file)
          
          for rx in just_episode_regexs:
            episode_match = re.search(rx, file, re.IGNORECASE)
            if episode_match is not None:
              the_episode = int(episode_match.group('ep'))
              the_season = 1
          
              # Now look for a season.
              if seasonNumber:
                the_season = seasonNumber
                
                # See if we accidentally parsed the episode as season.
                if the_episode >= 100 and int(the_episode / 100) == the_season:
                  the_episode = the_episode % 100
              
              tv_show = Media.Episode(show, the_season, the_episode, None, None)
              tv_show.parts.append(i)
              mediaList.append(tv_show)
              done = True
              break
          
        if done == False:
          print "Got nothing for:", file
          
  # Stack the results.
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
