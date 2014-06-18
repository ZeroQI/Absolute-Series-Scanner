__licence__ = """Copyright (c) 2010, Matthew Wilkes
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the the contributors' employers nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL MATTHEW WILKES BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import commands
import os.path
import re

# Other pipelines from Plex
import Media, VideoFiles, Stack

REGEXES = (
    """(?#Consume the path)
       (.*)/
       
       (?#The start of the filename to the episode is the series name)
       (?P<title>.+?)
       (
           (?# Match the series in S01E01 format)
           S(?P<series>[0-9]+)
           E(?P<episode>[0-9]+)
       )
   """,
   """(?#Consume the path)
       (.*)/
       
       (?#The start of the filename to the episode is the series name)
       (?P<title>.+?)
       (
           (?# Match the series in 01x01 format)
           (\(|\[)?
           (?P<series>[0-9]+)x
           (?P<episode>[0-9]+)
           (\)|\])?
       )
   """,
   """(?#Consume the path)
       (.*)/
       
       (?#The start of the filename to the episode is the series name)
       (?P<title>[a-z0-9\.\-\_]+?)
       (
           (?# Match the series in 2010-01-01 format)
           (?P<series>[0-9]{4})(.)
           (?P<month>[0-9]+).(?P<day>[0-9]+)
       )
   """,
   """(?#Consume the path)
       (.*)/
       
       (
           (?# Match the series in 2010-01-01 format)
           (?P<series>[0-9]{4})(.)
           (?P<month>[0-9]+).(?P<day>[0-9]+)
       )
       
       (?#The series name sometimes comes afterwards)
       (?P<title>[a-z0-9\.\-\_\ ]+?)
       ((\.)[a-z]+)+
        (?P<ext>(\.[a-z0-9]{3,4}$))
   """)

POSSIBLE_SEPS = ".-_ "

default_flags = re.X | re.I
def compile_re(exp):
    return re.compile(exp, flags=default_flags)

REGEXES = map(compile_re, REGEXES)

known_good = set()


def OnlyVideos(func):
    def Scan(path, files, mediaList, subdirs):
        VideoFiles.Scan(path, files, mediaList, subdirs)
        return func(path, files, mediaList, subdirs)
    return Scan

def SystemFiltering(func):
    def Scan(path, files, mediaList, subdirs):
        SystemFilter(path, files, mediaList, subdirs)
        return func(path, files, mediaList, subdirs)
    return Scan

def SystemFilter(path, files, mediaList, subdirs):
    if not subdirs:
        return

    if not files:
        base  = subdirs[0]
    else:
        base = files[0]

    extensions = "|".join(ext+"$" for ext in VideoFiles.video_exts)
    command = """find \"%s\" | egrep \"%s\"""" % (os.path.split(base)[0], extensions)
    existing_files = commands.getoutput(command)
    
    good_dirs = set(os.path.split(a)[0] for a in existing_files.split("\n"))
    parent_dirs = set()
    for good_dir in good_dirs:
        parents = good_dir.split(os.path.sep)
        for i in range(len(parents)):
            parent_dirs.add(os.path.sep.join(parents[:i]))
    
    good_dirs = good_dirs.union(parent_dirs)
    
    for subdir in subdirs:
        if subdir not in good_dirs:
            subdirs.remove(subdir)
    

@SystemFiltering
@OnlyVideos
def Scan(path, files, mediaList, subdirs):
    """Given a list of files add appropriate Media to the VideoFiles."""
    if not files:
        # We are called repeatedly with subdirs, we want ones without
        # video files to pass quickly.
        return
    
    for path in files:
        metadata = classify(path)
        if metadata is None:
            # We couldn't classify this file
            print path
            continue

        title = metadata.get('title', None)
        season = metadata.get('series', None)
        episode = metadata.get('episode', None)
        episode_title = metadata.get('episode_title', None)
        year = metadata.get('year', None)
        airdate = metadata.get('airdate', None)
                
        episode = Media.Episode(title, season, episode, episode_title, year)
        episode.released_at = airdate
        episode.parts.append(path)
        mediaList.append(episode)

def classify(path):
    for REGEX in REGEXES:
        found = REGEX.search(path)
        if not found:
            continue
        metadata = found.groupdict()
        
        metadata['title'] = tidyTitleWithPathHints(metadata['title'], path)
        
        if 'day' in metadata:
            year = int(metadata['series'])
            month = int(metadata['month'])
            day = int(metadata['day'])
            
            metadata['airdate'] = "%4d-%02d-%02d" % (year, month, day)
            del metadata['month']
            del metadata['day']
        
        if not all(map(str.isalnum, metadata['title'].split())) or \
            not (metadata.get('episode', None) or metadata.get('airdate', None)) or \
            not (metadata['series']):
           if metadata['title'] not in known_good:
               print "Warning - bad info for %s" % path
        
        return metadata
        
def tidyTitle(title):
    freqs = {}
    for sep in POSSIBLE_SEPS:
        freqs[sep] = title.count(sep)
    sep = max(freqs.items(), key=lambda x:x[1])[0]
    title = title.split(sep)
    for seg in title:
        for sep in POSSIBLE_SEPS:
            seg.strip(sep)
    title = " ".join(title)
    return title.title()

def tidyTitleWithPathHints(title, path):
    title = tidyTitle(title)
    path = path.split(os.path.sep)
    parentTitle = tidyTitle(path[-2])
    if parentTitle in title:
        return parentTitle
    else:
        return title
