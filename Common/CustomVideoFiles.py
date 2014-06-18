#!/usr/bin/python2.4
# Copyright (c) 2013 Modified by Cyrille Lefevre to remove french tags

import Filter
import os.path, re, datetime, titlecase, unicodedata, sys

video_exts = ['3g2', '3gp', 'asf', 'asx', 'avc', 'avi', 'avs', 'bin', 'bivx', 'bup', 'divx', 'dv', 'dvr-ms', 'evo', 'fli', 'flv', 'ifo', 'img', 
	      'iso', 'm2t', 'm2ts', 'm2v', 'm4v', 'mkv', 'mov', 'mp4', 'mpeg', 'mpg', 'mts', 'nrg', 'nsv', 'nuv', 'ogm', 'ogv',	 'tp',
	      'pva', 'qt', 'rm', 'rmvb', 'sdp', 'svq3', 'strm', 'ts', 'ty', 'vdr', 'viv', 'vob', 'vp3', 'wmv', 'wpl', 'wtv', 'xsp', 'xvid', 'webm']

ignore_suffixes = ['.dvdmedia']

source_dict = {'bluray':['bdrc','bdrip','bluray','bd','brrip','hdrip','hddvd','hddvdrip'],'cam':['cam'],'dvd':['ddc','dvdrip','dvd','r1','r3','r5'],'retail':['retail'],
	       'dtv':['dsr','dsrip','hdtv','pdtv','ppv'],'stv':['stv','tvrip','tv'],'screener':['bdscr','dvdscr','dvdscreener','scr','screener'],
	       'svcd':['svcd'],'vcd':['vcd'],'telecine':['tc','telecine'],'telesync':['ts','telesync'],'web':['webrip','web-dl'],'workprint':['wp','workprint'],'vhs':['vhs','vhsrip']}
source = []
for d in source_dict:
  for s in source_dict[d]:
    if source != '':
      source.append(s)

audio = ['([^0-9])5\.1[ ]*ch(.)','([^0-9])5\.1([^0-9]?)','([^0-9])7\.1[ ]*ch(.)','([^0-9])7\.1([^0-9])']
subs = ['multi','multisubs']
misc = ['cd1','cd2','1cd','2cd','custom','internal','repack','read.nfo','readnfo','nfofix','proper','rerip','dubbed','subbed','extended','unrated','xxx','nfo','dvxa','lte','rip','fansub']
french = ['french','truefrench','subfrench','frenchedit','fr','vf','vvf','vo','vostfr','vost']
format = ['ac3','dc','divx','fragment','limited','ogg','ogm','ntsc','pal','ps3avchd','r1','r3','r5','720i','720p','1080i','1080p','x264','xvid','vorbis','aac','dts','fs','ws','1920x1080','1280x720','h264']
edition = ['dc','se'] # dc = directors cut, se = special edition
yearRx = '([\(\[\.\-_])([1-2][0-9]{3})([\.\-\)\]_,+])'

# Cleanup folder / filenames
def CleanName(name, noYear=False):
  
  orig = name

  # Make sure we pre-compose.
  try:
    # maybe ANSI_X3.4-1968 instead of UTF-8 !
    uname = name.decode(sys.getfilesystemencoding())
  except UnicodeDecodeError:
    uname = name.decode('UTF-8')
  name = unicodedata.normalize('NFKC', uname)
  name = name.lower()

  # grab the year, if there is one. set ourselves up to ignore everything after the year later on.
  year = None
  if noYear == False:
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
  garbage.extend(french)
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
  try:
    # maybe ANSI_X3.4-1968 instead of UTF-8 !
    cleanedName = cleanedName.encode(sys.getfilesystemencoding())
  except UnicodeEncodeError:
    cleanedName = cleanedName.encode('UTF-8')
  return (titlecase.titlecase(cleanedName), year)
