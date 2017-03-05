from xmltv import Writer
import urllib2
import json
import datetime
from settings import *
import os.path


class Epg(object):
    channels = []

    def __init__(self, url):
        self.url = url
        self.prepare_channels()

    def xmltv_time(self, timestamp):
        return datetime.datetime.fromtimestamp(int(timestamp)).strftime("%Y%m%d%H%M%S") + '+0200'

    def format_date(self, date):
        return date.strftime("%d-%m-%Y")

    def format_programme_url(self, date, slug):
        return 'https://www.tv24.lt/programme/listing/none/' + date + '?filter=channel&subslug=' + slug


    def date_list(self):
        result = []
        date = datetime.datetime.now()
        result.append(self.format_date(date))
        for i in range(DAYS):
            date += datetime.timedelta(days=1)
            result.append(self.format_date(date))
        return result


    def prepare_channels(self):
        data = json.load(urllib2.urlopen(self.url), 'utf-8')
        for provider in data:
            for channel in provider['channels']:
                info = {}
                info['id'] = channel['id']
                info['name'] = channel['name']
                info['logo'] = channel['logo_64']
                info['slug'] = channel['slug']
                if info not in self.channels:
                    self.channels.append(info)


    def programme_url_list(self):
        result = []
        dates = self.date_list()
        for channel in self.channels:
            result += [self.format_programme_url(i, channel['slug']) for i in dates]
        return result

    def tv_programme(self):
        result = []
        url_list = self.programme_url_list()
        for url in url_list:
            data = json.load(urllib2.urlopen(url), 'utf-8')
            for programme in data['schedule']['programme']:
                data = {}
                data.setdefault('channel', programme['channel']['slug'])
                data.setdefault('start', self.xmltv_time(programme['start_unix']))
                data.setdefault('stop', self.xmltv_time(programme['stop_unix']))
                data.setdefault('title',[(programme['title'], '')])
                data.setdefault('desc', [(programme['description'], '')])
                result.append(data)
        return result


    def tv_channels(self):
        result = []
        for channel in self.channels:
            info = {}
            info.setdefault('display-name', [(channel['name'], '')])
            info.setdefault('id', channel['slug'])
            info.setdefault('icon', [{'src': 'https://cdn.tvstart.com/img/channel/' + channel['logo']}])
            result.append(info)
        return result

if __name__ == '__main__':
    w = Writer(encoding="UTF-8",
               date=datetime.datetime.today().strftime("%Y%m%d%H%M%S %z"),
               source_info_url="http://tv24.lt",
               source_info_name="tv24",
               generator_info_name="python-xmltv",
               generator_info_url="http://www.funktronics.ca/python-xmltv")

    epg = Epg('https://www.tv24.lt/data/channels/visi')

    for c in epg.tv_channels():
        w.addChannel(c)
    for p in epg.tv_programme():
        w.addProgramme(p)
    complete_name = os.path.join(SAVE_PATH, FILENAME + '.xml')
    w.write(complete_name)