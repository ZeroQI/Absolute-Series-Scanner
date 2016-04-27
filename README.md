Functionalities<BR>
===============
<UL>
      <LI> Grouping folders in parent directory and brackets with number to order series chronologically ([1], [2]), grouping folder need to be added as root folder</LI>
      <LI> Seasons folders with serie name afterwards (Season 1 Zero no tsukaima), including "Series" appelation</LI>
      <LI> Include all files not recognised as Season 0 episode 501+</LI>
      <LI> AniDB Specials (OP, NCOP, ED, NCED, Sxx, etc...)</LI>
      <LI> Specials chars handling ("CØDE：BREAKER") and files starting with dots (".Hack")</LI>
      <LI> Movie files in Series libraries accepted if they have the same name as the folder (or 01|ep 01|s01e01)</LI>
      <LI> Console output supported if launched from command line</LI>
      <LI> ".plexignore" file supported</LI>
      <LI> "keep_zero_size_files" file in logs folder to allow using zero size files, otherwise skip them</LI>
      <LI> "X-Plex-Token.id"      file in logs folder to create a scanner log per library</LI>
      <LI> "Plex Media Scanner (custom ASS).log" in Plex Logs folder with one line for the serie folder and per file</LI>
      <LI> "Plex Media Scanner (custom ASS) - filelist.log" contain all filenames so i can reproduce your library with a batch file after converting to utf-8 with notepad</LI>
      <LI> support id files "anidb.id", "tvdb.id", "tmdb.id" (might have to make thetvdb serie id "tsdb.id")</LI>
      <LI> support id files in folder names like "tv show [anidb-12345]" or "Serie name [tvdb-1234567]"</LI>
  </UL>

Forcing the metadata id and display conversion without renaming files
=====================================================================
You can use anidb|tvdb|tvdb2|tvdb3.id in serie folder or serie Extras folder to force the id, or use the following at the end of the folder name, there is a space in front of the bracket
<UL>
      <LI>" [anidb-xxxxx]" for anime in absolute numbering</LI>
      
      <LI>" [tvdb-xxxxx]" for tvdb season numbering. You can put separate sereis as seasons
      SAO can be split into "Season 1 - Sword Art Online" (1-25), "Season 2 - Alfheim & Gun Gale Online (1-25)</LI>
      
      <LI>" [tvdb2-xxxxx]" for absolute numbering displayed as tvdb numbering, episode number resets to 1 each season, for series like Sword art Online<BR>
      SAO can be numbered 1-49, but will automatically be split into Season 1 (1-25) and Season 2 (1-25).</LI>
      
      <LI>" [tvdb3-xxxxx]" for absolute numbering episodes displayed using tvdb season numbering but keeping the absolute episode number (aka Hybrid numbering) for long running series like One piece<BR>
      One Piece can be numbered 1-700+ and will be automatically split into seasons while keeping the ep number intact without havingto create seasons in the real folder</LI>
</UL>
tvdb2: SAO can be numbered 1-50, but will automatically be split into Season 1 (1-25) and Season 2 (1-25).

tvdb3: One Piece can be numbered 1-700+ and will be automatically split into seasons. There is no need to separate the files into folders.
Naming Conventions Rules<BR>
========================

<UL>
  <LI> Naming convention for Plex: (which this scanner kinda improve allowing more)
    <UL>
      <LI> https://support.plex.tv/hc/en-us/sections/200059498-Naming-and-Organizing-TV-Shows</LI>
    </UL>
  <LI> Naming convention for XBMC:  http://wiki.xbmc.org/index.php?title=Naming_video_files/TV_shows</LI>
</UL>

How to name the file ?
======================

   <CODE>Example: Optional: Grouping Folder / Show Name / Season 1 / Show Name s01e01-e02 - pt1.ext</CODE>
   <BR>
<TABLE>
<THEAD>
<TR> <TH> File naming convention </TH> <TH> Template / Folder </TH> <TH>Exemple </TH> </TR>
</THEAD>
<TBODY>
<TR> <TD> Splitting folders:     </TD> <TD> 0-9                 </TD> <TD> 0-9, A,...,Z folder. Add EACH as folder. Do not use the parent folder </TD> </TR>
<TR> <TD> Episode Name Pattern:  </TD> <TD> Season %S/%SN s%0Se%0E </TD> <TD> Season 2/Show Name s02e03.ext </TD> </TR>
<TR> <TD> Multi-Episode style:   </TD> <TD> Extend              </TD> <TD> Season 2/Show Name s02e03-04-05.ext </TD> </TR>
<TR> <TD> Multi-part episodes:   </TD> <TD> cdX, discX, diskX, dvdX, partX, ptX </TD> <TD> Season 2/Show Name s02e03 - pt1.ext </TD> </TR>
<TR> <TD> Multi-Media Version:   </TD> <TD> Movie Name (year) - 1080p.ext </TD> <TD> Movie Name (year) - 1080p.ext </TD> </TR>
<TR> <TD> Specials scrapped:     </TD> <TD> Specials, Season 0  </TD> <TD> s00e01/OP1/Ed3a/NCOP/S01/S1.ext </TD> </TR>
<TR> <TD> Other non scrapped:    </TD> <TD> Extras              </TD> <TD> Extras/Show Name xxxx.ext </TD> </TR>
<TR> <TD> BD rips                </TD> <TD> /path/to/series-library/Series Name Season 2 </TD> <TD> Series.Name.Disc1.S02.E01-E12/BDMV/STREAM </TD> </TR>
</TBODY>
</TABLE>

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
   
Where to get the perfect title ?
================================

<UL>
  <LI> Series: TheTVDB.com or TVrage or TheMovieDB, TV database, will not store boxset specific files(nor sport or porn for tvdb)</LI>
  <LI> Movies: TheMovieDB.org, naming convention: "Movie Title (Year).ext" </LI>
  <LI> Anime:  AniDB.net, the Anime main title is generally the best, or romaji (x-jat) </LI>
</UL>

Local metadata
==============
Use local media assets. If it doen't work with Hama, please let me know <BR />
https://support.plex.tv/hc/en-us/articles/200220717-Local-Media-Assets-TV-Shows

Big Storage Folder Structure ?
==============================
I thought my folder structure could help many.
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
      <LI> Maps </LI>
      <LI> Textures </LI>
    </UL>
    
  <LI> Scans </LI>
    <UL>
      <LI> Art Books </LI>
      <LI> Xx Comics </LI>
      <LI> Xx Mangas </LI>
    </UL>
</UL>
