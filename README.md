#Absolute Series Scanner

The Plex Scanner will make the video files showing in Plex, if not showing in Plex, it is a scanner issue.
A Plex series scanner choose the following from the folders and file names:
- Serie name
- Season number
- Episode number
- Episode title (not filled by plex default series scanner, until the metadata agent refreshes it)
- Episode year

The Plex metadata agent will find metadata (Serie Title, summary year, episode title, summary, posters, fanart, tags, ... ) for files showing in Plex. Anything missing there while the file shows up in Plex is an Agent issue, refer to the Agent readme here: https://github.com/ZeroQI/Hama.bundle/blob/master/README.md

###Which Metadata/Title source to select?
- Anime:     AniDB.net, Hama use an offline title database from them ("main title" is the best, or romaji "x-jat". "En" titles have hoorrors like "bombshells from the sky" for "Asobi ni Iku yo!" serie). AniDB use small posters, no background. Hama use ScudLee's xml mapping files to crosss reference the anidb id to the tvdb series
- TV Series: TheTVDB.com or TVrage or TheMovieDB (yep support series now), no db site will store (DVD) boxset specific files (nor sport or porn for tvdb). TVDB has high resolution posters, background images, screenshots, and episodes summaries, all lacking from AniBD.net, but they do not carry porn series so no metadata for this type. TheTVDB uses seasons which can be practical for long anime.
- Movies:    TheMovieDB.org, naming convention: "Movie Title (Year).ext" </LI>

###File Naming Conventions
This scanner supports absolute and season numbering, but here are two references for guidelines
- Naming convention for Plex: https://support.plex.tv/hc/en-us/sections/200059498-Naming-and-Organizing-TV-Shows
- Naming convention for XBMC:  http://wiki.xbmc.org/index.php?title=Naming_video_files/TV_shows

Naming
- Specials chars handling ("CØDE：BREAKER") and files starting with dots (".Hack")

Grouping folder
- If you use "Grouping folder / Show Name / Season 1 / Show Name e01.ext" convention from the root, it will now be skipped.
  You can just add it as additionnal root folder in the library: "D:/Anime/Dragon Ball/" for "D:/Anime/Dragon Ball/[2] Dragon Ball Z" folder for example...

Movie files in Series libraries (since this is a Series Scanner) are supported if:
-  Files are in a folder with the same name or with a single file inside it
-  Files are numbered (01|ep 01|s01e01)
-  Filename contain " - Complete Movie"

Season folders
- Seasons folders can have serie name afterwards ("Zero no tsukaima / Season 1 Zero no tsukaima")
- Files in "Extras" folders will be ignored.
- Allow grouping in Ark xxxxx folders transparently with seasons folders inside, or within a season folder
- Specials go in "Specials" or "Season 0" folders.
  - Single seasons series will follow anidb specials numbering (unless specific tvdb guid forced).
  - Multiple seasons series will follow tvdb specials numbering
  - You can use Anidb numbering for specials (OP1a, NCOP, etc...) or explicitely label them as follow (s00e101, etc...).
  - Include all files not recognised as Season 0 episode 501+

Files
<TABLE>
<THEAD>
<TR> <TH> File naming convention </TH> <TH> Template / Folder </TH> <TH>Exemple </TH> </TR>
</THEAD>
<TBODY>
<TR> <TD> Splitting folders:     </TD> <TD> 0-9                 </TD> <TD> 0-9, A,...,Z folder. Add EACH as folder. Do not use the parent folder </TD> </TR>
<TR> <TD> Episode Name Pattern:  </TD> <TD> Season %S/%SN s%0Se%0E </TD> <TD> Season 2/Show Name s02e03.ext </TD> </TR>
<TR> <TD> Multi-Episode style:   </TD> <TD> Extend              </TD> <TD> Season 2/Show Name s02e03-05.ext </TD> </TR>
<TR> <TD> Multi-part episodes:   </TD> <TD> cdX, discX, diskX, dvdX, partX, ptX </TD> <TD> Season 2/Show Name s02e03 - pt1.ext </TD> </TR>
<TR> <TD> Multi-Media Version:   </TD> <TD> Movie Name (year) - 1080p.ext </TD> <TD> Movie Name (year) - 1080p.ext </TD> </TR>
<TR> <TD> Specials scrapped:     </TD> <TD> Specials, Season 0  </TD> <TD> s00e01/OP1/Ed3a/NCOP/S01/S1.ext </TD> </TR>
<TR> <TD> Other non scrapped:    </TD> <TD> Extras              </TD> <TD> Extras/Show Name xxxx.ext </TD> </TR>
<TR> <TD> BD rips                </TD> <TD> /path/to/series-library/Series Name Season 2 </TD> <TD>Series.Name.Disc1.S02.E01-E12/BDMV/STREAM </TD> </TR>
</TBODY>
</TABLE>

