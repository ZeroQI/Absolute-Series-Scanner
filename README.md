## Plex scanner responsibilities
A Plex Series Scanner makes the video files showing in Plex and populate the following for the video files:
- Series name
- Series year
- Season number
- Episode number
- Episode title (not filled by plex default series scanner, but ASS fills it, but this will be overwritten by the metadata agent)

If a file is not showing in plex or showing at the wrong season and/or episode number, or is not passing through the forced id, then it is a scanner issue. Anything else is metadata related and agent specific.

If you post anything on the scanner github or thread for any issue like poster missing/wrong, episode thumbnail/screenshot/title/summary missing/wrong, then you clearly haven't read this and need to pay the RTFM tax by donating (or you just find this the best anime scanner and/or agent, much apreciated average is 5 euros). Also applies if you want assistance but didn't follow troubleshooting steps or include logs...

## Plex Agent responsabilities
A Plex metadata agent will:
- Search the metadata source using the Series name given by the scanner and assign the series a guid, a unique identifier used to download the metadataa informations
- Update all the metadata information ((Series Title, summary year, episode title, summary, posters, fanart, tags, ...) for series and files showing in Plex thanks to the scanner. 
- Full list of fields here:  see https://github.com/ZeroQI/Hama.bundle/wiki/Plex-Metadata-Fields-Available for full list of fields)
Any information missing or wrong inthere in Plex is an Agent issue, refer to the Agent readme here: https://github.com/ZeroQI/Hama.bundle/blob/master/README.md

## Which Metadata/Title source to select?
- Anime:     AniDB.net, Hama use an offline title database from them ("main title" is the best, or romaji "x-jat". "En" titles have horrors like "bombshells from the sky" for "Asobi ni Iku yo!" series). AniDB use small posters, no background. Hama use ScudLee's xml mapping files to crosss reference the anidb id to the tvdb series. Hama supports AniDB, TheTVDB, mainly, and if ScudLee mapping file has it, TheMoviedB, MyAnimeList, TelevisionTunes for full length theme songs, ...
- TV Series: TheTVDB.com or TVrage or TheMovieDB (support series now), no db site will store (DVD) boxset specific files (nor sport or porn for TheTVDB). TVDB has high resolution posters, background images, screenshots, and episodes summaries, all lacking from AniDB.net, but they do not carry porn series so no metadata for this type. TheTVDB uses seasons which can be practical for long anime. Episodes have titles and summary in many languages
- Movies:    TheMovieDB.org, naming convention: "Movie Title (Year).ext"
- YouTube:   Series/Movie library YouTube-Agent for Movies '[youtube-video_id]' and Series/seasons '[youtube-playlist_id]' (starts with PL then 16/32 chars)

## Absolute series scanner functions that differes from Plex Series Scanner
- .plexignore' fully working including subfolders
- YouTube playlist with id in series or season folder get added without numbering/renaming needed
- Video files inside zip file gets displayed (not playable)
- Seamless 'Grouping folder': For example 'Dragon Ball/[01] Dragon Ball/ep xxx.ext'
- Season folder advance support: 'Season xxx title_for season'
- Episode grouping in transparent/Ark folders: '[01] Saga xxx', '[02] Story xxx', '[03] Arc xxx'
- Episode title is taken from the filename (to be re-written by the agent but usefull if series is not matched yet)
- Japanese and Specials chars handling ("CØDE：BREAKER") and files starting with dots (".Hack")
- AniDB numbering support ((NC)OP/(NC)ED/SpXX, etc...)
- Movies in series libraries support (names same as folder or contain " - Complete Movie")
- Forced id in series name or id file for the agent gets passed through
- Display absolute series without file renaming displayed with seasons (tvdb2/3/4) or remapped chronology wise (tvdb5) or anidb sereis grouped and displayed as tvdb series (anidb2, need mapping accurate in scudlee files to work)
- Use sagas as seasons keeping absolute numbering with TVDB4 and it create even the seasons for you from a database if not specified
- Versatile file format support. if a logical numbering format isn't supported let me know (no episode number in brackets or parenthesis though, that's moronic)
- put per-series logs ('xxx.filelist.log' and 'xxx.scanner.log' in /Plex Media Server/Plug-in Support/Data/com.plexapp.agents.hama/DataItems/Logs).

