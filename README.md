<UL> A Plex series scanner choose the following from the folders and file names:
<LI>Serie name</LI>
<LI>Season number</LI>
<LI>Episode number</LI>
<LI>Episode title (not filled by plex default series scanner, until the metadata agent refreshes it)</LI>
<LI>Episode year</LI>
The files choosen by the scanner will be showing in Plex. If a file is not showing in plex it is the scanner responsability.<BR>

Functionalities<BR>
---------------<BR>
<UL>
      <LI> Grouping folders in parent directory and brackets with number to order series chronologically ([1], [2]), grouping folder need to be added as root folder, like "D:/Anime/Dragon Ball/[2] Dragon Ball Z"</LI>
      <LI> Seasons folders with serie name afterwards ("Zero no tsukaima / Season 1 Zero no tsukaima")</LI>
      <LI> Allow grouping in Ark xxxxx folders transparently</LI>
      <LI> Include all files not recognised as Season 0 episode 501+</LI>
      <LI> AniDB Specials (OP, NCOP, ED, NCED, Sxx, etc...) numbering is supported</LI>
      <LI> Specials chars handling ("CØDE：BREAKER") and files starting with dots (".Hack")</LI>
      <LI> Movie files in Series libraries accepted if they are in a folder with the same name (or 01|ep 01|s01e01, or " - Complete Movie" at the end)</LI>
      <LI> support id files "anidb.id", "tvdb.id", "tvdb2.id", "tvdb3.id", "tmdb.id"</LI>
      <LI> support id files in folder names like "tv show [anidb-12345]" or "Serie name [tvdb-1234567]"</LI>
      <LI> "keep_zero_size_files" file in logs folder to allow using zero size files, otherwise skip them</LI>
      <LI> "Plex Media Scanner (custom ASS).log" in Plex Logs folder with one line for the serie folder and per file</LI>
      <LI> "Plex Media Scanner (custom ASS) - filelist.log" contain all filenames so i can reproduce your library with a batch file after converting to utf-8 with notepad</LI>
  </UL>

Forcing the series ID
---------------------
You can specify the guid to use the following way:
   . In custom search serie name by adding " [guid_type-id_number]" at the end
   . In Serie folder name by adding " [guid_type-id_number]" at the end
   . guid_type.id file inside the serie folder or the "Extras" folder inside it

Hama supports the following guid_type:
   . anidb for AniDB.net
   . tvdb  for TheTVDB.com (and the behaviour changing modes: tvdb2, tvdb3, tvdb4)
   . tmdb  For TheMovieDB.net (and the serie part of TheMovieDB: tsdb)
   . imdb  For the International Movie DataBase (ids starts with "tt...")

You can have <u>absolutely numbered series</u> (i.e. without season number apart from Specials/season 0) being <u>displayed in Plex with seasons</u> without the need to rename the files with season numbering or creating season folders and moving absolutely numbered episodes inside by using the following custom modes, and episodes will be displayed as:

<TABLE>
<THEAD> <TR> <TH> guid_type </TH> <TH> Seasons numbering   </TH> <TH>Episodes numbering</TH> <TH>Use case (example)</TH></TR></THEAD>
<TBODY> <TR> <TD> tvdb2     </TD> <TD> TVDB                </TD> <TD>Season            </TD> <TD>Multiple single season series (Sword Art online)</TD> </TR>
        <TR> <TD> tvdb3     </TD> <TD> TVDB                </TD> <TD>Absolute          </TD> <TD>Long series (Detective Conan)</TD> </TR>
        <TR> <TD> tvdb4     </TD> <TD> Custom/Arc database </TD> <TD>Absolute          </TD> <TD>Long series with arc (one piece, dragon ball)</TD> </TR>
</TBODY>
</TABLE>

