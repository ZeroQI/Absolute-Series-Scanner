Functionalities<BR>
===============
<UL>
      <LI> Logs in Plex Logs folder "Plex Media Scanner (custom ASS).log" with one line per folder, season folder and per file</LI>
      <LI> Grouping folders in parent directory and brackets with number to order series chronologically ([1], [2])</LI>
      <LI> Seasons folders with serie name afterwards, including "Series" appelation</LI>
      <LI> AniDB Specials (OP, NCOP, ED, NCED, Sxx, etc...)</LI>
      <LI> Specials chars handling ("CØDE：BREAKER") and files starting with dors (".Hack")</LI>
      <LI> Movie files in Series accepted if they have the same name as the folder (or 01|ep 01|s01e01)</LI>
      <LI> Episodes from different series in single folder (dump folder) supported</LI>
      <LI> Console output supported if launched from command line</LI>
  </UL>
Naming Conventions Rules<BR>
========================

<UL>
  <LI> Naming convention for Plex:
    <UL>
      <LI> https://oldwiki.plexapp.com/index.php?title=Media_Naming_and_Organization_Guide</LI>
      <LI> https://support.plex.tv/hc/en-us/categories/200028098-Media-Preparation</LI>
    </UL>
  <LI> Naming convention for XBMC:  http://wiki.xbmc.org/index.php?title=Naming_video_files/TV_shows</LI>
</UL>

How to name the file ?
======================

   <CODE>Example: Show Name / Season 1 / Show Name s01e01-e02 - pt1.ext</CODE>
   <BR>
<TABLE>
<THEAD>
<TR> <TH> File naming convention </TH> <TH> Template            </TH> <TH>Exemple </TH> </TR>
</THEAD>
<TBODY>
<TR> <TD> Splitting folders:     </TD> <TD> 0-9                 </TD> <TD> 0-9, A,...,Z folder. Add EACH as folder. Do not use the parent folder </TD> </TR>
<TR> <TD> Episode Name Pattern:  </TD> <TD> Season %S/%SN s%0Se%0E </TD> <TD> Season 2/Show Name s02e03.ext </TD> </TR>
<TR> <TD> Multi-Episode style:   </TD> <TD> Extend              </TD> <TD> Season 2/Show Name s02e03-04-05.ext </TD> </TR>
<TR> <TD> Multi-part episodes:   </TD> <TD> cdX, discX, diskX, dvdX, partX, ptX </TD> <TD> Season 2/Show Name s02e03 - pt1.ext </TD> </TR>
<TR> <TD> Multi-Media Version:   </TD> <TD> Movie Name (year) - 1080p.ext </TD> <TD> Movie Name (year) - 1080p.ext </TD> </TR>
<TR> <TD> Specials scrapped:     </TD> <TD> Specials, Season 0  </TD> <TD> Specials/Show Name s00e01.ext </TD> </TR>
<TR> <TD> Other non scrapped:    </TD> <TD> Extras              </TD> <TD> Extras/Show Name xxxx.ext </TD> </TR>
<TR> <TD> BD rips                </TD> <TD> /path/to/series-library/Series Name Season 2 </TD> <TD> Series.Name.Disc1.S02.E01-E12/BDMV/STREAM </TD> </TR>
</TBODY>
</TABLE>

<TABLE>
<THEAD>
<TR> <TH> Data type </TH> <TH> Source                </TH> <TH>           Comment </TH> </TR>
</THEAD>
<TBODY>
<TR> <TD> fanart    </TD> <TD> title-fanart-1.ext or art/backdrop/background/fanart.ext (same level as Video TS)  </TD> </TR>
<TR> <TD> poster    </TD> <TD> Serie  (Show name-1.jpg folder, poster, show.ext (jpg, jpeg,png,tbn)),  Season          Season-1a.ext in season folder       </TD> <TR>          
<TR> <TD> Banner    </TD> <TD> Serie Name-bannera.ext or banner.jpg </TD> </TR>
<TR> <TD> theme song  </TD><TR>
<TR> <TD> .plexignore </TD><TR>
</TBODY>
</TABLE>
   
Where to get the perfect title ?
================================

<UL>
  <LI> Series: TheTVDB.com, TV database, will not store boxset specific files, nor sport or porn </LI>
  <LI> Movies: TheMovieDB.org, naming convention: "Movie Title (Year).ext" </LI>
  <LI> Anime:  AniDB.net, the Anime main title is generally the best, or romaji (x-jat) </LI>
</UL>

Local metadata
==============
In progress using HAMA

TeraStorage Folder Structure ?
==============================
Implied is original language, folder named dubbed otherwise

<UL>
  <LI> Series </LI>
    <UL>
      <LI> Xx </LI>
      <LI> Xx Documentaries </LI>
      <LI> Xx Reality-Shows </LI>
      <LI> Xx Stand-Up Comedy </LI>
      <LI> Xx Dubbed </LI>
    </UL>

  <LI> Movies </LI>
    <UL>
      <LI> Xx </LI>
      <LI> Xx Documentaries </LI>
      <LI> Xx Reality-Shows </LI>
      <LI> Xx Stand-Up Comedy </LI>
    </UL>
    
  <LI> Anime </LI>
    <UL>
      <LI> Xx </LI>
      <LI> Xx Hentai </LI>
      <LI> Xx Kids </LI>
      <LI> Xx Movies </LI>
      <LI> Xx Series </LI>
    </UL>
    
  <LI> Knowledge </LI>
    <UL>
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
