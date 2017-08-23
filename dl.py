#! /usr/bin/env python3

import youtube_dl
from datetime import datetime
from feedparser import parse as feedparse
from opml import parse as opmlp
from optparse import OptionParser
from os import path
from threading import Thread
from time import time, mktime, strptime

def parse_one(url, videos, ptime):
    feed = feedparse(url)
    for j in range(0,len(feed['items'])):
        timef = feed['items'][j]['published_parsed']
        dt = datetime.fromtimestamp(mktime(timef))
        if dt > ptime:
            videos.append(feed['items'][j]['link'])

# Option parsing
parser = OptionParser()
parser.usage = "%prog [-c|--config <config_directory>]"
parser.add_option("-c", "--config", action="store", default=path.expanduser("~/.config/ytdl-subscriptions"), dest="config", help="Config directory, containing last.txt and subs.xml.\nDefaults to ~/.config/ytdl-subscriptions. If not found, the current directory will be used instead.") 

(opts, args) = parser.parse_args()

config = ""
if path.isdir(opts.config):
    config = opts.config

last = path.join(config, 'last.txt')
content = None
try:
    f = open(last)
    content = f.read()
    f.close()
except OSError as e: 
    f = open(last, 'w')
    f.write(str(time()))
    print('Initialized {0} with current timestamp.'.format(last))
    f.close()
    exit(0)
outline = None
subs = path.join(config, 'subs.xml')
try:
    outline = opmlp(subs)
except OSError as e:
    print(e)
    print("The file {0} does not exist or is incorrectly formatted".format(subs))
    exit(1)

ptime = datetime.utcfromtimestamp(float(content))
ftime = time()

urls = []

for i in range(0,len(outline[0])):
    urls.append(outline[0][i].xmlUrl)

threads = []
videos = []
for url in urls:
    new_thread = Thread(target = parse_one, args = (url, videos, ptime))
    new_thread.start()
    threads.append(new_thread)
j = 1
for thread in threads:
    thread.join()
    print('Parsed through channel '+str(j)+' out of '+str(len(urls)), end='\r')
    j += 1

if len(videos) == 0:
    print('Sorry, no new video found')
else:
    print(str(len(videos))+' new videos found')

ydl_opts = {'outtmpl' : '~/Videos/%(uploader)s - %(title)s.%(ext)s'}

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download(videos)

# Write time after successfully downloaded all videos
f = open('last.txt', 'w')
f.write(str(ftime))
f.close()
