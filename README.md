#Absolute Series Scanner

A Plex series scanner choose the following from the folders and file names:
- Serie name
- Season number
- Episode number
- Episode title (not filled by plex default series scanner, until the metadata agent refreshes it)
- Episode year

The files choosen by the scanner will be showing in Plex.
The Plex metadata agent will find metadata for files showing.

###Which Metadata/Title source to select?
- Anime:     AniDB.net, Hama use an offline title database from them ("main title" is the best, or romaji "x-jat". "En" titles have hoorrors like "bombshells from the sky" for "Asobi ni Iku yo!" serie). AniDB use small posters, no background. Hama use ScudLee's xml mapping files to crosss reference the anidb id to the tvdb series
- TV Series: TheTVDB.com or TVrage or TheMovieDB (yep support series now), no db site will store (DVD) boxset specific files (nor sport or porn for tvdb). TVDB has high resolution posters, background images, screenshots, and episodes summaries, all lacking from AniBD.net, but they do not carry porn series so no metadata for this type.
- Movies:    TheMovieDB.org, naming convention: "Movie Title (Year).ext" </LI>

Grouping folder
- If you use "Grouping folder / Show Name / Season 1 / Show Name e01.ext" convention from the root, it will now be skipped.
  You can just add it as additionnal root folder in the library: "D:/Anime/Dragon Ball/" for "D:/Anime/Dragon Ball/[2] Dragon Ball Z" folder for example...

###Forcing the series ID
You can specify the guid to use the following way:
- In custom search serie name by adding " [guid_type-id_number]" at the end
- In Serie folder name by adding " [guid_type-id_number]" at the end
- In guid_type.id inside serie folder with the id in it (ex: tvdb.id file with tvdbid "114801" without double quotes in it)

Hama supports the following guid_type:
- anidb for AniDB.net
- tvdb  for TheTVDB.com (and the behaviour changing modes: tvdb2, tvdb3, tvdb4)
- tmdb  For TheMovieDB.net (and the serie part of TheMovieDB: tsdb)
- imdb  For the International Movie DataBase (ids starts with "tt...")

You can have **absolutely numbered series** (i.e. without season number apart from Specials/season 0) being **displayed in Plex with seasons** without the need to rename the files with season numbering or creating season folders and moving absolutely numbered episodes inside by using the following custom modes, and episodes will be displayed as:

<TABLE>
<THEAD> <TR> <TH> guid_type </TH> <TH> Seasons numbering   </TH> <TH>Episodes numbering</TH> <TH>Use case (example)</TH></TR></THEAD>
<TBODY> <TR> <TD> tvdb2     </TD> <TD> TVDB                </TD> <TD>Season            </TD> <TD>Multiple single season series (Sword Art online)</TD> </TR>
        <TR> <TD> tvdb3     </TD> <TD> TVDB                </TD> <TD>Absolute          </TD> <TD>Long series (Detective Conan)</TD> </TR>
        <TR> <TD> tvdb4     </TD> <TD> Custom/Arc database </TD> <TD>Absolute          </TD> <TD>Long series with arc (one piece, dragon ball)</TD> </TR>
</TBODY>
</TABLE>

Examples of force  guid in all modes and their applications:
- " [anidb-xxxxx]" for anime in absolute numbering. Force the anidb serie id
- " [tvdb-xxxxxx]" for tvdb season numbering. You can put separate anidb series as seasons as per tvdb numbering.
    SAO can be split at file level into "Season 1 - Sword Art Online" [1-25], "Season 2 - Alfheim & Gun Gale Online [1-25]".