## File Naming Conventions / Numbering
This scanner supports absolute and season numbering, but here are two references for guidelines
- Naming convention for Plex: https://support.plex.tv/hc/en-us/sections/200059498-Naming-and-Organizing-TV-Shows
- Naming convention for XBMC:  http://wiki.xbmc.org/index.php?title=Naming_video_files/TV_shows
- Specials chars handling ("CØDE：BREAKER") and files starting with dots (".Hack")
- Do not use semicolon: ';', replace with space as plex give only the title up to this character to media.title (if movie) / media.show (if TV Series) and truncate wven file path

### Files
<TABLE>
<THEAD>
<TR> <TH> File naming convention </TH> <TH> Template / Folder </TH> <TH>Example </TH> </TR>
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

##### Specials
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

####### Anidb type special numbering is detailed below:
<TABLE> 
<THEAD> <TR> <TH> Type     </TH> <TH> Internal letter </TH> <TH>  Episode number   </TH> </TR> </THEAD>
<TBODY> <TR> <TD> Specials </TD> <TD> S               </TD> <TD>  Episodes 001-100 </TD> </TR>
        <TR> <TD> OPs      </TD> <TD> C               </TD> <TD>  Episodes 101-150 </TD> </TR>
        <TR> <TD> EDs      </TD> <TD> C               </TD> <TD>  Episodes 151-200 </TD> </TR>
        <TR> <TD> Trailers </TD> <TD> T               </TD> <TD>  Episodes 201-300 </TD> </TR>
        <TR> <TD> OPs/EDs  </TD> <TD> P               </TD> <TD>  Episodes 301-400 </TD> </TR>
        <TR> <TD> Others   </TD> <TD> O               </TD> <TD>  Episodes 401-500 </TD> </TR>
        <TR> <TD> unmapped </TD> <TD>                 </TD> <TD>  Episodes 501-600 </TD> </TR> </TBODY>
</TABLE>

##### One libray for both movies and TV series
Movie files in Series libraries (since this is a Series Scanner) are supported if:
-  Files are in a folder with the same name or with a single file inside it
-  Filename contain " - Complete Movie"
-  Files are numbered (01|ep 01|s01e01)

