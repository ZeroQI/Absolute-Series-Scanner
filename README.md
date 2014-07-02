Naming Conventions Rules by ZeroQI
========================

Naming convention - Plex:  https://oldwiki.plexapp.com/index.php?title=Media_Naming_and_Organization_Guide
                           https://support.plex.tv/hc/en-us/categories/200028098-Media-Preparation
Naming convention - XBMC:  http://wiki.xbmc.org/index.php?title=Naming_video_files/TV_shows

How to name the file ?
======================

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

   
Where to get the perfect title ?
================================

   Data type                Source                         Comment
   ======================   ============================   ===================
   Series                   TheTVDB.com                    TV database, will not store boxset specific files
   Movies                   TheMovieDB.org                 Movie Title (Year)
   Anime                    AniDB.net                      Pick the Anime main title

Local metadata
==============

TeraStorage Folder Structure ?
==============================

Implied is original language, folder named dubbed otherwise

<UL>
  <LI> Series </LI>
</UL>
        . Xx
        . Xx Documentaries
        . Xx Reality-Shows
        . Xx Stand-Up Comedy
        . Xx Dubbed
   . Movies
        . Xx
        . Xx Documentaries
        . Xx Reality-Shows
        . Xx Stand-Up Comedy

   . Anime
        . Xx
        . Xx Hentai
        . Xx Kids
        . Xx Movies
        . Xx Series

   . Knowledge
        . Hobbies
        . Litterature
        . Trainings

   . Music
         . Albums [\Group\Album (Year)]
         . Compilations
         . Karaoke
         . Soundtracks
              . Ads
              . Anime
              . Movies
              . Series
         . Videos
              . Xx
              . Xx Concerts
         . Games
              . Karaoke
              . Guitar
              . Stepmania

   . Pictures
         . Wallpapers
         . Maps
         . Textures

   . Scans
         . Art Books
         . Xx Comics
         . Xx Mangas
