# coding: utf-8
import os
import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import urllib
import urllib2
import re
from stats import *
import HTMLParser
import xml.etree.ElementTree as ET
import email.utils as eut
import time

reload(sys)
sys.setdefaultencoding("utf-8")

_rssUrl_ = 'http://video.aktualne.cz/rss/'

_addon_ = xbmcaddon.Addon('plugin.video.dmd-czech.aktualne')
_lang_   = _addon_.getLocalizedString
_scriptname_ = _addon_.getAddonInfo('name')
_baseurl_ = 'http://video.aktualne.cz/'
_homepage_ = 'http://video.aktualne.cz/forcedevice/smart/'
_UserAgent_ = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
_quality_ = _addon_.getSetting('quality')
_format_ = 'video/' + _addon_.getSetting('format').lower()
_firetvhack_ = _addon_.getSetting('firetvhack') == "true"
home = _addon_.getAddonInfo('path')
_icon_ = xbmc.translatePath( os.path.join(home, 'resources/media/ikona-aktualne-57x57.png' ) )
_mediadir_ = xbmc.translatePath( os.path.join(home, 'resources/media/' ) )
_htmlParser_ = HTMLParser.HTMLParser()
_dialogTitle_ = 'Aktuálně TV'

fanart = xbmc.translatePath( os.path.join( home, 'fanart.jpg' ) )

if _quality_ == '':
    xbmc.executebuiltin("XBMC.Notification('Doplněk Aktuálně','Vyberte preferovanou kvalitu!',30000,"+_icon_+")")
    _addon_.openSettings() 

def log(msg, level=xbmc.LOGDEBUG):
	if type(msg).__name__=='unicode':
		msg = msg.encode('utf-8')
        xbmc.log("[%s] %s"%(_scriptname_,msg.__str__()), level)

def logDbg(msg):
	log(msg,level=xbmc.LOGDEBUG)

def logErr(msg):
	log(msg,level=xbmc.LOGERROR)

addon_handle = int(sys.argv[1])

xbmcplugin.setContent(addon_handle, 'episodes')

def showNotification(message, icon):
	xbmcgui.Dialog().notification(_dialogTitle_, message, icon)

def showErrorNotification(message):
	showNotification(message, 'error')

def fetchUrl(url, label):
	logDbg("fetchUrl " + url + ", label:" + label)
	pDialog = xbmcgui.DialogProgress()
	pDialog.create(_dialogTitle_, label)
	httpdata = ''	
	try:
		resp = urllib2.urlopen(url)
		size = resp.info().getheader('Content-Length', 9000)
		count=0
		for line in resp:
			if pDialog.iscanceled():
				resp.close()
				pDialog.close()
				return None
			count += len(line)
			httpdata += line
			percentage = int((float(count)/float(size))*100)
			pDialog.update(percentage)
	except:
		httpdata = None
		showErrorNotification(_lang_(30002))
	finally:
		resp.close()
		pDialog.close()	
	return httpdata

def listItems(offset, urladd):
	url = _rssUrl_ + urladd
	if offset > 0:
		url += '?offset=' + str(offset)
	rss = fetchUrl(url, _lang_(30003))
	if (not rss):
		return
	root = ET.fromstring(rss)
	for item in root.find('channel').findall('item'):
		link  = item.find('link').text
		title = item.find('title').text
		description = item.find('description').text
		contentEncoded = item.find('{http://purl.org/rss/1.0/modules/content/}encoded').text
		extra = item.find('{http://i0.cz/bbx/rss/}extra')
		subtype = extra.get('subtype')
		dur = extra.get('duration')
		datetime = eut.parsedate(item.find('pubDate').text.strip())
		date = time.strftime('%d.%m.%Y', datetime)
		image = re.compile('<img.+?src="([^"]*?)"').search(contentEncoded).group(1)
		li = xbmcgui.ListItem(title)
		if dur and ':' in dur:
			l = dur.strip().split(':')
			duration = 0
			for pos, value in enumerate(l[::-1]):
				duration += int(value) * 60 ** pos
			li.addStreamInfo('video', {'duration': duration})
		if subtype == 'playlist':
			li.setLabel2('Playlist')
		li.setThumbnailImage(image)
		li.setIconImage(_icon_)
		li.setInfo('video', {'title': title, 'plot': description, 'date': date})
		li.setProperty('fanart_image',image)
		u=sys.argv[0]+'?mode=10&url='+urllib.quote_plus(link.encode('utf-8'))
		xbmcplugin.addDirectoryItem(handle=addon_handle, url=u, listitem=li)
	o = offset + 30	
	u = sys.argv[0]+'?mode=1&url='+urllib.quote_plus(urladd.encode('utf-8'))+'&offset='+urllib.quote_plus(str(o))
	liNext = xbmcgui.ListItem(_lang_(30006))
	xbmcplugin.addDirectoryItem(handle=addon_handle,url=u,listitem=liNext,isFolder=True)	
	xbmcplugin.endOfDirectory(addon_handle)

