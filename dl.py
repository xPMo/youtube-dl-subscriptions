#! /usr/bin/env python3
import opml
import feedparser
import youtube_dl
from glob import glob
from pprint import pprint
from threading import Thread

from time import time, mktime, strptime
from datetime import datetime

def parse_one(url, videos, ptime):
    feed = feedparser.parse(url)
    for j in range(0,len(feed['items'])):
        timef = feed['items'][j]['published_parsed']
        dt = datetime.fromtimestamp(mktime(timef))
        if dt > ptime:
            videos.append(feed['items'][j]['link'])

if len(glob('last.txt')) == 0:
    f = open('last.txt', 'w')
    f.write(str(time()))
    print('Initialized a last.txt file with current timestamp.')
    f.close()

else:
    f = open('last.txt', 'r')
    content = f.read()
    f.close()

    outline = opml.parse('subs.xml')

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

    # feed just checked, so we can write out a new "last checked"
    # (Another video may be published while we download)
    f = open('last.txt', 'w')
    f.write(str(ftime))
    f.close()

    if len(videos) == 0:
        print('Sorry, no new video found')
    else:
        print(str(len(videos))+' new videos found')

    ydl_opts = {}

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(videos)

