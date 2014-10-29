from bs4 import BeautifulSoup
from couchpotato.core.helpers.encoding import tryUrlencode, toUnicode
from couchpotato.core.helpers.variable import tryInt, getIdentifier
from couchpotato.core.logger import CPLog
from couchpotato.core.media._base.providers.torrent.base import TorrentProvider
from couchpotato.core.media.movie.providers.base import MovieProvider
import traceback
import re

log = CPLog(__name__)

class TorrentDetails(object):

   def __init__(self, seeders, leechers, permalink, downlink, torrentID, torrentName, filesize, freeleech, qualityEncode):
      self.seeders = seeders
      self.leechers = leechers
      self.permalink = permalink
      self.downlink = downlink
      self.torrentID = torrentID
      self.torrentName = torrentName
      self.filesize = filesize
      self.freeleech = freeleech
      self.qualityEncode = qualityEncode


class TehConnection(TorrentProvider, MovieProvider):

    urls = {
        'baseurl': 'https://tehconnection.eu',
        'login': 'https://tehconnection.eu/login.php',
        'login_check': 'https://tehconnection.eu/index.php',
        'search': 'https://tehconnection.eu/torrents.php?searchstr=%s',
    }

    http_time_between_calls = 1 #seconds

    def _searchOnTitle(self, title, movie, quality, results):

        torrentlist = []

        if self.conf('only_freeleech'):
            onlyFreelech = True
        else:
            onlyFreelech = False

        if self.conf('only_verified'):
            onlyVerified = True
        else:
            onlyVerified = False


        if not '/logout.php' in self.urlopen(self.urls['login'], data = self.getLoginParams()).lower():
            log.info('problems logging into tehconnection.eu')
            return []

        data = self.getHTMLData(self.urls['search'] % tryUrlencode(getIdentifier(movie)))
        if data:
            try:
                resultsTable = BeautifulSoup(data).find('table', attrs = {'id' : 'browse_torrent_table'})
                if resultsTable is None:
                    log.info('movie not found on TehConnection')
                    return []

                pagelinkdata = resultsTable.find("a", { "title" : "View Torrent" })
                torrentpage = (pagelinkdata.attrs['href']).strip()
                indivTorrData = self.getHTMLData(self.urls['baseurl'] + (torrentpage))

                soup = BeautifulSoup(indivTorrData)
                items = soup.findAll("div", { "class" : "torrent_widget box pad" })
                for item in items:

                    torrentData = TorrentDetails(0, 0, '', '', 0, '', '', False, False)


                    detailstats = item.find("div", { "class" : "details_stats" })

                    #seeders
                    seed = detailstats.find("img", { "title" : "Seeders" }).parent
                    torrentData.seeders = ((seed.text).strip())

                    #leechers
                    leech = detailstats.find("img", { "title" : "Leechers" }).parent
                    torrentData.leechers = ((leech.text).strip())

                    #permalink
                    perma = detailstats.find("a", { "title" : "Permalink" })
                    torrentData.permalink = self.urls['baseurl'] + perma.attrs['href']

                    #download link
                    downlo = detailstats.find("a", { "title" : "Download" })
                    torrentData.downlink = self.urls['baseurl'] + downlo.attrs['href']

                    #Torrent ID
                    m = re.search(r'\d+$', torrentData.permalink)
                    torrentData.torrentID = (int(m.group()) if m else None)

                    #TorrentName
                    namedata = item.find("div", { "id" : "desc_%s" % torrentData.torrentID })
                    torrentData.torrentName = ((namedata.text).splitlines()[1]).strip()

                    #FileSize
                    sizedata = item.find("div", { "class" : "details_title" })
                    sizefile = ((sizedata.text).splitlines()[3]).replace("(","").replace(")","").strip()
                    torrentData.filesize = sizefile

                    #FreeLeech
                    freeleechdata = item.find("span", { "class" : "freeleech" })
                    if freeleechdata is None:
                        torrentData.freeleech = False
                    else:
                        torrentData.freeleech = True

                    #QualityEncode
                    qualityenc = detailstats.find("img", { "class" : "approved" })
                    if qualityenc is None:
                        torrentData.qualityEncode = False
                    else:
                        torrentData.qualityEncode = True

                    #Test if the Freelech or Verified boxes have been checked & add depending
                    if (onlyFreelech == False) or (onlyFreelech == True and torrentData.freeleech == True):
                        #Only Freelech is switched off OR only Freelech is ON and the torrent is a freelech, so safe to add to results
                        if (onlyVerified == False) or (onlyVerified == True and torrentData.qualityEncode == True):
                            #Only Verified is switched off OR only Verified is ON and the torrent is verified, so safe to add to results
                            torrentlist.append(torrentData)


                for torrentFind in torrentlist:
                    log.info('TehConnection found ' + torrentFind.torrentName)
                    results.append({
                        'leechers': torrentFind.leechers,
                        'seeders': torrentFind.seeders,
                        'name': torrentFind.torrentName,
                        'url': torrentFind.downlink,
                        'detail_url': torrentFind.permalink,
                        'id': torrentFind.torrentID,
                        'size': self.parseSize(torrentFind.filesize)
                    })

            except:
                log.error('Failed getting results from %s: %s', (self.getName(), traceback.format_exc()))


    def getLoginParams(self):
        return {
            'username': self.conf('username'),
            'password': self.conf('password'),
            'submit': 'Log In!',
        }

    def loginSuccess(self, output):
        return True