<UL>Examples:
      <LI>" [anidb-xxxxx]" for anime in absolute numbering</LI>
      
      <LI>" [tvdb-xxxxx]" for tvdb season numbering. You can put separate sereis as seasons
      SAO can be split into "Season 1 - Sword Art Online" (1-25), "Season 2 - Alfheim & Gun Gale Online (1-25)</LI>
      
      <LI>" [tvdb2-xxxxx]" for absolute numbering displayed as tvdb numbering, episode number resets to 1 each season, for series like Sword art Online<BR>
      SAO can be numbered 1-49, but will automatically be split into Season 1 (1-25) and Season 2 (1-25).</LI>
      
      <LI>" [tvdb3-xxxxx]" for absolute numbering episodes displayed using tvdb season numbering but keeping the absolute episode number (aka Hybrid numbering) for long running series like One piece<BR>
      One Piece can be numbered 1-700+ and will be automatically split into seasons while keeping the ep number intact without havingto create seasons in the real folder</LI>
      
      <LI>" [tvdb4-xxxxx]" for absolute numbering episodes displayed using series arc as season but keeping the absolute
      episode number (aka Hybrid numbering) for long running series with arcs like Dragon Ball Kai, or separated anidb series considered as half seasons by thetvdb (like 'Seraph of the end').<BR>
      The arc definition can be done using:
       <UL>
         <LI>Seasons folders manually created with absolute numbered episodes inside</LI>
         <LI>in a local "tvdb.mapping" file inside the serie folder or "Extras" folder inside it<BR>
             FORMAT: <season_num>|<starting_ep_num>|<ending_ep_num>|<freeform_text_naming_the_season>(optional)</LI>
         <LI>the online arc database (https://github.com/ZeroQI/Absolute-Series-Scanner/blob/master/tvdb4.mapping.xml)<BR>
             Format:<BR>
<PRE><CODE>
&lt;tvdb4entries&gt;
&lt;anime tvdbid="289906" name="Seraph of the End"&gt;
01|001|012|Vampire Reign
02|013|024|Battle in Nagoya
&lt;/anime&gt;
</CODE></PRE>
        </UL>
      </LI>
</UL>
<P>

Logs<BR>
====<BR>
List of configuration files, to put in logs folder.
in releases > logs.7z you will find the blank config files.<BR>
<UL>
  <LI>no_timestamp: when present, remove timestamps from the scanner log</LI>
  <LI>keep_zero_size_files: when present, accept empty files as valid</LI>
  <LI>season_from_folder: when present, use the season from the folder instead of the file when a conflict arises</LI>
  <LI>"X-Plex-Token.id: fill with plex token to create a scanner log per library</LI>
</UL>

List of logs files created by this scanner:
<UL>
  <LI>Plex Media Scanner (custom ASS) - Library_Name.log contain all folders and files processed in a readable fashion, perfect for troubleshooting scanner issues</LI>
  <LI>Plex Media Scanner (custom ASS) - Library_Name - filelist Root_Folder_name.log contain all files in the root folder, so i can re-create your library with zero size files.</LI>
</UL>

Naming Conventions<BR>
==================<BR>
This scanner supports absolute and season numbering, but here are two references for guidelines
<UL>
  <LI> Naming convention for Plex: https://support.plex.tv/hc/en-us/sections/200059498-Naming-and-Organizing-TV-Shows</LI>
  <LI> Naming convention for XBMC:  http://wiki.xbmc.org/index.php?title=Naming_video_files/TV_shows</LI>
</UL>

<CODE>Example: Show Name / Season 1 / Show Name s01e01-e02 - pt1.ext</CODE>
<CODE>Example: Show Name / Show Name EP001.ext</CODE>>

If you use "Grouping folder / Show Name / Season 1 / Show Name s01e01-e02 - pt1.ext" it will now be skipped, so you can just add it as additionnal root folder in the library: "D:/Anime/Jap sub En" and "D:/Anime/Jap sub En/grouping folder" for example

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

You can put specials in "Specials" or "Season 0" folders. "Extras" gets ignored apart for the tvdb.id and anidb.id type files<BR />
You can use Anidb numbering for specials (OP1a, NCOP, etc...) or explicitely label them as follow.<BR />
Series with seasons will follow tvdb specials numbering while others will follow anidb specials numbering (unless specific guid forced). 

<TABLE> 
  <THEAD> <TR> <TH> Type </TH> <TH> Internal letter </TH> <TH>  Episode number </TH> </TR> </THEAD>
<TBODY>
<TR> <TD> OPs      </TD> <TD> C </TD> <TD>  Episodes 101-150 </TD> </TR>
<TR> <TD> EDs      </TD> <TD> C </TD> <TD>  Episodes 151-200 </TD> </TR>
<TR> <TD> Trailers </TD> <TD> T </TD> <TD>  Episodes 201-300 </TD> </TR>
<TR> <TD> OPs/EDs  </TD> <TD> P </TD> <TD>  Episodes 301-400 </TD> </TR>
<TR> <TD> Others   </TD> <TD> O </TD> <TD>  Episodes 401-500 </TD> </TR>
<TR> <TD> unmapped </TD> <TD>   </TD> <TD>  Episodes 501-600 </TD> </TR>
</TBODY>
</TABLE>

Where to get the perfect title ?<BR>
================================<BR>
<UL>
  <LI> Anime:     AniDB.net, the Anime main title is generally the best, or romaji (x-jat). Hama use series titles from there as a base </LI>
  <LI> TV Series: TheTVDB.com or TVrage or TheMovieDB (yep support series now), no db site will store (DVD) boxset specific files(nor sport or porn for tvdb)</LI>
  <LI> Movies:    TheMovieDB.org, naming convention: "Movie Title (Year).ext" </LI>
</UL>

Local metadata<BR>
==============<BR>
It is supported but through "local media assets" agent, add it and and put it before HAMA in the priority order.<BR />
https://support.plex.tv/hc/en-us/articles/200220717-Local-Media-Assets-TV-Shows

<TABLE>
<THEAD>
<TR> <TH> Data type </TH> <TH> Source                </TH> <TH>           Comment </TH> </TR>
</THEAD>
<TBODY>
<TR> <TD> fanart    </TD> <TD> art/backdrop/background/fanart-1.ext</TD> <TD> -1 can be ommited (same level as Video TS) </TD> </TR>
<TR> <TD> Serie poster </TD> <TD> Serie folder: Show name-1/folder/poster/show.ext</TD> <TD> (jpg, jpeg, png, tbn) </TD> <TR>
<TR> <TD> Season poster</TD> <TD> Season folder: Season01a.ext </TD> <TD> (jpg, jpeg, png, tbn) </TD> <TR>          
<TR> <TD> Banner    </TD> <TD> banner/banner-1.jpg  </TD> <TD> </TD> </TR>
<TR> <TD> Theme song</TD> <TD> theme.mp3  </TD> <TD> </TD> <TR>
<TR> <TD> Subtitles </TD> <TD> file name.ext (srt, smi, ssa, ass)  </TD> <TD> </TD><TR>
<TR> <TD> Plexignore files  </TD> <TD> .plexignore  </TD> <TD> </TD> <TR>
</TBODY>
</TABLE>

Folder Structure for massive storages
=====================================
I thought my folder structure could help many, you can store anything in htere
Implied is original language, folder named dubbed otherwise

<UL>
  <LI> Series </LI>
    <UL>
      <LI> Xx (En/Fr/Sp/Jap sub En/...)</LI>
      <LI> Xx Reality-Shows </LI>
      <LI> Xx Stand-Up Comedy </LI>
      <LI> Xx Dubbed </LI>
    </UL>

  <LI> Movies </LI>
    <UL>
      <LI> Xx (En/Fr/Sp/Jap sub En/...)</LI>
      <LI> Xx Reality-Shows </LI>
      <LI> Xx Stand-Up Comedy </LI>
    </UL>
    
  <LI> Anime </LI>
    <UL>
      <LI> Xx (Jap sub En)</LI>
      <LI> Xx Movies (En/Fr/...)</LI>
      <LI> Xx Series (En/Fr/...)</LI>
    </UL>
    
  <LI> Knowledge </LI>
    <UL>
      <LI> Documentaries </LI>
      <LI> Hobbies </LI>
      <LI> Litterature </LI>
      <LI> Trainings </LI>
    </UL>
    
  <LI> Music </LI>
    <UL>
      <LI> Albums [\Group\Album (Year)] </LI>
        <UL>
          <LI> Compilations </LI>
          <LI> Karaoke </LI>
          <LI> Soundtracks </LI>
            <UL>
              <LI> Ads </LI>
              <LI> Anime </LI>
              <LI> Movies </LI>
              <LI> Series </LI>
            </UL>
        </UL>
      <LI> Videos </LI>
        <UL>
          <LI> Xx </LI>
          <LI> Xx Concerts </LI>
        </UL>
      <LI> Games </LI>
        <UL>
          <LI> Karaoke </LI>
          <LI> Guitar </LI>
          <LI> Stepmania </LI>
        </UL>
    </UL>
    
  <LI> Pictures </LI>
    <UL>
      <LI> Wallpapers </LI>
      <LI> Maps       </LI>
      <LI> Textures   </LI>
    </UL>
    
  <LI> Scans </LI>
    <UL>
      <LI> Art Books </LI>
      <LI> Xx Comics </LI>
      <LI> Xx Mangas </LI>
    </UL>

  <LI> Software </LI>
    <UL>
      <LI> Computer                   </LI>
        <UL>
          <LI> 1977 Apple II          </LI>
          <LI> Linux                  </LI>
          <LI> Mac-OS                 </LI>
          <LI> Synology DSM           </LI>
          <LI> Windows                </LI>
        </UL>
      <LI> Console Cartridge          </LI>
      <LI> Console CD                 </LI>
      <LI> Console DVD                </LI>
      <LI> Handheld                   </LI>
      <LI> Multi-Systems (Mame, Mess) </LI>
      <LI> Phone                      </LI>
    </UL>
</UL>
