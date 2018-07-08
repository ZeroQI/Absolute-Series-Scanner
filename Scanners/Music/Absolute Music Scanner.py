import os, sys, Media
import logging                   # Python       - logging.basicConfig
from mutagen import File as MFile
Virtual = True

### setup logging https://docs.python.org/2/library/logging.html ###  #logging.debug/info/warning/error/critical('some critical message: %s', 'highest category')
try:      platform = sys.platform.lower()  # sys.platform: win32 | darwin | linux2, 
except:   platform="other"
#  try:    platform = Platform.OS.lower()   # Platform.OS:  Windows, MacOSX, or Linux
#  except: p5latform = ""
if   (platform == 'win32'  or platform == 'windows'): LOG_PATH = os.path.expandvars( '%LOCALAPPDATA%\\Plex Media Server\Logs' )
elif (platform == 'darwin' or platform == 'macosx'):  LOG_PATH = os.path.expandvars( '$HOME/Library/Application Support/Plex Media Server\Logs' )
elif 'linux' in platform:                             LOG_PATH = os.path.expandvars( '$PLEX_HOME/Library/Application Support/Plex Media Server\Logs' )                          
if not os.path.isdir(LOG_PATH):                       LOG_PATH = os.path.expanduser('~')
logging.basicConfig(filename=os.path.join(LOG_PATH, LOG_FILE), format=LOG_FORMAT, level=logging.DEBUG)  

### Log function ########################################################################################
def Log(entry, filename='Plex Media Scanner Custom.log'): #need relative path
  logging.info(entry + "\r\n") # allow to use windows notepad with correct line feeds
  print entry                  # when ran from console

### Add files into Plex database ########################################################################
def explore_path(subdir, file_tree):
  files=[]
  for item in os.listdir(subdir): 
    fullpath = os.path.join(subdir, item)
    if os.path.isdir (fullpath): 
      for rx in ignore_dirs_re_findall: ### Skip unwanted folders ###
        result = re.findall(rx, item)   
        if len(result):  break