### Season folders
- Seasons folders can have series name afterwards ("Zero no Tsukaima / Season 1 Zero no Tsukaima"
- Files in "Extras" folders will be ignored.
- Allow grouping in Ark xxxxx folders transparently with seasons folders inside, or within a season folder
- Specials go in "Specials" or "Season 0" folders.
  - Single seasons series will follow anidb specials numbering (unless specific tvdb guid forced).
  - Multiple seasons series will follow tvdb specials numbering
  - You can use Anidb numbering for specials (OP1a, NCOP, etc...) or explicitely label them as follow (s00e101, etc...).
  - Include all files not recognised as Season 0 episode 501+

##### Local media assets
It is supported but through "local media assets" agent, add it and and put it before HAMA in the priority order.<BR />
https://support.plex.tv/hc/en-us/articles/200220717-Local-Media-Assets-TV-Shows

<TABLE>
<THEAD>
<TR> <TH> Data type </TH> <TH> Source                </TH> <TH>           Comment </TH> </TR>
</THEAD>
<TBODY>
<TR> <TD> fanart  </TD> <TD> art/backdrop/background/fanart-1.ext</TD> <TD> -1 can be ommited (same level as Video TS) </TD> </TR>
<TR> <TD> Series poster </TD> <TD> Series folder: Show name-1/folder/poster/show.ext</TD> <TD> (jpg, jpeg, png, tbn) </TD> <TR>
<TR> <TD> Season poster</TD> <TD> Season folder: Season01a.ext </TD> <TD> (jpg, jpeg, png, tbn) </TD> <TR>          
<TR> <TD> Banner    </TD> <TD> banner/banner-1.jpg  </TD> <TD> </TD> </TR>
<TR> <TD> Theme song</TD> <TD> theme.mp3  </TD> <TD> </TD> <TR>
<TR> <TD> Subtitles </TD> <TD> file name.ext (srt, smi, ssa, ass)  </TD> <TD> </TD><TR>
<TR> <TD> Plexignore files  </TD> <TD> .plexignore  </TD> <TD> </TD> <TR>
</TBODY>
</TABLE>

Movie libraries can have "Extra" in a specifically named folders or with the following at the end of the filename (hyphen important, no space afterwards):
<ul><li>"Behind The Scenes" folder or "-behindthescenes" at the end of the filename
    <li>"Deleted Scenes" folder or "-deleted" at the end of the filename
    <li>"Featurettes" folder or "-featurette" at the end of the filename
    <li>"Interviews" folder or "-interview" at the end of the filename
    <li>"Scenes" folder or "-scene" at the end of the filename
    <li>"Shorts" folder or "-short" at the end of the filename
    <li>"Trailers" folder or "-trailer" at the end of the filename
</ul>
Note: "Extras" folder is skipped by the absolute series scanner, put unsorted files in there, it won't show up in Plex

### Grouping folder
- If you use "Grouping folder / Show Name / Season 1 / Show Name e01.ext" convention from the root, it will work but be scanned every time.

### Forcing the movie/series ID
Hama supports the following guid_type:
- anidb for AniDB.net (and and the behaviour changing mode anidb2)
- tvdb  for TheTVDB.com (and the behaviour changing modes: tvdb2, tvdb3, tvdb4)
- [deprecated] tmdb  For TheMovieDB.net (and the series part of TheMovieDB: tsdb)
- [deprecated] imdb  For the International Movie DataBase (ids starts with "tt...")

You can specify the guid to use the following way:
- In Series folder name by adding " [guid_type-id_number]" at the end (like "Oruchuban Ebichu [anidb-150]")
- In "series_folder/guid_type.id" file with the id in it (ex: "Oruchuban Ebichu/anidb.id" file with "150" inside without double quotes)
- In custom search series name by adding " [guid_type-id_number]" at the end (ex " [anidb-150]") for modes which do not change the season or episode numbers at scanner level (so anidb, tvdb and not numbered guid_types unless tvdb4 and you already put the eps in their respective seasons folders)

<TABLE>
<THEAD> <TR> <TH> guid_type </TH> <TH> Real file numbering     </TH>  <TH> Seasons numbering   </TH> <TH>Episodes numbering</TH> <TH>Use case (example)</TH></TR></THEAD>
<TBODY>
        <TR> <TD> anidb     </TD> <TD> Absolute                </TD> <TD> 1                </TD> <TD>AniDb          </TD> <TD>Force the anidb series id. Series will follow anidb episode numbering convention including specials
        <UL><LI>Sword Art online                           [anidb-8692]</LI>
        </UL></TD> </TR>
        <TR> <TD> anidb2     </TD> <TD> Absolute                </TD> <TD> TVDB                </TD> <TD>TVDB          </TD> <TD>Map Anidb entries to the tvdb at the right season and ep number to show one Plex series entry only (need to be within a single tvdb entry)
        <UL><LI>Sword Art online                           [anidb2-8692]</LI>
            <LI>Sword Art online II                        [anidb2-10376]</LI>
            <LI>Sword Art Online Extra Edition             [anidb2-10022]</LI>
            <LI>Gekijouban Sword Art Online: Ordinal Scale [anidb2-11681]</LI>
        </UL></TD> </TR>
        <TR> <TD> anidb3     </TD> <TD> Absolute                </TD> <TD> TVDB                </TD> <TD>TVDB          </TD> <TD>Uses ScudLee mapping to map the AniDB series to TVDB entries BUT overrides the mapping for TVDB season 0 entries and puts them in AniDB relational order by appending to existing seasons or adding new seasons at after the last TVDB season
        <UL><LI>Date a Live                          [anidb3-8808]  => TVDB s1   </LI>
            <LI>Date a Live: Date to Date            [anidb3-9734]  => TVDB s0e1 -> s1e101</LI>
            <LI>Date a Live II                       [anidb3-9935]  => TVDB s2   </LI>
            <LI>Date a Live II: Kurumi Star Festival [anidb3-10568] => TVDB s0e2 -> s2e101</LI>
            <LI>TBD (prep entry in TVDB)                            => TVDB s3   </LI>
        </UL></TD> </TR>
        <TR> <TD> anidb4     </TD> <TD> Absolute                </TD> <TD> TVDB                </TD> <TD>TVDB          </TD> <TD>Uses ScudLee mapping to map the AniDB series to TVDB entries BUT overrides the mapping for TVDB seasons entries and puts them in AniDB relational order by inserting new seasons and pushing later TVDB seasons back
        <UL><LI>Date a Live                          [anidb3-8808]  => TVDB s1   -> s1</LI>
            <LI>Date a Live: Date to Date            [anidb3-9734]  => TVDB s0e1 -> s2</LI>
            <LI>Date a Live II                       [anidb3-9935]  => TVDB s2   -> s3</LI>
            <LI>Date a Live II: Kurumi Star Festival [anidb3-10568] => TVDB s0e2 -> s4</LI>
            <LI>TBD (prep entry in TVDB)                            => TVDB s3   -> s5</LI>
        </UL></TD> </TR>
        <TR> <TD> tvdb     </TD> <TD> Season                   </TD> <TD> TVDB                </TD> <TD>TVDB              </TD> <TD>Force the tvdbid, series will follow tvdb episode numbering convention including specials
        <UL>
          <LI>Sword Art Online [tvdb-259640]</LI>
          <LI>Season 1 - Sword Art Online [1-25]/ep ##.ext with ## from 1 to 25
          <LI>Season 2 - Alfheim & Gun Gale Online [1-25]/ep ##.ext ## from 1 to 25
        </UL>        
        </TD> </TR>
        <TR> <TD> tvdb2     </TD> <TD> Absolute                </TD> <TD> TVDB                </TD> <TD>TVDB              </TD> <TD>for absolute numbering displayed virtually as tvdb numbering, episode number resets to 1 each season, for series like Sword art Online(1-50, will be split into Season 1 [1-25] and Season 2 [1-25])
        <UL>
          <LI>Sword Art Online [tvdb2-259640]/Ep ##.ext with ## from 1 to 50</LI>
        </UL>        
        </TD> </TR>
        <TR> <TD> tvdb3     </TD> <TD> Absolute                </TD> <TD> TVDB                </TD> <TD>Absolute          </TD> <TD>For absolute numbering episodes displayed virtually using tvdb season numbering for long running series like One piece (1-700+, will be split into seasons while keeping the absolute episode number intact without having to create seasons in the real folder
        <UL><LI>Metantei Conan [tvdb3-72454] </LI></UL></TD> </TR>
        <TR> <TD> tvdb4     </TD> <TD> Absolute, random season </TD> <TD> Abs/Custom/Arc db   </TD> <TD>Absolute          </TD> <TD>For absolute numbering episodes displayed using series arc as season for long running series with arcs like Dragon Ball Kai, or separated anidb series considered as half seasons by thetvdb (like 'Seraph of the end' numbered 1-24 splitted into 2 seasons). Will take the arc definitions from tvdb4.mapping.xml and posters from tvdb4.posters.xml unless the absolute numbered episodes were placed in season folders already
        <UL><LI>One Piece [tvdb4-81797] </LI></UL>        
        </TD> </TR>
        <TR> <TD> tvdb5     </TD> <TD> TVDB                    </TD> <TD>Absolute             </TD> <TD>Absolute          </TD> <TD>TheTVDB Absolute numbering order (specifically for Star Wars: The Clone Wars) will remove seasons present and use the 'absolute_number' field order to re-sort the episodes. First ep is s02e15 from memory...
<UL><LI>Star Wars: The Clone Wars [tvdb5-83268] </LI></UL>
</TD> </TR>
        <TR> <TD> youtube     </TD> <TD> YouTube                    </TD> <TD> None             </TD> <TD> None          </TD> <TD> Put Playlist id (PL... 2+16/32 chars long) on series folder or season folder to have the youtube files downloaded with youtube-dl numbered as per the playlist order</LI></UL>
</TD> </TR>
</TBODY>
</TABLE>

##### Advanced modes
For when you have episodes of a series in SEPARATE parent folders but want them to show as a single series in Plex:
- " [anidb2-xxxxx]" will find the season & eposide offset defined in the ScudLee file and add into Plex with it's corresponding TVDB series/season/episode numbers
- " [anidb3-xxxxx]" will find the season & eposide offset defined in the ScudLee file and add into Plex ?????
- " [anidb4-xxxxx]" will find the season & eposide offset defined in the ScudLee file and add into Plex ????
- " [tvdb/2/3/4-xxxxx-sY]" episode numbers found in the files are left alone and added to season Y
- " [tvdb/2/3/4-xxxxx-eZ]" episode numbers found in the files are adjusted (epNum+Z-1)
- " [tvdb/2/3/4-xxxxx-sYeZ]" episode numbers found in the files are adjusted (epNum+Z-1) and added to season Y, Z is the offset for the episodes in season Y for when we want it to start mid tvdb season
- **!!IMPORTANT NOTES!!**
  - When defining your modes on your folders:
    - If you don't use the same mode or compatible modes for all separate folders for a series, you will run into issues.
      - "anidb2", "anidb3", "tvdb" & "tvdb2" will work together
    - You might have to manually merge Plex series together if "anidb2"/"tvdb2" or "tvdb"/"tvdb2" are both used.
    - "anidb2"/"anidb3"/"tvdb" should automatically merge (but Plex is not perfect so you still might have to manually merge)
    - "anidb4" will not work correctly with any other modes so all folders of a series will have to have this mode
    - "tvdb3" will not work correctly with any other modes so all folders of a series will have to have this mode
    - "tvdb4" will not work correctly with any other modes so all folders of a series will have to have this mode

##### Examples: 
<PRE><CODE>== Example 1 ==
- "Bakuman      [anidb2-7251]" = "Bakuman      [tvdb-193811-s1]" = "Bakuman [tvdb-193811]"
- "Bakuman 2011 [anidb2-8150]" = "Bakuman 2011 [tvdb-193811-s2]"
- "Bakuman 2012 [anidb2-8836]" = "Bakuman 2012 [tvdb-193811-s3]"

== Example 2 ==
- "Sailor Moon Crystal [tvdb2-275039]"
- "Sailor Moon Crystal Season 3 [anidb2-11665]" = "[tvdb-275039-s3]" | "[tvdb2-275039-s3]" (depending if you keep absolute numbered eps in seasons)
  
== Example 3 ==
  "Bleach                                    [tvdb3-74796]"
  "Bleach movie 1 Memories in the Rain       [tvdb3-74796-s0e3]"
  "Bleach movie 2 The Diamond Dust Rebellion [tvdb3-74796-s0e4]"
  
== Example 4 == tvdb4 Custom selected Arcs as seasons (as tvdb use them as half seasons for black lagoon for example)
  The arc definition to split into seasons the absolute numbering is done using the following order:
    - Seasons folders manually created by the user with absolute numbered episodes inside (seasons already mapped manually)
    - in a local "tvdb4.mapping" file inside series folder with the following format lines, one per arc/season:
      <CODE>\<season_num\>|\<starting_ep_num\>|\<ending_ep_num\>|\<freeform_text_naming_the_season\>(optional)</CODE>
    - without doing anything using the online arc database [github tvdb4.mapping.xml](https://github.com/ZeroQI/Absolute-Series-Scanner/blob/master/tvdb4.mapping.xml)
    
    &lt;anime tvdbid="79604" name="Black Lagoon"&gt;
      01|001|012|The First Barrage
      02|013|024|The Second Barrage
      03|025|029|Roberta's Blood Trail
    &lt;/anime&gt;
    &lt;anime tvdbid="289906" name="Seraph of the End"&gt;
      01|001|012|Vampire Reign
      02|013|024|Battle in Nagoya
    &lt;/anime&gt;

  "Black Lagoon                         [tvdb4-79604]"
  "Black Lagoon - The Second Barrage    [tvdb4-79604-s2]"
  "Black Lagoon - Roberta`s Blood Trail [tvdb4-79604-s3]"
  
  "Seraph of the End - Vampire Reign    [tvdb4-79604]"
  "Seraph of the End - Battle in Nagoya [tvdb4-79604-s2]"
</CODE></PRE>

### .plexignore files
https://support.plex.tv/articles/201375253-excluding-new-content-with-plexignore/
- Warning: This is an advanced feature and is not intended for general users.
- Blank lines and lines starting with #  are ignored.
- The * character is a wildcard.
- Patterns without the forward-slash (/) character (e.g. *.mkv) match filenames in the same directory as the .plexignore file, or its subfolders
- Patterns with the forward-slash (/) character (e.g. somedir/*) match directory and file patterns relative to the directory containing the .plexignore file only, not is subfolders


## Plex system folder location
Source: https://support.plex.tv/articles/202915258-where-is-the-plex-media-server-data-directory-located/
Location:
- Windows:                                 %LOCALAPPDATA%\Plex Media Server
- OSX:                                     ~/Library/Application Support/Plex Media Server/
- Linux and NAS Devices:                   $PLEX_HOME/Library/Application Support/Plex Media Server/
- Debian, Fedora, CentOS, Ubuntu:          /var/lib/plexmediaserver/Library/Application Support/Plex Media Server/
- FreeBSD:                                 /usr/local/plexdata/Plex Media Server/
- FreeNAS:                                 ${JAIL_ROOT}/var/db/plexdata/Plex Media Server/
- ReadyNAS:                                /apps/plexmediaserver/MediaLibrary/Plex Media Server/
/data/plex_conf/Library/Application Support/Plex Media Server
- Synology, Asustor:                        /Volume1/Plex/Library/Application Support/Plex Media Server/
- TerraMaster:                              /home/plex/Library/Application Support/Plex Media Server
- Thecus:                                   /raid/data/module/Plex/sys/Plex Media Server/
- Western Digital                           /mnt/HD/HD_a2/plex_conf/Plex Media Server/
- Western Digital My Passport Wireless Pro: /shares/Storage/.wdcache/.plexmediaserver/Application Support/Plex Media Server/
Variable path:
- QNAP:                                     getcfg -f /etc/config/qpkg.conf PlexMediaServer Install_path  then add '/Library/Plex Media Server'
- Seagate:                                  sudo rainbow —enter com.plex.plexmediaserver. Once in, you can go to the data directory: 

You can actually move the plex system folder/storage/database here: (i give no warranty it works, you lunatic!)
- PMS:             PMS settings > Server > General > 'The path where local application data is stored'
- registry:        HKEY_CURRENT_USER\Software\Plex, Inc.\Plex Media Server key\LocalAppDataPath [type REG_SZ] the full path to the directory
- Windows simlink: stop PMS,  mklink /D "C:\Users\<yourusername>\Appdata\Local\Plex Media Server" "G:\Plex Media Server" then start PMS

## Install / Update
- Download  https://raw.githubusercontent.com/ZeroQI/Absolute-Series-Scanner/master/Scanners/Series/Absolute%20Series%20Scanner.py
- Save into [...]/Plex Media Server/Scanners/Series/Absolute Series Scanner.py
Note:
- "Scanners" and "Series" folder are not created by default and will need to be created.
- "Scanners" folder will be at the same level as "Plug-in Support" folder (in other words the same parent directory)
- "Absolute Series Scanner.py" resides in Series folder, do not create an additional folder not listed like "absolute-series-scanner-master" and add the correct permissions on the init.py file. This should be done with chmod +x under linux
- Once the scanner is installed correctly, when creating a library you can select the custom scanner, otherwise the drop-down selection list is not shown when creating a TV Series library on the advanced tab.

Linux install script example
<PRE><CODE>
mkdir -p '/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Scanners/Series'
wget -O '/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Scanners/Series/Absolute Series Scanner.py' https://raw.githubusercontent.com/ZeroQI/Absolute-Series-Scanner/master/Scanners/Series/Absolute%20Series%20Scanner.py
chown -R plex:plex '/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Scanners'
chmod 775 -R '/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Scanners'
</CODE></PRE>

## Troubleshooting:
- Update the scanner to the latest (on windows, powershell script in same folder as the scanner can be used to update)
- If the scanner not listed in scanner list
  - Make sure you did create a "Series" library, as a "Movie" library will not show a "Series" scanner like ASS
  - Make sure it is saved in [...]/Plex/Library/Application Support/Plex Media Server/Scanners/Series/Absolute Series Scanner.py
  - Check scanner file size and open the scanner file to check if it does have html/xml tags.
- Recreate a Series library to the same folder, using Hama agent, this way all logs will start afresh
- if no files are showing, the scanner is crashing, probably a code error, check Plex Media Scanner.log for crash errors
- If Episodes are missing, wrong seasons or episode numbers, or series missing, check all "(custom ASS)" logs
- If library doesn't add new content then most likelly the scanner is crashing (after scanner update) and will revert any changes to the library so nothing changes...
- For scanner or agent issues where the agent doesn't crash, please include impacted series filelist and scanner logs, location below

## Logs
Absolute series Scanner saves its custom logs in this relative path Plex Media Server\Plug-in Support\Data\com.plexapp.agents.hama\DataItems\_Logs\...
You may create a X-Plex-Token.id file in 'Plex Media Server' folder with your token inside to have logs saved per library.
See this link to find your token value: https://support.plex.tv/hc/en-us/articles/204059436-Finding-your-account-token-X-Plex-Token

If the scanner crash, you will get either no files (library creation) or no change (library already created) and will need to attach the Plex log "Plex Media Scanner.log"

Include the following logs (in any case, specify if file not present):
- [...]/Plex Media Server/Logs/Plex Media Scanner.log (scanner crash info, no new files added, etc...)
- [...]/Plex Media Server/Plug-in Support/Data/com.plexapp.agents.hama/DataItems/Library_name/Logs/root_folder_name.filelist.log
- [...]/Plex Media Server/Plug-in Support/Data/com.plexapp.agents.hama/DataItems/Library_name/Logs/root_folder_name.scanner.log
- [...]/Plex Media Server/Plug-in Support/Data/com.plexapp.agents.hama/DataItems/Logs/root_folder_name.filelist.log
- [...]/Plex Media Server/Plug-in Support/Data/com.plexapp.agents.hama/DataItems/Logs/root_folder_name.scanner.log

You will find per-serie logs there with the following extensions as HAMA and ASS gather all logs in one place
- _root_/root folder name.filelist.log - Scanner filelist and 'plexignore logs
- _root_/root folder name.scanner.log - Scanner logs including: serie title season, episode number and preliminary title
- _root_/root folder name.agent-search.log - Agent search, show the assignment to the right serie
- _root_/root folder name.agent-update.log - Agent metadata update logs grom the guid assigned by the agent search function.

And post in either:
- [Plex Support thread for Scanner (you are unsure if it is a bug)](https://forums.plex.tv/discussion/113967/absolute-series-scanner-for-anime-mainly/#latest)
- [Github issue page (you have a bug)](https://github.com/ZeroQI/Absolute-Series-Scanner/issues)
- Creating a post or bug report without including relevant information like logs, serie impacted, or having not said the troubleshooting steps were followed will be recommended to pay the RTFM tax by donating. This part is called 'Exhibit A'. 

### Known issues:

<PRE><CODE>
Nov 16, 2016 18:48:53.594 [0x7f48c2324800] DEBUG - Adding subdirectory for scanner: /home/plex/things/anime/Ah! My Goddess 2
Nov 16, 2016 18:48:53.597 [0x7f48c2324800] ERROR - No module in VideoFiles
Nov 16, 2016 18:48:53.597 [0x7f48c2324800] ERROR - Error scanning directory .
Nov 16, 2016 18:48:53.597 [0x7f48c2324800] ERROR - No module in Absolute Series Scanner
Nov 16, 2016 18:48:53.598 [0x7f48c2324800] ERROR - We got an error scanning in /home/plex/things/anime
</CODE></PRE>
You bloody downloaded the web page and not the actual py file:

<PRE><CODE>
Jul 23, 2016 12:55:54.558 [5288] ERROR - Error scanning directory .
Jul 23, 2016 12:55:54.574 [5288] ERROR - No module in Absolute Series Scanner
Jul 23, 2016 12:55:54.574 [5288] ERROR - Error in Python: Looking up module:
Traceback (most recent call last):
File "C:\Users\Administrator\AppData\Local\Plex Media Server\Scanners\Series\Absolute Series Scanner.py", line 8, in 
from lxml import etree # fromstring
ImportError: DLL load failed: The specified module could not be found.
</CODE></PRE>
On windows install https://www.microsoft.com/en-us/download/details.aspx?id=48145 or other runtimes

<PRE><CODE>
2016-06-29 23:30:09,104 (30c) : CRITICAL (core:574) - Exception while loading code (most recent call last):
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
</CODE></PRE>
Rights issues on Windows 2008 R2, solved by changing rights for:
- ...\Users\Administrator\AppData\Local\Plex Media Server\Plug-Ins
- ...\Users\Administrator\AppData\Local\Plex Media Server\Scanners

On linux (and Mac OS-X), permissions issues could prevent the scanner execution, but after creating folder and setting proper permissions, all was working. Exemples solved by creating folders and setting proper permissions:
- Mac OS-X" the logs don't go in default logs folder but a user folder: '/Users/renaldobryan/Library/Application Support/Plex Media Server/Logs/Plex Media Scanner (custom ASS).log'. 
- "Feral Hosting Seedbox" error "IOError: (2, 'No such file or directory', '/media/sdt1/jusjtk91/Library/Application Support/Plex Media Server/Logs/Plex Media Scanner (custom ASS).log')".

### Task list
- [ ] Support Media stubs .Disc files ? http://kodi.wiki/view/Media_stubs
- [ ] Shall i write a Movie scanner using the same code? The Plex default movie scanner does an good job i believe ?

Reference for editing Read-Me: [Link to Markdown](https://guides.github.com/features/mastering-markdown/) or https://help.github.com/articles/basic-writing-and-formatting-syntax/

Donation link: https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=S8CUKCX4CWBBG&lc=IE&item_name=ZeroQI&item_number=Absolute%20Series%20Scanner%20%2b%20Http%20AniDB%20Metadata%20Agent&currency_code=EUR&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted
