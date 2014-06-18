# Copyright (c) 2013 Modified by Cyrille Lefevre to make use of CustomVideoFiles

import Media, CustomVideoFiles
import re, os.path, difflib

#import sys

SeriesScanner = __import__('Custom Plex Series Scanner')
	  
def compareFilenames(elem):
  return elem.parts[0]

def Scan(dir, files, mediaList, subdirs):
  
  # Go through the files and see if any of them need to be stacked.
  stack_dict = {}
  stackDiffs = '123456789abcdefghijklmn' # These are the characters we are looking for being different across stackable filenames
  stackSuffixes = ['cd', 'dvd', 'part', 'pt', 'disk', 'disc', 'scene']
  
  # Sort the mediaList by filename, so we can do our compares properly
  mediaList[:] = sorted(mediaList, key=compareFilenames)
  
  # Search for parts.
  count = 0 
  for mediaItem in mediaList[:-1]:
    m1 = mediaList[count]
    m2 = mediaList[count + 1]
    f1 = os.path.basename(m1.parts[0])
    f2 = os.path.basename(m2.parts[0])
    
    opcodes = difflib.SequenceMatcher(None, f1, f2).get_opcodes()
    if len(opcodes) == 3: # We only have one transform
      (tag, i1, i2, j1, j2) = opcodes[1]
      if tag == 'replace': # The transform is a replace
	if (i2-i1 == 1) and (j2-j1 == 1): # The transform is only one character
	  if 1 in [c in f1[i1:i2].lower() for c in stackDiffs]: # That one character is 1-4 or a-d
	    root = f1[:i1]
	    xOfy = False
	    if f1[i1+1:].lower().strip().startswith('of'): #check to see if this an x of y style stack, if so flag it
	      xOfy = True
	    #prefix = f1[:i1] + f1[i2:]
	    #(root, ext) = os.path.splitext(prefix)
	    
	    # Fix cases where it is something like part 01 ... part 02 -- remove that 0, so the suffix check works later
	    if root[-1:] == '0': 
	      root = root[:-1]
	      
	    # This is a special case for folders with multiple Volumes of a series (not a stacked movie) [e.g, Kill Bill Vol 1 / 2]
	    if not root.lower().strip().endswith('vol') and not root.lower().strip().endswith('volume'): 
	      
	      # Strip any suffixes like CD, DVD.
	      foundSuffix = False
	      for suffix in stackSuffixes:
		if root.lower().strip().endswith(suffix):
		  root = root[0:-len(suffix)].strip()
		  foundSuffix = True
		  break
	      
	      if foundSuffix or xOfy:
		title = root
		for rx in SeriesScanner.episode_regexps:
		  match = re.search(rx, root, re.IGNORECASE)
		  if match and match.groupdict().has_key('title') and match.group('title'):
		    title = match.group('title')
		    break

		# Replace the name, which probably had the suffix.
		(name, year) = CustomVideoFiles.CleanName(title)
		#print >> sys.stderr, ('root', root, 'title', title, 'name', name)
		mediaItem.name = name
		if stack_dict.has_key(root):
		  stack_dict[root].append(m2)
		else:
		  stack_dict[root] = [m1]
		  stack_dict[root].append(m2)
    count += 1
  
  # Now combine stacked parts
  for stack in stack_dict.keys():
    for media in stack_dict[stack][1:]:
      stack_dict[stack][0].parts.append(media.parts[0])
      mediaList.remove(media)
