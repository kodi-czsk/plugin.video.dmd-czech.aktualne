# Video plugin for aktualne.cz

This plugin adds support for online videos from czech website aktualne.cz.
It is based on the code of Štěpán Ort for DVTV. Now DVTV is part of this plugin.
List of shows is generated automatically, so if the new show is added, it should automatically appear.
Fanarts are downloaded automaticaly, icons for Shows are hardcoded in the plugin.

## Settings

* You can choose video quality and format.
* FireTV hack: There is some strange bug, causing desynchronization
of video and audio always in the first video in the playlist. 
By activating FireTV hack, all files are added twice as a playlist and second 
video is then playing without problems. I don't know better solution for now.
Try to activate this hack when you have problems with playing videos.

## To Do
* Add dynamic list of the newest videos across shows
* Add listing by categories
* Add searching

Feel free to suggest more. 

# Video plugin pro aktualne.cz

Tento plugin přidává podporu pro všechna videa z video.aktualne.cz. 
Je založen na ködu od Štěpána Orta pro DVTV. Původní plugin již není potřeba, protože DVTV je jedním z pořadů na aktualne.cz.
Seznam pořadů je automaticky parsován z webu, pokud se tedy objeví nový pořad, měl by automaticky fungovat.
Fanarty jsou stahovány automaticky, narozdíl od ikonek pro pořady, které jsou součástí tohoto pluginu.

## Nastavení

* Preferovaná kvalita videa a formát streamu.
* FireTV hack: Z neznámého důvodu nefungoval plugin na Amazon FireTV. 
U prvního videa v playlistu se vždy kompletně rozsynchronizoval audio s video stopou a přehrávání se ukončilo.
Kupodivu se to neděje u dalších položek v playlistu. Proto když se přehrává pouze jedno video, je přidáno do playlistu dvakrát.
To druhé pak již funguje.
Aktivujte si tento hack, pokud máte problémy s přehráváním videí.

## To Do
* Zobrazit výpis nejnovějších streamů napříš kategoriemi
* Zobrazit videa dle kategorie
* Přidat vyhledávání