- " [tvdb2-xxxxx]" for absolute numbering displayed virtually as tvdb numbering, episode number resets to 1 each season, for series like Sword art Online(1-50, will be split into Season 1 [1-25] and Season 2 [1-25])
- " [tvdb3-xxxxx]" for absolute numbering episodes displayed virtually using tvdb season numbering for long running series like One piece (1-700+, will be split into seasons while keeping the absolute episode number intact without having to create seasons in the real folder
- " [tvdb4-xxxxx]" for absolute numbering episodes displayed using series arc as season for long running series with arcs like Dragon Ball Kai, or separated anidb series considered as half seasons by thetvdb (like 'Seraph of the end' numbered 1-24 splitted into 2 seasons).
  The arc definition to split into seasons the absolute numbering is done using the following order:
    - Seasons folders manually created by the user with absolute numbered episodes inside (seasons already mapped manually)
    - in a local "tvdb.mapping" file inside serie folder
      FORMAT: <season_num>|<starting_ep_num>|<ending_ep_num>|<freeform_text_naming_the_season>(optional)
    - without doing anything using the online arc database [github tvdb4.mapping.xml](https://github.com/ZeroQI/Absolute-Series-Scanner/blob/master/tvdb4.mapping.xml)
      Format:<PRE><CODE>
&lt;tvdb4entries&gt;
&lt;anime tvdbid="289906" name="Seraph of the End"&gt;
01|001|012|Vampire Reign
02|013|024|Battle in Nagoya
&lt;/anime&gt;
</CODE></PRE>

Series
- Specials chars handling ("CØDE：BREAKER") and files starting with dots (".Hack")
- Movie files in Series libraries accepted if they are in a folder with the same name (or 01|ep 01|s01e01, or " - Complete Movie" at the end)

Season folders
- Seasons folders can have serie name afterwards ("Zero no tsukaima / Season 1 Zero no tsukaima")
- Files in "Extras" folders will be ignored.
- Allow grouping in Ark xxxxx folders transparently with seasons folders inside, or within a season folder
- Specials go in "Specials" or "Season 0" folders.
  - Single seasons series will follow anidb specials numbering (unless specific tvdb guid forced).
  - Multiple seasons series will follow tvdb specials numbering
  - You can use Anidb numbering for specials (OP1a, NCOP, etc...) or explicitely label them as follow (s00e101, etc...).
  - Include all files not recognised as Season 0 episode 501+

<TABLE> 
<THEAD> <TR> <TH> Type     </TH> <TH> Internal letter </TH> <TH>  Episode number   </TH> </TR> </THEAD>
<TBODY> <TR> <TD> OPs      </TD> <TD> C               </TD> <TD>  Episodes 101-150 </TD> </TR>
        <TR> <TD> EDs      </TD> <TD> C               </TD> <TD>  Episodes 151-200 </TD> </TR>
        <TR> <TD> Trailers </TD> <TD> T               </TD> <TD>  Episodes 201-300 </TD> </TR>
        <TR> <TD> OPs/EDs  </TD> <TD> P               </TD> <TD>  Episodes 301-400 </TD> </TR>
        <TR> <TD> Others   </TD> <TD> O               </TD> <TD>  Episodes 401-500 </TD> </TR>
        <TR> <TD> unmapped </TD> <TD>                 </TD> <TD>  Episodes 501-600 </TD> </TR> </TBODY>
</TABLE>

###File Naming Conventions
This scanner supports absolute and season numbering, but here are two references for guidelines
- Naming convention for Plex: https://support.plex.tv/hc/en-us/sections/200059498-Naming-and-Organizing-TV-Shows
- Naming convention for XBMC:  http://wiki.xbmc.org/index.php?title=Naming_video_files/TV_shows

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

###Local metadata
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

###Logs
Absolute series Scanner uses a pre-made list of folders to try to locate Plex Logs folder. 
If custom logs are not present, then either you created a library using default Plex scanner and not my "Absolute Series Scanner" or you have an unknown Logs folder location and will need to forward me the path to add in the source code...
If the scanner crash, you will get either no files (library creation) or no change (library already created) and will need to attach the Plex log "Plex Media Scanner.log"

List of logs files:
- Plex Media Scanner (custom ASS) - Library_Name.log contain all folders and files processed in a readable fashion, perfect for troubleshooting scanner issues.
- Plex Media Scanner (custom ASS) - Library_Name - filelist Root_Folder_name.log contain all files in the root folder, so i can re-create your library with zero size files. I use a batch file to recreate a user's library after converting to utf-8 with notepad
- Plex Media Scanner.log - Standard Plex Scanner Log, contain crash error in case of a bug in the scanner code

List of configuration files, to put in logs folder, can be found the (blank) config files in GitHub > ASS > releases > logs.7z
- no_timestamp: when present, remove timestamps from the scanner log
- keep_zero_size_files: when present, accept empty (zero size) files as valid, good when reproducing issues with a fake library
- season_from_folder: when present, use the season from the folder instead of the file when a conflict arises
- "X-Plex-Token.id: Allow to get the library name to get a log per library (optional). Fill with plex token by following https://support.plex.tv/hc/en-us/articles/204059436-Finding-your-account-token-X-Plex-Token. **_Do not share that file when uploading the whole Logs folders_**

###Task list
- [ ] no_timestamp: should we remove the file and put no timestamp by default in the source?
- [ ] keep_zero_size_files: should we accept that as the default (use it a lot for reproducing issues) ?
- [ ] season_from_folder: when present, use the season from the folder instead of the file when a conflict arises. Remove ?
- [ ] Support Media stubs .Disc files ? http://kodi.wiki/view/Media_stubs
- [ ] Shall i write a Movie scanner using the same code? The Plex default movie scanner does an good job i believe ?

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

Reference: [Link to Markdown](https://guides.github.com/features/mastering-markdown/) or https://help.github.com/articles/basic-writing-and-formatting-syntax/