Local metadata
It is supported but through "local media assets" agent, add it and and put it before HAMA in the priority order.<BR />
https://support.plex.tv/hc/en-us/articles/200220717-Local-Media-Assets-TV-Shows

<TABLE>
<THEAD>
<TR> <TH> Data type </TH> <TH> Source                </TH> <TH>           Comment </TH> </TR>
</THEAD>
<TBODY>
<TR> <TD> fanart  </TD> <TD> art/backdrop/background/fanart-1.ext</TD> <TD> -1 can be ommited (same level as Video TS) </TD> </TR>
<TR> <TD> Serie poster </TD> <TD> Serie folder: Show name-1/folder/poster/show.ext</TD> <TD> (jpg, jpeg, png, tbn) </TD> <TR>
<TR> <TD> Season poster</TD> <TD> Season folder: Season01a.ext </TD> <TD> (jpg, jpeg, png, tbn) </TD> <TR>          
<TR> <TD> Banner    </TD> <TD> banner/banner-1.jpg  </TD> <TD> </TD> </TR>
<TR> <TD> Theme song</TD> <TD> theme.mp3  </TD> <TD> </TD> <TR>
<TR> <TD> Subtitles </TD> <TD> file name.ext (srt, smi, ssa, ass)  </TD> <TD> </TD><TR>
<TR> <TD> Plexignore files  </TD> <TD> .plexignore  </TD> <TD> </TD> <TR>
</TBODY>
</TABLE>

Specials
Hama is a anidb (single season) & tvdb (multiple seasons) agent so either naming convention is fine.
It will detect either successfully but you can convert one convention to the other whicle displaying by forcing ids (further down)

Let's use One piece special "Heart of Gold":

TVDB seasons
- http://thetvdb.com/?tab=episode&seriesid=81797&seasonid=31892&id=5687281&lid=7
- "One piece/One Piece s00e35 Heart of Gold [sub fr].ext"

Anidb (single) season
- http://anidb.net/perl-bin/animedb.pl?show=anime&aid=69
- "One piece/One Piece s00e23 Heart of Gold [sub fr].ext"
- "One piece/One Piece S23 Heart of Gold [sub fr].ext"

Anidb type special numbering is detailed below:
<TABLE> 
<THEAD> <TR> <TH> Type     </TH> <TH> Internal letter </TH> <TH>  Episode number   </TH> </TR> </THEAD>
<TBODY> <TR> <TD> OPs      </TD> <TD> C               </TD> <TD>  Episodes 101-150 </TD> </TR>
        <TR> <TD> EDs      </TD> <TD> C               </TD> <TD>  Episodes 151-200 </TD> </TR>
        <TR> <TD> Trailers </TD> <TD> T               </TD> <TD>  Episodes 201-300 </TD> </TR>
        <TR> <TD> OPs/EDs  </TD> <TD> P               </TD> <TD>  Episodes 301-400 </TD> </TR>
        <TR> <TD> Others   </TD> <TD> O               </TD> <TD>  Episodes 401-500 </TD> </TR>
        <TR> <TD> unmapped </TD> <TD>                 </TD> <TD>  Episodes 501-600 </TD> </TR> </TBODY>
</TABLE>

###Forcing the series ID
You can specify the guid to use the following way:
- In custom search serie name by adding " [guid_type-id_number]" at the end
- In Serie folder name by adding " [guid_type-id_number]" at the end
- In guid_type.id inside serie folder with the id in it (ex: tvdb.id file with tvdbid "114801" without double quotes in it)

Hama supports the following guid_type:
- anidb for AniDB.net (and and the behaviour changing mode anibd2)
- tvdb  for TheTVDB.com (and the behaviour changing modes: tvdb2, tvdb3, tvdb4)
- tmdb  For TheMovieDB.net (and the serie part of TheMovieDB: tsdb)
- imdb  For the International Movie DataBase (ids starts with "tt...")

You can have **absolutely numbered series** (i.e. without season number apart from Specials/season 0) being **displayed in Plex with seasons** without the need to rename the files with season numbering or creating season folders and moving absolutely numbered episodes inside by using the following custom modes, and episodes will be displayed as:

<TABLE>
<THEAD> <TR> <TH> guid_type </TH> <TH> Seasons numbering   </TH> <TH>Episodes numbering</TH> <TH>Use case (example)</TH></TR></THEAD>
<TBODY>
        <TR> <TD> anib2     </TD> <TD> None                </TD> <TD>Absolute           </TD> <TD>Map to the tvdb at the right season and ep number to show 1 serie only</TD> </TR>
        <TR> <TD> tvdb2     </TD> <TD> TVDB                </TD> <TD>Season            </TD> <TD>Multiple single season series (Sword Art online)</TD> </TR>
        <TR> <TD> tvdb3     </TD> <TD> TVDB                </TD> <TD>Absolute          </TD> <TD>Long series (Detective Conan)</TD> </TR>
        <TR> <TD> tvdb4     </TD> <TD> Custom/Arc database </TD> <TD>Absolute          </TD> <TD>Long series with arc (one piece, dragon ball)</TD> </TR>
</TBODY>
</TABLE>

Examples of force guid in all modes and their applications:

When you have all episodes of a series in a single parent folder:
- " [anidb-xxxxx]" for anime in absolute numbering. Force the anidb serie id
- " [tvdb-xxxxxx]" for tvdb season numbering. You can put separate anidb series as seasons as per tvdb numbering.
    SAO can be split at file level into "Season 1 - Sword Art Online" [1-25], "Season 2 - Alfheim & Gun Gale Online [1-25]".