def playUrl(url):
	httpdata = fetchUrl(url, _lang_(30004))
	twice = False
	if (not httpdata):
		return
	if httpdata: 
		videos = re.compile('{[^i]*?image.*?sources:[^]]*?][^}]*?}', re.S).findall(httpdata)
		if videos:
			pl=xbmc.PlayList(1)
			pl.clear()
			if _firetvhack_ and len(videos) == 1:
				twice = True        
			for video in videos:
				image = 'http:' + re.compile('image: ?\'([^\']*?)\'').search(video).group(1).strip()
				title = _htmlParser_.unescape(re.compile('title: ?\'([^\']*?)\'').search(video).group(1).strip())
				description = re.compile('description: ?\'([^\']*?)\'').search(video);
				if description:				
					description = _htmlParser_.unescape(description.group(1).strip())
				sources = re.compile('sources: ?(\[[^\]]*?])', re.S).search(video).group(1)
				if sources:		
					versions = re.compile('{[^}]*?}', re.S).findall(sources)
					if versions:
						for version in versions:
							url = re.compile('file: ?\'([^\']*?)\'').search(version).group(1).strip()
							mime = re.compile('type: ?\'([^\']*?)\'').search(version).group(1).strip()
							quality = re.compile('label: ?\'([^\']*?)\'').search(version).group(1).strip()
							li = xbmcgui.ListItem(title)
							li.setThumbnailImage(image)							
							li.addStreamInfo('video', {'language': 'cs'})
							if (quality == _quality_ and mime == _format_):
								xbmc.PlayList(1).add(url, li)
								if twice:
									xbmc.PlayList(1).add(url, li)  					
			xbmc.Player().play(pl)
		else:
			showErrorNotification(_lang_(30005))

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
        return param

def listShows():
    request = urllib2.Request(_homepage_)
    con = urllib2.urlopen(request)
    data = con.read()
    con.close()
    match = re.compile('<a href="/#porady">.+?</a>.+?<ul class="dropdown">(.+?)</ul>', re.DOTALL).findall(data)
    if len(match):
      match2 = re.compile('<li class="menusec-bvs.+?"><a href="/(.+?)/">(.+?)</a></li>').findall(match[0])
      if len(match2) > 1:
          for url2, name in match2:
              addDir(name,url2,1)  
    else:
      #add all without parsing, just in case of the change of the page layout
      addDir(u'DV TV','dvtv',1)
      addDir(u'Petr Čtvrtníček TV','petr-ctvrtnicek-tv',1)
    xbmcplugin.endOfDirectory(addon_handle)
    
def addDir(name,url,mode):
    iconimage = _mediadir_ + url + ".jpg"
    logDbg("addDir(): '"+name+"' url='"+url+"' icon='"+iconimage+"' mode='"+str(mode)+"'")
    u=sys.argv[0]+"?url="+urllib.quote_plus(url.encode('utf-8'))+"&mode="+str(mode)+"&name="+urllib.quote_plus(name.encode('utf-8'))
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)   
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    changer = {
        "zkrotte-sve-penize": "zkrotte-sve-penize.png",
        "ze-sveta": "zesveta.jpg",
        "48-hodin-v": "48-hodin.jpg",
        "ego-night": "egonight.jpg",
    }
    urlfanart = changer.get(url, url + ".jpg")
    liz.setProperty( "Fanart_Image", "http://i0.cz/bbx/video/img/video/porad-d-page-" + urlfanart )
    ok=xbmcplugin.addDirectoryItem(handle=addon_handle,url=u,listitem=liz,isFolder=True)
    return ok
    
    


params=get_params()
url=None
name=None
thumb=None
mode=None
offset=0

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        offset=int(urllib.unquote_plus(params["offset"]))
except:
        pass
        
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass



if mode==None or url==None or len(url)<1:
    STATS("OBSAH", "Function")
    listShows()
    logDbg("List Shows end")
elif mode==1:
    STATS("listItems", "Function")
    listItems(offset, url)
elif mode==10:
    STATS(url, "Item")
    playUrl(url)

