Naming Conventions Rules by ZeroQI
========================

Naming convention - Plex:  https://oldwiki.plexapp.com/index.php?title=Media_Naming_and_Organization_Guide
                           https://support.plex.tv/hc/en-us/categories/200028098-Media-Preparation
Naming convention - XBMC:  http://wiki.xbmc.org/index.php?title=Naming_video_files/TV_shows

How to name the file ?
======================

<CODE>
   Example: Show Name / Season 1 / Show Name s01e01-e02 - pt1.ext
   
   File naming convention   Template                              Exemple
   ======================   ===================================   ==================================================================
   Splitting folders:       0-9                                   0-9, A,...,Z folder. Add EACH as folder. Do not use the parent folder
   ----------------------   -----------------------------------   ------------------------------------------------------------------
   Episode Name Pattern:    Season %S/%SN s%0Se%0E                Season 2/Show Name s02e03.ext
   Multi-Episode style:     Extend                                Season 2/Show Name s02e03-04-05.ext
   Multi-part episodes:     cdX, discX, diskX, dvdX, partX, ptX   Season 2/Show Name s02e03 - pt1.ext
   Multi-Media Version:     Movie Name (year) - 1080p.ext         Movie Name (year) - 1080p.ext         
   Specials scrapped:       Specials, Season 0                    Specials/Show Name s00e01.ext
   Other non scrapped:      Extras                                Extras/Show Name xxxx.ext
   ----------------------   -----------------------------------   ------------------------------------------------------------
   BD rips                                                        /path/to/series-library/Series Name Season 2/Series.Name.Disc1.S02.E01-E12/BDMV/STREAM

   Data type                Source                         Comment
   ======================   ============================   ===================
   fanart                                                  title-fanart-1.ext or art/backdrop/background/fanart.ext (same level as Video TS)
   poster                                                  Show name-1.jpg folder, poster, show.ext (jpg, jpeg,png,tbn)
                            Season                         Season-1a.ext in season folder 
                            Banner                         Serie Name-bannera.ext or banner.jpg
   theme song                                              theme.mp3
   .plexignore
</CODE>
   
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