- " [tvdb2-xxxxx]" for absolute numbering displayed virtually as tvdb numbering, episode number resets to 1 each season, for series like Sword art Online(1-50, will be split into Season 1 [1-25] and Season 2 [1-25])
- " [tvdb3-xxxxx]" for absolute numbering episodes displayed virtually using tvdb season numbering for long running series like One piece (1-700+, will be split into seasons while keeping the absolute episode number intact without having to create seasons in the real folder
- " [tvdb4-xxxxx]" for absolute numbering episodes displayed using series arc as season for long running series with arcs like Dragon Ball Kai, or separated anidb series considered as half seasons by thetvdb (like 'Seraph of the end' numbered 1-24 splitted into 2 seasons).
  The arc definition to split into seasons the absolute numbering is done using the following order:
    - Seasons folders manually created by the user with absolute numbered episodes inside (seasons already mapped manually)
    - in a local "tvdb.mapping" file inside serie folder
      FORMAT: <CODE>\<season_num\>|\<starting_ep_num\>|\<ending_ep_num\>|\<freeform_text_naming_the_season\>(optional)</CODE>
    - without doing anything using the online arc database [github tvdb4.mapping.xml](https://github.com/ZeroQI/Absolute-Series-Scanner/blob/master/tvdb4.mapping.xml)
      Format:<PRE><CODE>&lt;tvdb4entries&gt;
&lt;anime tvdbid="289906" name="Seraph of the End"&gt;
01|001|012|Vampire Reign
02|013|024|Battle in Nagoya
&lt;/anime&gt;
</CODE></PRE>

Advanced modes for when you have episodes of a series in SEPARATE parent folders but want them to show as a single series in Plex:
- " [anidb2-xxxxx]"
  - will find the season & eposide offset defiend in the ScudLee file and add into Plex with it's corresponding TVDB series/season/episode numbers
- " [tvdb/2/3/4-xxxxx-sY]"
  - episode numbers found in the files are left alone and added to season Y
- " [tvdb/2/3/4-xxxxx-eZ]"
  - episode numbers found in the files are adjusted (epNum+Z-1)
- " [tvdb/2/3/4-xxxxx-sYeZ]" 
  - episode numbers found in the files are adjusted (epNum+Z-1) and added to season Y
  - Z is the offset for the episodes in season Y for when we want it to start mid tvdb season
- **!!IMPORTANT NOTES FOR ADVANCED MODES!!**
  - When defining you modes on your folders:
    - If you don't use the same mode or compatible modes for all separate folders for a series, you will run into issues.
      - "anidb2", "tvdb", & "tvdb2" will work together
    - You might have to manually merge Plex series if "anidb2"/"tvdb2" or "tvdb"/"tvdb2" are both used.
    - "anidb2"/"tvdb" should automatically merge (but Plex is not perfect so you still might have to manually merge)
    - "tvdb3" will not work correctly with any other modes so all folders of a series will have to have this mode
    - "tvdb4" will not work correctly with any other modes so all folders of a series will have to have this mode

  Examples: <PRE><CODE>
== Example 1 ==
Bakuman [anidb2-7251]       =  Bakuman [tvdb-193811-s1]      = Bakuman [tvdb-193811]
Bakuman 2011 [anidb2-8150]  =  Bakuman 2011 [tvdb-193811-s2]
Bakuman 2012 [anidb2-8836]  =  Bakuman 2012 [tvdb-193811-s3]
== Example 2 ==
  "Sailor Moon Crystal [tvdb2-275039]"
  "Sailor Moon Crystal Season 3 [anidb2-11665]"  (or "[tvdb-275039-s3]" or "[tvdb2-275039-s3]")
== Example 3 ==
  "Bleach [tvdb3-74796]"
  "Bleach movie 1 Memories in the Rain [tvdb3-74796-s0e3]"
  "Bleach movie 2 The Diamond Dust Rebellion [tvdb3-74796-s0e4]"
== Example 4 ==
  https://github.com/ZeroQI/Absolute-Series-Scanner/blob/master/tvdb4.mapping.xml
    \<anime tvdbid="79604" name="Black Lagoon"\>
      01|001|012|The First Barrage
      02|013|024|The Second Barrage
      03|025|029|Roberta's Blood Trail
    \</anime\>
  "Black Lagoon [tvdb4-79604]"  (or "[tvdb4-79604-s1]")
  "Black Lagoon - The Second Barrage [tvdb4-79604-s2]"
  "Black Lagoon - Roberta`s Blood Trail [tvdb4-79604-s3]"
</CODE></PRE>

Install
=======
Put latest scanner file from:
- https://github.com/ZeroQI/Absolute-Series-Scanner/blob/master/Scanners/Series/Absolute%20Series%20Scanner.py
Into:
- [...]/Plex/Library/Application Support/Plex Media Server/Scanners/Series/Absolute Series Scanner.py

One user had folders rights issues on Windows 2008 R2
<code>2016-06-29 23:30:09,104 (30c) : CRITICAL (core:574) - Exception while loading code (most recent call last):
File "C:\Program Files (x86)\Plex\Plex Media Server\Resources\Plug-ins-a17e99e\Framework.bundle\Contents\Resources\Versions\2\Python\Framework\core.py", line 563, in load_code
self.init_code = self.loader.load(self.init_path, elevated, use_xpython = Framework.constants.flags.use_xpython in self.sandbox.flags)
File "C:\Program Files (x86)\Plex\Plex Media Server\Resources\Plug-ins-a17e99e\Framework.bundle\Contents\Resources\Versions\2\Python\Framework\code\loader.py", line 47, in load
code = self.compile(str(source), str(uni(filename)), elevated)
File "C:\Program Files (x86)\Plex\Plex Media Server\Resources\Plug-ins-a17e99e\Framework.bundle\Contents\Resources\Versions\2\Python\Framework\code\loader.py", line 52, in compile
return RestrictedPython.compile_restricted(source, name, 'exec', elevated=elevated)
File "C:\Program Files (x86)\Plex\Plex Media Server\Resources\Plug-ins-a17e99e\Framework.bundle\Contents\Resources\Platforms\Shared\Libraries\RestrictedPython\RCompile.py", line 115, in compile_restricted
gen.compile()
File "C:\Program Files (x86)\Plex\Plex Media Server\Resources\Plug-ins-a17e99e\Framework.bundle\Contents\Resources\Platforms\Shared\Libraries\RestrictedPython\RCompile.py", line 68, in compile
tree = self._get_tree()
File "C:\Program Files (x86)\Plex\Plex Media Server\Resources\Plug-ins-a17e99e\Framework.bundle\Contents\Resources\Platforms\Shared\Libraries\RestrictedPython\RCompile.py", line 59, in _get_tree
tree = self.parse()
File "C:\Program Files (x86)\Plex\Plex Media Server\Resources\Plug-ins-a17e99e\Framework.bundle\Contents\Resources\Platforms\Shared\Libraries\RestrictedPython\RCompile.py", line 56, in parse
return niceParse(self.source, self.filename, self.mode)
File "C:\Program Files (x86)\Plex\Plex Media Server\Resources\Plug-ins-a17e99e\Framework.bundle\Contents\Resources\Platforms\Shared\Libraries\RestrictedPython\RCompile.py", line 38, in niceParse
compile(source, filename, mode)
TypeError: compile() expected string without null bytes
</code>

He solved it by changing rights for:
- ...\Users\Administrator\AppData\Local\Plex Media Server\Plug-Ins
- ...\Users\Administrator\AppData\Local\Plex Media Server\Scanners

###Logs
Absolute series Scanner uses a pre-made list of folders to try to locate Plex Logs folder. 
If custom logs are not present, then either you created a library using default Plex scanner and not my "Absolute Series Scanner" or you have an unknown Logs folder location and will need to forward me the path to add in the source code...
If the scanner crash, you will get either no files (library creation) or no change (library already created) and will need to attach the Plex log "Plex Media Scanner.log"

List of logs files:
- Plex Media Scanner (custom ASS) - Library_Name.log contain all folders and files processed in a readable fashion, perfect for troubleshooting scanner issues.
- Plex Media Scanner (custom ASS) - Library_Name - filelist Root_Folder_name.log contain all files in the root folder, so i can re-create your library with zero size files. I use a batch file to recreate a user's library after converting to utf-8 with notepad
- Plex Media Scanner.log - Standard Plex Scanner Log, contain crash error in case of a bug in the scanner code

List of configuration files, to put in logs folder, can be found the (blank) config files in GitHub > ASS > releases > logs.7z
- "X-Plex-Token.id: Allow to get the library name to get a log per library (optional). Fill with plex token by following https://support.plex.tv/hc/en-us/articles/204059436-Finding-your-account-token-X-Plex-Token. **_Do not share that file when uploading the whole Logs folders_**

Troubleshooting:
================
If the scanner not listed in scanner list:
- Make sure you did not create a movie library, as it will mot show a SERIES scanner....
- check size and open file to check for corruption
- If you have HTML tags at the beginning you saved the scanner file wrong and should feel bad

On windows install https://www.microsoft.com/en-us/download/details.aspx?id=48145 if you experience this error:
<PRE><CODE>
Jul 23, 2016 12:55:54.558 [5288] ERROR - Error scanning directory .
Jul 23, 2016 12:55:54.574 [5288] ERROR - No module in Absolute Series Scanner
Jul 23, 2016 12:55:54.574 [5288] ERROR - Error in Python: Looking up module:
Traceback (most recent call last):
File "C:\Users\Administrator\AppData\Local\Plex Media Server\Scanners\Series\Absolute Series Scanner.py", line 8, in 
from lxml import etree # fromstring
ImportError: DLL load failed: The specified module could not be found.
</CODE></PRE>

On linux, permissions issues could prevent the scanner execution. Check hama readme for commands and posts the ones not documented if any.

If you have these or similar symptoms (or others):
- nothing is scanned
- episodes are missing
- Series are missing
- library doesn't add new content (after scanner update) then most likelly the scanner is crashing and revert any changed to the library

Include the following logs (in any case, specify if file not present):
- [...]/Plex Media Server/Logs/Plex Media Scanner.log                       (scanner crash info)
- [...]/Plex Media Server/Logs/Plex Media Scanner (custom ASS).log          (episodes info)
- [...]/Plex Media Server/Logs/Plex Media Scanner (custom ASS) filelist.log (library file list)

And post in:
- Support thread for Scanner (you are unsure): https://forums.plex.tv/discussion/113967/absolute-series-scanner-for-anime-mainly/#latest
- Github issue page (you have a bug):          https://github.com/ZeroQI/Absolute-Series-Scanner/issues

###Folder Structure for massive storages
I thought my folder structure could help many, you can store anything in htere
Implied is original language, folder named dubbed otherwise

- Series
  - Xx (En/Fr/Sp/Jap sub En/...)
  - Xx Reality-Shows
  - Xx Stand-Up Comedy
  - Xx Dubbed

- Movies
  - Xx (En/Fr/Sp/Jap sub En/...)
  - Xx Reality-Shows
  - Xx Stand-Up Comedy

- Anime
  - Xx (Jap sub En)
  - Xx Movies (En/Fr/...)
  - Xx Series (En/Fr/...)

- Knowledge
  - Documentaries
  - Hobbies
  - Litterature
  - Trainings

- Music
  - Albums [\Group\Album (Year)]
  - Compilations
  - Soundtracks
    - Ads
    - Anime
    - Movies
    - Series
  - Videos
    - Xx
    - Xx Concerts
  - Games
    - Karaoke
    - Guitar
    - DDR

  - Pictures
    - Wallpapers
    - Maps
    - Textures

  - Scans
    - Art Books
    - Xx Comics
    - Xx Mangas

  - Software
    - Computer
      - 1977 Apple II
      - Linux
      - Mac-OS
      - Synology DSM
      - Windows
    - Console Cartridge
    - Console CD
    - Console DVD
    - Handheld
    - Multi-Systems (Mame, Mess)
    - Phone

###Japanese Media Manager
It uses anidb as source and uses hash info from file to determine what the show is (release included) and where it goes.
So this means that shows like SOA/Fate stay night..etc are all in there own folder for each part of the series.
Movies are also in there own folder since anidb treats every movie as its own show.
http://jmediamanager.org/jmm-desktop/utilities/file-renaming/

Renaming Script:
<code><pre>
IF I(eng) DO ADD '%eng'
IF I(ann);I(!eng) DO ADD '%ann'
DO REPLACE '[' ''
DO REPLACE ']' ''
IF T(!Movie);H(!S);T(!OVA) DO ADD ' - %enr - '
IF H(S),T(OVA),T(Movie) DO ADD ' - %enr - '
DO ADD '%epr '
DO ADD '[%grp]'

// Replace all illegal file name characters
DO REPLACE '<' '('
DO REPLACE '>' ')'
DO REPLACE ':' ' -'
DO REPLACE '"' '`'
DO REPLACE '/' '-'
DO REPLACE '\' '_'
DO REPLACE '|' '_'
DO REPLACE '?' ''
DO REPLACE '*' '+'
//DO REPLACE 'S0' '0'
DO REPLACE '[%grp]' ''
</pre></code>

###Batch file to create filelist.txt or re-create a library from the filelist with 0 size files
<code><pre>
@ECHO OFF
REM 1 - if no filelist create filelist no folders
REM 2 - if file there restore
chcp 1252>nul

IF EXIST filelist.txt goto RESTORE
ECHO Press Enter to create listfile.txt containing all files relative path
rundll32 user32.dll,MessageBeep -1
PAUSE
SETLOCAL DisableDelayedExpansion
SET "r=%__CD__%"
type nul > filelist.txt
FOR /R . %%F IN (*) DO (
  SET "p=%%F"
  SETLOCAL EnableDelayedExpansion
  ECHO(!p:%r%=!
  ENDLOCAL
) >> filelist.txt
ECHO [filelist.txt] created list
rundll32 user32.dll,MessageBeep -1
GOTO EXIT

:RESTORE
ECHO Press enter to create all dummy files from filelist.txt
rundll32 user32.dll,MessageBeep -1
PAUSE
rem for /f "tokens=2 delims=:." %%x in ('chcp') do set cp=%%x
rem chcp 437>nul

REM IMPORTANT LOOP DOING ALL THE WORK
for /f "tokens=*" %%a in (filelist.txt) do (
IF NOT EXIST "%%~pa" mkdir "%%~pa"
IF NOT EXIST "%%a" TYPE nul > "%%a"
)
rem chcp %cp%>nul
ECHO [filelist.txt] processed, blank files created
rundll32 user32.dll,MessageBeep -1
GOTO EXIT

:EXIT
ECHO Finished!
PAUSE
</pre></code>

###Task list
- [ ] Support Media stubs .Disc files ? http://kodi.wiki/view/Media_stubs
- [ ] Shall i write a Movie scanner using the same code? The Plex default movie scanner does an good job i believe ?

Reference: [Link to Markdown](https://guides.github.com/features/mastering-markdown/) or https://help.github.com/articles/basic-writing-and-formatting-syntax/
