from bs4 import BeautifulSoup
from couchpotato.core.helpers.encoding import tryUrlencode, toUnicode
from couchpotato.core.helpers.variable import tryInt, getIdentifier
from couchpotato.core.logger import CPLog
from couchpotato.core.media._base.providers.torrent.base import TorrentProvider
from couchpotato.core.media.movie.providers.base import MovieProvider
import traceback
import re
import time

log = CPLog(__name__)


class TorrentDetails(object):
    def __init__(self, seeders, leechers, permalink, downlink, torrentid, torrentname, filesize, freeleech,
                 qualityencode, torrentscore, datetorrentadded, ageindays):
        self.seeders = seeders
        self.leechers = leechers
        self.permalink = permalink
        self.downlink = downlink
        self.torrentid = torrentid
        self.torrentname = torrentname
        self.filesize = filesize
        self.freeleech = freeleech
        self.qualityencode = qualityencode
        self.torrentscore = torrentscore
        self.datetorrentadded = datetorrentadded
        self.ageindays = ageindays


class PorkParts(TorrentProvider, MovieProvider):

    http_time_between_calls = 2  # seconds

    def __init__(self):

        super(PorkParts, self).__init__()

        _BASE_URL = self.conf('base_url')
        self.urls = {
            'baseurl': _BASE_URL,
            'login': '{0}/login.php'.format(_BASE_URL),
            'login_check': '{0}/index.php'.format(_BASE_URL),
            'search': '{0}/torrents.php?searchstr=%s&action=basic&filter_cat[9]=1'.format(_BASE_URL),
        }


    def _searchOnTitle(self, title, movie, quality, results):

        torrentlist = []

        if self.conf('only_freeleech'):
            onlyfreeleech = True
        else:
            onlyfreeleech = False

        if self.conf('only_verified'):
            onlyverified = True
        else:
            onlyverified = False

        if not '/logout.php' in self.urlopen(self.urls['login'], data=self.getLoginParams()).lower():
            log.info('problems logging in')
            return []

        data = self.getHTMLData(self.urls['search'] % tryUrlencode(getIdentifier(movie)))
        if data:
            try:
                resultstable = BeautifulSoup(data).find('table', attrs={'id': 'torrent_table'})
                if resultstable is None:
                    log.info('movie not found')
                    return []

                #pagelinkdata = resultstable.find("a", {"title": "View Torrent"})
                #torrentpage = (pagelinkdata.attrs['href']).strip()
                #indivtorrdata = self.getHTMLData(self.urls['baseurl'] + torrentpage)

                #soup = BeautifulSoup(indivtorrdata)
                #items = soup.findAll("div", {"class": "torrent_widget box pad"})

                items = resultstable.findAll("tr", {"class": "torrent"})
                for item in items:

                    torrentdata = TorrentDetails(0, 0, '', '', 0, '', '', False, False, 0, 0, 0)

                    columns = item.findAll('td')

                    #detailstats = item.find("div", {"class": "details_stats"})

                    # seeders
                    seed = columns[7] #detailstats.find("img", {"title": "Seeders"}).parent
                    torrentdata.seeders = (seed.text.strip())

                    # leechers
                    leech = columns[8] #detailstats.find("img", {"title": "Leechers"}).parent
                    torrentdata.leechers = (leech.text.strip())

                    #permalink
                    perma = item.find("a", {"title": "View Torrent"}) #detailstats.find("a", {"title": "Permalink"})
                    torrentdata.permalink = self.urls['baseurl'] + perma.attrs['href']

                    #download link
                    downlo = item.find("a", {"title": "Download"})
                    torrentdata.downlink = self.urls['baseurl'] + downlo.attrs['href']

                    #Torrent ID
                    m = re.search(r'\d+$', torrentdata.permalink)
                    torrentdata.torrentid = (int(m.group()) if m else None)

                    #torrentname
                    #namedata = item.find("div", {"id": "desc_%s" % torrentdata.torrentid})
                    torrentdata.torrentname = perma.text.strip()

                    #FileSize
                    sizedata = columns[4] #item.find("div", {"class": "details_title"})
                    sizefile = sizedata.text.strip() #(sizedata.text.splitlines()[3]).replace("(", "").replace(")", "").strip()
                    torrentdata.filesize = sizefile

                    #FreeLeech
                    #freeleechdata = item.find("span", {"class": "freeleech"})
                    #if freeleechdata is None:
                    #    torrentdata.freeleech = False
                    #else:
                    #    torrentdata.freeleech = True
                    torrentdata.freeleech = "[Freeleech!]" in columns[1].text

                    #QualityEncode
                    if "BluRay" in columns[1].text or "DVDRip" in columns[1].text:
                        torrentdata.torrentname += " HQ"
                        torrentdata.qualityencode = True
                    else:
                        torrentdata.qualityencode = False

                    #TorrentScore
                    torrscore = 0
                    if torrentdata.qualityencode is True:
                        torrscore += self.conf('extrascore_qualityencode')
                    if torrentdata.freeleech is True:
                        torrscore += self.conf('extrascore_freelech')
                    torrentdata.torrentscore = torrscore

                    #datetorrentadded
                    #try:
                    #    addeddata = item.find("div", {"class": "details"})
                    #    addedparagraphdata = addeddata.find("p", {"style": "float: left"})
                    #    dateaddedstr = (addedparagraphdata.find('span')['title']).strip()
                    #    addeddatetuple = time.strptime(dateaddedstr, '%b %d %Y, %H:%M')
                    #    torrentdata.datetorrentadded = int(time.mktime(addeddatetuple))
                    #except:
                    #    log.error('Unable to convert datetime from %s: %s', (self.getName(), traceback.format_exc()))
                    #    torrentdata.datetorrentadded = 0

                    #ageindays
                    #torrentdata.ageindays = int((time.time() - torrentdata.datetorrentadded) / 24 / 60 / 60)

                    #Test if the Freelech or Verified boxes have been checked & add depending
                    if (onlyfreeleech is False) or (onlyfreeleech is True and torrentdata.freeleech is True):
                        #Only Freelech is switched off OR only Freelech is ON and the torrent is a freeleech,
                        # so safe to add to results
                        if (onlyverified is False) or (onlyverified is True and torrentdata.qualityencode is True):
                            #Only Verified is switched off OR only Verified is ON and the torrent is verified,
                            # so safe to add to results
                            torrentlist.append(torrentdata)

                log.info('Number of torrents found = ' + str(len(torrentlist)))

                for torrentfind in torrentlist:
                    log.info('PorkParts found ' + torrentfind.torrentname)
                    results.append({
                        'leechers': torrentfind.leechers,
                        'seeders': torrentfind.seeders,
                        'name': torrentfind.torrentname,
                        'url': torrentfind.downlink,
                        'detail_url': torrentfind.permalink,
                        'id': torrentfind.torrentid,
                        'size': self.parseSize(torrentfind.filesize),
                        'score': torrentfind.torrentscore,
                        'date': torrentfind.datetorrentadded,
                        'age': torrentfind.ageindays
                    })

            except:
                log.error('Failed getting results from %s: %s', (self.getName(), traceback.format_exc()))


    def getLoginParams(self):
        return {
            'username': str(self.conf('username')),
            'password': str(self.conf('password')),
            'login': 'Log In!',
        }

    def loginSuccess(self, output):
        return True
